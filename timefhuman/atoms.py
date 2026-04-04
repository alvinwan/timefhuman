import re
from datetime import timedelta

from dateutil.relativedelta import relativedelta, weekdays

from timefhuman.renderers import tfhDate, tfhDatetime, tfhTime, tfhTimedelta
from timefhuman.semantics import (
    DATE_NAME_TO_OFFSET,
    DATE_TIME_NAME_TO_TEMPLATE,
    MODIFIER_TO_OFFSET,
    NUMBER_WORDS,
    POSITION_TO_DELTA,
    TIME_NAME_TO_TEMPLATE,
    UNIT_ALIASES,
    build_date,
    build_numeric_date_parts,
    build_time,
    clone_datetime,
    clone_time,
    is_rejected_compact_meridiem_text,
    month_number,
    normalize_duration_unit,
    normalize_year,
    strip_duration_prefix,
    supports_numeric_date_text,
    timedelta_for_unit,
    weekday_index,
)
from timefhuman.utils import Direction, direction_to_offset


__all__ = ("parse_date_atom", "parse_datetime_atom", "parse_duration_atom", "parse_time_atom")


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
ISO_PATTERN = re.compile(
    r"^(?P<year>\d{4})-(?P<month>\d{1,2})-(?P<day>\d{1,2})"
    r"T"
    r"(?P<hour>\d{1,2}):(?P<minute>\d{2})"
    r"(?::(?P<second>\d{2})(?:\.(?P<millisecond>\d{1,6}))?)?$"
)
NUMERIC_DATE_PATTERN = re.compile(r"^(?P<a>\d{1,4})(?P<sep>[./-])(?P<b>\d{1,4})(?:(?P=sep)(?P<c>\d{1,4}))?$")
MONTHNAME_PATTERN = re.compile(
    r"(?ix)^"
    r"(?P<month>[a-z]+)"
    r"\s+"
    r"(?P<first>\d{1,4})"
    r"(?P<suffix>st|nd|rd|th)?"
    r"(?:\s*,?\s*(?P<year>\d{2,4}))?$"
)
DAY_MONTH_PATTERN = re.compile(
    r"(?ix)^"
    r"(?P<day>\d{1,2})"
    r"(?P<suffix>st|nd|rd|th)?"
    r"\s+"
    r"(?P<month>[a-z]+)"
    r"(?:\s*,?\s*(?P<year>\d{2,4}))?$"
)
DAY_YEAR_PATTERN = re.compile(
    r"(?ix)^"
    r"(?P<day>\d{1,2})"
    r"(?P<suffix>st|nd|rd|th)?"
    r"(?:\s*,\s*|\s+)"
    r"(?P<year>\d{2,4})$"
)
DAY_OF_MONTH_PATTERN = re.compile(
    r"(?ix)^"
    r"(?P<day>\d{1,2})"
    r"(?P<suffix>st|nd|rd|th)"
    r"\s+of\s+"
    r"(?P<month>[a-z]+)"
    r"(?:\s*,?\s*(?P<year>\d{2,4}))?$"
)
DAY_SUFFIX_PATTERN = re.compile(r"(?ix)^(?P<day>\d{1,2})(?:st|nd|rd|th)$")
POSITION_WEEKDAY_MONTH_PATTERN = re.compile(
    r"(?ix)^(?P<position>first|second|third|fourth|last)\s+(?P<weekday>[a-z]+)\s+(?:of|in)\s+(?P<month>[a-z]+)$"
)
ORDINAL_POSITION_WEEKDAY_MONTH_PATTERN = re.compile(
    r"(?ix)^(?P<ordinal>[1-4])(?:st|nd|rd|th)\s+(?P<weekday>[a-z]+)\s+(?:of|in)\s+(?P<month>[a-z]+)$"
)
ORDINAL_POSITION_NAME = {
    "1": "first",
    "2": "second",
    "3": "third",
    "4": "fourth",
}
def parse_date_atom(text: str, config, normalize_space):
    text = normalize_space(text)
    if not text:
        return None
    lower = text.lower()

    if lower in DATE_NAME_TO_OFFSET:
        return tfhDate.from_object(config.now.date() + timedelta(days=DATE_NAME_TO_OFFSET[lower]))

    match = POSITION_WEEKDAY_MONTH_PATTERN.fullmatch(text)
    if match:
        weekday = _parse_weekday_name(match.group("weekday"))
        month = _parse_month_name(match.group("month"))
        if weekday is None or month is None:
            return None
        return tfhDate(month=month, delta=POSITION_TO_DELTA[match.group("position").lower()](weekdays[weekday]))

    match = ORDINAL_POSITION_WEEKDAY_MONTH_PATTERN.fullmatch(text)
    if match:
        weekday = _parse_weekday_name(match.group("weekday"))
        month = _parse_month_name(match.group("month"))
        if weekday is None or month is None:
            return None
        return tfhDate(month=month, delta=POSITION_TO_DELTA[ORDINAL_POSITION_NAME[match.group("ordinal")]](weekdays[weekday]))

    tokens = text.split()
    lowered_tokens = [token.lower() for token in tokens]
    offset, lowered_remainder = _parse_modifier_prefix(lowered_tokens)
    remainder = tokens[len(tokens) - len(lowered_remainder):]
    if len(remainder) == 1:
        weekday = _parse_weekday_name(remainder[0])
        if weekday is not None:
            weekday_offset = offset if lowered_tokens[: len(lowered_tokens) - 1] else direction_to_offset(config.direction)
            value = config.now.date() + relativedelta(weekday=weekdays[weekday](weekday_offset))
            return tfhDate.from_object(value)

        month = _parse_month_name(remainder[0])
        if month is not None and lowered_tokens[: len(lowered_tokens) - 1]:
            return tfhDate(month=month, delta=relativedelta(years=offset))

    stripped = _strip_leading_weekday(text) if len(tokens) >= 2 else text
    if stripped.lower() in DATE_NAME_TO_OFFSET:
        return tfhDate.from_object(config.now.date() + timedelta(days=DATE_NAME_TO_OFFSET[stripped.lower()]))

    numeric = _parse_numeric_date(stripped)
    if numeric is not None:
        return numeric

    monthname = _parse_monthname_date(stripped)
    if monthname is not None:
        return monthname

    day_month_or_year = _parse_day_month_or_year(stripped)
    if day_month_or_year is not None:
        return day_month_or_year

    day_suffix = DAY_SUFFIX_PATTERN.fullmatch(lower)
    if day_suffix:
        return build_date(day=int(day_suffix.group("day")))

    weekday = _parse_weekday_name(lower)
    if weekday is not None:
        value = config.now.date() + relativedelta(weekday=weekdays[weekday](direction_to_offset(config.direction)))
        return tfhDate.from_object(value)

    return None


def parse_datetime_atom(text: str, config, tzinfo, normalize_space):
    text = normalize_space(text)
    if not text:
        return None
    lower_body = text.lower()

    iso_match = ISO_PATTERN.fullmatch(text)
    if iso_match:
        date = build_date(
            year=int(iso_match.group("year")),
            month=int(iso_match.group("month")),
            day=int(iso_match.group("day")),
        )
        time = build_time(
            hour=int(iso_match.group("hour")),
            minute=int(iso_match.group("minute")),
            second=int(iso_match.group("second") or 0),
            millisecond=int(iso_match.group("millisecond") or 0),
        )
        if date is None or time is None:
            return None
        return tfhDatetime(date=date, time=time, tz=tzinfo)

    if lower_body in DATE_TIME_NAME_TO_TEMPLATE:
        value = clone_datetime(DATE_TIME_NAME_TO_TEMPLATE[lower_body])
        value.date = tfhDate.from_object(config.now.date())
        value.tz = tzinfo
        return value

    time = parse_time_atom(text, allow_houronly=False, normalize_space=normalize_space)
    if time is not None:
        return tfhDatetime(time=time, tz=tzinfo)

    date = parse_date_atom(text, config, normalize_space)
    if date is not None:
        return tfhDatetime(date=date, tz=tzinfo)

    return None


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
    if not _looks_duration_text(text):
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


def _looks_duration_text(text: str):
    lowered = text.lower()
    if any(char.isspace() for char in lowered):
        return True
    if ":" in lowered or "/" in lowered:
        return False
    if lowered.endswith(("am", "pm", "a", "p")):
        return False
    suffix_start = len(lowered)
    while suffix_start > 0 and lowered[suffix_start - 1].isalpha():
        suffix_start -= 1
    if suffix_start == len(lowered):
        return False
    return normalize_duration_unit(lowered[suffix_start:]) is not None


def _parse_numeric_date(text: str):
    match = NUMERIC_DATE_PATTERN.fullmatch(text)
    if not match:
        return None
    if not supports_numeric_date_text(text):
        return None
    return build_numeric_date_parts(match.group("a"), match.group("b"), match.group("c"))


def _parse_monthname_date(text: str):
    match = MONTHNAME_PATTERN.fullmatch(text)
    if not match:
        return None

    month = _parse_month_name(match.group("month"))
    if month is None:
        return None

    first = int(match.group("first"))
    suffix = match.group("suffix")
    year = match.group("year")

    if year is not None:
        return build_date(month=month, day=first, year=normalize_year(int(year)))
    if suffix or first <= 31:
        return build_date(month=month, day=first)
    return build_date(month=month, year=normalize_year(first))


def _parse_day_month_or_year(text: str):
    match = DAY_OF_MONTH_PATTERN.fullmatch(text)
    if match:
        month = _parse_month_name(match.group("month"))
        if month is None:
            return None
        year = match.group("year")
        if year is not None:
            return build_date(day=int(match.group("day")), month=month, year=normalize_year(int(year)))
        return build_date(day=int(match.group("day")), month=month)

    match = DAY_MONTH_PATTERN.fullmatch(text)
    if match:
        month = _parse_month_name(match.group("month"))
        if month is None:
            return None
        year = match.group("year")
        if year is not None:
            return build_date(day=int(match.group("day")), month=month, year=normalize_year(int(year)))
        return build_date(day=int(match.group("day")), month=month)

    match = DAY_YEAR_PATTERN.fullmatch(text)
    if match:
        return build_date(day=int(match.group("day")), year=normalize_year(int(match.group("year"))))

    return None


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


def _parse_modifier_prefix(tokens):
    offset = 0
    index = 0
    while index < len(tokens) and tokens[index] in MODIFIER_TO_OFFSET:
        offset += MODIFIER_TO_OFFSET[tokens[index]]
        index += 1
    return offset, tokens[index:]


def _strip_leading_weekday(text: str):
    parts = text.split(maxsplit=1)
    if len(parts) == 2 and weekday_index(parts[0].rstrip(".,")) is not None:
        return parts[1]
    return text


def _parse_month_name(value: str):
    return month_number(value)


def _parse_weekday_name(value: str):
    return weekday_index(value)
