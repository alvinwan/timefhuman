import re

from timefhuman.semantics import (
    DATE_NAME_TO_OFFSET,
    DATE_TIME_NAME_TO_TEMPLATE,
    MODIFIER_TO_OFFSET,
    NUMBER_WORDS,
    POSITION_TO_DELTA,
    TIME_NAME_TO_TEMPLATE,
    UNIT_ALIASES,
    WEEKDAY_ALIASES,
    duration_prefix_length,
    month_number,
    supports_numeric_date_text,
    weekday_index,
)
from timefhuman.utils import get_month_mapping, get_timezone_words


__all__ = ("extract_fast", "prefer_extraction")


MERIDIEM_PATTERN = r"(?:[ap](?:\.?m\.?)?)"
TOKEN_PATTERN = re.compile(
    rf"(?ix)\d+(?:[/:.-]\d+)*(?:st|nd|rd|th)?(?:{MERIDIEM_PATTERN})?|[a-z]+(?:\.[a-z]+\.?)?|\S"
)
DAY_SUFFIX_PATTERN = re.compile(r"(?ix)^(?P<day>\d{1,2})(?:st|nd|rd|th)$")
MERIDIEM_ONLY_PATTERN = re.compile(rf"(?ix)^{MERIDIEM_PATTERN}$")
COMPACT_TIME_RANGE_PATTERN = re.compile(
    rf"(?ix)^\d{{1,2}}(?::\d{{2}})?(?:{MERIDIEM_PATTERN})?-\d{{1,2}}(?::\d{{2}})?(?:{MERIDIEM_PATTERN})?$"
)
HYPHENATED_NUMERIC_DATE_PATTERN = re.compile(r"^\d{1,4}-\d{1,4}(?:-\d{1,4})?$")
PHONE_LIKE_PATTERN = re.compile(r"^\d{3,4}-\d{4}$|^\d{3}-\d{3}-\d{4}$")
COMPACT_ALNUM_PATTERN = re.compile(r"(?i)^\d{1,4}(?:[a-z]|am|pm|mo)$")
UPPERCASE_COMPACT_SUFFIX_PATTERN = re.compile(r"^\d{1,4}[A-Z]$")
LOWERCASE_SHORT_TIME_PATTERN = re.compile(r"^\d{1,2}[ap]$")
EXPRESSION_CONNECTORS = frozenset({"at", "on", "of", "in", "to", "or", "and", "for", "ago", "the"})
INLINE_PUNCTUATION = frozenset({",", "-"})
TERMINAL_PUNCTUATION = frozenset({".", "?", "!"})
LARGE_DOCUMENT_LINE_THRESHOLD = 1024
LARGE_DOCUMENT_CHAR_THRESHOLD = 262144


def prefer_extraction(text: str):
    stripped = text.strip()
    if not stripped:
        return False
    if (
        stripped.count("\n") + stripped.count("\r") >= LARGE_DOCUMENT_LINE_THRESHOLD
        or len(stripped) >= LARGE_DOCUMENT_CHAR_THRESHOLD
    ):
        return True

    tokens = [(match.group(0), match.start(), match.end()) for match in TOKEN_PATTERN.finditer(stripped)]
    head = tokens[0][0].rstrip(",.?!") if tokens else ""
    if head and _is_expression_head(head):
        return False
    if tokens and _is_plausible_start(tokens, 0):
        return False

    for index in range(1, len(tokens)):
        prev_token = tokens[index - 1][0].lower()
        current_token = tokens[index][0].lower()
        next_token = tokens[index + 1][0].lower() if index + 1 < len(tokens) else ""
        next_next_token = tokens[index + 2][0].lower() if index + 2 < len(tokens) else ""
        if _is_plausible_start_tokens(prev_token, current_token, next_token, next_next_token):
            return index - 1 > 0

    last_token = tokens[-1][0].lower()
    if _is_plausible_start_tokens(last_token, "", "", ""):
        return len(tokens) - 1 > 0

    return len(tokens) > 1


def extract_fast(text: str, parse_candidate):
    tokens = [(match.group(0), match.start(), match.end()) for match in TOKEN_PATTERN.finditer(text)]
    if not tokens:
        return []

    results = []
    saw_plausible_start = False
    index = 0
    while index < len(tokens):
        if not _is_plausible_start(tokens, index):
            index += 1
            continue

        saw_plausible_start = True
        expression, next_index = _extract_longest_match(tokens, index, text, parse_candidate)
        if expression is None:
            index += 1
            continue

        results.extend(expression)
        index = next_index

    if results:
        return results
    if not saw_plausible_start:
        return []
    return None


def _extract_longest_match(tokens, start_index: int, text: str, parse_candidate):
    max_end = _candidate_end_limit(tokens, start_index)
    last_candidate = None
    for end_index in range(max_end, start_index, -1):
        start = tokens[start_index][1]
        end = tokens[end_index - 1][2]
        candidate = text[start:end].strip()
        if candidate and candidate[-1] in ".?!":
            candidate = candidate[:-1].rstrip()
            end = start + len(candidate)
        if not candidate or candidate == last_candidate:
            continue
        last_candidate = candidate
        if _should_skip_candidate(text, tokens, start_index, candidate, start, end):
            continue

        expression = parse_candidate(candidate, start)
        if expression is not None:
            return expression, end_index

    return None, start_index + 1


def _candidate_end_limit(tokens, start_index: int):
    max_end = min(len(tokens), start_index + 8)
    end_index = start_index + 1
    for index in range(start_index + 1, max_end):
        token = tokens[index][0]
        if token in TERMINAL_PUNCTUATION:
            return index + 1
        if token in INLINE_PUNCTUATION or _is_expression_token(token):
            end_index = index + 1
            continue
        break
    return end_index


def _is_expression_token(token: str):
    lowered = token.lower()
    if lowered in EXPRESSION_CONNECTORS:
        return True
    if lowered in DATE_NAME_TO_OFFSET or lowered in TIME_NAME_TO_TEMPLATE or lowered in DATE_TIME_NAME_TO_TEMPLATE:
        return True
    if lowered in MODIFIER_TO_OFFSET or lowered in POSITION_TO_DELTA:
        return True
    if lowered in NUMBER_WORDS or lowered in UNIT_ALIASES or lowered in WEEKDAY_ALIASES:
        return True
    if lowered in get_timezone_words():
        return True
    if month_number(lowered) is not None or weekday_index(lowered) is not None:
        return True
    if lowered.isdigit():
        return True
    if re.fullmatch(rf"(?ix)\d+(?:{MERIDIEM_PATTERN})", token):
        return True
    if COMPACT_TIME_RANGE_PATTERN.fullmatch(token):
        return True
    if any(char.isdigit() for char in token) and any(separator in token for separator in "/:.-"):
        return True
    if "t" in lowered and "-" in token:
        return True
    if MERIDIEM_ONLY_PATTERN.fullmatch(lowered) or DAY_SUFFIX_PATTERN.fullmatch(lowered):
        return True
    if token.isupper() and 2 <= len(token) <= 4:
        return True
    return False


def _is_expression_head(token: str):
    lowered = token.lower()
    if lowered in DATE_NAME_TO_OFFSET or lowered in TIME_NAME_TO_TEMPLATE or lowered in DATE_TIME_NAME_TO_TEMPLATE:
        return True
    if lowered in MODIFIER_TO_OFFSET or lowered in POSITION_TO_DELTA:
        return True
    if lowered in NUMBER_WORDS or lowered in UNIT_ALIASES or lowered in WEEKDAY_ALIASES:
        return True
    if lowered in get_month_mapping():
        return True
    if lowered.isdigit():
        return True
    if COMPACT_TIME_RANGE_PATTERN.fullmatch(token):
        return True
    if any(char.isdigit() for char in token) and any(separator in token for separator in "/:.-"):
        return True
    if MERIDIEM_ONLY_PATTERN.fullmatch(lowered) or DAY_SUFFIX_PATTERN.fullmatch(lowered):
        return True
    if token.isupper() and 2 <= len(token) <= 4:
        return True
    return False


def _is_plausible_start(tokens, index: int):
    token = tokens[index][0].lower()
    next_token = tokens[index + 1][0].lower() if index + 1 < len(tokens) else ""
    next_next_token = tokens[index + 2][0].lower() if index + 2 < len(tokens) else ""
    next_next_next_token = tokens[index + 3][0].lower() if index + 3 < len(tokens) else ""
    return _is_plausible_start_tokens(token, next_token, next_next_token, next_next_next_token)


def _is_plausible_start_tokens(token: str, next_token: str, next_next_token: str = "", next_next_next_token: str = ""):
    if duration_prefix_length([token, next_token, next_next_token, next_next_next_token]):
        return True
    if token in DATE_NAME_TO_OFFSET or token in TIME_NAME_TO_TEMPLATE or token in DATE_TIME_NAME_TO_TEMPLATE:
        return True
    if token in MODIFIER_TO_OFFSET and (weekday_index(next_token) is not None or month_number(next_token) is not None):
        return True
    if token in POSITION_TO_DELTA and weekday_index(next_token) is not None:
        return True
    if month_number(token) is not None or weekday_index(token) is not None:
        return True
    if token in NUMBER_WORDS and next_token in UNIT_ALIASES:
        return True
    if COMPACT_TIME_RANGE_PATTERN.fullmatch(token):
        return True
    if HYPHENATED_NUMERIC_DATE_PATTERN.fullmatch(token):
        return True
    if "." in token and supports_numeric_date_text(token):
        return True
    if "/" in token or ":" in token or "t" in token and "-" in token:
        return True
    if re.fullmatch(rf"(?ix)\d+(?:{MERIDIEM_PATTERN})", token):
        return True
    if token.isdigit():
        return next_token in UNIT_ALIASES or next_token in WEEKDAY_ALIASES or next_token in DATE_NAME_TO_OFFSET or bool(
            MERIDIEM_ONLY_PATTERN.fullmatch(next_token)
        )

    return False


def _should_skip_candidate(text: str, tokens, start_index: int, candidate: str, start: int, end: int):
    if PHONE_LIKE_PATTERN.fullmatch(candidate):
        return True

    if not COMPACT_ALNUM_PATTERN.fullmatch(candidate):
        return False

    before = text[start - 1] if start > 0 else ""
    after = text[end] if end < len(text) else ""
    if before.isalnum() or after.isalnum():
        return True

    if UPPERCASE_COMPACT_SUFFIX_PATTERN.fullmatch(candidate):
        return True

    if LOWERCASE_SHORT_TIME_PATTERN.fullmatch(candidate):
        previous_token = tokens[start_index - 1][0] if start_index > 0 else ""
        if _looks_like_identifier_token(previous_token):
            return True

    return False


def _looks_like_identifier_token(token: str):
    if not token:
        return False
    if any(char.isdigit() for char in token):
        return True
    if token.isupper() and len(token) <= 4:
        return True
    if any(separator in token for separator in "._/-"):
        return True
    return False
