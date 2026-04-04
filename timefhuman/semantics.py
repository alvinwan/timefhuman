from datetime import date, timedelta
import re

from dateutil.relativedelta import relativedelta

from timefhuman.renderers import tfhAmbiguous, tfhDate, tfhDatelike, tfhDatetime, tfhTime
from timefhuman.utils import Direction, get_month_mapping


def _expand_aliases(groups):
    return {alias: value for value, names in groups for alias in names.split()}


def _time(hour: int, meridiem, minute: int = 0):
    return tfhTime(hour=hour, minute=minute, meridiem=meridiem)


TIME_NAME_TO_TEMPLATE = {
    **{name: _time(12, tfhTime.Meridiem.PM) for name in ("noon", "midday")},
    "midnight": _time(0, tfhTime.Meridiem.AM),
    "morning": _time(6, tfhTime.Meridiem.AM),
    "afternoon": _time(15, tfhTime.Meridiem.PM),
    "evening": _time(18, tfhTime.Meridiem.PM),
    "night": _time(20, tfhTime.Meridiem.PM),
}
DATE_NAME_TO_OFFSET = {
    "today": 0,
    "tomorrow": 1,
    "tmw": 1,
    "mañana": 1,
    "manana": 1,
    "yesterday": -1,
    "ayer": -1,
}
DATE_TIME_NAME_TO_TEMPLATE = {
    "tonight": tfhDatetime(date=None, time=_time(20, tfhTime.Meridiem.PM)),
}
MODIFIER_TO_OFFSET = _expand_aliases(
    (
        (1, "next upcoming following"),
        (-1, "previous last past preceding"),
        (0, "this"),
    )
)
POSITION_TO_DELTA = {
    "first": lambda weekday: relativedelta(day=1, weekday=weekday(+1)),
    "second": lambda weekday: relativedelta(day=8, weekday=weekday(+1)),
    "third": lambda weekday: relativedelta(day=15, weekday=weekday(+1)),
    "fourth": lambda weekday: relativedelta(day=22, weekday=weekday(+1)),
    "last": lambda weekday: relativedelta(day=31, weekday=weekday(-1)),
}
NUMBER_WORDS = _expand_aliases(
    (
        (1, "a an one"),
        (2, "two"),
        (3, "three"),
        (4, "four"),
        (5, "five"),
        (6, "six"),
        (7, "seven"),
        (8, "eight"),
        (9, "nine"),
        (10, "ten"),
        (11, "eleven"),
        (12, "twelve"),
        (13, "thirteen"),
        (14, "fourteen"),
        (15, "fifteen"),
        (16, "sixteen"),
        (17, "seventeen"),
        (18, "eighteen"),
        (19, "nineteen"),
        (20, "twenty"),
        (30, "thirty"),
        (40, "forty"),
        (50, "fifty"),
        (60, "sixty"),
        (70, "seventy"),
        (80, "eighty"),
        (90, "ninety"),
    )
)
UNIT_ALIASES = _expand_aliases(
    (
        ("seconds", "second seconds sec secs s"),
        ("minutes", "minute minutes min mins m"),
        ("hours", "hour hours hr hrs h"),
        ("days", "day days d"),
        ("days", "jour jours"),
        ("weeks", "week weeks wk wks w"),
        ("months", "month months mos mo"),
        ("years", "year years yr yrs y"),
    )
)
CASE_SENSITIVE_SINGLE_LETTER_DURATION_UNITS = frozenset({"s", "m", "h", "d", "w", "y"})
WEEKDAY_ALIASES = _expand_aliases(
    (
        (0, "monday mon"),
        (1, "tuesday tues tue tu"),
        (2, "wednesday wed"),
        (3, "thursday thurs thur thu"),
        (4, "friday fri"),
        (5, "saturday sat"),
        (6, "sunday sun"),
    )
)
DURATION_PREFIX_PATTERNS = (
    (("for", "the", "past"), Direction.previous),
    (("for", "past"), Direction.previous),
    (("the", "past"), Direction.previous),
    (("past",), Direction.previous),
    (("in",), Direction.next),
    (("dans",), Direction.next),
    (("for",), Direction.next),
)


def normalize_year(value: int):
    if 50 < value < 100:
        return 1900 + value
    if 0 < value < 50:
        return 2000 + value
    return value


def supports_numeric_date_text(value: str):
    if "." not in value:
        return True
    parts = value.split(".")
    return len(parts) == 3 and any(len(part) == 4 for part in parts)


MIXED_FRACTION_RANGE_PATTERN = re.compile(r"^\d+-\d+/\d+$")


def is_rejected_fraction_text(value: str):
    return bool(MIXED_FRACTION_RANGE_PATTERN.fullmatch(value.strip()))


def is_invalid_ambiguous_date_range(left, right):
    if not isinstance(left, tfhAmbiguous):
        return False
    if not isinstance(right, tfhDatelike):
        return False
    return bool((right.date or right.year or right.month or right.day) and not right.time)


def build_date(year: int | None = None, month: int | None = None, day: int | None = None):
    if year is not None and not 1 <= year <= 9999:
        return None
    if month is not None and not 1 <= month <= 12:
        return None
    if day is not None and not 1 <= day <= 31:
        return None
    if month is not None and day is not None:
        validation_year = year if year is not None else 2000
        try:
            date(validation_year, month, day)
        except ValueError:
            return None
    return tfhDate(year=year, month=month, day=day)


def build_numeric_date(first: int, second: int, third: int | None = None):
    if third is None:
        if first >= 1000:
            return build_date(year=first, month=second)
        if second > 31:
            return build_date(month=first, year=normalize_year(second))
        if 1 <= first <= 12:
            return build_date(month=first, day=second)
        if 1 <= second <= 12:
            return build_date(month=second, day=first)
        return None

    if first >= 1000:
        return build_date(year=first, month=second, day=third)

    year = normalize_year(third)
    if 1 <= first <= 12:
        return build_date(month=first, day=second, year=year)
    if 1 <= second <= 12:
        return build_date(year=year, month=second, day=first)
    return None


def build_numeric_date_parts(first: str, second: str, third: str | None = None):
    if third is None:
        if int(second) > 31 and len(second) not in (2, 4):
            return None
    elif len(third) not in (2, 4):
        return None

    return build_numeric_date(int(first), int(second), int(third) if third is not None else None)


def build_time(
    hour: int,
    minute: int = 0,
    second: int = 0,
    millisecond: int = 0,
    meridiem=None,
):
    if not 0 <= minute <= 59 or not 0 <= second <= 59 or not 0 <= millisecond <= 999999:
        return None
    if meridiem is None:
        if not 0 <= hour <= 23:
            return None
    elif not 1 <= hour <= 12:
        return None

    return tfhTime(
        hour=hour,
        minute=minute,
        second=second,
        millisecond=millisecond,
        meridiem=meridiem,
    )


def clone_time(template: tfhTime):
    return tfhTime(
        hour=template.hour,
        minute=template.minute,
        second=template.second,
        millisecond=template.millisecond,
        meridiem=template.meridiem,
    )


def clone_datetime(template: tfhDatetime):
    return tfhDatetime(date=template.date, time=clone_time(template.time), tz=template.tz)


def month_number(value: str, fallback: int | None = None):
    return get_month_mapping().get(value.lower(), fallback)


def weekday_index(value: str):
    return WEEKDAY_ALIASES.get(value.lower())


def timedelta_for_unit(unit: str, amount: float):
    if unit == "months":
        return timedelta(days=30 * amount)
    if unit == "years":
        return timedelta(days=365 * amount)
    return timedelta(**{unit: amount})


def is_duration_value_token(token: str):
    lowered = token.lower()
    return lowered.isdigit() or lowered in NUMBER_WORDS


def normalize_duration_unit(token: str):
    lowered = token.lower()
    if lowered not in UNIT_ALIASES:
        return None
    if len(token) == 1 and lowered in CASE_SENSITIVE_SINGLE_LETTER_DURATION_UNITS and token != lowered:
        return None
    return UNIT_ALIASES[lowered]


def is_rejected_compact_meridiem_text(value: str):
    stripped = value.strip()
    if len(stripped) < 2:
        return False
    suffix = stripped[-1]
    if suffix not in {"A", "P"}:
        return False
    return stripped[:-1].isdigit()


def duration_prefix_length(tokens, index: int = 0):
    lowered = [token.lower() for token in tokens[index:]]
    for prefix, _ in DURATION_PREFIX_PATTERNS:
        prefix_length = len(prefix)
        if lowered[:prefix_length] != list(prefix):
            continue
        value_index = prefix_length
        if value_index < len(lowered) and is_duration_value_token(lowered[value_index]):
            return prefix_length
    return 0


def strip_duration_prefix(text: str):
    stripped = text.strip()
    tokens = stripped.split()
    lowered = [token.lower() for token in tokens]
    for prefix, direction in DURATION_PREFIX_PATTERNS:
        prefix_length = len(prefix)
        if lowered[:prefix_length] != list(prefix):
            continue
        value_index = prefix_length
        if value_index < len(tokens) and is_duration_value_token(lowered[value_index]):
            return " ".join(tokens[value_index:]), direction
    return stripped, Direction.next
