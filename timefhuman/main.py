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

from .tokenize import tokenize
from .categorize import categorize
from .tree import TimeToken
from .tree import DayToken
from .tree import TimeRangeToken
from .tree import DayRangeToken
import datetime
import string


__all__ = ('timefhuman',)


def timefhuman(string, now=None):
    """A simple parsing function for date-related strings.

    >>> now = datetime.datetime(year=2018, month=8, day=4)
    >>> timefhuman('upcoming Monday noon', now=now)  # natural language
    datetime.datetime(2018, 8, 6, 12, 0)
    >>> timefhuman('Monday 3 pm, Tu noon', now=now)  # multiple datetimes
    [datetime.datetime(2018, 8, 6, 15, 0), datetime.datetime(2018, 8, 7, 12, 0)]
    >>> timefhuman('7/17 3:30-4 PM', now=now)  # time range
    (datetime.datetime(2018, 7, 17, 15, 30), datetime.datetime(2018, 7, 17, 16, 0))


    # date range
    # multiple datetimes, with ranges
    """
    if now is None:
        now = datetime.datetime.now()

    tokens = tokenize(string)
    tokens = categorize(tokens, now)
    datetimes = assemble_date(tokens, now)

    if len(datetimes) == 1:  # TODO: bad idea?
        return datetimes[0]
    return datetimes

    # TODO: What if user specifies vernacular AND actual date time. Let
    # specified date time take precedence.


def assemble_date(tokens, now=datetime.datetime.now()):
    """Assemble datetime object optionally using time.

    >>> assemble_date([TimeToken(9, 0), 'on', DayToken(7, 5, 2018)])
    [datetime.datetime(2018, 7, 5, 9, 0)]
    >>> now = datetime.datetime(2018, 7, 5, 9, 0)
    >>> assemble_date([DayToken(7, 5, 2018)], now)
    [datetime.datetime(2018, 7, 5, 0, 0)]
    >>> assemble_date([TimeToken(9, 0)], now)
    [datetime.datetime(2018, 7, 5, 9, 0)]
    >>> time_range_token = TimeRangeToken(TimeToken(3, 'pm'), TimeToken(5, 'pm'))
    >>> assemble_date([DayToken(7, 5, 2018), time_range_token])
    [(datetime.datetime(2018, 7, 5, 15, 0), datetime.datetime(2018, 7, 5, 17, 0))]
    """
    datetimes = []
    day = time = None
    for token in tokens:
        if isinstance(token, (DayToken, DayRangeToken)):
            day = token
        elif isinstance(token, (TimeToken, TimeRangeToken)):
            time = token
        if day is not None and time is not None:
            datetimes.append(day.combine(time))
            day = None
            time = None

    if day is not None:
        datetimes.append(datetime.datetime(day.year, day.month, day.day, 0, 0))
    elif time is not None:
        datetimes.append(datetime.datetime(now.year, now.month, now.day, time.hour, time.minute))
    return datetimes
