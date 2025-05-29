from dataclasses import dataclass, replace
from datetime import datetime, date, time
from pathlib import Path
from lark import Lark, Transformer
from timefhuman.utils import get_month_mapping

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

    def start(self, items):
        return list(items)

    def hour(self, items):
        return int(items[0])

    def minute(self, items):
        return int(items[0])

    def day(self, items):
        return int(items[0])

    def month(self, items):
        return int(items[0])

    def year(self, items):
        return int(items[0])

    def MONTHNAME(self, token):
        return self.months[token.value.lower()]

    def MERIDIEM(self, token):
        return token.value.lower()

    def time_only(self, items):
        hour = items[0]
        if len(items) == 3:
            minute = items[1]
            meridiem = items[2]
        else:
            minute = 0
            meridiem = items[1]
        if meridiem.startswith('p') and hour < 12:
            hour += 12
        if meridiem.startswith('a') and hour == 12:
            hour = 0
        t = time(hour, minute)
        if self.config.infer_datetimes:
            return datetime.combine(self.config.now.date(), t)
        return t

    def date_only(self, items):
        m, d, y = [i for i in items if not isinstance(i, str)]
        if y < 100:
            y += 2000
        dt = date(y, m, d)
        if self.config.infer_datetimes:
            return datetime.combine(dt, time(0, 0))
        return dt

    def datetime(self, items):
        if isinstance(items[0], datetime):
            d = items[0].date()
            t = items[1].time()
        elif isinstance(items[1], datetime):
            t = items[0].time()
            d = items[1].date()
        else:
            d, t = items
        return datetime.combine(d, t)


def timefhuman(text: str, config: tfhConfig = DEFAULT_CONFIG):
    if not text.strip():
        return []
    config = replace(config, now=config.now or datetime.now())
    parser = get_parser()
    tree = parser.parse(text)
    results = _Transformer(config).transform(tree)
    return results
