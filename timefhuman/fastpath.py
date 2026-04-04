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


CACHEABLE_PARSE_TEXT_LIMIT = 80
_CACHED_TIMEZONE_MAPPING = None
_CACHED_NO_RENDERER = object()


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
        renderer = _clone_renderer(_parse_renderer_cached(normalized, config.now, config.direction))
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
def _parse_renderer_cached(text: str, now, direction):
    config = tfhConfig(now=now, direction=direction)
    expression = parse_expression(text, config, _CACHED_TIMEZONE_MAPPING, allow_ambiguous=False)
    if expression is None or is_ambiguous_only(expression):
        return _CACHED_NO_RENDERER
    return materialize_expression(expression, now.year)


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
