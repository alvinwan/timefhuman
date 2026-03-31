import re
from datetime import timedelta

from dateutil.relativedelta import relativedelta, weekdays
import pytz

from timefhuman.inference import infer
from timefhuman.renderers import tfhAmbiguous, tfhDatetime, tfhDate, tfhList, tfhRange, tfhTime, tfhTimedelta
from timefhuman.utils import Direction, direction_to_offset, get_month_mapping, get_timezone_word_lengths, tfhConfig


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
NUMERIC_DATE_PATTERN = re.compile(r"^(?P<a>\d{1,4})(?P<sep>[/-])(?P<b>\d{1,4})(?:(?P=sep)(?P<c>\d{1,4}))?$")
MONTHNAME_PATTERN = re.compile(
    r"(?ix)^"
    r"(?P<month>[a-z]+)"
    r"\s+"
    r"(?P<first>\d{1,4})"
    r"(?P<suffix>st|nd|rd|th)?"
    r"(?:\s*,?\s*(?P<year>\d{2,4}))?$"
)
DAY_SUFFIX_PATTERN = re.compile(r"(?ix)^(?P<day>\d{1,2})(?:st|nd|rd|th)$")
POSITION_WEEKDAY_MONTH_PATTERN = re.compile(
    r"(?ix)^(?P<position>first|second|third|fourth|last)\s+(?P<weekday>[a-z]+)\s+(?:of|in)\s+(?P<month>[a-z]+)$"
)
ISO_PATTERN = re.compile(
    r"^(?P<year>\d{4})-(?P<month>\d{1,2})-(?P<day>\d{1,2})"
    r"T"
    r"(?P<hour>\d{1,2}):(?P<minute>\d{2})"
    r"(?::(?P<second>\d{2})(?:\.(?P<millisecond>\d{1,6}))?)?$"
)
NUMBER_UNIT_PATTERN = re.compile(
    r"(?ix)"
    r"(?P<number>\d+(?:\.\d+)?)"
    r"\s*"
    r"(?P<unit>seconds?|secs?|sec|minutes?|mins?|min|hours?|hour|hrs?|hr|days?|day|weeks?|week|wks?|wk|months?|month|mos|years?|year|yrs?|yr|mo|[smhdwy])"
)
TOKEN_PATTERN = re.compile(rf"(?ix)\d+(?:[/:.-]\d+)*(?:{MERIDIEM_PATTERN})?|[a-z]+(?:\.[a-z]+\.?)?|\S")

TIME_NAMES = {
    "noon": tfhTime(hour=12, minute=0, meridiem=tfhTime.Meridiem.PM),
    "midday": tfhTime(hour=12, minute=0, meridiem=tfhTime.Meridiem.PM),
    "midnight": tfhTime(hour=0, minute=0, meridiem=tfhTime.Meridiem.AM),
    "morning": tfhTime(hour=6, minute=0, meridiem=tfhTime.Meridiem.AM),
    "afternoon": tfhTime(hour=15, minute=0, meridiem=tfhTime.Meridiem.PM),
    "evening": tfhTime(hour=18, minute=0, meridiem=tfhTime.Meridiem.PM),
    "night": tfhTime(hour=20, minute=0, meridiem=tfhTime.Meridiem.PM),
}
DATE_NAMES = {"today": 0, "tomorrow": 1, "tmw": 1, "yesterday": -1}
DATE_TIME_NAMES = {"tonight": tfhDatetime(date=None, time=tfhTime(hour=20, minute=0, meridiem=tfhTime.Meridiem.PM))}
MODIFIER_TO_OFFSET = {
    "next": 1,
    "upcoming": 1,
    "following": 1,
    "previous": -1,
    "last": -1,
    "past": -1,
    "preceding": -1,
    "this": 0,
}
POSITION_TO_DELTA = {
    "first": lambda weekday: relativedelta(day=1, weekday=weekday(+1)),
    "second": lambda weekday: relativedelta(day=8, weekday=weekday(+1)),
    "third": lambda weekday: relativedelta(day=15, weekday=weekday(+1)),
    "fourth": lambda weekday: relativedelta(day=22, weekday=weekday(+1)),
    "last": lambda weekday: relativedelta(day=31, weekday=weekday(-1)),
}
NUMBER_WORDS = {
    "a": 1,
    "an": 1,
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
    "eleven": 11,
    "twelve": 12,
    "thirteen": 13,
    "fourteen": 14,
    "fifteen": 15,
    "sixteen": 16,
    "seventeen": 17,
    "eighteen": 18,
    "nineteen": 19,
    "twenty": 20,
    "thirty": 30,
    "forty": 40,
    "fifty": 50,
    "sixty": 60,
    "seventy": 70,
    "eighty": 80,
    "ninety": 90,
}
UNIT_ALIASES = {
    "second": "seconds",
    "seconds": "seconds",
    "sec": "seconds",
    "secs": "seconds",
    "s": "seconds",
    "minute": "minutes",
    "minutes": "minutes",
    "min": "minutes",
    "mins": "minutes",
    "m": "minutes",
    "hour": "hours",
    "hours": "hours",
    "hr": "hours",
    "hrs": "hours",
    "h": "hours",
    "day": "days",
    "days": "days",
    "d": "days",
    "week": "weeks",
    "weeks": "weeks",
    "wk": "weeks",
    "wks": "weeks",
    "w": "weeks",
    "month": "months",
    "months": "months",
    "mos": "months",
    "mo": "months",
    "year": "years",
    "years": "years",
    "yr": "years",
    "yrs": "years",
    "y": "years",
}
WEEKDAY_ALIASES = {
    "monday": 0,
    "mon": 0,
    "tuesday": 1,
    "tues": 1,
    "tue": 1,
    "tu": 1,
    "wednesday": 2,
    "wed": 2,
    "thursday": 3,
    "thurs": 3,
    "thur": 3,
    "thu": 3,
    "friday": 4,
    "fri": 4,
    "saturday": 5,
    "sat": 5,
    "sunday": 6,
    "sun": 6,
}


def parse_fast(text: str, config: tfhConfig, timezone_mapping, start_pos: int = 0):
    expression = _parse_expression(_normalize_space(text), config, timezone_mapping, allow_ambiguous=False)
    if expression is None:
        return None
    expression.matched_text_pos = (start_pos, start_pos + len(text))
    return [expression]


def extract_fast(text: str, config: tfhConfig, timezone_mapping):
    tokens = [(match.group(0), match.start(), match.end()) for match in TOKEN_PATTERN.finditer(text)]
    if not tokens:
        return []

    results = []
    saw_plausible_start = False
    index = 0
    while index < len(tokens):
        if not _is_plausible_start(tokens, index):
            index += 1
            continue

        saw_plausible_start = True
        expression, next_index = _extract_longest_match(tokens, index, text, config, timezone_mapping)
        if expression is None:
            index += 1
            continue

        results.extend(expression)
        index = next_index

    if results:
        return results
    if not saw_plausible_start:
        return []
    return None


def _parse_expression(text: str, config: tfhConfig, timezone_mapping, allow_ambiguous: bool):
    if not text:
        return None

    if _prefer_collection_parse(text):
        listed = _parse_list(text, config, timezone_mapping)
        if listed is not None:
            return listed

        ranged = _parse_range(text, config, timezone_mapping)
        if ranged is not None:
            return ranged

    single = _parse_single(text, config, timezone_mapping, allow_ambiguous=allow_ambiguous)
    if single is not None:
        return single

    if not _prefer_collection_parse(text):
        listed = _parse_list(text, config, timezone_mapping)
        if listed is not None:
            return listed

        ranged = _parse_range(text, config, timezone_mapping)
        if ranged is not None:
            return ranged

    return None


def _parse_list(text: str, config: tfhConfig, timezone_mapping):
    body, tzinfo = _strip_trailing_timezone(text, timezone_mapping)

    patterns = [r"\s+or\s+"]
    if _supports_comma_list(body, config, timezone_mapping):
        patterns.append(r"\s*,\s*")

    for pattern in patterns:
        parts = [part.strip() for part in re.split(pattern, body) if part.strip()]
        if len(parts) < 2:
            continue

        items = []
        for part in parts:
            item = _parse_range_or_single(part, config, timezone_mapping, allow_ambiguous=True)
            if item is None:
                items = []
                break
            items.append(item)

        if items:
            result = tfhList(infer(items))
            if tzinfo:
                result.tz = tzinfo
            return result

    return None


def _parse_range(text: str, config: tfhConfig, timezone_mapping):
    body, tzinfo = _strip_trailing_timezone(text, timezone_mapping)

    if " to " in body.lower():
        parts = re.split(r"(?i)\s+to\s+", body, maxsplit=1)
        if len(parts) == 2:
            result = _build_range(parts[0], parts[1], config, timezone_mapping)
            if result and tzinfo:
                result.tz = tzinfo
            return result

    indices = [i for i, char in enumerate(body) if char == "-"]
    preferred = [i for i in indices if _looks_like_range_hyphen(body, i)]
    for index in preferred + [i for i in indices if i not in preferred]:
        result = _build_range(body[:index], body[index + 1 :], config, timezone_mapping)
        if result:
            if tzinfo:
                result.tz = tzinfo
            return result

    return None


def _build_range(left_text: str, right_text: str, config: tfhConfig, timezone_mapping):
    left = _parse_single(left_text.strip(), config, timezone_mapping, allow_ambiguous=True)
    right = _parse_single(right_text.strip(), config, timezone_mapping, allow_ambiguous=True)
    if left is None or right is None:
        return None
    return tfhRange(infer([left, right]))


def _parse_range_or_single(text: str, config: tfhConfig, timezone_mapping, allow_ambiguous: bool):
    return _parse_range(text, config, timezone_mapping) or _parse_single(
        text, config, timezone_mapping, allow_ambiguous=allow_ambiguous
    )


def _parse_single(text: str, config: tfhConfig, timezone_mapping, allow_ambiguous: bool):
    duration = _parse_duration(text, config)
    if duration is not None:
        return duration

    datetime_like = _parse_datetime(text, config, timezone_mapping)
    if datetime_like is not None:
        return datetime_like

    if allow_ambiguous and text.isdigit():
        return tfhAmbiguous(int(text))

    return None


def _parse_datetime(text: str, config: tfhConfig, timezone_mapping):
    text = _normalize_space(text)
    if not text:
        return None

    body, tzinfo = _strip_trailing_timezone(text, timezone_mapping)
    lower_body = body.lower()

    iso_match = ISO_PATTERN.fullmatch(body)
    if iso_match:
        return tfhDatetime(
            date=tfhDate(
                year=int(iso_match.group("year")),
                month=int(iso_match.group("month")),
                day=int(iso_match.group("day")),
            ),
            time=tfhTime(
                hour=int(iso_match.group("hour")),
                minute=int(iso_match.group("minute")),
                second=int(iso_match.group("second") or 0),
                millisecond=int(iso_match.group("millisecond") or 0),
            ),
            tz=tzinfo,
        )

    if lower_body in DATE_TIME_NAMES:
        result = tfhDatetime(
            date=tfhDate.from_object(config.now.date()),
            time=tfhTime(hour=20, minute=0, meridiem=tfhTime.Meridiem.PM),
            tz=tzinfo,
        )
        return result

    for separator, mode in ((" at ", "date_time"), (" on ", "time_date")):
        if separator in lower_body:
            left, right = re.split(rf"(?i){separator.strip()}", body, maxsplit=1)
            if mode == "date_time":
                date = _parse_date(left, config)
                time = _parse_time_component(right, allow_houronly=True)
            else:
                time = _parse_time_component(left, allow_houronly=True)
                date = _parse_date(right, config)
            if date and time:
                return tfhDatetime(date=date, time=time, tz=tzinfo)

    date = _parse_date(body, config)
    if date is not None:
        return tfhDatetime(date=date, tz=tzinfo)

    time = _parse_time_component(body, allow_houronly=False)
    if time is not None:
        return tfhDatetime(time=time, tz=tzinfo)

    parts = body.split()
    best = None
    best_score = -1
    for index in range(1, len(parts)):
        left = " ".join(parts[:index])
        right = " ".join(parts[index:])

        date = _parse_date(left, config)
        time = _parse_time_component(right, allow_houronly=True)
        if date and time:
            score = _date_score(date) + _time_score(time)
            if score > best_score:
                best = tfhDatetime(date=date, time=time, tz=tzinfo)
                best_score = score

        time = _parse_time_component(left, allow_houronly=True)
        date = _parse_date(right, config)
        if date and time:
            score = _date_score(date) + _time_score(time)
            if score > best_score:
                best = tfhDatetime(date=date, time=time, tz=tzinfo)
                best_score = score

    return best


def _parse_date(text: str, config: tfhConfig):
    text = _normalize_space(text)
    if not text:
        return None
    lower = text.lower()

    if lower in DATE_NAMES:
        return tfhDate.from_object(config.now.date() + timedelta(days=DATE_NAMES[lower]))

    match = POSITION_WEEKDAY_MONTH_PATTERN.fullmatch(lower)
    if match:
        weekday_index = _parse_weekday_name(match.group("weekday"))
        month = _parse_month_name(match.group("month"))
        if weekday_index is None or month is None:
            return None
        weekday = weekdays[weekday_index]
        return tfhDate(month=month, delta=POSITION_TO_DELTA[match.group("position")](weekday))

    tokens = lower.split()
    modifier_offset, remainder = _parse_modifier_prefix(tokens)
    if remainder:
        if len(remainder) == 1:
            weekday_index = _parse_weekday_name(remainder[0])
            if weekday_index is not None:
                offset = modifier_offset if tokens[: len(tokens) - len(remainder)] else direction_to_offset(config.direction)
                value = config.now.date() + relativedelta(weekday=weekdays[weekday_index](offset))
                return tfhDate.from_object(value)

            month = _parse_month_name(remainder[0])
            if month is not None and modifier_offset is not None and tokens[: len(tokens) - len(remainder)]:
                return tfhDate(month=month, delta=relativedelta(years=modifier_offset))

    if len(tokens) >= 2:
        stripped = _strip_leading_weekday(text)
    else:
        stripped = text

    if stripped.lower() in DATE_NAMES:
        return tfhDate.from_object(config.now.date() + timedelta(days=DATE_NAMES[stripped.lower()]))

    numeric = _parse_numeric_date(stripped)
    if numeric is not None:
        return numeric

    monthname = _parse_monthname_date(stripped)
    if monthname is not None:
        return monthname

    day_suffix = DAY_SUFFIX_PATTERN.fullmatch(lower)
    if day_suffix:
        return tfhDate(day=int(day_suffix.group("day")))

    weekday_index = _parse_weekday_name(lower)
    if weekday_index is not None:
        value = config.now.date() + relativedelta(weekday=weekdays[weekday_index](direction_to_offset(config.direction)))
        return tfhDate.from_object(value)

    return None


def _parse_numeric_date(text: str):
    match = NUMERIC_DATE_PATTERN.fullmatch(text)
    if not match:
        return None

    first = int(match.group("a"))
    second = int(match.group("b"))
    third = match.group("c")

    if third is None:
        if second > 31:
            return tfhDate(month=first, year=_normalize_year(second))
        return tfhDate(month=first, day=second)

    third_value = _normalize_year(int(third))
    if len(match.group("a")) == 4:
        return tfhDate(year=first, month=second, day=int(third))
    return tfhDate(month=first, day=second, year=third_value)


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
        return tfhDate(month=month, day=first, year=_normalize_year(int(year)))

    if suffix or first <= 31:
        return tfhDate(month=month, day=first)

    return tfhDate(month=month, year=_normalize_year(first))


def _parse_time_component(text: str, allow_houronly: bool):
    text = _normalize_space(text)
    if not text:
        return None

    lowered = text.lower()
    if lowered in TIME_NAMES:
        template = TIME_NAMES[lowered]
        return tfhTime(
            hour=template.hour,
            minute=template.minute,
            second=template.second,
            millisecond=template.millisecond,
            meridiem=template.meridiem,
        )

    match = OCLOCK_PATTERN.fullmatch(lowered)
    if match:
        return tfhTime(hour=int(match.group("hour")), meridiem=_parse_meridiem(match.group("meridiem")))

    match = TIME_PATTERN.fullmatch(lowered)
    if not match:
        return None

    meridiem = _parse_meridiem(match.group("meridiem"))
    has_colon = match.group("minute") is not None
    if meridiem is None and not has_colon and not allow_houronly:
        return None

    return tfhTime(
        hour=int(match.group("hour")),
        minute=int(match.group("minute") or 0),
        second=int(match.group("second") or 0),
        millisecond=int(match.group("millisecond") or 0),
        meridiem=meridiem,
    )


def _parse_duration(text: str, config: tfhConfig):
    lowered = text.strip().lower()
    if not lowered:
        return None

    direction = Direction.next
    if lowered.startswith("in "):
        lowered = lowered[3:].strip()
    elif lowered.startswith("for "):
        lowered = lowered[4:].strip()

    if lowered.endswith(" ago"):
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

        numeric_match = NUMBER_UNIT_PATTERN.match(lowered, position)
        if numeric_match:
            amount = float(numeric_match.group("number"))
            normalized_unit = UNIT_ALIASES[numeric_match.group("unit")]
            total += _timedelta_for_unit(normalized_unit, amount)
            unit = unit or normalized_unit
            position = numeric_match.end()
            continue

        word_match = re.match(r"[a-z]+(?:\s+[a-z]+)*", lowered[position:])
        if not word_match:
            return None

        segment = word_match.group(0)
        consumed = _consume_word_duration(segment)
        if consumed is None:
            return None
        amount, normalized_unit, segment_len = consumed
        total += _timedelta_for_unit(normalized_unit, amount)
        unit = unit or normalized_unit
        position += segment_len

    if unit is None:
        return None

    if direction == Direction.previous:
        total = -total

    return tfhTimedelta.from_object(total, unit=unit)


def _consume_word_duration(segment: str):
    tokens = segment.split()
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
        consumed_text = " ".join(tokens[: unit_index + 1])
        return float(amount), unit, len(consumed_text)

    return None


def _timedelta_for_unit(unit: str, amount: float):
    if unit == "months":
        return timedelta(days=30 * amount)
    if unit == "years":
        return timedelta(days=365 * amount)
    return timedelta(**{unit: amount})


def _strip_trailing_timezone(text: str, timezone_mapping):
    lowered = text.lower()
    timezone_name = timezone_mapping.get(lowered)
    if timezone_name is not None:
        return "", pytz.timezone(timezone_name)

    words = text.split()
    lowered_words = lowered.split()
    for word_count in get_timezone_word_lengths():
        if len(words) < word_count:
            continue
        candidate = " ".join(lowered_words[-word_count:])
        timezone_name = timezone_mapping.get(candidate)
        if timezone_name is not None:
            return " ".join(words[:-word_count]).strip(), pytz.timezone(timezone_name)
    return text, None


def _parse_modifier_prefix(tokens):
    offset = 0
    index = 0
    while index < len(tokens) and tokens[index] in MODIFIER_TO_OFFSET:
        offset += MODIFIER_TO_OFFSET[tokens[index]]
        index += 1
    return offset, tokens[index:]


def _strip_leading_weekday(text: str):
    parts = text.split(maxsplit=1)
    if len(parts) == 2 and _parse_weekday_name(parts[0].lower()) is not None:
        return parts[1]
    return text


def _normalize_year(value: int):
    if 50 < value < 100:
        return 1900 + value
    if 0 < value < 50:
        return 2000 + value
    return value


def _parse_month_name(value: str):
    return get_month_mapping().get(value.lower())


def _parse_weekday_name(value: str):
    return WEEKDAY_ALIASES.get(value.lower())


def _parse_meridiem(value: str):
    if value is None:
        return None
    if value.startswith("a"):
        return tfhTime.Meridiem.AM
    return tfhTime.Meridiem.PM


def _normalize_space(text: str):
    return " ".join(text.strip().split())


def _looks_like_range_hyphen(text: str, index: int):
    left = text[index - 1] if index > 0 else ""
    right = text[index + 1] if index + 1 < len(text) else ""
    if left == " " or right == " ":
        return True
    if left.isdigit() and right.isdigit():
        return True
    if left.isalpha() or right.isalpha():
        return True
    return False


def _date_score(value: tfhDate):
    return int(value.year is not None) + int(value.month is not None) + int(value.day is not None)


def _time_score(value: tfhTime):
    score = 0
    if value.meridiem is not None:
        score += 2
    if value.minute:
        score += 1
    if value.second:
        score += 1
    if value.hour is not None:
        score += 1
    return score


def _prefer_collection_parse(text: str):
    lowered = text.lower()
    return "," in text or " or " in lowered or " to " in lowered or " -" in text or "- " in text


def _supports_comma_list(text: str, config: tfhConfig, timezone_mapping):
    if "," not in text:
        return False
    if text.count(",") > 1:
        return True

    collapsed = text.replace(",", " ")
    return _parse_single(collapsed, config, timezone_mapping, allow_ambiguous=False) is None


def _extract_longest_match(tokens, start_index: int, text: str, config: tfhConfig, timezone_mapping):
    max_end = min(len(tokens), start_index + 8)
    for end_index in range(max_end, start_index, -1):
        start = tokens[start_index][1]
        end = tokens[end_index - 1][2]
        candidate = text[start:end].strip()
        if candidate and candidate[-1] in ".?!":
            candidate = candidate[:-1].rstrip()
            end = start + len(candidate)
        if not candidate:
            continue

        expression = parse_fast(candidate, config, timezone_mapping, start_pos=start)
        if expression is not None:
            return expression, end_index

    return None, start_index + 1


def _is_plausible_start(tokens, index: int):
    token = tokens[index][0].lower()
    next_token = tokens[index + 1][0].lower() if index + 1 < len(tokens) else ""

    if token in DATE_NAMES or token in TIME_NAMES or token in DATE_TIME_NAMES:
        return True
    if token in MODIFIER_TO_OFFSET and (
        _parse_weekday_name(next_token) is not None or _parse_month_name(next_token) is not None
    ):
        return True
    if token in POSITION_TO_DELTA and _parse_weekday_name(next_token) is not None:
        return True
    if _parse_month_name(token) is not None or _parse_weekday_name(token) is not None:
        return True
    if token in NUMBER_WORDS and next_token in UNIT_ALIASES:
        return True
    if "/" in token or ":" in token or "t" in token and "-" in token:
        return True
    if re.fullmatch(rf"(?ix)\d+(?:{MERIDIEM_PATTERN})", token):
        return True
    if token.isdigit():
        return next_token in UNIT_ALIASES or next_token in WEEKDAY_ALIASES or next_token in DATE_NAMES or bool(
            re.fullmatch(MERIDIEM_PATTERN, next_token, flags=re.IGNORECASE)
        )

    return False
