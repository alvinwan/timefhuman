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

list: single ((","|"or")+ single)+ 
    | range ((","|"or")+ range)+

single: datetime 
       | duration
       | unknown

// Only add houronly to specific formats that immediately
// indicate this is an hour-only time.
datetime: date ("at" (time | houronly))?
        | date (time | houronly)
        | (time | houronly) date
        | (time | houronly) "on" date
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

// intentionally not allowing int-only time, so that single-integers can be
// classified as an unknown token (in case it's a month, day, year, etc.)
// However, that means to support single-integer (e.g., hour) times, we need
// to manually add them to the `datetime` rule above.
time: hour ":" minute meridiem?
    | hour meridiem
    | timename

duration: ("in"|"for")? duration_part (("and"|",")? duration_part)* ("ago")?
duration_part: duration_number duration_unit
duration_number: DURATION_NUMBER
duration_unit: DURATION_UNIT

weekday: WEEKDAY
monthname: MONTHNAME
datename: DATENAME
dayoryear: INT

day: INT
month: INT
year: INT

timename: TIMENAME
hour: INT
minute: INT
meridiem: MERIDIEM
houronly: INT

unknown: INT
"""


class tfhResult:
    """
    A result is a single object that can be converted to a datetime, date, or time.
    
    It must provide settable properties for date, time, and meridiem.
    """
    date: Optional['tfhDate'] = None
    month: Optional[int] = None
    year: Optional[int] = None
    day: Optional[int] = None
    time: Optional['tfhTime'] = None
    meridiem: Optional['tfhTime.Meridiem'] = None
    
    def to_object(self, config: tfhConfig = tfhConfig()) -> Union[datetime, 'date', 'time', timedelta]:
        """Convert to real datetime, date, or time. Assumes partial fields are filled."""
        raise NotImplementedError("Subclass must implement to_object()")
    
    @classmethod
    def from_object(cls, obj: Union[datetime, 'date', 'time', timedelta]):
        raise NotImplementedError("Subclass must implement from_object()")


class tfhCollection(tfhResult):
    def __init__(self, items):
        self.items = items
    
    # TODO: simplify these properties. they're all the same
    @property
    def date(self):
        for item in self.items:
            if item.date:
                return item.date
        return None
    
    @date.setter
    def date(self, value):
        for item in self.items:
            item.date = value
    
    @property
    def time(self):
        for item in self.items:
            if item.time:
                return item.time
        return None
    
    @time.setter
    def time(self, value):
        for item in self.items:
            item.time = value
    
    @property
    def meridiem(self):
        for item in self.items:
            if item.meridiem:
                return item.meridiem
        return None
    
    @meridiem.setter
    def meridiem(self, value):
        for item in self.items:
            item.meridiem = value
            
    @property
    def year(self):
        for item in self.items:
            if item.year:
                return item.year
        return None
    
    @year.setter
    def year(self, value):
        for item in self.items:
            item.year = value
            
    @property
    def month(self):
        for item in self.items:
            if item.month:
                return item.month
        return None
    
    @month.setter
    def month(self, value):
        for item in self.items:
            item.month = value
            
    @property
    def day(self):
        for item in self.items:
            if item.day:
                return item.day
        return None
    
    @day.setter
    def day(self, value):
        for item in self.items:
            item.day = value


class tfhRange(tfhCollection):
    def to_object(self, config: tfhConfig = tfhConfig()):
        if config.infer_datetimes:
            _start, _end = self.items
            start, end = _start.to_object(config), _end.to_object(config)
            if start > end and not _end.date:
                end += timedelta(days=1)
            return (start, end)
        return tuple([item.to_object(config) for item in self.items])

    def __repr__(self):
        return f"tfhRange({self.items})"


class tfhList(tfhCollection):
    def to_object(self, config: tfhConfig = tfhConfig()):
        return list([item.to_object(config) for item in self.items])

    def __repr__(self):
        return f"tfhList({self.items})"


class tfhTimedelta(tfhResult):
    def __init__(self, days: int = 0, seconds: int = 0):
        self.days = days
        self.seconds = seconds

    def to_object(self, config: tfhConfig = tfhConfig()):
        return timedelta(days=self.days, seconds=self.seconds)
    
    @classmethod
    def from_object(cls, obj: timedelta):
        return cls(days=obj.days, seconds=obj.seconds)
    
    def __repr__(self):
        return f"tfhTimedelta(days={self.days}, seconds={self.seconds})"


class tfhDate:
    def __init__(
        self, 
        year: Optional[int] = None, 
        month: Optional[int] = None, 
        day: Optional[int] = None,
    ):
        self.year = year
        self.month = month
        self.day = day

    def to_object(self, config: tfhConfig = tfhConfig()) -> date:
        """Convert to a real date. Assumes all fields are filled in."""
        # NOTE: This must be here, because we need values for each field
        return date(self.year or config.now.year, self.month or config.now.month, self.day or 1)
    
    @classmethod
    def from_object(cls, obj: date):
        return cls(year=obj.year, month=obj.month, day=obj.day)

    def __repr__(self):
        return (f"tfhDate("
                f"year={self.year}, month={self.month}, day={self.day})")


class tfhTime:
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

    def to_object(self, config: tfhConfig = tfhConfig()) -> time:
        """Convert to a real time object. Assumes all fields are filled in."""
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


class tfhDatetime(tfhResult):
    """A combination of tfhDate + tfhTime."""
    
    @property
    def meridiem(self):
        return self.time.meridiem if self.time else None
    
    @meridiem.setter
    def meridiem(self, value):
        if self.time:
            self.time.meridiem = value
            
    @property
    def year(self):
        return self.date.year if self.date else None
    
    @year.setter
    def year(self, value):
        if self.date:
            self.date.year = value
            
    @property
    def month(self):
        return self.date.month if self.date else None
    
    @month.setter
    def month(self, value):
        if self.date:
            self.date.month = value
            
    @property
    def day(self):
        return self.date.day if self.date else None
    
    @day.setter
    def day(self, value):
        if self.date:
            self.date.day = value
    
    def __init__(
        self, 
        date: Optional[tfhDate] = None, 
        time: Optional[tfhTime] = None
    ):
        self.date = date
        self.time = time

    def to_object(self, config: tfhConfig = tfhConfig()) -> Union[datetime, date, time]:
        """Convert to real datetime, assumes partial fields are filled."""
        if self.date and self.time:
            return datetime.combine(self.date.to_object(config), self.time.to_object(config))
        elif self.date:
            if config.infer_datetimes:
                return datetime.combine(self.date.to_object(config), time(0, 0))
            return self.date.to_object(config)
        elif self.time:
            if config.infer_datetimes:
                return datetime.combine(config.now.date(), self.time.to_object(config))
            return self.time.to_object(config)
        raise ValueError("Datetime is missing both date and time")
        
    @classmethod
    def from_object(cls, obj: datetime):
        return cls(date=tfhDate.from_object(obj.date()), time=tfhTime.from_object(obj.time()))

    def __repr__(self):
        return f"tfhDatetime({self.date}, {self.time})"
    

class tfhAmbiguous:
    """Can represent an hour, a day, month, or year."""
    
    def __init__(self, value: int):
        self.value = value

    def __repr__(self):
        return f"tfhAmbiguous({self.value})"


def timefhuman(string, config: tfhConfig = tfhConfig(), raw=None):
    parser = Lark(grammar, start="start")
    tree = parser.parse(string)
    
    if raw:
        return tree

    transformer = tfhTransformer(config=config)
    results = transformer.transform(tree)
    
    results = [result.to_object(config) for result in results]
    if len(results) == 1:
        return results[0]
    return results


def infer_from(source: tfhResult, target: tfhResult):
    if isinstance(source, tfhAmbiguous) and not isinstance(target, tfhAmbiguous):
        return target
    if isinstance(target, tfhAmbiguous) and not isinstance(source, tfhAmbiguous):
        if source.time:
            target = tfhDatetime(time=tfhTime(hour=target.value, meridiem=source.meridiem))
        elif source.year:
            target = tfhDatetime(date=tfhDate(year=target.value))
        elif source.day:
            target = tfhDatetime(date=tfhDate(day=target.value))
        elif source.month:
            target = tfhDatetime(date=tfhDate(month=target.value))
        else:
            raise NotImplementedError(f"Not enough context to infer what {target} is")
    if isinstance(source, tfhAmbiguous) and isinstance(target, tfhAmbiguous):
        # NOTE: nothing we can do here. both are ambiguous.
        return target
    if source.date and not target.date:
        target.date = source.date
    if source.time and not target.time:
        target.time = source.time
    if source.month and not target.month:
        target.month = source.month
    if source.year and not target.year:
        target.year = source.year
    if source.meridiem and not target.meridiem:
        target.meridiem = source.meridiem
    return target


def infer(datetimes):
    """
    Infer any missing components of datetimes from the first or last datetime.
    """
    for i, dt in enumerate(datetimes[1:], start=1):
        datetimes[i] = infer_from(datetimes[0], dt)
        
    for i, dt in enumerate(datetimes[:-1]):
        datetimes[i] = infer_from(datetimes[-1], dt)

    return datetimes


class tfhTransformer(Transformer):
    def __init__(self, config: tfhConfig = tfhConfig()):
        self.config = config

    def start(self, children):
        """Strip the 'start' rule and return child(ren) directly."""
        return children

    def expression(self, children):
        """The top-level expression could be a range, list, or single."""
        if len(children) == 1:
            return children[0]
        return children

    def single(self, children):
        """A single object can be a datetime, a date, or a time."""
        if len(children) == 1 and hasattr(children[0], 'data') and children[0].data.value == 'unknown':
            return tfhAmbiguous(int(children[0].children[0].value))
        return children[0]

    def range(self, children):
        """Handles expressions like '7/17 3 PM - 7/18 4 PM'."""
        assert len(children) == 2
        return tfhRange(infer(children))

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
        
        year = data.get('year', -1)
        if 50 < year < 100:
            data["year"] = 1900 + year
        elif 0 < year < 50:
            data["year"] = 2000 + year

        return tfhDate(year=data.get("year"), month=data.get("month"), day=data.get("day"))

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

    def houronly(self, children):
        return tfhTime(hour=int(children[0].value))
