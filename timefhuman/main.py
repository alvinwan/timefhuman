from dataclasses import dataclass, replace
from datetime import datetime, date, time, timedelta
from pathlib import Path
from lark import Lark, Transformer
from timefhuman.utils import get_month_mapping
import re

__all__ = ['timefhuman', 'tfhConfig', 'DEFAULT_CONFIG']

@dataclass
class tfhConfig:
    infer_datetimes: bool = True
    now: datetime | None = None

DEFAULT_CONFIG = tfhConfig()
DIRECTORY = Path(__file__).parent
_parser = None


@dataclass
class _Meta:
    value: datetime | date | time
    has_date: bool
    meridiem: str | None = None



def get_parser():
    global _parser
    if _parser is None:
        with open(DIRECTORY / 'grammar.lark', 'r') as f:
            grammar = f.read()
        _parser = Lark(grammar, start='start', parser='lalr')
    return _parser


class _Transformer(Transformer):
    def __init__(self, config: tfhConfig):
        super().__init__()
        self.config = config
        self.months = get_month_mapping()

    def MONTHNAME(self, token):
        return self.months[token.value.lower()]

    def MERIDIEM(self, token):
        return token.value.lower()

    def ORDINAL(self, token):
        return int(re.match(r"\d+", token.value).group())

    def RELATIVE_DAY(self, token):
        return token.value.lower()

    # Helpers
    def _year(self, value: int) -> int:
        return value + 2000 if value < 100 else value

    def _make_date(self, y, m, d):
        dt = date(self._year(y), m, d)
        if self.config.infer_datetimes:
            val = datetime.combine(dt, time(0, 0))
        else:
            val = dt
        return _Meta(val, True)

    def _make_time(self, hour, minute=0, meridiem=None):
        if meridiem:
            if meridiem.startswith('p') and hour < 12:
                hour += 12
            if meridiem.startswith('a') and hour == 12:
                hour = 0
        t = time(hour, minute)
        if self.config.infer_datetimes:
            val = datetime.combine(self.config.now.date(), t)
        else:
            val = t
        return _Meta(val, False, meridiem)

    def _apply_meridiem(self, meta: _Meta, meridiem: str) -> _Meta:
        if meta.meridiem is None:
            val = meta.value
            if isinstance(val, datetime):
                hour = val.hour
                if meridiem.startswith('p') and hour < 12:
                    hour += 12
                if meridiem.startswith('a') and hour == 12:
                    hour = 0
                val = val.replace(hour=hour)
            elif isinstance(val, time):
                hour = val.hour
                if meridiem.startswith('p') and hour < 12:
                    hour += 12
                if meridiem.startswith('a') and hour == 12:
                    hour = 0
                val = val.replace(hour=hour)
            return _Meta(val, meta.has_date, meridiem)
        return meta

    def start(self, items):
        def unwrap(obj):
            if isinstance(obj, _Meta):
                return obj.value
            if isinstance(obj, tuple):
                return tuple(unwrap(x) for x in obj)
            return obj

        return [unwrap(item) for item in items]

    # Time only
    def time_only(self, items):
        hour = int(items[0])
        minute = 0
        meridiem = None
        if len(items) == 2:
            token = items[1]
            if isinstance(token, str) and any(c.isalpha() for c in token):
                meridiem = token
            else:
                minute = int(token)
        elif len(items) == 3:
            minute = int(items[1])
            meridiem = items[2]
        return self._make_time(hour, minute, meridiem)

    # Date components
    def dash_date(self, items):
        a, b, c = map(int, items)
        if a > 31:
            y, m, d = a, b, c
        else:
            m, d, y = a, b, c
        return self._make_date(y, m, d)

    def slash_date_full(self, items):
        m, d, y = map(int, items)
        return self._make_date(y, m, d)

    def slash_date_short(self, items):
        a, b = map(int, items)
        if b > 31:
            m, y = a, b
            d = 1
        else:
            m, d = a, b
            y = self.config.now.year
        return self._make_date(y, m, d)

    def monthname_expression(self, items):
        m = int(items[0])
        val = items[1]
        if isinstance(val, str):
            day_or_year = int(re.match(r"\d+", val).group())
        else:
            day_or_year = int(val)
        if len(items) == 3:
            y = int(items[2])
            d = day_or_year
        else:
            if day_or_year > 31:
                y = day_or_year
                d = 1
            else:
                y = self.config.now.year
                d = day_or_year
        return self._make_date(y, m, d)

    def date_only(self, items):
        return items[0]

    def datetime(self, items):
        if len(items) == 3:
            first, _, second = items
        else:
            first, second = items
        f_val, s_val = first.value, second.value

        if isinstance(f_val, datetime) and isinstance(s_val, datetime):
            if f_val.time() != time(0, 0) and s_val.time() == time(0, 0):
                t = f_val.time()
                d = s_val.date()
                mer = first.meridiem
            elif s_val.time() != time(0, 0) and f_val.time() == time(0, 0):
                t = s_val.time()
                d = f_val.date()
                mer = second.meridiem
            else:
                d = f_val.date()
                t = s_val.time()
                mer = second.meridiem or first.meridiem
        elif isinstance(f_val, datetime):
            t = f_val.time()
            d = s_val if isinstance(s_val, date) else s_val.date()
            mer = first.meridiem
        elif isinstance(s_val, datetime):
            t = s_val.time()
            d = f_val if isinstance(f_val, date) else f_val.date()
            mer = second.meridiem
        else:
            d = f_val
            t = s_val
            mer = second.meridiem

        dt = datetime.combine(d, t)
        return _Meta(dt, True, mer)

    def relative_datetime(self, items):
        if isinstance(items[0], str):
            rel = items[0]
            t = items[1]
        else:
            t = items[0]
            rel = items[1]
        base = self.config.now.date()
        if rel == 'today':
            d = base
        elif rel == 'tomorrow':
            d = base + timedelta(days=1)
        else:
            d = base - timedelta(days=1)
        if isinstance(t, _Meta):
            val = t.value
            mer = t.meridiem
            if isinstance(val, datetime):
                val = val.time()
        else:
            val = t
            mer = None
        dt = datetime.combine(d, val)
        return _Meta(dt, True, mer)

    def month_day_range(self, items):
        month = int(items[0])
        start_day = int(items[1])
        end_day = int(items[2])
        year = int(items[3]) if len(items) == 4 else self.config.now.year
        start = self._make_date(year, month, start_day)
        end = self._make_date(year, month, end_day)
        return (start, end)

    def time_range_shorthand(self, items):
        start_hour = int(items[0])
        end_hour = int(items[1])
        mer = items[2]
        start = self._make_time(start_hour, 0, mer)
        end = self._make_time(end_hour, 0, mer)
        return (start, end)

    def range(self, items):
        if len(items) == 3:
            start, _, end = items
        else:
            start, end = items
        if end.meridiem and not start.meridiem:
            start = self._apply_meridiem(start, end.meridiem)
        s_val, e_val = start.value, end.value
        if (
            isinstance(s_val, datetime)
            and isinstance(e_val, datetime)
            and s_val > e_val
            and not start.has_date
            and not end.has_date
        ):
            e_val = e_val + timedelta(days=1)
            end = _Meta(e_val, end.has_date, end.meridiem)
        return (start, end)

    def range_value(self, items):
        return items[0]


def timefhuman(text: str, config: tfhConfig = DEFAULT_CONFIG):
    if not text.strip():
        return []
    text = text.strip()
    config = replace(config, now=config.now or datetime.now())
    parser = get_parser()
    tree = parser.parse(text)
    return _Transformer(config).transform(tree)
