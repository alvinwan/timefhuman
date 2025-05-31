from dataclasses import dataclass, replace
from datetime import datetime, date, time, timedelta
from pathlib import Path
from lark import Lark, Transformer, Token
from timefhuman.utils import get_month_mapping
from typing import List, Union
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

    def UNIT(self, token):
        return token.value.lower()

    def H(self, token):
        return token.value.lower()

    def M(self, token):
        return token.value.lower()

    def FLOAT(self, token):
        return float(token)

    def WORDNUM(self, token):
        return token.value.lower()

    def NEXT(self, token):
        return token.value.lower()

    def LAST(self, token):
        return token.value.lower()

    def THIS(self, token):
        return token.value.lower()

    def OF(self, token):
        return token.value.lower()

    def ORDINAL_WORD(self, token):
        mapping = {'first': 1, 'second': 2, 'third': 3, 'fourth': 4}
        return mapping[token.value.lower()]

    def modifier(self, items):
        return items[0]

    def word_number(self, items):
        words = [str(w).lower() for w in items]
        return self._words_to_int(words)

    def amount(self, items):
        return items[0]

    def unit(self, items):
        return items[0]

    def IN(self, token):
        return token.value.lower()

    def AGO(self, token):
        return token.value.lower()

    def ORDINAL(self, token):
        return int(re.match(r"\d+", token.value).group())

    def RELATIVE_DAY(self, token):
        return token.value.lower()
    
    def WEEKDAY(self, token):
        text = token.value.lower()
        for i, day in enumerate([
            'mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'
        ]):
            if text.startswith(day):
                return i
        raise ValueError(f"Invalid weekday: {token.value}")

    # Helpers
    def _year(self, value: int) -> int:
        if value < 100:
            return 1900 + value if value >= 70 else 2000 + value
        return value

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

    def _relative_weekday(self, weekday: int, mods: List[str]) -> date:
        base = self.config.now.date()
        date_val = base + timedelta((weekday - base.weekday()) % 7)
        count_next = sum(1 for m in mods if m == 'next')
        count_last = sum(1 for m in mods if m == 'last')
        week_offset = count_next - count_last
        if count_next:
            week_offset -= 1
        return date_val + timedelta(weeks=week_offset)

    def _weekday_of_month_date(
        self, year: int, month: int, weekday: int, ordinal: int = 1, last: bool = False
    ) -> date:
        if last:
            if month == 12:
                next_month = date(year + 1, 1, 1)
            else:
                next_month = date(year, month + 1, 1)
            last_day = next_month - timedelta(days=1)
            return last_day - timedelta((last_day.weekday() - weekday) % 7)
        first = date(year, month, 1)
        offset = (weekday - first.weekday()) % 7
        return first + timedelta(days=offset + 7 * (ordinal - 1))

    def _year_with_mods(self, mods: Union[str, List[str]]) -> int:
        if isinstance(mods, str):
            mods = [mods]
        offset = sum(1 if m == 'next' else -1 if m == 'last' else 0 for m in mods)
        return self.config.now.year + offset

    def _duration_to_timedelta(self, amount: float, unit: str) -> timedelta:
        unit = unit.lower()
        if unit.startswith('min') or unit == 'm':
            return timedelta(minutes=amount)
        if unit.startswith('hour') or unit.startswith('hr') or unit == 'h':
            return timedelta(hours=amount)
        if unit.startswith('day'):
            return timedelta(days=amount)
        if unit.startswith('week') or unit.startswith('wk'):
            return timedelta(weeks=amount)
        if unit.startswith('month') or unit.startswith('mo'):
            return timedelta(days=30 * amount)
        if unit.startswith('year'):
            return timedelta(days=365 * amount)
        raise ValueError(f'Unknown unit: {unit}')

    def _words_to_int(self, words):
        ones = {
            'a': 1, 'an': 1, 'one': 1, 'two': 2, 'three': 3, 'four': 4,
            'five': 5, 'six': 6, 'seven': 7, 'eight': 8, 'nine': 9,
            'ten': 10, 'eleven': 11, 'twelve': 12, 'thirteen': 13,
            'fourteen': 14, 'fifteen': 15, 'sixteen': 16, 'seventeen': 17,
            'eighteen': 18, 'nineteen': 19,
        }
        tens = {
            'twenty': 20, 'thirty': 30, 'forty': 40, 'fifty': 50,
            'sixty': 60, 'seventy': 70, 'eighty': 80, 'ninety': 90,
        }
        total = 0
        i = 0
        while i < len(words):
            word = words[i]
            if word in tens:
                val = tens[word]
                if i + 1 < len(words) and words[i + 1] in ones:
                    val += ones[words[i + 1]]
                    i += 1
                total += val
            else:
                total += ones.get(word, 0)
            i += 1
        return total

    def start(self, items):
        def unwrap(obj):
            if isinstance(obj, _Meta):
                return obj.value
            if isinstance(obj, tuple):
                return tuple(unwrap(x) for x in obj)
            if isinstance(obj, list):
                return [unwrap(x) for x in obj]
            return obj

        return [unwrap(item) for item in items]
    
    def choice(self, items):
        items = [item for item in items if not isinstance(item, Token)]
        if len(items) == 1 and isinstance(items[0], list):
            return items[0]
        return items

    def month_partial_choice(self, items):
        month = int(items[0])
        first_day = int(items[1])
        second_day = int(items[3])
        time_part = items[4]
        first = self._make_date(self.config.now.year, month, first_day)
        second = self._make_date(self.config.now.year, month, second_day)
        first_dt = self.datetime([first, time_part])
        second_dt = self.datetime([second, time_part])
        return [first_dt, second_dt]

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
    
    def time_shorthand(self, items):
        mapping = {
            'noon': (12, 0, 'p'),
            'midday': (12, 0, 'p'),
            'midnight': (0, 0, 'a'),
            'morning': (6, 0, None),
            'afternoon': (15, 0, None),
            'evening': (18, 0, None),
            'night': (20, 0, None),
        }
        word = items[0]
        hour, minute, mer = mapping.get(word)
        return self._make_time(hour, minute, mer)

    def tonight(self, items):
        dt = datetime.combine(self.config.now.date(), time(20, 0))
        return _Meta(dt, True)

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
        if len(items) == 1:
            return items[0]
        # if a weekday is present, ignore it
        return items[1] if isinstance(items[0], int) else items[0]

    def date_simple(self, items):
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
    
    def relative_range(self, items):
        if isinstance(items[0], str):
            rel = items[0]
            rng = items[1]
        else:
            rng = items[0]
            rel = items[1]
        base = self.config.now.date()
        if rel == 'today':
            d = base
        elif rel == 'tomorrow':
            d = base + timedelta(days=1)
        else:
            d = base - timedelta(days=1)
        start, end = rng
        def combine(meta: _Meta):
            val = meta.value
            if isinstance(val, datetime):
                val = val.time()
            return _Meta(datetime.combine(d, val), True, meta.meridiem)
        return (combine(start), combine(end))

    def weekday_datetime(self, items):
        if isinstance(items[0], int):
            wd = items[0]
            t = items[1]
        else:
            t = items[0]
            wd = items[1]
        base = self.config.now
        days_ahead = (wd - base.weekday()) % 7
        d = base.date() + timedelta(days=days_ahead)
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

    def weekday_mod(self, items):
        month = None
        if len(items) >= 4 and items[-2] == 'of':
            month = items[-1]
            items = items[:-2]
        *mods, wd = items

        if month is None:
            date_val = self._relative_weekday(wd, mods)
            return self._make_date(date_val.year, date_val.month, date_val.day)

        year = self.config.now.year
        is_last = mods and mods[-1] == 'last'
        target = self._weekday_of_month_date(year, month, wd, last=is_last)
        return self._make_date(target.year, target.month, target.day)

    def month_mod(self, items):
        mod, month = items
        year = self._year_with_mods(mod)
        return self._make_date(year, month, 1)

    def weekday_of_month(self, items):
        if len(items) == 4:
            ord_token, weekday, _, month = items
        else:
            ord_token, weekday, month = items
        year = self.config.now.year
        if ord_token == 'last':
            target = self._weekday_of_month_date(year, month, weekday, last=True)
        else:
            target = self._weekday_of_month_date(
                year, month, weekday, ordinal=int(ord_token)
            )
        return self._make_date(target.year, target.month, target.day)

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

    def duration(self, items):
        def get_amount(token):
            return float(int(token)) if isinstance(token, Token) else float(token)

        is_ago = False
        if items and isinstance(items[-1], str) and items[-1].lower() == 'ago':
            is_ago = True
            items = items[:-1]

        if len(items) in (2, 4, 5):
            amount1 = get_amount(items[0])
            unit1 = items[1]
            delta = self._duration_to_timedelta(amount1, unit1)
            if len(items) >= 4:
                second_idx = 3 if isinstance(items[2], str) and items[2].lower() == 'and' else 2
                amount2 = get_amount(items[second_idx])
                unit2 = items[second_idx + 1]
                delta += self._duration_to_timedelta(amount2, unit2)
        else:
            return None

        if self.config.infer_datetimes:
            return self.config.now - delta if is_ago else self.config.now + delta
        return -delta if is_ago else delta

    def duration_range_short(self, items):
        start_amt = float(items[0])
        end_amt = float(items[1])
        unit = items[2]
        start_delta = self._duration_to_timedelta(start_amt, unit)
        end_delta = self._duration_to_timedelta(end_amt, unit)
        if self.config.infer_datetimes:
            return (self.config.now + start_delta, self.config.now + end_delta)
        return (start_delta, end_delta)

    def duration_choice_short(self, items):
        first_amt = float(items[0])
        second_amt = float(items[2])
        unit = items[3]
        first_delta = self._duration_to_timedelta(first_amt, unit)
        second_delta = self._duration_to_timedelta(second_amt, unit)
        if self.config.infer_datetimes:
            return [self.config.now + first_delta, self.config.now + second_delta]
        return [first_delta, second_delta]

    def relative_duration(self, items):
        amount = float(items[1])
        unit = items[2]
        delta = self._duration_to_timedelta(amount, unit)
        return self.config.now + delta if self.config.infer_datetimes else delta

    def range(self, items):
        if len(items) == 3:
            start, _, end = items
        else:
            start, end = items
        if end.meridiem and not start.meridiem:
            start = self._apply_meridiem(start, end.meridiem)
        s_val, e_val = start.value, end.value
        if isinstance(s_val, datetime) and isinstance(e_val, datetime):
            if start.has_date and not end.has_date:
                e_val = e_val.replace(year=s_val.year, month=s_val.month, day=s_val.day)
                end = _Meta(e_val, True, end.meridiem)
            elif end.has_date and not start.has_date:
                s_val = s_val.replace(year=e_val.year, month=e_val.month, day=e_val.day)
                start = _Meta(s_val, True, start.meridiem)
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
