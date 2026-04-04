import re
from datetime import timedelta, timezone as dt_timezone

import pytz

from timefhuman.atoms import parse_date_atom, parse_datetime_atom, parse_duration_atom, parse_time_atom
from timefhuman.inference import infer
from timefhuman.renderers import tfhAmbiguous, tfhDatelike, tfhDatetime, tfhDate, tfhList, tfhRange, tfhTime
from timefhuman.semantics import is_invalid_ambiguous_date_range
from timefhuman.utils import get_timezone_word_lengths


__all__ = ("is_ambiguous_only", "normalize_space", "parse_expression")


BETWEEN_RANGE_PATTERN = re.compile(r"(?is)^between\s+(?P<left>.+?)\s+and\s+(?P<right>.+)$")
NUMERIC_TIMEZONE_OFFSET_PATTERN = re.compile(r"^(?P<body>.*\S)\s+(?P<sign>[+-])(?P<hour>\d{2})(?::?(?P<minute>\d{2}))$")
HYPHENATED_NUMERIC_DATE_TOKEN_PATTERN = re.compile(r"^\d{1,4}-\d{1,4}-\d{1,4}$")


def parse_expression(text: str, config, timezone_mapping, allow_ambiguous: bool):
    if not text:
        return None

    if _prefer_atomic_comma_parse(text):
        single = _parse_single(text, config, timezone_mapping, allow_ambiguous=allow_ambiguous)
        if single is not None:
            return single

    if _prefer_collection_parse(text):
        parsers = (_parse_range, _parse_list) if _prefer_range_first(text) else (_parse_list, _parse_range)
        for parser in parsers:
            expression = parser(text, config, timezone_mapping)
            if expression is not None:
                return expression

    single = _parse_single(text, config, timezone_mapping, allow_ambiguous=allow_ambiguous)
    if single is not None:
        return single

    if not _prefer_collection_parse(text):
        parsers = (_parse_range, _parse_list) if _prefer_range_first(text) else (_parse_list, _parse_range)
        for parser in parsers:
            expression = parser(text, config, timezone_mapping)
            if expression is not None:
                return expression

    return None


def is_ambiguous_only(expression):
    if isinstance(expression, tfhAmbiguous):
        return True
    if isinstance(expression, (tfhList, tfhRange)):
        return all(is_ambiguous_only(item) for item in expression.items)
    return False


def normalize_space(text: str):
    stripped = text.strip()
    if not stripped:
        return ""
    if "  " not in stripped and "\t" not in stripped and "\n" not in stripped and "\r" not in stripped:
        return stripped
    return " ".join(stripped.split())


def _parse_list(text: str, config, timezone_mapping):
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
            if all(isinstance(item, tfhAmbiguous) for item in items):
                continue
            result = tfhList(infer(items))
            if tzinfo:
                result.tz = tzinfo
            return result

    return None


def _parse_range(text: str, config, timezone_mapping):
    body, tzinfo = _strip_trailing_timezone(text, timezone_mapping)

    between_match = BETWEEN_RANGE_PATTERN.fullmatch(body)
    if between_match:
        result = _build_range(between_match.group("left"), between_match.group("right"), config, timezone_mapping)
        if result and tzinfo:
            result.tz = tzinfo
        return result

    if " to " in body.lower():
        parts = re.split(r"(?i)\s+to\s+", body, maxsplit=1)
        if len(parts) == 2:
            result = _build_range(parts[0], parts[1], config, timezone_mapping)
            if result and tzinfo:
                result.tz = tzinfo
            return result

    indices = [index for index, char in enumerate(body) if char == "-"]
    preferred = [index for index in indices if _looks_like_range_hyphen(body, index)]
    for index in preferred:
        result = _build_range(body[:index], body[index + 1 :], config, timezone_mapping)
        if result:
            if tzinfo:
                result.tz = tzinfo
            return result

    return None


def _build_range(left_text: str, right_text: str, config, timezone_mapping):
    left = _parse_single(left_text.strip(), config, timezone_mapping, allow_ambiguous=True)
    right = _parse_single(right_text.strip(), config, timezone_mapping, allow_ambiguous=True)
    if left is None or right is None:
        return None
    if is_invalid_ambiguous_date_range(left, right):
        return None
    if isinstance(left, tfhAmbiguous) and isinstance(right, tfhAmbiguous):
        return None
    left_missing_year = _datelike_missing_year(left)
    right_missing_year = _datelike_missing_year(right)
    items = infer([left, right])
    _adjust_cross_year_range(items, left_missing_year, right_missing_year, config.now.year)
    result = tfhRange(items)
    return None if is_ambiguous_only(result) else result


def _parse_range_or_single(text: str, config, timezone_mapping, allow_ambiguous: bool):
    return _parse_range(text, config, timezone_mapping) or _parse_single(
        text, config, timezone_mapping, allow_ambiguous=allow_ambiguous
    )


def _parse_single(text: str, config, timezone_mapping, allow_ambiguous: bool):
    duration = parse_duration_atom(text, normalize_space)
    if duration is not None:
        return duration

    datetime_like = _parse_datetime(text, config, timezone_mapping)
    if datetime_like is not None:
        return datetime_like

    if allow_ambiguous and text.isdigit():
        return tfhAmbiguous(int(text))

    return None


def _datelike_missing_year(value):
    if not isinstance(value, tfhDatelike):
        return False
    if isinstance(value, (tfhList, tfhRange)):
        return False
    return value.date is not None and value.year is None and value.month is not None and value.day is not None


def _adjust_cross_year_range(items, left_missing_year: bool, right_missing_year: bool, default_year: int):
    if len(items) != 2:
        return
    left, right = items
    if not (
        left_missing_year
        and right_missing_year
        and isinstance(left, tfhDatelike)
        and isinstance(right, tfhDatelike)
        and left.date
        and right.date
        and left.month is not None
        and left.day is not None
        and right.month is not None
        and right.day is not None
    ):
        return

    if (right.month, right.day) < (left.month, left.day):
        base_year = right.year or left.year or default_year
        right.year = base_year + 1


def _parse_datetime(text: str, config, timezone_mapping):
    text = normalize_space(text)
    if not text:
        return None

    body, tzinfo = _strip_trailing_timezone(text, timezone_mapping)
    if not body:
        return None

    atomic = parse_datetime_atom(body, config, tzinfo, normalize_space)
    if atomic is not None:
        return atomic

    timezone_datetime = _parse_inline_timezone_datetime(body, config, timezone_mapping)
    if timezone_datetime is not None:
        return timezone_datetime

    lower_body = body.lower()
    for separator, mode in ((" at ", "date_time"), (" on ", "time_date")):
        if separator in lower_body:
            left, right = re.split(rf"(?i){separator.strip()}", body, maxsplit=1)
            if mode == "date_time":
                date = parse_date_atom(left, config, normalize_space)
                time = parse_time_atom(right, allow_houronly=True, normalize_space=normalize_space)
            else:
                time = parse_time_atom(left, allow_houronly=True, normalize_space=normalize_space)
                date = parse_date_atom(right, config, normalize_space)
            if date and time:
                return tfhDatetime(date=date, time=time, tz=tzinfo)

    parts = body.split()
    best = None
    best_score = -1
    for index in range(1, len(parts)):
        left = " ".join(parts[:index])
        right = " ".join(parts[index:])

        date = parse_date_atom(left, config, normalize_space)
        time = parse_time_atom(right, allow_houronly=True, normalize_space=normalize_space)
        if date and time:
            score = _date_score(date) + _time_score(time)
            if score > best_score:
                best = tfhDatetime(date=date, time=time, tz=tzinfo)
                best_score = score

        time = parse_time_atom(left, allow_houronly=True, normalize_space=normalize_space)
        date = parse_date_atom(right, config, normalize_space)
        if date and time:
            score = _date_score(date) + _time_score(time)
            if score > best_score:
                best = tfhDatetime(date=date, time=time, tz=tzinfo)
                best_score = score

    return best


def _parse_inline_timezone_datetime(text: str, config, timezone_mapping):
    comma_indices = [index for index, char in enumerate(text) if char == ","]
    for comma_index in comma_indices:
        left = text[:comma_index].strip()
        right = text[comma_index + 1 :].strip()
        if not left or not right:
            continue

        date = parse_date_atom(right, config, normalize_space)
        if date is None:
            continue

        time_with_timezone = _parse_time_with_inline_timezone(left, timezone_mapping)
        if time_with_timezone is None:
            continue

        time, timezone = time_with_timezone
        return tfhDatetime(date=date, time=time, tz=timezone)

    return None


def _parse_time_with_inline_timezone(text: str, timezone_mapping):
    body, timezone = _strip_trailing_timezone(text.strip().rstrip(","), timezone_mapping)
    if timezone is None:
        return None

    time = parse_time_atom(body.rstrip(", ").strip(), allow_houronly=True, normalize_space=normalize_space)
    if time is None:
        return None

    return time, timezone


def _strip_trailing_timezone(text: str, timezone_mapping):
    offset_match = NUMERIC_TIMEZONE_OFFSET_PATTERN.fullmatch(text)
    if offset_match:
        hours = int(offset_match.group("hour"))
        minutes = int(offset_match.group("minute"))
        if hours <= 23 and minutes <= 59:
            sign = -1 if offset_match.group("sign") == "-" else 1
            offset = sign * timedelta(hours=hours, minutes=minutes)
            return offset_match.group("body").strip(), dt_timezone(offset)

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


def _looks_like_range_hyphen(text: str, index: int):
    token_start = index
    while token_start > 0 and not text[token_start - 1].isspace():
        token_start -= 1
    token_end = index + 1
    while token_end < len(text) and not text[token_end].isspace():
        token_end += 1
    token = text[token_start:token_end]
    if HYPHENATED_NUMERIC_DATE_TOKEN_PATTERN.fullmatch(token):
        return False

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


def _prefer_atomic_comma_parse(text: str):
    lowered = text.lower()
    return "," in text and " or " not in lowered and " to " not in lowered and " -" not in text and "- " not in text


def _prefer_range_first(text: str):
    lowered = text.lower()
    return "-" in text and " or " not in lowered


def _supports_comma_list(text: str, config, timezone_mapping):
    if "," not in text:
        return False
    if text.count(",") > 1:
        return True

    collapsed = text.replace(",", " ")
    return _parse_single(collapsed, config, timezone_mapping, allow_ambiguous=False) is None
