"""
timefhuman
===
Convert human-readable date-like string to Python datetime object.
"""


__all__ = ('timefhuman',)

from datetime import datetime, date, time, timedelta
from typing import Optional, Union
from enum import Enum
from dataclasses import dataclass
from pathlib import Path

from lark import Lark, Transformer, Tree, Token
import pytz
from timefhuman.utils import generate_timezone_mapping, nodes_to_dict, get_month_mapping


DIRECTORY = Path(__file__).parent
Direction = Enum('Direction', ['previous', 'next', 'nearest'])

@dataclass
class tfhConfig:
    direction: Direction = Direction.next
    infer_datetimes: bool = True
    now: datetime = datetime.now()
    
    # NOTE: Right now, unmatched text is returned character by character.
    # And it doesn't retain whitespace. So it's generally useless, except
    # for debugging.
    return_unmatched: bool = False


class tfhDatelike:
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
    tz: Optional[pytz.timezone] = None
    
    def to_object(self, config: tfhConfig = tfhConfig()) -> Union[datetime, 'date', 'time', timedelta]:
        """Convert to real datetime, date, or time. Assumes partial fields are filled."""
        raise NotImplementedError("Subclass must implement to_object()")
    
    @classmethod
    def from_object(cls, obj: Union[datetime, 'date', 'time', timedelta]):
        raise NotImplementedError("Subclass must implement from_object()")


class tfhCollection(tfhDatelike):
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
            
    @property
    def tz(self):
        for item in self.items:
            if item.tz:
                return item.tz
        return None
    
    @tz.setter
    def tz(self, value):
        for item in self.items:
            item.tz = value


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


class tfhTimedelta:
    def __init__(self, days: int = 0, seconds: int = 0, unit: Optional[str] = None):
        self.days = days
        self.seconds = seconds
        self.unit = unit

    def to_object(self, config: tfhConfig = tfhConfig()):
        return timedelta(days=self.days, seconds=self.seconds)
    
    @classmethod
    def from_object(cls, obj: timedelta, unit: Optional[str] = None):
        return cls(days=obj.days, seconds=obj.seconds, unit=unit)
    
    def __repr__(self):
        return f"tfhTimedelta(days={self.days}, seconds={self.seconds}, unit='{self.unit}')"


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


class tfhWeekday:
    def __init__(self, day: int):
        self.day = day
        
    def to_object(self, config: tfhConfig = tfhConfig()):
        current_weekday = config.now.weekday()
        
        days_until = (7 - (current_weekday - self.day)) % 7
        if config.direction == Direction.previous:
            days_until -= 7
        elif config.direction == Direction.next:
            days_until = days_until or 7
        
        return config.now.date() + timedelta(days=days_until)
    
    @classmethod
    def from_object(cls, obj: int):
        return cls(day=obj)

    def __repr__(self):
        return f"tfhWeekday({self.day})"


class tfhTime:
    Meridiem = Enum('Meridiem', ['AM', 'PM'])
    
    def __init__(
        self, 
        hour: Optional[int] = None, 
        minute: Optional[int] = None, 
        second: Optional[int] = None,
        millisecond: Optional[int] = None,
        meridiem: Optional[Meridiem] = None,
        tz: Optional[pytz.timezone] = None,
    ):
        self.hour = hour
        self.minute = minute
        self.second = second
        self.millisecond = millisecond
        self.meridiem = meridiem
        self.tz = tz

    def to_object(self, config: tfhConfig = tfhConfig()) -> time:
        """Convert to a real time object. Assumes all fields are filled in."""
        if self.meridiem == tfhTime.Meridiem.PM and self.hour < 12:
            self.hour += 12
        elif self.meridiem == tfhTime.Meridiem.AM and self.hour == 12:
            self.hour = 0
        object = time(self.hour, self.minute or 0, self.second or 0, self.millisecond or 0, tzinfo=self.tz)
        return object
    
    @classmethod
    def from_object(cls, obj: time):
        return cls(hour=obj.hour, minute=obj.minute, second=obj.second, millisecond=obj.millisecond, meridiem=obj.meridiem, tz=obj.tz)

    def __repr__(self):
        return (f"tfhTime("
                f"hour={self.hour}, minute={self.minute}, second={self.second}, millisecond={self.millisecond}, meridiem={self.meridiem}, tz={self.tz})")


class tfhDatetime(tfhDatelike):
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
            
    @property
    def tz(self):
        return self.time.tz if self.time else None
    
    @tz.setter
    def tz(self, value):
        if self.time:
            self.time.tz = value
    
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
            return datetime.combine(self.date.to_object(config), self.time.to_object(config), tzinfo=self.time.tz)
        elif self.date:
            if config.infer_datetimes:
                return datetime.combine(self.date.to_object(config), time(0, 0))
            return self.date.to_object(config)
        elif self.time:
            if config.infer_datetimes:
                _now = config.now.replace(tzinfo=self.time.tz)
                candidate = datetime.combine(_now.date(), self.time.to_object(config))
                if candidate < _now and config.direction == Direction.next:
                    candidate += timedelta(days=1)
                elif candidate > _now and config.direction == Direction.previous:
                    candidate -= timedelta(days=1)
                return candidate
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
        
    def to_object(self, config: tfhConfig = tfhConfig()):
        # NOTE: If the ambiguous token was never resolved, simply return the value as a str
        return str(self.value)
    
    @classmethod
    def from_object(cls, obj: int):
        return cls(obj)

    def __repr__(self):
        return f"tfhAmbiguous({self.value})"


class tfhUnknown:
    def __init__(self, value: str):
        self.value = value
        
    def to_object(self, config: tfhConfig = tfhConfig()):
        return self.value
    
    @classmethod
    def from_object(cls, obj: str):
        return cls(obj)

    def __repr__(self):
        return f"tfhUnknown({self.value})"


parser = None
timezone_mapping = None


def get_parser():
    global parser, timezone_mapping
    if parser is None:
        timezone_mapping = generate_timezone_mapping()
        with open(DIRECTORY / 'grammar.lark', 'r') as file:
            grammar = file.read()
        grammar = grammar.replace('(TIMEZONE_MAPPING)', '|'.join(timezone_mapping.keys()))
        parser = Lark(grammar, start="start")
    return parser


def timefhuman(string, config: tfhConfig = tfhConfig(), raw=None):
    parser = get_parser()
    tree = parser.parse(string)
    print(tree.pretty())
    if raw:
        return tree

    transformer = tfhTransformer(config=config)
    results = transformer.transform(tree)
    
    # NOTE: intentionally did not filter by hasattr(result, 'to_object') to 
    # catch any other objects that might be returned
    results = [result.to_object(config) for result in results]
    
    if config.return_unmatched:
        return results

    results = list(filter(lambda s: not isinstance(s, str), results))
    
    if len(results) == 1:
        return results[0]

    return results


def infer_from(source: tfhDatelike, target: tfhDatelike):
    if isinstance(source, tfhAmbiguous):
        # NOTE: Ambiguous tokens have no information to offer
        return target
    if isinstance(target, tfhAmbiguous) and isinstance(source, tfhDatelike):
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
    if isinstance(source, tfhDatelike) and isinstance(target, tfhDatelike):
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
        if source.tz and not target.tz:
            target.tz = source.tz
    if isinstance(source, tfhTimedelta) and isinstance(target, tfhAmbiguous):
        target = tfhTimedelta.from_object(timedelta(**{source.unit: target.value}), unit=source.unit)
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
        return children[0]

    def expression(self, children):
        """The top-level expression could be a range, list, or single."""
        return children
    
    def unknown(self, children):
        return tfhUnknown(children[0].value)

    def single(self, children):
        """A single object can be a datetime, a date, or a time."""
        if len(children) == 1 and hasattr(children[0], 'data') and children[0].data.value == 'ambiguous':
            return tfhAmbiguous(int(children[0].children[0].value))
        return children[0]
    
    ###############
    # Collections #
    ###############
    
    def range(self, children):
        """Handles expressions like '7/17 3 PM - 7/18 4 PM'."""
        assert len(children) == 2
        return tfhRange(infer(children))

    def list(self, children):
        """Handles comma/or lists like '7/17, 7/18, 7/19' or '7/17 or 7/18'."""
        return tfhList(infer(children))
    
    ############
    # Duration #
    ############
    
    def duration(self, children):
        # TODO: just grabbing the first may cause problems later. how to do this more generically?
        return tfhTimedelta.from_object(sum([child.to_object(self.config) for child in children], timedelta()), unit=children[0].unit)
    
    def duration_part(self, children):
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
        # TODO: write my own multidict?
        data = {child.data.value: [_child.value for _child in child.children] for child in children}
        duration_number = float(data['duration_number'][0]) if 'duration_number' in data else sum([mapping[value] for value in data.get('duration_numbername', [])])
        duration_unit = data.get('duration_unit', data.get('duration_unit_letter', None))[0]
        for group in (
            ('minutes', 'minute', 'mins', 'min', 'm'),
            ('hours', 'hour', 'hrs', 'hr', 'h'),
            ('days', 'day', 'd'),
            ('weeks', 'week', 'wks', 'wk'),
            ('months', 'month', 'mos'),
            ('years', 'year', 'yrs', 'yr'),
        ):
            if duration_unit in group:
                return tfhTimedelta.from_object(timedelta(**{group[0]: duration_number}), unit=group[0])
        raise NotImplementedError(f"Unknown duration unit: {data['duration_unit']}")

    ############
    # Datetime #
    ############

    def datetime(self, children):
        """
        A 'datetime' node can contain:
          - date + time
          - date + 'at' + time
          - just date
          - just time
        We combine them here into a single datetime if both parts are present.
        """
        data = nodes_to_dict(children)
        return tfhDatetime(date=data.get('date'), time=data.get('time'))
    
    def date(self, children):
        # The pops here are a hack, because we want to check if any data is left
        # after we've popped other detected dates.
        data = nodes_to_dict(children)
        date = data.pop('date', None)
        weekday = data.pop('weekday', None)
        
        if date:
            return {'date': date}
        
        # If there's a weekday and no other date info, use the weekday
        if weekday and not data:
            return {'date': tfhDate.from_object(weekday.to_object(self.config))}

        # According to our grammar, day, month, and year must be stringified ints
        day = int(data['day']) if 'day' in data else None
        year = int(data['year']) if 'year' in data else None
        month = int(data['month']) if 'month' in data else None

        month_mapping = get_month_mapping()
        if "monthname" in data:
            assert "month" not in data
            key = data['monthname'].lower()
            month = month_mapping.get(key, self.config.now.month) # TODO: move to infer_now?

        if year and 50 < year < 100:
            year = 1900 + year
        elif year and 0 < year < 50:
            year = 2000 + year

        return {'date': tfhDate(year=year, month=month, day=day)}
    
    def weekday(self, children):
        weekdays = ['mo', 'tu', 'we', 'th', 'fr', 'sa', 'su']
        weekday = children[0].value[:2].lower()
        target_weekday = weekdays.index(weekday)
        return {'weekday': tfhWeekday(target_weekday)}
    
    def datename(self, children):
        datename = children[0].value.lower()
        if datename == 'today':
            _date = tfhDate.from_object(self.config.now.date())
        elif datename == 'tomorrow':
            _date = tfhDate.from_object(self.config.now.date() + timedelta(days=1))
        elif datename == 'yesterday':
            _date = tfhDate.from_object(self.config.now.date() - timedelta(days=1))
        else:
            raise NotImplementedError(f"Unknown datename: {datename}")
        return {'date': _date}
    
    def dayoryear(self, children):
        if children[0].value.isdigit():
            value = int(children[0].value)
            return {'day': value} if value < 32 else {'year': value}
        raise NotImplementedError(f"Unknown day or year: {children[0]}")

    def time(self, children):
        data = nodes_to_dict(children)
        time = data.pop('time', None)
        
        if time:
            return {'time': time}
        
        hour = int(data.get("hour", 0))
        minute = int(data.get("minute", 0))
        second = int(data.get("second", 0))
        millisecond = int(data.get("millisecond", 0))
        
        meridiem = None
        if data.get("meridiem", '').lower().startswith("a"):
            meridiem = tfhTime.Meridiem.AM
        elif data.get("meridiem", '').lower().startswith("p"):
            meridiem = tfhTime.Meridiem.PM
            
        tz = None
        if 'timezone' in data:
            tz = pytz.timezone(timezone_mapping[data['timezone']])

        return {'time': tfhTime(hour=hour, minute=minute, second=second, millisecond=millisecond, meridiem=meridiem, tz=tz)}

    def timename(self, children):
        timename = children[0].value.lower()
        if timename == 'noon':
            _time = tfhTime(hour=12, minute=0, meridiem=tfhTime.Meridiem.PM)
        elif timename == 'midday':
            _time = tfhTime(hour=12, minute=0, meridiem=tfhTime.Meridiem.PM)
        elif timename == 'midnight':
                _time = tfhTime(hour=0, minute=0, meridiem=tfhTime.Meridiem.AM)
        else:
            raise NotImplementedError(f"Unknown timename: {timename}")
        return {'time': _time}
    
    def houronly(self, children):
        return {'time': tfhTime(hour=int(children[0].value))}
