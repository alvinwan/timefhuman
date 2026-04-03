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
    supports_numeric_date_text,
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
DIMENSION_LIKE_PATTERN = re.compile(r"(?i)^\d+\s+[a-z]$")
WEEKDAY_FOLLOWED_BY_DATE_PATTERN = re.compile(
    r"(?ix)^[\s\W]+[a-z]{3,9}\s+\d{1,2}(?:st|nd|rd|th)?(?:\s+\d{4})?(?:\s+at\s+\d{1,2}(?::\d{2})?(?:[ap](?:\.?m\.?)?)?)?"
)
EXPRESSION_CONNECTORS = frozenset({"at", "on", "of", "in", "to", "or", "and", "for", "ago", "the"})
INLINE_PUNCTUATION = frozenset({",", "-"})
TERMINAL_PUNCTUATION = frozenset({".", "?", "!"})
LARGE_DOCUMENT_LINE_THRESHOLD = 1024
LARGE_DOCUMENT_CHAR_THRESHOLD = 262144
MONTH_WORDS = frozenset(get_month_mapping())
WEEKDAY_WORDS = frozenset(WEEKDAY_ALIASES)
DIRECT_START_WORDS = frozenset(DATE_NAME_TO_OFFSET) | frozenset(TIME_NAME_TO_TEMPLATE) | frozenset(
    DATE_TIME_NAME_TO_TEMPLATE
) | MONTH_WORDS | WEEKDAY_WORDS
EXPRESSION_WORDS = (
    EXPRESSION_CONNECTORS
    | DIRECT_START_WORDS
    | frozenset(MODIFIER_TO_OFFSET)
    | frozenset(POSITION_TO_DELTA)
    | frozenset(NUMBER_WORDS)
    | frozenset(UNIT_ALIASES)
)
START_WORDS = DIRECT_START_WORDS | frozenset(MODIFIER_TO_OFFSET) | frozenset(POSITION_TO_DELTA) | frozenset(
    NUMBER_WORDS
) | frozenset({"in", "for", "the", "past"})
DIRECT_START_PATTERN = "|".join(re.escape(word) for word in sorted(DIRECT_START_WORDS | frozenset(MODIFIER_TO_OFFSET) | frozenset(POSITION_TO_DELTA), key=len, reverse=True))
NUMBER_WORD_PATTERN = "|".join(re.escape(word) for word in sorted(NUMBER_WORDS, key=len, reverse=True))
UNIT_WORD_PATTERN = "|".join(re.escape(word) for word in sorted(UNIT_ALIASES, key=len, reverse=True))
WEEKDAY_WORD_PATTERN = "|".join(re.escape(word) for word in sorted(WEEKDAY_ALIASES, key=len, reverse=True))
DATE_WORD_PATTERN = "|".join(re.escape(word) for word in sorted(DATE_NAME_TO_OFFSET, key=len, reverse=True))
START_PATTERN = re.compile(
    rf"(?ix)"
    rf"(?<![a-z0-9])"
    rf"(?:"
    rf"{DIRECT_START_PATTERN}"
    rf"|(?:in|past)\s+(?:\d+|{NUMBER_WORD_PATTERN})"
    rf"|for\s+(?:the\s+past\s+|past\s+)?(?:\d+|{NUMBER_WORD_PATTERN})"
    rf"|(?:\d+|{NUMBER_WORD_PATTERN})\s+(?:{MERIDIEM_PATTERN}|{UNIT_WORD_PATTERN}|{WEEKDAY_WORD_PATTERN}|{DATE_WORD_PATTERN})"
    rf"|\d+(?:[/:.-]\d+)+(?:st|nd|rd|th)?(?:{MERIDIEM_PATTERN}|s|m|h|d|w|mo)?"
    rf"|\d+(?:st|nd|rd|th)"
    rf"|\d+(?:{MERIDIEM_PATTERN}|s|m|h|d|w|mo)"
    rf")"
    rf"(?![a-z])"
)


def _tokenize(text: str):
    return [(match.group(0), match.group(0).lower(), match.start(), match.end()) for match in TOKEN_PATTERN.finditer(text)]


def _window_tokens(text: str, start_pos: int):
    tokens = []
    for match in TOKEN_PATTERN.finditer(text, start_pos):
        if not tokens and match.start() != start_pos:
            return []
        tokens.append((match.group(0), match.group(0).lower(), match.start(), match.end()))
        if len(tokens) >= 8:
            break
    return tokens


def prefer_extraction(text: str):
    stripped = text.strip()
    if not stripped:
        return False
    newline_count = stripped.count("\n") + stripped.count("\r")
    if (
        newline_count >= LARGE_DOCUMENT_LINE_THRESHOLD
        or len(stripped) >= LARGE_DOCUMENT_CHAR_THRESHOLD
    ):
        return True
    if newline_count >= 4:
        return True

    tokens = _tokenize(stripped)
    head = tokens[0][0].rstrip(",.?!") if tokens else ""
    if head and _is_expression_head(head):
        return False
    if tokens and _is_plausible_start(tokens, 0):
        return False

    for index in range(1, len(tokens)):
        prev_token = tokens[index - 1][1]
        current_token = tokens[index][1]
        next_token = tokens[index + 1][1] if index + 1 < len(tokens) else ""
        next_next_token = tokens[index + 2][1] if index + 2 < len(tokens) else ""
        if _is_plausible_start_tokens(prev_token, current_token, next_token, next_next_token):
            return index - 1 > 0

    last_token = tokens[-1][1]
    if _is_plausible_start_tokens(last_token, "", "", ""):
        return len(tokens) - 1 > 0

    return len(tokens) > 1


def extract_fast(text: str, parse_candidate):
    if not text:
        return []

    results = []
    miss_cache = set()
    saw_plausible_start = False
    cursor = 0
    for start_match in START_PATTERN.finditer(text):
        start = start_match.start()
        if start < cursor:
            continue

        tokens = _window_tokens(text, start)
        if not tokens or not _is_plausible_start(tokens, 0):
            continue

        saw_plausible_start = True
        expression, next_index = _extract_longest_match(tokens, 0, text, parse_candidate, miss_cache)
        if expression is None:
            continue

        results.extend(expression)
        cursor = tokens[next_index - 1][3]

    if results:
        return results
    if not saw_plausible_start:
        return []
    return None


def _extract_longest_match(tokens, start_index: int, text: str, parse_candidate, miss_cache):
    max_end = _candidate_end_limit(tokens, start_index, text)
    last_candidate = None
    for end_index in range(max_end, start_index, -1):
        start = tokens[start_index][2]
        end = tokens[end_index - 1][3]
        candidate = text[start:end].strip()
        if candidate and candidate[-1] in ".?!":
            candidate = candidate[:-1].rstrip()
            end = start + len(candidate)
        if not candidate or candidate == last_candidate:
            continue
        last_candidate = candidate
        if _should_skip_candidate(text, candidate, start, end):
            continue
        if candidate in miss_cache:
            continue

        expression = parse_candidate(candidate, start)
        if expression is not None:
            return expression, end_index
        miss_cache.add(candidate)

    return None, start_index + 1


def _candidate_end_limit(tokens, start_index: int, text: str):
    max_end = min(len(tokens), start_index + 8)
    end_index = start_index + 1
    for index in range(start_index + 1, max_end):
        token = tokens[index][0]
        lowered = tokens[index][1]
        gap = text[tokens[index - 1][3] : tokens[index][2]]
        if "\n" in gap or "\r" in gap:
            return end_index
        if token in TERMINAL_PUNCTUATION:
            return index + 1
        if token in INLINE_PUNCTUATION or _is_expression_token(token, lowered):
            end_index = index + 1
            continue
        break
    return end_index


def _is_expression_token(token: str, lowered: str | None = None):
    lowered = token.lower() if lowered is None else lowered
    if lowered in EXPRESSION_WORDS or lowered in get_timezone_words():
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
    if lowered in EXPRESSION_WORDS:
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
    token = tokens[index][1]
    next_token = tokens[index + 1][1] if index + 1 < len(tokens) else ""
    next_next_token = tokens[index + 2][1] if index + 2 < len(tokens) else ""
    next_next_next_token = tokens[index + 3][1] if index + 3 < len(tokens) else ""
    return _is_plausible_start_tokens(token, next_token, next_next_token, next_next_next_token)


def _is_plausible_start_tokens(token: str, next_token: str, next_next_token: str = "", next_next_next_token: str = ""):
    if _has_duration_prefix(token, next_token, next_next_token, next_next_next_token):
        return True
    if token in DIRECT_START_WORDS:
        return True
    if token in MODIFIER_TO_OFFSET and (next_token in WEEKDAY_WORDS or next_token in MONTH_WORDS):
        return True
    if token in POSITION_TO_DELTA and next_token in WEEKDAY_WORDS:
        return True
    if token in NUMBER_WORDS and next_token in UNIT_ALIASES:
        return True
    if COMPACT_TIME_RANGE_PATTERN.fullmatch(token):
        return True
    if HYPHENATED_NUMERIC_DATE_PATTERN.fullmatch(token):
        return True
    if "." in token and any(char.isdigit() for char in token) and supports_numeric_date_text(token):
        return True
    if any(char.isdigit() for char in token) and ("/" in token or ":" in token or ("t" in token and "-" in token)):
        return True
    if re.fullmatch(rf"(?ix)\d+(?:{MERIDIEM_PATTERN})", token):
        return True
    if token.isdigit():
        return next_token in UNIT_ALIASES or next_token in WEEKDAY_ALIASES or next_token in DATE_NAME_TO_OFFSET or bool(
            MERIDIEM_ONLY_PATTERN.fullmatch(next_token)
        )

    return False


def _has_duration_prefix(token: str, next_token: str, next_next_token: str, next_next_next_token: str):
    if token == "in" or token == "past":
        return _is_duration_value_token(next_token)
    if token == "the":
        return next_token == "past" and _is_duration_value_token(next_next_token)
    if token != "for":
        return False
    if next_token == "the":
        return next_next_token == "past" and _is_duration_value_token(next_next_next_token)
    if next_token == "past":
        return _is_duration_value_token(next_next_token)
    return _is_duration_value_token(next_token)


def _is_duration_value_token(token: str):
    return token.isdigit() or token in NUMBER_WORDS


def _should_skip_candidate(text: str, candidate: str, start: int, end: int):
    before = text[start - 1] if start > 0 else ""
    after = text[end] if end < len(text) else ""

    if PHONE_LIKE_PATTERN.fullmatch(candidate):
        return True

    if candidate.isalpha() and (before == "-" or after == "-"):
        return True

    if DIMENSION_LIKE_PATTERN.fullmatch(candidate) and (before == ":" or after == ":"):
        return True

    if candidate.rstrip(".,").lower() in WEEKDAY_WORDS and WEEKDAY_FOLLOWED_BY_DATE_PATTERN.match(text[end : end + 32]):
        return True

    if not COMPACT_ALNUM_PATTERN.fullmatch(candidate):
        return False

    if before.isalnum() or after.isalnum():
        return True

    if UPPERCASE_COMPACT_SUFFIX_PATTERN.fullmatch(candidate):
        return True

    if LOWERCASE_SHORT_TIME_PATTERN.fullmatch(candidate):
        previous_token = _previous_token(text, start)
        if _looks_like_identifier_token(previous_token):
            return True

    return False


def _previous_token(text: str, start: int):
    prefix_start = max(0, start - 64)
    previous = ""
    for match in TOKEN_PATTERN.finditer(text, prefix_start, start):
        previous = match.group(0)
    return previous


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
