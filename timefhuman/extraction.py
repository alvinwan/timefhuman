import re
from collections import OrderedDict

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
    is_month_context_token,
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
SEGMENTED_EXTRACTION_LINE_THRESHOLD = 32
SEGMENTED_EXTRACTION_CHAR_THRESHOLD = 1024
LINEWISE_SEGMENT_LINE_THRESHOLD = 8
EXTRACTION_TOKEN_LIMIT = 24
GLOBAL_EXTRACTION_MISS_LIMIT = 65536
DANGLING_TAIL_TOKENS = frozenset({"at", "on", "of", "in", "to", "or", "and", "for", "the", "between", "past"})
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
_GLOBAL_EXTRACTION_MISS_CACHE = OrderedDict()


def _window_tokens(text: str, start_pos: int):
    token_iter = iter(iter_tokens(text, start_pos))
    first = next(token_iter, None)
    if first is None or first[2] != start_pos:
        return []

    tokens = [first]
    pending = None
    while len(tokens) < EXTRACTION_TOKEN_LIMIT:
        token = pending
        if token is None:
            token = next(token_iter, None)
        pending = None
        if token is None:
            break

        gap = text[tokens[-1][3] : token[2]]
        if "\n" in gap or "\r" in gap:
            probe = tokens + [token]
            lookahead = next(token_iter, None)
            if lookahead is not None:
                probe.append(lookahead)
            if not _allows_newline_continuation(probe, len(tokens)):
                break
            tokens.append(token)
            pending = lookahead
            continue

        if token[0] == ".":
            probe = tokens + [token]
            lookahead = next(token_iter, None)
            if lookahead is not None:
                probe.append(lookahead)
            if _is_weekday_period_continuation(probe, 0, len(tokens)):
                tokens.append(token)
                pending = lookahead
                continue
            if lookahead is not None:
                pending = lookahead

        if token[0] in ".?!":
            tokens.append(token)
            break
        if token[0] in ",-" or is_expression_token(token):
            tokens.append(token)
            continue
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

    if _should_segment_extraction(text):
        return _extract_segmented(text, parse_candidate)

    results, saw_plausible_start = _extract_segment(text, parse_candidate, 0)
    if results:
        return results
    if not saw_plausible_start:
        return []
    return None


def _extract_segmented(text: str, parse_candidate):
    results = []
    miss_cache = set()
    saw_plausible_start = False
    saw_unresolved_segment = False
    for segment, offset, line_count in _iter_extraction_segments(text):
        if line_count > LINEWISE_SEGMENT_LINE_THRESHOLD and _is_header_like_segment(segment):
            segment_results, segment_saw_plausible, segment_unresolved = _extract_segment_by_lines(
                segment, parse_candidate, offset, miss_cache
            )
        else:
            segment_results, segment_saw_plausible = _extract_segment(segment, parse_candidate, offset, miss_cache)
            segment_unresolved = segment_results is None

        if segment_results is None:
            saw_unresolved_segment = True
            saw_plausible_start = saw_plausible_start or segment_saw_plausible
            continue

        if segment_unresolved:
            saw_unresolved_segment = True
        results.extend(segment_results)
        saw_plausible_start = saw_plausible_start or segment_saw_plausible

    if results:
        return results
    if not saw_plausible_start:
        return []
    if saw_unresolved_segment:
        return None
    return []


def _extract_segment(text: str, parse_candidate, base_offset: int = 0, miss_cache=None):
    if miss_cache is None:
        miss_cache = set()
    results = []
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
        expression, next_index = _extract_longest_match(tokens, 0, text, parse_candidate, miss_cache, base_offset)
        if expression is None:
            continue

        results.extend(expression)
        cursor = tokens[next_index - 1][3]

    if results:
        return results, saw_plausible_start
    if not saw_plausible_start:
        return [], saw_plausible_start
    return None, saw_plausible_start


def _extract_segment_by_lines(text: str, parse_candidate, base_offset: int, miss_cache):
    results = []
    saw_plausible_start = False
    saw_unresolved_segment = False
    offset = base_offset
    for line in text.splitlines(keepends=True):
        segment = line.rstrip("\r\n")
        if not segment:
            offset += len(line)
            continue
        if _should_skip_header_line(segment):
            offset += len(line)
            continue
        segment_results, segment_saw_plausible = _extract_segment(segment, parse_candidate, offset, miss_cache)
        if segment_results is None:
            saw_unresolved_segment = True
            saw_plausible_start = saw_plausible_start or segment_saw_plausible
            offset += len(line)
            continue
        results.extend(segment_results)
        saw_plausible_start = saw_plausible_start or segment_saw_plausible
        offset += len(line)
    return results, saw_plausible_start, saw_unresolved_segment


def _extract_longest_match(tokens, start_index: int, text: str, parse_candidate, miss_cache, base_offset: int = 0):
    last_candidate = None
    minimum_end_index = start_index + _minimum_candidate_token_count(tokens, start_index)
    for end_index in range(len(tokens), minimum_end_index - 1, -1):
        start = tokens[start_index][2]
        end = tokens[end_index - 1][3]
        candidate = text[start:end].strip()
        if candidate and candidate[-1] in ".?!":
            candidate = candidate[:-1].rstrip()
            end = start + len(candidate)
        if not candidate or candidate == last_candidate:
            continue
        last_candidate = candidate
        if tokens[end_index - 1][1] in DANGLING_TAIL_TOKENS:
            continue
        parse_candidate_text = candidate
        if (
            parse_candidate_text.endswith(",")
            and " " not in parse_candidate_text
            and parse_candidate_text.count(",") == 1
            and any(char.isalpha() for char in parse_candidate_text[:-1])
        ):
            parse_candidate_text = parse_candidate_text[:-1]
        if _should_skip_candidate(text, parse_candidate_text, start, end):
            continue
        if parse_candidate_text in miss_cache:
            continue
        global_miss_key = _global_miss_key(parse_candidate, parse_candidate_text)
        if global_miss_key is not None and global_miss_key in _GLOBAL_EXTRACTION_MISS_CACHE:
            _GLOBAL_EXTRACTION_MISS_CACHE.move_to_end(global_miss_key)
            continue

        try:
            expression = parse_candidate(parse_candidate_text, base_offset + start)
        except (NotImplementedError, OverflowError, ValueError):
            miss_cache.add(parse_candidate_text)
            _remember_global_miss(global_miss_key)
            continue
        if expression is not None:
            if parse_candidate_text != candidate:
                for renderer in expression:
                    if renderer.matched_text_pos is None:
                        continue
                    match_start, match_end = renderer.matched_text_pos
                    renderer.matched_text_pos = (match_start, match_end + 1)
            return expression, end_index
        miss_cache.add(parse_candidate_text)
        _remember_global_miss(global_miss_key)

    return None, start_index + 1


def _minimum_candidate_token_count(tokens, start_index: int):
    token = tokens[start_index][1]
    next_token = tokens[start_index + 1][1] if start_index + 1 < len(tokens) else ""
    next_next_token = tokens[start_index + 2][1] if start_index + 2 < len(tokens) else ""

    if token == "between":
        return 4
    if token == "for":
        if next_token == "the" and next_next_token == "past":
            return 5
        if next_token == "past":
            return 4
        return 3
    if token in {"in", "past"}:
        return 3
    if token in MODIFIER_TO_OFFSET or token in POSITION_TO_DELTA or token in NUMBER_WORDS:
        return 2
    if token.isdigit() and "/" not in token and ":" not in token and "-" not in token and "." not in token:
        return 2
    return 1


def _should_segment_extraction(text: str):
    newline_count = text.count("\n") + text.count("\r")
    return (
        newline_count >= SEGMENTED_EXTRACTION_LINE_THRESHOLD
        and len(text) >= SEGMENTED_EXTRACTION_CHAR_THRESHOLD
    )


def _iter_extraction_segments(text: str):
    lines = text.splitlines(keepends=True)
    chunk = []
    chunk_offset = 0
    offset = 0
    for line in lines:
        if not chunk:
            chunk_offset = offset
        chunk.append(line)
        offset += len(line)
        if line.strip():
            continue
        yield "".join(chunk).rstrip("\r\n"), chunk_offset, len(chunk)
        chunk = []
    if chunk:
        yield "".join(chunk).rstrip("\r\n"), chunk_offset, len(chunk)


def _is_header_like_segment(text: str):
    header_like = 0
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if "@" in stripped:
            header_like += 1
            continue
        colon_index = stripped.find(":")
        if 0 < colon_index <= 24:
            key = stripped[:colon_index]
            if key.replace("-", "").replace("_", "").isalnum():
                header_like += 1
    return header_like >= 4


HEADER_SKIP_KEYS = {
    "message-id",
    "from",
    "to",
    "cc",
    "bcc",
    "mime-version",
    "content-type",
    "content-transfer-encoding",
    "x-from",
    "x-to",
    "x-cc",
    "x-bcc",
    "x-folder",
    "x-origin",
    "x-filename",
}
HEADER_KEEP_KEYS = {"date", "subject"}


def _should_skip_header_line(text: str):
    stripped = text.strip()
    if not stripped:
        return False
    colon_index = stripped.find(":")
    if not (0 < colon_index <= 24):
        return "@" in stripped and stripped.count("@") >= 2
    key = stripped[:colon_index].strip().lower()
    if key in HEADER_KEEP_KEYS:
        return False
    if key in HEADER_SKIP_KEYS:
        return True
    if key.startswith("x-"):
        return True
    return "@" in stripped and stripped.count("@") >= 1
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
    lowered = tokens[index][1]
    next_token = tokens[index + 1][0] if index + 1 < len(tokens) else ""
    next_next_token = tokens[index + 2][0] if index + 2 < len(tokens) else ""
    next_next_next_token = tokens[index + 3][0] if index + 3 < len(tokens) else ""
    if is_plausible_start_tokens(token, next_token, next_next_token, next_next_next_token):
        return True
    if lowered in MONTH_WORDS:
        probe_index = index + 1
        probe_token = next_token
        while probe_token in {".", ","} and probe_index + 1 < len(tokens):
            probe_index += 1
            probe_token = tokens[probe_index][0]
        if probe_token and is_month_context_token(probe_token):
            return True
        return False
    if lowered in WEEKDAY_WORDS:
        probe_index = index + 1
        probe_token = next_token
        while probe_token in {".", ","} and probe_index + 1 < len(tokens):
            probe_index += 1
            probe_token = tokens[probe_index][0]
        if probe_token and is_expression_token(probe_token):
            return True
        return False
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


def _global_miss_key(parse_candidate, candidate: str):
    cache_tag = getattr(parse_candidate, "_cache_tag", None)
    if cache_tag is None:
        return None
    return cache_tag, candidate


def _remember_global_miss(key):
    if key is None:
        return
    _GLOBAL_EXTRACTION_MISS_CACHE[key] = None
    _GLOBAL_EXTRACTION_MISS_CACHE.move_to_end(key)
    if len(_GLOBAL_EXTRACTION_MISS_CACHE) > GLOBAL_EXTRACTION_MISS_LIMIT:
        _GLOBAL_EXTRACTION_MISS_CACHE.popitem(last=False)
