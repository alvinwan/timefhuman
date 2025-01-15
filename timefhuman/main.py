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
from typing import Optional, Union
from enum import Enum
from dataclasses import dataclass


Direction = Enum('Direction', ['previous', 'next'])

@dataclass
class tfhConfig:
    direction: Direction = Direction.next
    infer_datetimes: bool = True
    now: datetime = datetime.now()

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
       | duration

datetime: date ("at" time)?
        | date time
        | time date
        | time "on" date
        | date
        | time

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


class tfhToken:
    pass


class tfhRange(tfhToken):
    def __init__(self, start, end):
        self.start = start
        self.end = end

    def to_object(self):
        return (self.start.to_object(), self.end.to_object())

    def __repr__(self):
        return f"tfhRange({self.start}, {self.end})"


class tfhList(tfhToken):
    def __init__(self, items):
        self.items = items

    def to_object(self):
        return [item.to_object() for item in self.items]

    def __repr__(self):
        return f"tfhList({self.items})"


class tfhTimedelta(tfhToken):
    def __init__(self, days: int = 0, seconds: int = 0):
        self.days = days
        self.seconds = seconds

    def to_object(self):
        return timedelta(days=self.days, seconds=self.seconds)
    
    @classmethod
    def from_object(cls, obj: timedelta):
        return cls(days=obj.days, seconds=obj.seconds)
    
    def __repr__(self):
        return f"tfhTimedelta(days={self.days}, seconds={self.seconds})"


class tfhDate(tfhToken):
    def __init__(
        self, 
        year: Optional[int] = None, 
        month: Optional[int] = None, 
        day: Optional[int] = None,
    ):
        self.year = year
        self.month = month
        self.day = day

    def to_object(self) -> date:
        """Convert to a real date. Assumes all fields are filled in."""
        return date(self.year, self.month, self.day)
    
    @classmethod
    def from_object(cls, obj: date):
        return cls(year=obj.year, month=obj.month, day=obj.day)

    def __repr__(self):
        return (f"tfhDate("
                f"year={self.year}, month={self.month}, day={self.day})")


class tfhTime(tfhToken):
    Meridiem = Enum('Meridiem', ['AM', 'PM'])
    
    def __init__(
        self, 
        hour: Optional[int] = None, 
        minute: Optional[int] = None, 
        meridiem: Optional[Meridiem] = None,
    ):
        self.hour = hour
        self.minute = minute
        self.meridiem = meridiem

    def to_object(self) -> time:
        """Convert to a real time object. Assumes all fields are filled in."""
        # TODO: handle pm in a global infer function?
        if self.meridiem == tfhTime.Meridiem.PM and self.hour < 12:
            self.hour += 12
        elif self.meridiem == tfhTime.Meridiem.AM and self.hour == 12:
            self.hour = 0
        return time(self.hour, self.minute or 0)
    
    @classmethod
    def from_object(cls, obj: time):
        return cls(hour=obj.hour, minute=obj.minute, meridiem=obj.meridiem)

    def __repr__(self):
        return (f"tfhTime("
                f"hour={self.hour}, minute={self.minute}, meridiem={self.meridiem})")


class tfhDatetime(tfhToken):
    """A combination of tfhDate + tfhTime."""
    def __init__(
        self, 
        date: Optional[tfhDate] = None, 
        time: Optional[tfhTime] = None
    ):
        self.date = date
        self.time = time

    def to_object(self) -> Union[datetime, date, time]:
        """Convert to real datetime, assumes partial fields are filled."""
        if self.date and self.time:
            return datetime.combine(self.date.to_object(), self.time.to_object())
        elif self.date:
            return self.date.to_object()
        elif self.time:
            return self.time.to_object()
        raise ValueError("Datetime is missing both date and time")
        
    @classmethod
    def from_object(cls, obj: datetime):
        return cls(date=tfhDate.from_object(obj.date()), time=tfhTime.from_object(obj.time()))

    def __repr__(self):
        return f"tfhDatetime({self.date}, {self.time})"
    

def timefhuman(string, config: tfhConfig = tfhConfig(), raw=None):
    parser = Lark(grammar, start="start")
    tree = parser.parse(string)
    
    if raw:
        return tree

    transformer = tfhTransformer(config=config)
    results = transformer.transform(tree)
    
    results = [result.to_object() for result in results]
    if config.infer_datetimes:
        # TODO: move this logic into single after we correctly abstract away details
        # in the main `infer` function
        results = infer_datetimes(results, config.now)

    if len(results) == 1:
        return results[0]
    return results


def infer_from(source, target):
    if source.date and not target.date:
        target.date = source.date
    if source.time and not target.time:
        target.time = source.time
    if source.time and source.time.meridiem and target.time and not target.time.meridiem:
        target.time.meridiem = source.time.meridiem
    return target


def infer(datetimes):
    """
    Infer any missing components of datetimes from the first or last datetime.
    """
    for dt in datetimes[1:]:
        infer_from(datetimes[0], dt)
        
    for dt in datetimes[:-1]:
        infer_from(datetimes[-1], dt)

    # # distribute last time range's meridiem to all previous datetime ranges
    # if isinstance(datetimes[-1], tuple) and isinstance(datetimes[-1][0], time) and datetimes[-1][0].meridiem and datetimes[-1][0].meridiem.startswith("p"):
    #     for i, dt in enumerate(datetimes[:-1]):
    #         if isinstance(dt, tuple) and isinstance(dt[0], (time, datetime)):
    #             _dts = []
    #             for _dt in dt:
    #                 if isinstance(_dt, time):
    #                     _dt = tfhTime(_dt.hour + 12, _dt.minute, meridiem=datetimes[-1][0].meridiem)
    #                 elif isinstance(_dt, datetime) and _dt._time and not _dt._time.meridiem:
    #                     _dt._time.meridiem = datetimes[-1][0].meridiem
    #                     _dt = _dt + timedelta(hours=12)
    #                 _dts.append(_dt)
    #             datetimes[i] = tuple(_dts)

    # # distribute first datetime range's date across all following time ranges
    # if isinstance(datetimes[0], tuple) and isinstance(datetimes[0][0], datetime):
    #     for i, dt in enumerate(datetimes[1:], start=1):
    #         if isinstance(dt, time) or isinstance(dt, tuple) and isinstance(dt[0], time): # if a time range
    #             datetimes[i] = tuple(
    #                 tfhDatetime.combine(datetimes[0][0], dt)
    #                 for dt in datetimes[i]
    #             )
    
    return datetimes


def infer_datetimes(datetimes, now):
    # TODO: move this logic to classes?
    result = []
    for dt in datetimes:
        if isinstance(dt, (date, time, datetime)):
            if isinstance(dt, date) and not isinstance(dt, datetime):
                result.append(datetime.combine(dt, time(0, 0)))
            elif isinstance(dt, time):
                result.append(datetime.combine(now.date(), dt))
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
    def __init__(self, config: tfhConfig = tfhConfig()):
        self.config = config

    def start(self, children):
        """Strip the 'start' rule and return child(ren) directly."""
        # TODO: move this logic to timefhuman?
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
        return tfhRange(*infer(children))

    def list(self, children):
        """Handles comma/or lists like '7/17, 7/18, 7/19' or '7/17 or 7/18'."""
        return tfhList(infer(children))
    
    def duration(self, children):
        return tfhTimedelta.from_object(sum(children, timedelta()))
    
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
        date_part = next((c for c in children if isinstance(c, tfhDate)), None)
        time_part = next((c for c in children if isinstance(c, tfhTime)), None)
        return tfhDatetime(date=date_part, time=time_part)

    
    def weekday(self, children):
        weekdays = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
        weekday = children[0].value[:3].lower()
        target_weekday = weekdays.index(weekday)
        current_weekday = self.config.now.weekday()
        
        if self.config.direction == Direction.previous:
            days_until = (target_weekday - current_weekday) % 7 - 7
        elif self.config.direction == Direction.next:
            days_until = (7 - (current_weekday - target_weekday)) % 7
        else:
            raise ValueError(f"Invalid direction: {self.config.direction}")
        days_until = days_until or 7  # If today is the target day, go to the next week
        
        dt = self.config.now.date() + timedelta(days=days_until)
        return tfhDate.from_object(dt)
    
    def datename(self, children):
        datename = children[0].value.lower()
        if datename == 'today':
            return tfhDate.from_object(self.config.now.date())
        elif datename == 'tomorrow':
            return tfhDate.from_object(self.config.now.date() + timedelta(days=1))
        elif datename == 'yesterday':
            return tfhDate.from_object(self.config.now.date() - timedelta(days=1))
        
    def timename(self, children):
        timename = children[0].value.lower()
        if timename == 'noon':
            return tfhTime(hour=12, minute=0, meridiem=tfhTime.Meridiem.PM)
        elif timename == 'midday':
            return tfhTime(hour=12, minute=0, meridiem=tfhTime.Meridiem.PM)
        elif timename == 'midnight':
            return tfhTime(hour=0, minute=0, meridiem=tfhTime.Meridiem.AM)
        
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
        if children and isinstance(children[0], tfhDate):
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
            key = data.pop("monthname").lower().replace(".", "")
            data["month"] = month_mapping.get(key, self.config.now.month) # TODO: move to infer_now?
            
        if data.get("day", -1) > 31 and "year" not in data:
            data["year"] = data.pop("day")

        if "day" not in data:
            data["day"] = 1  # the only exception. just use the first day of the month
        if "year" not in data:
            data["year"] = self.config.now.year
        if "month" not in data:
            data["month"] = self.config.now.month
            
        if 50 < data["year"] < 100:
            data["year"] = 1900 + data["year"]
        elif data["year"] < 50:
            data["year"] = 2000 + data["year"]

        return tfhDate(year=data["year"], month=data["month"], day=data["day"])

    def time(self, children):
        """
        A 'time' node might contain:
        - hour, minute, optional am/pm (captured by the MERIDIEM token)
        - just hour + am/pm
        - the literal string 'noon'
        We produce a timedelta, which is easier to add to a date.
        """
        if children and isinstance(children[0], tfhTime):
            return children[0]
        
        # TODO: guard against random other objects
        data = {child.data.value: child.children[0].value for child in children}

        # Extract the final hour/minute/meridiem
        hour = int(data.get("hour", 0))
        minute = int(data.get("minute", 0))
        
        meridiem = None
        if data.get("meridiem", '').lower().startswith("a"):
            meridiem = tfhTime.Meridiem.AM
        elif data.get("meridiem", '').lower().startswith("p"):
            meridiem = tfhTime.Meridiem.PM
        
        # 5) Apply am/pm logic
        # TODO: move to infer / tfhTime?
        if meridiem == tfhTime.Meridiem.PM and hour != 12:
            hour += 12
        elif meridiem == tfhTime.Meridiem.AM and hour == 12:
            hour = 0

        return tfhTime(hour=hour, minute=minute, meridiem=meridiem)
