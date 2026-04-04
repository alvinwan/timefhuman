from datetime import timedelta, timezone as dt_timezone
from pathlib import Path
import re

from dataclasses import replace
from lark import Lark, Transformer, UnexpectedInput
from lark.exceptions import VisitError
import pytz
from dateutil.relativedelta import relativedelta, weekdays

from timefhuman.inference import infer
from timefhuman.renderers import tfhDatetime, tfhDate, tfhTime, tfhRange, tfhList, tfhTimedelta, tfhAmbiguous
from timefhuman.semantics import (
    DATE_NAME_TO_OFFSET,
    DATE_TIME_NAME_TO_TEMPLATE,
    MODIFIER_TO_OFFSET,
    NUMBER_WORDS,
    build_date,
    build_numeric_date_parts,
    build_time,
    POSITION_TO_DELTA,
    TIME_NAME_TO_TEMPLATE,
    UNIT_ALIASES,
    clone_datetime,
    clone_time,
    is_invalid_ambiguous_date_range,
    is_rejected_compact_meridiem_text,
    is_rejected_fraction_text,
    month_number,
    normalize_year,
    supports_numeric_date_text,
    timedelta_for_unit,
    weekday_index,
)
from timefhuman.utils import (
    Direction,
    direction_to_offset,
    generate_timezone_mapping,
    nodes_to_dict,
    nodes_to_multidict,
    tfhConfig,
)


DIRECTORY = Path(__file__).parent
lalr_parsers = {}
timezone_mapping = None
__all__ = ("parse_lalr_renderers",)
MONTHNAME_DATE_PATTERN = re.compile(
    r"(?ix)^"
    r"(?P<month>[a-z]+)"
    r"\s+"
    r"(?P<first>\d{1,4})"
    r"(?P<suffix>st|nd|rd|th)?"
    r"(?:\s*,?\s*(?P<year>\d{2,4}))?$"
)
DAY_ORDINAL_PATTERN = re.compile(r"(?i)^(?P<day>\d{1,2})(?:st|nd|rd|th)$")


def get_lalr_parser():
    global lalr_parsers, timezone_mapping
    if 'default' not in lalr_parsers:
        timezone_mapping = generate_timezone_mapping()
        with open(DIRECTORY / 'grammar.lark', 'r') as file:
            grammar = file.read()
        grammar = grammar.replace('(TIMEZONE_MAPPING)', '|'.join(timezone_mapping.keys()))
        lalr_parsers['default'] = Lark(
            grammar,
            start="start",
            parser="lalr",
            lexer="contextual",
            g_regex_flags=re.IGNORECASE,
        )
    return lalr_parsers['default']


def _trimmed_span(string: str, start_pos: int = 0):
    stripped = string.strip()
    if not stripped:
        return "", start_pos, start_pos
    leading = len(string) - len(string.lstrip())
    trailing = len(string.rstrip())
    return stripped, start_pos + leading, start_pos + trailing


def parse_lalr_renderers(string: str, config: tfhConfig, start_pos: int = 0):
    stripped, span_start, span_end = _trimmed_span(string, start_pos)
    if not stripped:
        return None
    if is_rejected_fraction_text(stripped):
        return None

    try:
        tree = get_lalr_parser().parse(stripped)
    except UnexpectedInput:
        return None

    try:
        renderers = tfhTransformer(config=config).transform(tree)
    except VisitError as exc:
        if isinstance(exc.orig_exc, (KeyError, ValueError)):
            return None
        raise
    for renderer in renderers:
        renderer.matched_text_pos = (span_start, span_end)
    return renderers


class tfhTransformer(Transformer):
    def __init__(self, config: tfhConfig = tfhConfig()):
        self.config = config

    def start(self, children):
        return children

    def expression(self, children):
        return children[0]

    def single(self, children):
        return children[0]

    def range_item(self, children):
        return children[0]

    def list_item(self, children):
        return children[0]

    def range(self, children):
        assert len(children) == 2
        if is_invalid_ambiguous_date_range(children[0], children[1]):
            raise ValueError("Ambiguous-date range")
        if all(isinstance(child, tfhAmbiguous) for child in children):
            raise ValueError("Ambiguous-only range")
        return tfhRange(infer(children))

    def list(self, children):
        if all(isinstance(child, tfhAmbiguous) for child in children):
            raise ValueError("Ambiguous-only list")
        return tfhList(infer(children))

    def duration(self, children):
        config = replace(self.config, infer_datetimes=False)
        direction = Direction.next
        total = timedelta()
        unit = None
        for child in children:
            if hasattr(child, "type"):
                if child.type == 'DURATION_PAST':
                    direction = Direction.previous
                elif child.type == 'DURATION_FUTURE':
                    direction = Direction.next
                elif child.type == 'DURATION_PREFIX_PAST':
                    direction = Direction.previous
            else:
                total += child.to_object(config)
                if unit is None:
                    unit = child.unit

        if direction == Direction.previous:
            total = -total
        return tfhTimedelta.from_object(total, unit=unit)

    def duration_part(self, children):
        data = {child.data.value: [_child.value for _child in child.children] for child in children}
        duration_number = float(data['duration_number'][0]) if 'duration_number' in data else sum(
            NUMBER_WORDS[value] for value in data.get('duration_numbername', [])
        )
        raw_unit = data.get('duration_unit', data.get('duration_unit_letter', None))[0]
        if len(raw_unit) == 1 and raw_unit.isalpha() and raw_unit != raw_unit.lower():
            raise ValueError(f"Invalid duration unit: {raw_unit}")
        duration_unit = UNIT_ALIASES[raw_unit.lower()]
        return tfhTimedelta.from_object(timedelta_for_unit(duration_unit, duration_number), unit=duration_unit)

    def datetime(self, children):
        data = nodes_to_dict(children)
        if 'datetime' in data:
            return data['datetime']
        return tfhDatetime(date=data.get('date'), time=data.get('time'), tz=data.get('timezone'))

    def date(self, children):
        data = nodes_to_dict(children)

        if 'date' in data:
            return {'date': data['date']}

        if 'weekday' in data and all(key not in data for key in ('day', 'month', 'year')):
            return {'date': data['weekday']}

        delta = None
        if 'offset' in data and 'month' in data and 'weekday' in data:
            weekday = weekdays[data['weekday'].to_object(self.config).weekday()]
            offset = sum(nodes_to_multidict(children)['offset'])
            if offset == -1:
                delta = relativedelta(day=31, weekday=weekday(-1))
            elif offset == 1:
                delta = relativedelta(day=1, weekday=weekday(+1))
        elif 'offset' in data:
            delta = relativedelta(years=sum(nodes_to_multidict(children)['offset']))
        elif 'position' in data:
            weekday = weekdays[data['weekday'].to_object(self.config).weekday()]
            delta = POSITION_TO_DELTA[data['position']](weekday)

        return {'date': tfhDate(
            year=data.get('year'),
            month=data.get('month'),
            day=data.get('day'),
            delta=delta,
        )}

    def numeric_date(self, children):
        value = children[0].value
        if not supports_numeric_date_text(value):
            raise ValueError(f"Invalid numeric date: {value}")
        if "/" in value:
            sep = "/"
        elif "-" in value:
            sep = "-"
        else:
            sep = "."
        raw_parts = value.split(sep)
        result = build_numeric_date_parts(*raw_parts)
        if result is None:
            raise ValueError(f"Invalid numeric date: {value}")
        return {'date': result}

    def day(self, children):
        return {'day': int(children[0].value)}

    def month(self, children):
        return {'month': int(children[0].value)}

    def year(self, children):
        return {'year': normalize_year(int(children[0].value))}

    def monthname(self, children):
        month = month_number(children[0].value)
        if month is None:
            raise ValueError(f"Invalid month name: {children[0].value}")
        return {'month': month}

    def monthname_date(self, children):
        match = MONTHNAME_DATE_PATTERN.fullmatch(children[0].value)
        if match is None:
            raise NotImplementedError(f"Unknown monthname date: {children[0].value}")

        month = month_number(match.group('month'))
        if month is None:
            raise ValueError(f"Invalid monthname date: {children[0].value}")
        first = int(match.group('first'))
        year = match.group('year')

        if year is not None:
            result = build_date(month=month, day=first, year=normalize_year(int(year)))
            if result is None:
                raise ValueError(f"Invalid monthname date: {children[0].value}")
            return {'date': result}
        if match.group('suffix') or first <= 31:
            result = build_date(month=month, day=first)
            if result is None:
                raise ValueError(f"Invalid monthname date: {children[0].value}")
            return {'date': result}
        result = build_date(month=month, year=normalize_year(first))
        if result is None:
            raise ValueError(f"Invalid monthname date: {children[0].value}")
        return {'date': result}

    def day_ordinal(self, children):
        match = DAY_ORDINAL_PATTERN.fullmatch(children[0].value)
        if match is None:
            raise NotImplementedError(f"Unknown day ordinal: {children[0].value}")
        result = build_date(day=int(match.group('day')))
        if result is None:
            raise ValueError(f"Invalid day ordinal: {children[0].value}")
        return {'date': result}

    def modified_month(self, children):
        offset = sum(child['offset'] for child in children[:-1])
        month = month_number(children[-1].value)
        if month is None:
            raise ValueError(f"Invalid modified month: {children[-1].value}")
        return {'month': month, 'offset': offset}

    def weekday(self, children):
        target_weekday = weekday_index(children[0].value)
        offset = direction_to_offset(self.config.direction)
        date = self.config.now.date() + relativedelta(weekday=weekdays[target_weekday](offset))
        return {'weekday': tfhDate.from_object(date)}

    def modified_weekday(self, children):
        offset = sum(child['offset'] for child in children[:-1])
        target_weekday = weekday_index(children[-1].value)
        date = self.config.now.date() + relativedelta(weekday=weekdays[target_weekday](offset))
        return {'weekday': tfhDate.from_object(date)}

    def modifier(self, children):
        value = children[0].value
        if value not in MODIFIER_TO_OFFSET:
            raise NotImplementedError(f"Unknown modifier: {value}")
        return {'offset': MODIFIER_TO_OFFSET[value]}

    def datename(self, children):
        datename = children[0].value.lower()
        if datename not in DATE_NAME_TO_OFFSET:
            raise NotImplementedError(f"Unknown datename: {datename}")
        return {'date': tfhDate.from_object(self.config.now.date() + timedelta(days=DATE_NAME_TO_OFFSET[datename]))}

    def dayoryear(self, children):
        if children[0].value.isdigit():
            value = int(children[0].value)
            return {'day': value} if value < 32 else {'year': value}
        raise NotImplementedError(f"Unknown day or year: {children[0]}")

    def ambiguous(self, children):
        return tfhAmbiguous(int(children[0].value))

    def time(self, children):
        data = nodes_to_dict(children)

        if 'time' in data:
            return {'time': data['time']}

        result = build_time(
            hour=int(data.get("hour", 0)),
            minute=int(data.get("minute", 0)),
            second=int(data.get("second", 0)),
            millisecond=int(data.get("millisecond", 0)),
            meridiem=data.get("meridiem", None),
        )
        if result is None:
            raise ValueError(f"Invalid time: {data}")
        return {'time': result}

    def meridiem(self, children):
        raw = children[0].value
        if len(raw) == 1 and raw != raw.lower():
            raise ValueError(f"Invalid meridiem: {raw}")
        meridiem = raw.lower()
        if meridiem.startswith('a'):
            return {'meridiem': tfhTime.Meridiem.AM}
        if meridiem.startswith('p'):
            return {'meridiem': tfhTime.Meridiem.PM}
        raise NotImplementedError(f"Unknown meridiem: {meridiem}")

    def timezone(self, children):
        timezone = children[0].value.lower()
        if timezone.startswith(("+", "-")):
            sign = -1 if timezone[0] == "-" else 1
            body = timezone[1:].replace(":", "")
            hours = int(body[:2])
            minutes = int(body[2:])
            if hours > 23 or minutes > 59:
                raise ValueError(f"Invalid timezone offset: {timezone}")
            return {'timezone': dt_timezone(sign * timedelta(hours=hours, minutes=minutes))}
        return {'timezone': pytz.timezone(timezone_mapping[timezone])}

    def timename(self, children):
        timename = children[0].value.lower()
        if timename not in TIME_NAME_TO_TEMPLATE:
            raise NotImplementedError(f"Unknown timename: {timename}")
        return {'time': clone_time(TIME_NAME_TO_TEMPLATE[timename])}

    def houronly(self, children):
        result = build_time(hour=int(children[0].value))
        if result is None:
            raise ValueError(f"Invalid hour: {children[0].value}")
        return {'time': result}

    def datetimename(self, children):
        datetimename = children[0].value.lower()
        if datetimename not in DATE_TIME_NAME_TO_TEMPLATE:
            raise NotImplementedError(f"Unknown datetimename: {datetimename}")
        value = clone_datetime(DATE_TIME_NAME_TO_TEMPLATE[datetimename])
        value.date = tfhDate.from_object(self.config.now.date())
        return {'datetime': value}

    def iso_datetime(self, children):
        value = children[0].value
        date_part, time_part = value.split('T', 1)
        year, month, day = [int(part) for part in date_part.split('-')]

        millisecond = 0
        second = 0
        if '.' in time_part:
            time_part, fraction = time_part.split('.', 1)
            millisecond = int(fraction)
        time_parts = [int(part) for part in time_part.split(':')]
        hour, minute = time_parts[:2]
        if len(time_parts) > 2:
            second = time_parts[2]

        date = build_date(year=year, month=month, day=day)
        time = build_time(hour=hour, minute=minute, second=second, millisecond=millisecond)
        if date is None or time is None:
            raise ValueError(f"Invalid ISO datetime: {value}")
        return {'datetime': tfhDatetime(
            date=date,
            time=time,
        )}
