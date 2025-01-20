"""
Renderers for timefhuman. Responsible for converting the custom data structures
into native Python objects, such as datetime, date, time, and timedelta.
"""


from typing import Optional, Union, Tuple
from datetime import datetime, date, time, timedelta
from enum import Enum
import pytz
from timefhuman.utils import tfhConfig, Direction
from dateutil.relativedelta import relativedelta


class tfhMatchable:
    matched_text_pos: Optional[Tuple[int, int]] = None


class tfhDatelike(tfhMatchable):
    """
    A result is a single object that can be converted to a datetime, date, or time.
    
    It must provide settable properties for date, time, and meridiem.
    """
    date: Optional['tfhDate'] = None
    time: Optional['tfhTime'] = None
    year: Optional[int] = None
    month: Optional[int] = None
    day: Optional[int] = None
    meridiem: Optional['tfhTime.Meridiem'] = None
    tz: Optional[pytz.timezone] = None
    
    def to_object(self, config: tfhConfig = tfhConfig()) -> Union[datetime, 'date', 'time', timedelta]:
        """Convert to real datetime, date, or time. Assumes partial fields are filled."""
        raise NotImplementedError("Subclass must implement to_object()")
    
    @classmethod
    def from_object(cls, obj: Union[datetime, 'date', 'time', timedelta]):
        raise NotImplementedError("Subclass must implement from_object()")


class tfhCollection(tfhDatelike):
    """
    A collection of tfhDatelike objects. Provides direct getters and setters for each
    tfhDatelike property.
    """
    def __init__(self, items):
        self.items = items
        
    def getter(key):
        def get(self):
            for item in self.items:
                if getattr(item, key):
                    return getattr(item, key)
            return None
        return get

    def setter(key):
        def set(self, value):
            for item in self.items:
                setattr(item, key, value)
        return set
    
    date = property(getter('date'), setter('date'))
    time = property(getter('time'), setter('time'))
    year = property(getter('year'), setter('year'))
    month = property(getter('month'), setter('month'))
    day = property(getter('day'), setter('day'))
    meridiem = property(getter('meridiem'), setter('meridiem'))
    tz = property(getter('tz'), setter('tz'))


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


class tfhTimedelta(tfhMatchable):
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
        delta: Optional[relativedelta] = None,
    ):
        self.year = year
        self.month = month
        self.day = day
        self.delta = delta
    def to_object(self, config: tfhConfig = tfhConfig()) -> date:
        """Convert to a real date. Assumes all fields are filled in."""
        # NOTE: This must be here, because we need values for each field
        value = date(self.year or config.now.year, self.month or config.now.month, self.day or 1)
        if self.delta:
            value += self.delta
        return value
    
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
    
    def getter(attr, key):
        def get(self):
            obj = getattr(self, attr)
            return getattr(obj, key) if obj else None
        return get
    
    def setter(attr, key):
        def set(self, value):
            obj = getattr(self, attr)
            if obj:
                setattr(obj, key, value)
        return set
    
    year = property(getter('date', 'year'), setter('date', 'year'))
    month = property(getter('date', 'month'), setter('date', 'month'))
    day = property(getter('date', 'day'), setter('date', 'day'))
    meridiem = property(getter('time', 'meridiem'), setter('time', 'meridiem'))
    tz = property(getter('time', 'tz'), setter('time', 'tz'))

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
                elif config.direction == Direction.this:
                    pass
                return candidate
            return self.time.to_object(config)
        raise ValueError("Datetime is missing both date and time")
        
    @classmethod
    def from_object(cls, obj: datetime):
        return cls(date=tfhDate.from_object(obj.date()), time=tfhTime.from_object(obj.time()))

    def __repr__(self):
        return f"tfhDatetime({self.date}, {self.time})"
    

class tfhAmbiguous(tfhMatchable):
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


class tfhUnknown(tfhMatchable):
    def __init__(self, value: str):
        self.value = value
        
    def to_object(self, config: tfhConfig = tfhConfig()):
        return self.value
    
    @classmethod
    def from_object(cls, obj: str):
        return cls(obj)

    def __repr__(self):
        return f"tfhUnknown({self.value})"