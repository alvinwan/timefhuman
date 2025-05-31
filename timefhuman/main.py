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
            return datetime.combine(dt, time(0, 0))
        return dt

    def _make_time(self, hour, minute=0, meridiem=None):
        if meridiem:
            if meridiem.startswith('p') and hour < 12:
                hour += 12
            if meridiem.startswith('a') and hour == 12:
                hour = 0
        t = time(hour, minute)
        if self.config.infer_datetimes:
            return datetime.combine(self.config.now.date(), t)
        return t

    def start(self, items):
        return list(items)

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

        if isinstance(first, datetime) and isinstance(second, datetime):
            if first.time() != time(0, 0) and second.time() == time(0, 0):
                t = first.time()
                d = second.date()
            elif second.time() != time(0, 0) and first.time() == time(0, 0):
                t = second.time()
                d = first.date()
            else:
                d = first.date()
                t = second.time()
        elif isinstance(first, datetime):
            t = first.time()
            d = second if isinstance(second, date) else second.date()
        elif isinstance(second, datetime):
            t = second.time()
            d = first if isinstance(first, date) else first.date()
        else:
            d = first
            t = second
        return datetime.combine(d, t)

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
        if isinstance(t, datetime):
            t = t.time()
        return datetime.combine(d, t)


def timefhuman(text: str, config: tfhConfig = DEFAULT_CONFIG):
    if not text.strip():
        return []
    config = replace(config, now=config.now or datetime.now())
    parser = get_parser()
    tree = parser.parse(text)
    return _Transformer(config).transform(tree)
