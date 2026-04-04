from timefhuman.normalizer import is_ambiguous_only, materialize_expression
from timefhuman.semantics import is_rejected_fraction_text
from timefhuman.structure_parser import normalize_space, parse_expression
from timefhuman.utils import tfhConfig


__all__ = ("parse_fast",)


def parse_fast(text: str, config: tfhConfig, timezone_mapping, start_pos: int = 0):
    stripped, span_start, span_end = _trimmed_span(text, start_pos)
    if not stripped:
        return None
    if is_rejected_fraction_text(stripped):
        return None

    expression = parse_expression(normalize_space(stripped), config, timezone_mapping, allow_ambiguous=False)
    if expression is None or is_ambiguous_only(expression):
        return None

    renderer = materialize_expression(expression, config.now.year)
    renderer.matched_text_pos = (span_start, span_end)
    return [renderer]


def _trimmed_span(text: str, start_pos: int):
    stripped = text.strip()
    if not stripped:
        return "", start_pos, start_pos
    leading = len(text) - len(text.lstrip())
    stripped = stripped.rstrip(".?!").rstrip()
    if not stripped:
        return "", start_pos, start_pos
    trailing = leading + len(stripped)
    return stripped, start_pos + leading, start_pos + trailing
