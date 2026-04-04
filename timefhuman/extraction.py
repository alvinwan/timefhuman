import re

from timefhuman.scanner import (
    MERIDIEM_PATTERN,
    first_token,
    iter_tokens,
)
from timefhuman.semantics import (
    DATE_NAME_TO_OFFSET,
    MODIFIER_TO_OFFSET,
    NUMBER_WORDS,
    POSITION_TO_DELTA,
    UNIT_ALIASES,
    WEEKDAY_ALIASES,
    is_duration_value_token,
    normalize_duration_unit,
    supports_numeric_date_text,
)
from timefhuman.token_classifier import (
    DAY_SUFFIX_PATTERN,
    DIRECT_START_WORDS,
    MERIDIEM_ONLY_PATTERN,
    MONTH_WORDS,
    TIMEZONE_WORDS,
    WEEKDAY_WORDS,
    is_expression_head,
    is_expression_token,
    is_plausible_start_tokens,
)


__all__ = ("extract_fast", "prefer_extraction")


HYPHENATED_NUMERIC_DATE_PATTERN = re.compile(r"^\d{1,4}-\d{1,4}(?:-\d{1,4})?$")
PHONE_LIKE_PATTERN = re.compile(r"^\d{3,4}-\d{4}$|^\d{3}-\d{3}-\d{4}$")
REFERENCE_LIKE_NUMERIC_DATE_PATTERN = re.compile(r"^\d{1,2}-\d{1,2}-\d{3}$")
BARE_HYPHEN_NUMERIC_PATTERN = re.compile(r"^\d{1,2}-\d{1,2}$")
SLASH_FRACTION_PATTERN = re.compile(r"^\d+/\d+$")
COMPACT_ALNUM_PATTERN = re.compile(r"(?i)^\d{1,4}(?:[a-z]|am|pm|mo)$")
LOWERCASE_SHORT_TIME_PATTERN = re.compile(r"^\d{1,2}[ap]$")
LARGE_DOCUMENT_LINE_THRESHOLD = 1024
LARGE_DOCUMENT_CHAR_THRESHOLD = 262144
EXTRACTION_TOKEN_LIMIT = 24
START_WORDS = DIRECT_START_WORDS | frozenset(MODIFIER_TO_OFFSET) | frozenset(POSITION_TO_DELTA) | frozenset(
    NUMBER_WORDS
) | frozenset({"in", "dans", "for", "the", "past", "between"})
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
    rf"|(?:in|dans|past)\s+(?:\d+|{NUMBER_WORD_PATTERN})"
    rf"|for\s+(?:the\s+past\s+|past\s+)?(?:\d+|{NUMBER_WORD_PATTERN})"
    rf"|between\s+\S+"
    rf"|(?:\d+|{NUMBER_WORD_PATTERN})\s+(?:{MERIDIEM_PATTERN}|{UNIT_WORD_PATTERN}|{WEEKDAY_WORD_PATTERN}|{DATE_WORD_PATTERN})"
    rf"|\d+(?:[/:.-]\d+)+(?:st|nd|rd|th)?(?:{MERIDIEM_PATTERN}|s|m|h|d|w|mo)?"
    rf"|\d+(?:st|nd|rd|th)"
    rf"|\d+(?:{MERIDIEM_PATTERN}|s|m|h|d|w|mo)"
    rf")"
    rf"(?![a-z])"
)
def _window_tokens(text: str, start_pos: int):
    tokens = []
    for token in iter_tokens(text, start_pos):
        if not tokens and token[2] != start_pos:
            return []
        tokens.append(token)
        if len(tokens) >= EXTRACTION_TOKEN_LIMIT:
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

    if START_PATTERN.match(stripped):
        return False

    head_token = first_token(stripped)
    head = head_token[0].rstrip(",.?!") if head_token else ""
    if head and is_expression_head(head):
        return False

    start_match = START_PATTERN.search(stripped)
    if start_match is not None:
        return start_match.start() > 0

    return any(char.isspace() for char in stripped)


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
    max_end = min(len(tokens), start_index + EXTRACTION_TOKEN_LIMIT)
    end_index = start_index + 1
    for index in range(start_index + 1, max_end):
        gap = text[tokens[index - 1][3] : tokens[index][2]]
        if ("\n" in gap or "\r" in gap) and not _allows_newline_continuation(tokens, index):
            return end_index
        if _is_weekday_period_continuation(tokens, start_index, index):
            end_index = index + 1
            continue
        if tokens[index][0] in ".?!":
            return index + 1
        if tokens[index][0] in ",-" or is_expression_token(tokens[index]):
            end_index = index + 1
            continue
        break
    return end_index


def _allows_newline_continuation(tokens, index: int):
    if index <= 0 or index >= len(tokens):
        return False

    previous = tokens[index - 1][0]
    current = tokens[index][0]
    next_token = tokens[index + 1][0] if index + 1 < len(tokens) else ""
    next_lower = tokens[index + 1][1] if index + 1 < len(tokens) else ""

    if (HYPHENATED_NUMERIC_DATE_PATTERN.fullmatch(previous) or supports_numeric_date_text(previous)) and (
        re.fullmatch(rf"(?ix)\d+(?:{MERIDIEM_PATTERN})", current)
        or (current.isdigit() and MERIDIEM_ONLY_PATTERN.fullmatch(next_lower))
    ):
        return True

    previous_lower = tokens[index - 1][1]
    current_lower = tokens[index][1]
    if previous_lower in TIMEZONE_WORDS and current_lower in TIMEZONE_WORDS:
        return True
    if re.fullmatch(rf"(?ix)\d+(?::\d{{2}})?(?:{MERIDIEM_PATTERN})", previous) and current_lower in TIMEZONE_WORDS:
        return True

    return False


def _is_weekday_period_continuation(tokens, start_index: int, index: int):
    if tokens[index][0] != "." or index <= start_index:
        return False
    previous = tokens[index - 1][1].rstrip(".,")
    if previous not in WEEKDAY_WORDS:
        return False
    if index + 1 >= len(tokens):
        return False
    next_token = tokens[index + 1][0]
    next_lower = tokens[index + 1][1]
    return next_token == "," or is_expression_token(next_token, next_lower)


def _is_plausible_start(tokens, index: int):
    token = tokens[index][0]
    next_token = tokens[index + 1][0] if index + 1 < len(tokens) else ""
    next_next_token = tokens[index + 2][0] if index + 2 < len(tokens) else ""
    next_next_next_token = tokens[index + 3][0] if index + 3 < len(tokens) else ""
    if is_plausible_start_tokens(token, next_token, next_next_token, next_next_next_token):
        return True
    if HYPHENATED_NUMERIC_DATE_PATTERN.fullmatch(token):
        return True
    if "." in token and any(char.isdigit() for char in token) and supports_numeric_date_text(token):
        return True
    if any(char.isdigit() for char in token) and ("/" in token or ":" in token or ("t" in token.lower() and "-" in token)):
        return True
    return False


def _is_duration_value_token(token: str):
    return is_duration_value_token(token)


def _should_skip_candidate(text: str, candidate: str, start: int, end: int):
    before = text[start - 1] if start > 0 else ""
    after = text[end] if end < len(text) else ""

    if PHONE_LIKE_PATTERN.fullmatch(candidate):
        return True
    if REFERENCE_LIKE_NUMERIC_DATE_PATTERN.fullmatch(candidate):
        return True
    if BARE_HYPHEN_NUMERIC_PATTERN.fullmatch(candidate):
        previous_token = _previous_token(text, start)
        next_token = _next_token(text, end)
        if _looks_like_reference_token(previous_token) or _looks_like_reference_token(next_token):
            return True

    if SLASH_FRACTION_PATTERN.fullmatch(candidate):
        previous_token = _previous_token(text, start)
        next_token = _next_token(text, end).lower().strip(".,:;)")
        if previous_token.isdigit() or next_token in {"percent", "%", "in", "inch", "inches"}:
            return True

    if candidate.isalpha() and (before == "-" or after == "-"):
        return True

    if not COMPACT_ALNUM_PATTERN.fullmatch(candidate):
        return False

    if before.isalnum() or after.isalnum():
        return True

    if LOWERCASE_SHORT_TIME_PATTERN.fullmatch(candidate):
        previous_token = _previous_token(text, start)
        if _looks_like_identifier_token(previous_token):
            return True

    return False


def _previous_token(text: str, start: int):
    prefix_start = max(0, start - 64)
    previous = ""
    for token in iter_tokens(text, prefix_start, start):
        previous = token[0]
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


def _next_token(text: str, end: int):
    window_end = min(len(text), end + 64)
    for token in iter_tokens(text, end, window_end):
        if token[0].strip():
            return token[0]
    return ""


def _looks_like_reference_token(token: str):
    if not token:
        return False
    lowered = token.strip(".,:;()[]{}").lower()
    if not lowered:
        return False
    if lowered in {"article", "articles", "section", "sections", "series", "figure", "figures", "rcw", "wac"}:
        return True
    return token[:1].isupper() and lowered not in MONTH_WORDS and lowered not in WEEKDAY_WORDS
