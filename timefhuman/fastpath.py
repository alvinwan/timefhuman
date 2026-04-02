import re
from datetime import timedelta

from dateutil.relativedelta import relativedelta, weekdays
import pytz

from timefhuman.inference import infer
from timefhuman.renderers import tfhAmbiguous, tfhDatetime, tfhDate, tfhList, tfhRange, tfhTime, tfhTimedelta
from timefhuman.semantics import (
    DATE_NAME_TO_OFFSET,
    DATE_TIME_NAME_TO_TEMPLATE,
    MODIFIER_TO_OFFSET,
    NUMBER_WORDS,
    POSITION_TO_DELTA,
    TIME_NAME_TO_TEMPLATE,
    UNIT_ALIASES,
    WEEKDAY_ALIASES,
    clone_datetime,
    clone_time,
    month_number,
    normalize_year,
    timedelta_for_unit,
    weekday_index,
)
from timefhuman.utils import Direction, direction_to_offset, get_timezone_word_lengths, tfhConfig


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


def parse_fast(text: str, config: tfhConfig, timezone_mapping, start_pos: int = 0):
    stripped, span_start, span_end = _trimmed_span(text, start_pos)
    if not stripped:
        return None

    expression = _parse_expression(_normalize_space(stripped), config, timezone_mapping, allow_ambiguous=False)
    if expression is None:
        return None

    expression.matched_text_pos = (span_start, span_end)
    return [expression]


def prefer_extraction(text: str):
    stripped = text.strip()
    if not stripped:
        return False
    if stripped[-1] in ".?!":
        return True

    tokens = [(match.group(0), match.start(), match.end()) for match in TOKEN_PATTERN.finditer(stripped)]
    if not tokens:
        return False

    for index in range(len(tokens)):
        if _is_plausible_start(tokens, index):
            return index > 0

    return len(tokens) > 1


def extract_fast(text: str, parse_candidate):
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
        expression, next_index = _extract_longest_match(tokens, index, text, parse_candidate)
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

    indices = [index for index, char in enumerate(body) if char == "-"]
    preferred = [index for index in indices if _looks_like_range_hyphen(body, index)]
    for index in preferred + [item for item in indices if item not in preferred]:
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
    duration = _parse_duration(text)
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
    if not body:
        return None

    atomic = _parse_atomic_datetime(body, config, tzinfo)
    if atomic is not None:
        return atomic

    lower_body = body.lower()
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


def _parse_atomic_datetime(text: str, config: tfhConfig, tzinfo):
    lower_body = text.lower()
    iso_match = ISO_PATTERN.fullmatch(text)
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

    if lower_body in DATE_TIME_NAME_TO_TEMPLATE:
        value = clone_datetime(DATE_TIME_NAME_TO_TEMPLATE[lower_body])
        value.date = tfhDate.from_object(config.now.date())
        value.tz = tzinfo
        return value

    time = _parse_time_component(text, allow_houronly=False)
    if time is not None:
        return tfhDatetime(time=time, tz=tzinfo)

    date = _parse_date(text, config)
    if date is not None:
        return tfhDatetime(date=date, tz=tzinfo)

    return None


def _parse_date(text: str, config: tfhConfig):
    text = _normalize_space(text)
    if not text:
        return None
    lower = text.lower()

    if lower in DATE_NAME_TO_OFFSET:
        return tfhDate.from_object(config.now.date() + timedelta(days=DATE_NAME_TO_OFFSET[lower]))

    match = POSITION_WEEKDAY_MONTH_PATTERN.fullmatch(lower)
    if match:
        weekday = _parse_weekday_name(match.group("weekday"))
        month = _parse_month_name(match.group("month"))
        if weekday is None or month is None:
            return None
        return tfhDate(month=month, delta=POSITION_TO_DELTA[match.group("position")](weekdays[weekday]))

    tokens = lower.split()
    offset, remainder = _parse_modifier_prefix(tokens)
    if len(remainder) == 1:
        weekday = _parse_weekday_name(remainder[0])
        if weekday is not None:
            if tokens[: len(tokens) - 1]:
                weekday_offset = offset
            else:
                weekday_offset = direction_to_offset(config.direction)
            value = config.now.date() + relativedelta(weekday=weekdays[weekday](weekday_offset))
            return tfhDate.from_object(value)

        month = _parse_month_name(remainder[0])
        if month is not None and tokens[: len(tokens) - 1]:
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

    day_suffix = DAY_SUFFIX_PATTERN.fullmatch(lower)
    if day_suffix:
        return tfhDate(day=int(day_suffix.group("day")))

    weekday = _parse_weekday_name(lower)
    if weekday is not None:
        value = config.now.date() + relativedelta(weekday=weekdays[weekday](direction_to_offset(config.direction)))
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
            return tfhDate(month=first, year=normalize_year(second))
        return tfhDate(month=first, day=second)

    if len(match.group("a")) == 4:
        return tfhDate(year=first, month=second, day=int(third))
    return tfhDate(month=first, day=second, year=normalize_year(int(third)))


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
        return tfhDate(month=month, day=first, year=normalize_year(int(year)))
    if suffix or first <= 31:
        return tfhDate(month=month, day=first)
    return tfhDate(month=month, year=normalize_year(first))


def _parse_time_component(text: str, allow_houronly: bool):
    text = _normalize_space(text)
    if not text:
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

    return tfhTime(
        hour=int(match.group("hour")),
        minute=int(match.group("minute") or 0),
        second=int(match.group("second") or 0),
        millisecond=int(match.group("millisecond") or 0),
        meridiem=meridiem,
    )


def _parse_duration(text: str):
    lowered = text.lower()
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
            total += timedelta_for_unit(normalized_unit, amount)
            unit = unit or normalized_unit
            position = numeric_match.end()
            continue

        word_match = re.match(r"[a-z]+(?:\s+[a-z]+)*", lowered[position:])
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
        return float(amount), unit, len(" ".join(tokens[: unit_index + 1]))

    return None


def _strip_trailing_timezone(text: str, timezone_mapping):
    if not text or not text[-1].isalpha():
        return text, None

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
    if len(parts) == 2 and weekday_index(parts[0]) is not None:
        return parts[1]
    return text


def _parse_month_name(value: str):
    return month_number(value)


def _parse_weekday_name(value: str):
    return weekday_index(value)


def _parse_meridiem(value: str):
    if value is None:
        return None
    if value.startswith("a"):
        return tfhTime.Meridiem.AM
    return tfhTime.Meridiem.PM


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


def _normalize_space(text: str):
    stripped = text.strip()
    if not stripped:
        return ""
    if "  " not in stripped and "\t" not in stripped and "\n" not in stripped and "\r" not in stripped:
        return stripped
    return " ".join(stripped.split())


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


def _extract_longest_match(tokens, start_index: int, text: str, parse_candidate):
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

        expression = parse_candidate(candidate, start)
        if expression is not None:
            return expression, end_index

    return None, start_index + 1


def _is_plausible_start(tokens, index: int):
    token = tokens[index][0].lower()
    next_token = tokens[index + 1][0].lower() if index + 1 < len(tokens) else ""

    if token in DATE_NAME_TO_OFFSET or token in TIME_NAME_TO_TEMPLATE or token in DATE_TIME_NAME_TO_TEMPLATE:
        return True
    if token in MODIFIER_TO_OFFSET and (weekday_index(next_token) is not None or month_number(next_token) is not None):
        return True
    if token in POSITION_TO_DELTA and weekday_index(next_token) is not None:
        return True
    if month_number(token) is not None or weekday_index(token) is not None:
        return True
    if token in NUMBER_WORDS and next_token in UNIT_ALIASES:
        return True
    if "/" in token or ":" in token or "t" in token and "-" in token:
        return True
    if re.fullmatch(rf"(?ix)\d+(?:{MERIDIEM_PATTERN})", token):
        return True
    if token.isdigit():
        return next_token in UNIT_ALIASES or next_token in WEEKDAY_ALIASES or next_token in DATE_NAME_TO_OFFSET or bool(
            re.fullmatch(MERIDIEM_PATTERN, next_token, flags=re.IGNORECASE)
        )

    return False
