import re
from datetime import timedelta

from timefhuman.renderers import tfhTime, tfhTimedelta
from timefhuman.semantics import (
    NUMBER_WORDS,
    TIME_NAME_TO_TEMPLATE,
    UNIT_ALIASES,
    build_time,
    clone_time,
    is_rejected_compact_meridiem_text,
    normalize_duration_unit,
    strip_duration_prefix,
    timedelta_for_unit,
)
from timefhuman.utils import Direction


__all__ = ("parse_duration_atom", "parse_time_atom")


MERIDIEM_PATTERN = r"(?:[ap](?:\.?m\.?)?)"
TIME_PATTERN = re.compile(
    rf"(?ix)^"
    rf"(?P<hour>\d{{1,2}})"
    rf"(?::(?P<minute>\d{{1,2}})"
    rf"(?::(?P<second>\d{{1,2}})(?:\.(?P<millisecond>\d{{1,6}}))?)?"
    rf")?"
    rf"\s*(?P<meridiem>{MERIDIEM_PATTERN})?$"
)
OCLOCK_PATTERN = re.compile(rf"(?ix)^(?P<hour>\d{{1,2}})\s*o'?clock\s*(?P<meridiem>{MERIDIEM_PATTERN})$")
NUMBER_UNIT_PATTERN = re.compile(
    r"(?ix)"
    r"(?P<number>\d+(?:\.\d+)?)"
    r"\s*"
    r"(?P<unit>seconds?|secs?|sec|minutes?|mins?|min|hours?|hour|hrs?|hr|jours?|days?|day|weeks?|week|wks?|wk|months?|month|mos|years?|year|yrs?|yr|mo|[smhdwy])"
)


def parse_time_atom(text: str, allow_houronly: bool, normalize_space):
    text = normalize_space(text)
    if not text:
        return None
    if is_rejected_compact_meridiem_text(text):
        return None
    lowered = text.lower()
    if lowered in TIME_NAME_TO_TEMPLATE:
        return clone_time(TIME_NAME_TO_TEMPLATE[lowered])

    match = OCLOCK_PATTERN.fullmatch(lowered)
    if match:
        return tfhTime(hour=int(match.group("hour")), meridiem=_parse_meridiem(match.group("meridiem")))

    match = TIME_PATTERN.fullmatch(lowered)
    if not match:
        return None

    meridiem = _parse_meridiem(match.group("meridiem"))
    if meridiem is None and match.group("minute") is None and not allow_houronly:
        return None

    return build_time(
        hour=int(match.group("hour")),
        minute=int(match.group("minute") or 0),
        second=int(match.group("second") or 0),
        millisecond=int(match.group("millisecond") or 0),
        meridiem=meridiem,
    )


def parse_duration_atom(text: str, normalize_space):
    text = normalize_space(text)
    if not text:
        return None

    body, direction = strip_duration_prefix(text)
    body = body.strip()
    if not body:
        return None
    lowered = body.lower()

    if lowered.endswith(" ago"):
        body = body[:-4].rstrip()
        lowered = lowered[:-4].strip()
        direction = Direction.previous

    position = 0
    total = timedelta()
    unit = None
    while position < len(lowered):
        while position < len(lowered) and lowered[position] in " ,":
            position += 1
        if lowered[position : position + 4] == "and ":
            position += 4
            continue
        if position >= len(lowered):
            break

        numeric_match = NUMBER_UNIT_PATTERN.match(body, position)
        if numeric_match:
            amount = float(numeric_match.group("number"))
            normalized_unit = normalize_duration_unit(numeric_match.group("unit"))
            if normalized_unit is None:
                return None
            total += timedelta_for_unit(normalized_unit, amount)
            unit = unit or normalized_unit
            position = numeric_match.end()
            continue

        word_match = re.match(r"(?i)[a-z]+(?:\s+[a-z]+)*", body[position:])
        if not word_match:
            return None

        consumed = _consume_word_duration(word_match.group(0))
        if consumed is None:
            return None
        amount, normalized_unit, segment_len = consumed
        total += timedelta_for_unit(normalized_unit, amount)
        unit = unit or normalized_unit
        position += segment_len

    if unit is None:
        return None
    if direction == Direction.previous:
        total = -total
    return tfhTimedelta.from_object(total, unit=unit)


def _consume_word_duration(segment: str):
    tokens = [token.lower() for token in segment.split()]
    if len(tokens) < 2:
        return None

    for unit_index in range(1, len(tokens)):
        unit = UNIT_ALIASES.get(tokens[unit_index])
        if not unit:
            continue
        number_tokens = tokens[:unit_index]
        if not all(token in NUMBER_WORDS for token in number_tokens):
            continue
        amount = sum(NUMBER_WORDS[token] for token in number_tokens)
        return float(amount), unit, len(" ".join(tokens[: unit_index + 1]))

    return None


def _parse_meridiem(value: str):
    if value is None:
        return None
    if value.startswith("a"):
        return tfhTime.Meridiem.AM
    return tfhTime.Meridiem.PM
