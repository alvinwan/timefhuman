"""
timefhuman
===
Convert human-readable date-like string to Python datetime object.

1. Tokenize string
2. Parse possible synctatic categories: "day", "time", "time range" etc.
3. Build parse tree.
4. Use grammar to resolve lexical ambiguities.
5. Impute with default values. Output extracted datetime and/or ranges.

@author: Alvin Wan
@site: alvinwan.com
"""


__all__ = ('timefhuman',)

from lark import Lark, Transformer, Tree, Token
from datetime import datetime, date, time, timedelta
from typing import Optional
from enum import Enum
from dataclasses import dataclass


Direction = Enum('Direction', ['previous', 'next'])

@dataclass
class tfhConfig:
    direction: Direction = Direction.next
    infer_datetimes: bool = True

grammar = """
%import common.WS
%import common.INT
%ignore WS

// ----------------------
// TERMINAL DEFINITIONS
// ----------------------

// Month names as a regex token, case-insensitive
MONTHNAME: /(?i)(january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|jun|jul|aug|sep|oct|nov|dec)/

// For weekdays, also as a single regex token, case-insensitive
WEEKDAY: /(?i)(mon|tue|wed|thu|fri|sat|sun)/

// Meridiem token (am/pm, with optional dots)
MERIDIEM: /(?i)([ap](\.?m\.?)?)/

// Datename token (today, tomorrow, yesterday)
DATENAME: /(?i)(today|tomorrow|tmw|yesterday)/

// Timename token (noon)
TIMENAME: /(?i)(noon|midday|midnight)/

// Duration unit (minutes, hours, days, etc.)
DURATION_UNIT: /(?i)(minutes|mins|min|m|hours|hour|hrs|hr|h|days|day|d|weeks|week|wks|wk|months|month|mos|years|years)/

// Duration number (digits like "1", or words like "an", "a", "one", "two", etc.)
DURATION_NUMBER: /(?i)(an|a|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|[0-9]+(\.[0-9]+)?)/

// Day suffix (th, rd, st, nd)
DAY_SUFFIX: /(?i)(th|rd|st|nd)/

// ----------------------
// PARSER RULES
// ----------------------
start: expression

expression: single
          | list
          | range

range: single ("to" | "-") single

list: single ("," single)+ 
    | single ("or" single)+
    | range ("or" range)+

single: datetime 
       | date 
       | time
       | duration

datetime: date ("at" time)?
        | date time
        | time date
        | time "on" date

date: month "/" day "/" year
    | month "/" dayoryear
    | month "-" day "-" year
    | month "-" dayoryear
    | datename
    | weekday
    | monthname day DAY_SUFFIX? (",")? year
    | monthname day DAY_SUFFIX
    | day DAY_SUFFIX
    | monthname dayoryear

time: hour ":" minute meridiem?
    | hour meridiem?
    | timename

duration: ("in"|"for")? duration_part (("and"|",")? duration_part)* ("ago")?
duration_part: duration_number duration_unit
duration_number: DURATION_NUMBER
duration_unit: DURATION_UNIT

timename: TIMENAME
weekday: WEEKDAY
monthname: MONTHNAME
datename: DATENAME
dayoryear: INT

day: INT
month: INT
year: INT

hour: INT
minute: INT
meridiem: MERIDIEM
"""


class tfhTime(time):
    meridiem: Optional[str] = None
    
    def __new__(cls, *args, meridiem=None, **kwargs):
        result = time.__new__(cls, *args, **kwargs)
        result.meridiem = meridiem
        return result


class tfhDatetime(datetime):
    _date: Optional[date] = None
    _time: Optional[time] = None
    
    @classmethod
    def combine(cls, date, time):
        result = datetime.combine(date, time)
        result = cls(result.year, result.month, result.day, result.hour, result.minute)
        result._date = date
        result._time = time
        return result
    

def timefhuman(string, now=None, raw=None, config: tfhConfig = tfhConfig()):
    parser = Lark(grammar, start="start")
    tree = parser.parse(string)

    transformer = tfhTransformer(now=now, config=config)
    result = transformer.transform(tree)

    if raw:
        return tree
    return result


def infer(datetimes):
    # TODO: This needs a major refactor to abstract away details and apply to all cases
    # TODO: distribute any to any (dates/meridiems/times etc.)

    # distribute first or last datetime's date to all datetimes
    if (isinstance(datetimes[0], datetime) and (target_date := datetimes[0]._date)) or \
        (isinstance(datetimes[-1], datetime) and (target_date := datetimes[-1]._date)):
        for i, dt in enumerate(datetimes):
            if isinstance(dt, time):
                datetimes[i] = tfhDatetime.combine(target_date, dt)

    # distribute last time's meridiem to all datetimes
    if (
        isinstance(datetimes[-1], datetime) and (meridiem := datetimes[-1]._time.meridiem)
    ) or (
        isinstance(datetimes[-1], time) and (meridiem := datetimes[-1].meridiem)
    ):
        for i, dt in enumerate(datetimes[:-1]):
            # TODO: force all datetimes to have _date and _time
            if meridiem.startswith("a"):
                break
            if isinstance(dt, datetime) and dt._time and not dt._time.meridiem:
                dt._time.meridiem = meridiem
                datetimes[i] = dt + timedelta(hours=12)
            elif isinstance(dt, time) and not dt.meridiem:
                dt.meridiem = meridiem
                datetimes[i] = tfhTime(dt.hour + 12, dt.minute, meridiem=meridiem)

    # distribute last time across previous dates
    if isinstance(datetimes[-1], (time, datetime)):
        for i, dt in enumerate(datetimes[:-1]):
            # NOTE: subclass date so can we match date-only's
            if isinstance(dt, date) and not isinstance(dt, datetime):
                datetimes[i] = tfhDatetime.combine(dt, datetimes[-1] if isinstance(datetimes[-1], time) else datetimes[-1]._time)

    # distribute last time range's meridiem to all previous datetime ranges
    if isinstance(datetimes[-1], tuple) and isinstance(datetimes[-1][0], time) and datetimes[-1][0].meridiem and datetimes[-1][0].meridiem.startswith("p"):
        for i, dt in enumerate(datetimes[:-1]):
            if isinstance(dt, tuple) and isinstance(dt[0], (time, datetime)):
                _dts = []
                for _dt in dt:
                    if isinstance(_dt, time):
                        _dt = tfhTime(_dt.hour + 12, _dt.minute, meridiem=datetimes[-1][0].meridiem)
                    elif isinstance(_dt, datetime) and _dt._time and not _dt._time.meridiem:
                        _dt._time.meridiem = datetimes[-1][0].meridiem
                        _dt = _dt + timedelta(hours=12)
                    _dts.append(_dt)
                datetimes[i] = tuple(_dts)

    # distribute first datetime range's date across all following time ranges
    if isinstance(datetimes[0], tuple) and isinstance(datetimes[0][0], datetime):
        for i, dt in enumerate(datetimes[1:], start=1):
            if isinstance(dt, time) or isinstance(dt, tuple) and isinstance(dt[0], time): # if a time range
                datetimes[i] = tuple(
                    tfhDatetime.combine(datetimes[0][0], dt)
                    for dt in datetimes[i]
                )
    return datetimes


def infer_datetimes(datetimes, now):
    result = []
    for dt in datetimes:
        if isinstance(dt, (date, time, datetime)):
            if isinstance(dt, date) and not isinstance(dt, datetime):
                result.append(tfhDatetime.combine(dt, time(0, 0)))
            elif isinstance(dt, time):
                result.append(tfhDatetime.combine(now.date(), dt))
            else:
                result.append(dt)
        elif isinstance(dt, (tuple, list)):
            result.append(infer_datetimes(dt, now))
        else:
            result.append(dt)
    if isinstance(datetimes, tuple):
        return tuple(result)
    return result


class tfhTransformer(Transformer):
    def __init__(self, now=None, config: tfhConfig = tfhConfig()):
        self.now = now
        self.config = config

    def start(self, children):
        """Strip the 'start' rule and return child(ren) directly."""
        if self.config.infer_datetimes:
            # TODO: move this logic into single after we correctly abstract away details
            # in the main `infer` function
            children = infer_datetimes(children, self.now)
        if len(children) == 1:
            return children[0]
        return children

    def expression(self, children):
        """The top-level expression could be a range, list, or single."""
        if len(children) == 1:
            return children[0]
        return children

    def single(self, children):
        """A single object can be a datetime, a date, or a time."""
        return children[0]

    def range(self, children):
        """Handles expressions like '7/17 3 PM - 7/18 4 PM'."""
        assert len(children) == 2
        return tuple(infer(children))

    def list(self, children):
        """Handles comma/or lists like '7/17, 7/18, 7/19' or '7/17 or 7/18'."""
        return list(infer(children))
    
    def duration(self, children):
        return sum(children, timedelta())
    
    def duration_part(self, children):
        data = {child.data.value: child.children[0].value for child in children}
        mapping = {
            'an': 1,
            'a': 1,
            'one': 1,
            'two': 2,
            'three': 3,
            'four': 4,
            'five': 5,
            'six': 6,
            'seven': 7,
            'eight': 8,
            'nine': 9,
            'ten': 10,
            'eleven': 11,
            'twelve': 12,
            'thirteen': 13,
            'fourteen': 14,
            'fifteen': 15,
            'sixteen': 16,
            'seventeen': 17,
            'eighteen': 18,
            'nineteen': 19,
            'twenty': 20,
            'thirty': 30,
            'forty': 40,
            'fifty': 50,
            'sixty': 60,
            'seventy': 70,
            'eighty': 80,
            'ninety': 90,
        }
        data['duration_number'] = mapping.get(data['duration_number'], data['duration_number'])
        for group in (
            ('minutes', 'minute', 'mins', 'min', 'm'),
            ('hours', 'hour', 'hrs', 'hr', 'h'),
            ('days', 'day', 'd'),
            ('weeks', 'week', 'wks', 'wk'),
            ('months', 'month', 'mos'),
            ('years', 'year', 'yrs', 'yr'),
        ):
            if data['duration_unit'] in group:
                return timedelta(**{group[0]: float(data['duration_number'])})
        raise NotImplementedError(f"Unknown duration unit: {data['duration_unit']}")

    def datetime(self, children):
        """
        A 'datetime' node can contain:
          - date + time
          - date + 'at' + time
          - just date
          - just time
        We combine them here into a single datetime if both parts are present.
        """
        date_part = next((c for c in children if isinstance(c, date)), None)
        time_part = next((c for c in children if isinstance(c, time)), None)

        if date_part and time_part:
            result = tfhDatetime.combine(date_part, time_part)
            result._date = date_part
            result._time = time_part
            return result
        elif date_part:
            return date_part
        elif time_part:
            return time_part
        return None
    
    def weekday(self, children):
        weekdays = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
        weekday = children[0].value[:3].lower()
        target_weekday = weekdays.index(weekday)
        current_weekday = self.now.weekday()
        
        if self.config.direction == Direction.previous:
            days_until = (target_weekday - current_weekday) % 7 - 7
        elif self.config.direction == Direction.next:
            days_until = (7 - (current_weekday - target_weekday)) % 7
        else:
            raise ValueError(f"Invalid direction: {self.config.direction}")
        days_until = days_until or 7  # If today is the target day, go to the next week
        
        dt = self.now.date() + timedelta(days=days_until)
        return dt
    
    def datename(self, children):
        datename = children[0].value.lower()
        if datename == 'today':
            return self.now.date()
        elif datename == 'tomorrow':
            return self.now.date() + timedelta(days=1)
        elif datename == 'yesterday':
            return self.now.date() - timedelta(days=1)
        
    def timename(self, children):
        timename = children[0].value.lower()
        if timename == 'noon':
            return tfhTime(hour=12, minute=0, meridiem="pm")
        elif timename == 'midday':
            return tfhTime(hour=12, minute=0, meridiem="pm")
        elif timename == 'midnight':
            return tfhTime(hour=0, minute=0, meridiem="am")
        
    def dayoryear(self, children):
        if children[0].value.isdigit():
            value = int(children[0].value)
            rule = 'day' if value < 32 else 'year'
            return Tree(Token('RULE', rule), [Token('INT', value)])
        raise NotImplementedError(f"Unknown day or year: {children[0]}")

    def date(self, children):
        """
        A 'date' node can match:
          1) month/day/year (numeric)
          2) 'tomorrow', 'today', or a weekday
          3) monthname day, optional year
        We iterate through tokens, collect info, then build a datetime.
        """
        if children and isinstance(children[0], date):
            return children[0]
        
        data = {child.data.value: child.children[0].value for child in children if hasattr(child, 'children')}

        if isinstance(data.get('day'), str) and data.get('day').isdigit():
            data['day'] = int(data['day'])
        
        if isinstance(data.get('year'), str) and data.get('year').isdigit():
            data['year'] = int(data['year'])
        if isinstance(data.get('month'), str) and data.get('month').isdigit():
            data['month'] = int(data['month'])

        # If we have a named month, map it to a numeric month
        month_mapping = {
            "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
            "july": 7, "august": 8, "september": 9, "october": 10, "november": 11, "december": 12,
            "jan": 1, "feb": 2, "mar": 3, "apr": 4, "jun": 6, "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12
        }

        if "monthname" in data and "month" not in data:
            key = data["monthname"].lower().replace(".", "")
            data["month"] = month_mapping.get(key, self.now.month)
            
        if data.get("day", -1) > 31 and "year" not in data:
            data["year"] = data.pop("day")

        if "day" not in data:
            data["day"] = 1  # the only exception. just use the first day of the month
        if "year" not in data:
            data["year"] = self.now.year
        if "month" not in data:
            data["month"] = self.now.month
            
        if 50 < data["year"] < 100:
            data["year"] = 1900 + data["year"]
        elif data["year"] < 50:
            data["year"] = 2000 + data["year"]

        return date(data["year"], data["month"], data["day"])

    def time(self, children):
        """
        A 'time' node might contain:
        - hour, minute, optional am/pm (captured by the MERIDIEM token)
        - just hour + am/pm
        - the literal string 'noon'
        We produce a timedelta, which is easier to add to a date.
        """
        if children and isinstance(children[0], time):
            return children[0]
        
        # 1) Check for 'noon' as a direct match (often a plain string)
        for child in children:
            if isinstance(child, str) and child.lower() == "noon":
                return tfhTime(hour=12, minute=0, meridiem=None)

        data = {child.data.value: child.children[0].value for child in children}
        
        # Extract the final hour/minute/meridiem
        hour = int(data.get("hour", 0))
        minute = int(data.get("minute", 0))
        meridiem = data.get("meridiem", '').lower()  # e.g. 'pm' or 'am'

        # 5) Apply am/pm logic
        if meridiem and meridiem.startswith("p") and hour != 12:
            hour += 12
        elif meridiem and meridiem.startswith("a") and hour == 12:
            hour = 0

        return tfhTime(hour=hour, minute=minute, meridiem=meridiem)
