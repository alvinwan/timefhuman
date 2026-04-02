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
    month_number,
    weekday_index,
)
from timefhuman.utils import get_month_mapping, get_timezone_words


__all__ = ("extract_fast", "prefer_extraction")


MERIDIEM_PATTERN = r"(?:[ap](?:\.?m\.?)?)"
TOKEN_PATTERN = re.compile(rf"(?ix)\d+(?:[/:.-]\d+)*(?:{MERIDIEM_PATTERN})?|[a-z]+(?:\.[a-z]+\.?)?|\S")
DAY_SUFFIX_PATTERN = re.compile(r"(?ix)^(?P<day>\d{1,2})(?:st|nd|rd|th)$")
MERIDIEM_ONLY_PATTERN = re.compile(rf"(?ix)^{MERIDIEM_PATTERN}$")
EXPRESSION_CONNECTORS = frozenset({"at", "on", "of", "in", "to", "or", "and", "for", "ago"})
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
    head = stripped.split(None, 1)[0].rstrip(",.?!")
    if head and _is_expression_head(head):
        return False

    previous = None
    count = 0
    for match in TOKEN_PATTERN.finditer(stripped):
        token = match.group(0)
        if previous is not None and _is_plausible_start_tokens(previous.lower(), token.lower()):
            return count - 1 > 0
        previous = token
        count += 1

    if previous is not None and _is_plausible_start_tokens(previous.lower(), ""):
        return count - 1 > 0
    return count > 1


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
    return _is_plausible_start_tokens(token, next_token)


def _is_plausible_start_tokens(token: str, next_token: str):
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
    if "/" in token or ":" in token or "t" in token and "-" in token:
        return True
    if re.fullmatch(rf"(?ix)\d+(?:{MERIDIEM_PATTERN})", token):
        return True
    if token.isdigit():
        return next_token in UNIT_ALIASES or next_token in WEEKDAY_ALIASES or next_token in DATE_NAME_TO_OFFSET or bool(
            MERIDIEM_ONLY_PATTERN.fullmatch(next_token)
        )

    return False
