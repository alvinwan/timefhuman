import re
from functools import lru_cache

from timefhuman.scanner import MERIDIEM_PATTERN
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
    normalize_duration_unit,
    supports_numeric_date_text,
)
from timefhuman.utils import get_month_mapping, get_timezone_words


__all__ = (
    "COMPACT_TIME_RANGE_PATTERN",
    "DAY_SUFFIX_PATTERN",
    "DIRECT_START_WORDS",
    "EXPRESSION_WORDS",
    "MERIDIEM_ONLY_PATTERN",
    "MONTH_WORDS",
    "TIMEZONE_WORDS",
    "WEEKDAY_WORDS",
    "is_month_context_token",
    "is_expression_head",
    "is_expression_token",
    "is_month_token",
    "is_plausible_start_tokens",
)


DAY_SUFFIX_PATTERN = re.compile(r"(?ix)^(?P<day>\d{1,2})(?:st|nd|rd|th)$")
MERIDIEM_ONLY_PATTERN = re.compile(rf"(?ix)^{MERIDIEM_PATTERN}$")
COMPACT_TIME_RANGE_PATTERN = re.compile(
    rf"(?ix)^\d{{1,2}}(?::\d{{2}})?(?:{MERIDIEM_PATTERN})?-\d{{1,2}}(?::\d{{2}})?(?:{MERIDIEM_PATTERN})?$"
)

MONTH_WORDS = frozenset(get_month_mapping())
WEEKDAY_WORDS = frozenset(WEEKDAY_ALIASES)
DIRECT_START_WORDS = frozenset(DATE_NAME_TO_OFFSET) | frozenset(TIME_NAME_TO_TEMPLATE) | frozenset(
    DATE_TIME_NAME_TO_TEMPLATE
) | MONTH_WORDS | WEEKDAY_WORDS
EXPRESSION_CONNECTORS = frozenset({"at", "on", "of", "in", "to", "or", "and", "for", "ago", "the", "between"})
EXPRESSION_WORDS = (
    EXPRESSION_CONNECTORS
    | DIRECT_START_WORDS
    | frozenset(MODIFIER_TO_OFFSET)
    | frozenset(POSITION_TO_DELTA)
    | frozenset(NUMBER_WORDS)
    | frozenset(UNIT_ALIASES)
)
TIMEZONE_WORDS = frozenset(get_timezone_words())


def _token_value(token):
    return token[0] if isinstance(token, tuple) else token


def _token_lower(token, lowered: str | None = None):
    if lowered is not None:
        return lowered
    if isinstance(token, tuple):
        return token[1]
    return token.lower()


def is_expression_token(token, lowered: str | None = None):
    token = _token_value(token)
    lowered = _token_lower(token, lowered)
    return _is_expression_token_cached(token, lowered)


@lru_cache(maxsize=8192)
def _is_expression_token_cached(token: str, lowered: str):
    if lowered in EXPRESSION_WORDS or lowered in TIMEZONE_WORDS:
        return True
    if token.isdigit():
        return True
    if re.fullmatch(rf"(?ix)\d+(?:{MERIDIEM_PATTERN})", token):
        return True
    if COMPACT_TIME_RANGE_PATTERN.fullmatch(token):
        return True
    if _has_supported_numeric_separator_shape(token):
        return True
    if "t" in lowered and "-" in token:
        return True
    if MERIDIEM_ONLY_PATTERN.fullmatch(lowered) or DAY_SUFFIX_PATTERN.fullmatch(lowered):
        return True
    if token.isalpha() and token.isupper() and 2 <= len(token) <= 4:
        return True
    return False


def is_expression_head(token):
    token = _token_value(token)
    lowered = _token_lower(token)
    return _is_expression_head_cached(token, lowered)


@lru_cache(maxsize=8192)
def _is_expression_head_cached(token: str, lowered: str):
    if lowered in DIRECT_START_WORDS or lowered in NUMBER_WORDS:
        return True
    if token.isdigit():
        return True
    if COMPACT_TIME_RANGE_PATTERN.fullmatch(token):
        return True
    if _has_supported_numeric_separator_shape(token):
        return True
    if MERIDIEM_ONLY_PATTERN.fullmatch(lowered) or DAY_SUFFIX_PATTERN.fullmatch(lowered):
        return True
    if token.isalpha() and token.isupper() and 2 <= len(token) <= 4:
        return True
    return False


def is_month_token(token):
    return _token_lower(token) in MONTH_WORDS


@lru_cache(maxsize=8192)
def _has_supported_numeric_separator_shape(token: str):
    if not any(char.isdigit() for char in token):
        return False
    if any(separator in token for separator in "/:-"):
        return True
    if "." in token:
        return supports_numeric_date_text(token)
    return False


def is_month_context_token(token: str, lowered: str | None = None):
    lowered = lowered or token.lower()
    return _is_month_context_token_cached(token, lowered)


@lru_cache(maxsize=8192)
def _is_month_context_token_cached(token: str, lowered: str):
    if token.isdigit():
        return True
    if DAY_SUFFIX_PATTERN.fullmatch(lowered):
        return True
    if lowered in NUMBER_WORDS:
        return True
    return _has_supported_numeric_separator_shape(token)


def is_plausible_start_tokens(
    token: str,
    next_token: str,
    next_next_token: str = "",
    next_next_next_token: str = "",
    *,
    lowered: str | None = None,
    next_lowered: str | None = None,
    next_next_lowered: str | None = None,
    next_next_next_lowered: str | None = None,
):
    return _is_plausible_start_tokens_cached(
        token,
        lowered or token.lower(),
        next_token,
        next_lowered or next_token.lower(),
        next_next_token,
        next_next_lowered or next_next_token.lower(),
        next_next_next_token,
        next_next_next_lowered or next_next_next_token.lower(),
    )


@lru_cache(maxsize=16384)
def _is_plausible_start_tokens_cached(
    token: str,
    lowered: str,
    next_token: str,
    next_lower: str,
    next_next_token: str = "",
    next_next_lower: str = "",
    next_next_next_token: str = "",
    next_next_next_lower: str = "",
):
    if lowered in MONTH_WORDS:
        probe_tokens = (next_token, next_next_token, next_next_next_token)
        probe_index = 0
        while probe_index < len(probe_tokens) and probe_tokens[probe_index] in {".", ","}:
            probe_index += 1
        return probe_index < len(probe_tokens) and is_month_context_token(probe_tokens[probe_index])

    if duration_prefix_length((lowered, next_lower, next_next_lower, next_next_next_lower)) > 0:
        return True
    if lowered == "between":
        return is_expression_head(next_token) or duration_prefix_length((next_lower, next_next_lower, next_next_next_lower, "")) > 0
    if lowered.isdigit():
        return (
            normalize_duration_unit(next_token) is not None
            or next_lower in WEEKDAY_ALIASES
            or next_lower in DATE_NAME_TO_OFFSET
            or bool(MERIDIEM_ONLY_PATTERN.fullmatch(next_lower))
        )
    if lowered in DIRECT_START_WORDS or lowered in NUMBER_WORDS:
        return True
    if COMPACT_TIME_RANGE_PATTERN.fullmatch(token):
        return True
    if re.fullmatch(rf"(?ix)\d+(?:{MERIDIEM_PATTERN})", token):
        return True
    if _is_expression_head_cached(token, lowered):
        return True
    if lowered in MODIFIER_TO_OFFSET and (next_lower in WEEKDAY_WORDS or next_lower in MONTH_WORDS):
        return True
    if lowered in POSITION_TO_DELTA and next_lower in WEEKDAY_WORDS:
        return True
    if DAY_SUFFIX_PATTERN.fullmatch(lowered) and next_lower in WEEKDAY_WORDS and next_next_lower in {"of", "in"}:
        return True
    if lowered in NUMBER_WORDS and normalize_duration_unit(next_token) is not None:
        return True
    if COMPACT_TIME_RANGE_PATTERN.fullmatch(token):
        return True
    if re.fullmatch(rf"(?ix)\d+(?:{MERIDIEM_PATTERN})", token):
        return True
    return False
