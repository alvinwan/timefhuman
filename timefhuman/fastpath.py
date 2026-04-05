import re
from datetime import datetime
from functools import lru_cache

from timefhuman.normalizer import is_ambiguous_only, materialize_expression
from timefhuman.semantics import is_rejected_fraction_text
from timefhuman.renderers import (
    tfhAmbiguous,
    tfhDate,
    tfhDatetime,
    tfhList,
    tfhRange,
    tfhTime,
    tfhTimedelta,
    tfhUnknown,
)
from timefhuman.structure_parser import normalize_space, parse_expression
from timefhuman.utils import tfhConfig


__all__ = ("parse_fast",)


CACHEABLE_PARSE_TEXT_LIMIT = 120
_CACHED_TIMEZONE_MAPPING = None
_CACHED_NO_RENDERER = object()
_ABSOLUTE_CACHE_NOW = datetime(2000, 1, 1, 12, 0)
_EXPLICIT_YEAR_PATTERN = re.compile(r"\b\d{4}\b")
_MONTH_NAME_PATTERN = re.compile(
    r"(?ix)\b(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:t(?:ember)?)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)\b"
)
_DATE_ONLY_WORD_PATTERN = re.compile(
    r"(?ix)\b(?:"
    r"today|tomorrow|yesterday|tonight|"
    r"next|last|this|first|second|third|fourth|"
    r"sun(?:day)?|mon(?:day)?|tu(?:esday)?|tue(?:sday)?|wed(?:nesday)?|thu(?:rsday)?|thur(?:sday)?|fri(?:day)?|sat(?:urday)?|"
    r"jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:t(?:ember)?)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?"
    r")\b"
)
_COMPACT_MONTH_YEAR_PATTERN = re.compile(
    r"(?ix)^(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:t(?:ember)?)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)\d{4}$"
)


def parse_fast(text: str, config: tfhConfig, timezone_mapping, start_pos: int = 0):
    global _CACHED_TIMEZONE_MAPPING
    if _CACHED_TIMEZONE_MAPPING is None:
        _CACHED_TIMEZONE_MAPPING = timezone_mapping

    stripped, span_start, span_end = _trimmed_span(text, start_pos)
    if not stripped:
        return None
    if is_rejected_fraction_text(stripped):
        return None

    normalized = normalize_space(stripped)
    if len(normalized) <= CACHEABLE_PARSE_TEXT_LIMIT:
        if _is_absolute_cacheable_text(normalized):
            renderer = _clone_renderer(_parse_renderer_absolute_cached(normalized))
        elif _is_date_only_cacheable_text(normalized):
            renderer = _clone_renderer(
                _parse_renderer_date_cached(
                    normalized,
                    config.now.year,
                    config.now.month,
                    config.now.day,
                    config.direction,
                )
            )
        else:
            renderer = _clone_renderer(
                _parse_renderer_cached(
                    normalized,
                    config.now.year,
                    config.now.month,
                    config.now.day,
                    config.direction,
                )
            )
        if renderer is None:
            return None
    else:
        expression = parse_expression(normalized, config, timezone_mapping, allow_ambiguous=False)
        if expression is None or is_ambiguous_only(expression):
            return None
        renderer = materialize_expression(expression, config.now.year)
    renderer.matched_text_pos = (span_start, span_end)
    return [renderer]


def _trimmed_span(text: str, start_pos: int):
    if not text:
        return "", start_pos, start_pos
    if not text[0].isspace() and not text[-1].isspace() and text[-1] not in ".?!":
        return text, start_pos, start_pos + len(text)

    left = 0
    right = len(text)
    while left < right and text[left].isspace():
        left += 1
    if left == right:
        return "", start_pos + left, start_pos + left

    while right > left and text[right - 1].isspace():
        right -= 1
    while right > left and text[right - 1] in ".?!":
        right -= 1
    while right > left and text[right - 1].isspace():
        right -= 1
    if right <= left:
        return "", start_pos + left, start_pos + left
    return text[left:right], start_pos + left, start_pos + right


@lru_cache(maxsize=16384)
def _parse_renderer_cached(text: str, year: int, month: int, day: int, direction):
    now = datetime(year, month, day, 12, 0)
    config = tfhConfig(now=now, direction=direction)
    expression = parse_expression(text, config, _CACHED_TIMEZONE_MAPPING, allow_ambiguous=False)
    if expression is None or is_ambiguous_only(expression):
        return _CACHED_NO_RENDERER
    return materialize_expression(expression, now.year)


@lru_cache(maxsize=16384)
def _parse_renderer_absolute_cached(text: str):
    config = tfhConfig(now=_ABSOLUTE_CACHE_NOW)
    expression = parse_expression(text, config, _CACHED_TIMEZONE_MAPPING, allow_ambiguous=False)
    if expression is None or is_ambiguous_only(expression):
        return _CACHED_NO_RENDERER
    return materialize_expression(expression, _ABSOLUTE_CACHE_NOW.year)


def _is_absolute_cacheable_text(text: str):
    lower = text.lower()
    if any(unit in lower for unit in (" day", " days", " week", " weeks", " month", " months", " year", " years", " hour", " hours", " minute", " minutes", " second", " seconds")):
        return True
    if _COMPACT_MONTH_YEAR_PATTERN.fullmatch(text):
        return True
    if _EXPLICIT_YEAR_PATTERN.search(text):
        return any(separator in text for separator in "/-.") or _MONTH_NAME_PATTERN.search(text) is not None
    return False


@lru_cache(maxsize=16384)
def _parse_renderer_date_cached(text: str, year: int, month: int, day: int, direction):
    now = datetime(year, month, day, 12, 0)
    config = tfhConfig(now=now, direction=direction)
    expression = parse_expression(text, config, _CACHED_TIMEZONE_MAPPING, allow_ambiguous=False)
    if expression is None or is_ambiguous_only(expression):
        return _CACHED_NO_RENDERER
    return materialize_expression(expression, now.year)


def _is_date_only_cacheable_text(text: str):
    if any(char.isdigit() for char in text) and any(separator in text for separator in "/-."):
        return True
    if re.search(r"(?ix)\b\d{1,2}(?:st|nd|rd|th)\b", text):
        return True
    return _DATE_ONLY_WORD_PATTERN.search(text) is not None


def _clone_renderer(renderer):
    if renderer is _CACHED_NO_RENDERER:
        return None
    if isinstance(renderer, tfhDatetime):
        return tfhDatetime(
            date=_clone_date(renderer.date),
            time=_clone_time(renderer.time),
            tz=renderer.tz,
        )
    if isinstance(renderer, tfhDate):
        return _clone_date(renderer)
    if isinstance(renderer, tfhTime):
        return _clone_time(renderer)
    if isinstance(renderer, tfhTimedelta):
        return tfhTimedelta(days=renderer.days, seconds=renderer.seconds, unit=renderer.unit)
    if isinstance(renderer, tfhAmbiguous):
        return tfhAmbiguous(renderer.value)
    if isinstance(renderer, tfhUnknown):
        return tfhUnknown(renderer.value)
    if isinstance(renderer, tfhList):
        return tfhList([_clone_renderer(item) for item in renderer.items])
    if isinstance(renderer, tfhRange):
        return tfhRange(tuple(_clone_renderer(item) for item in renderer.items))
    raise TypeError(f"Unsupported renderer type: {type(renderer)!r}")


def _clone_date(value):
    if value is None:
        return None
    return tfhDate(
        year=value.year,
        month=value.month,
        day=value.day,
        delta=value.delta,
    )


def _clone_time(value):
    if value is None:
        return None
    return tfhTime(
        hour=value.hour,
        minute=value.minute,
        second=value.second,
        millisecond=value.millisecond,
        meridiem=value.meridiem,
    )
