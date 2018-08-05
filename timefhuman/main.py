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
import datetime
import string


__all__ = ('timefhuman',)


def timefhuman(string, now=None):
    """A simple parsing function for date-related strings.

    >>> now = datetime.datetime(year=2018, month=7, day=7)
    >>> timefhuman('7/17 3 PM', now=now)
    datetime.datetime(2018, 7, 17, 15, 0)
    >>> timefhuman('July 17, 2018 at 3p.m.')
    datetime.datetime(2018, 7, 17, 15, 0)
    >>> timefhuman('July 17, 2018 3 p.m.')
    datetime.datetime(2018, 7, 17, 15, 0)
    >>> timefhuman('3PM on July 17', now=now)
    datetime.datetime(2018, 7, 17, 15, 0)
    >>> timefhuman('July 17 at 3')
    datetime.datetime(2018, 7, 17, 3, 0)
    >>> timefhuman('July 2019')
    datetime.datetime(2019, 7, 1, 0, 0)
    >>> timefhuman('7/17/18 3:00 p.m.')
    datetime.datetime(2018, 7, 17, 15, 0)
    """
    if now is None:
        now = datetime.datetime.now()

    tokens = tokenize(string)
    tokens = categorize(tokens, now)
    return assemble_date(tokens, now)

    # TODO: What if user specifies vernacular AND actual date time. Let
    # specified date time take precedence.


def assemble_date(tokens, now=datetime.datetime.now()):
    """Assemble datetime object optionally using time.

    >>> assemble_date([TimeToken(9, 0), 'on', DayToken(7, 5, 2018)])
    datetime.datetime(2018, 7, 5, 9, 0)
    >>> now = datetime.datetime(2018, 7, 5, 9, 0)
    >>> assemble_date([DayToken(7, 5, 2018)], now)
    datetime.datetime(2018, 7, 5, 0, 0)
    >>> assemble_date([TimeToken(9, 0)], now)
    datetime.datetime(2018, 7, 5, 9, 0)
    >>> time_range_token = TimeRangeToken(TimeToken(3, 'pm'), TimeToken(5, 'pm'))

    # >>> assemble_date([DayToken(7, 5, 2018), time_range_token])
    # (datetime.datetime(2018, 7, 5, 15, 0), datetime.datetime(2018, 7, 5, 17, 0))
    """
    day = time = None
    for token in tokens:
        if isinstance(token, DayToken):
            day = token
        elif isinstance(token, TimeToken):
            time = token

    if day is not None and time is not None:
        return datetime.datetime(day.year, day.month, day.day, time.hour, time.minute)
    elif time is None:
        return datetime.datetime(day.year, day.month, day.day, 0, 0)
    return datetime.datetime(now.year, now.month, now.day, time.hour, time.minute)
