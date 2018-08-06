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
from .tree import build_tree
from .data import Token
from .data import TimeToken
from .data import DayToken
from .data import TimeRangeToken
from .data import DayRangeToken
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
    >>> timefhuman('7/17 3:30 p.m. - 4 p.m.', now=now)
    (datetime.datetime(2018, 7, 17, 15, 30), datetime.datetime(2018, 7, 17, 16, 0))
    >>> timefhuman('7/17 or 7/18 3 p.m.', now=now)  # date range
    [datetime.datetime(2018, 7, 17, 15, 0), datetime.datetime(2018, 7, 18, 15, 0)]
    >>> timefhuman('today or tomorrow noon', now=now)  # choices w. natural language
    [datetime.datetime(2018, 8, 4, 12, 0), datetime.datetime(2018, 8, 5, 12, 0)]
    >>> timefhuman('2 PM on 7/17 or 7/19')  # time applies to both dates
    [datetime.datetime(2018, 7, 17, 14, 0), datetime.datetime(2018, 7, 19, 14, 0)]
    """
    if now is None:
        now = datetime.datetime.now()

    tokens = tokenize(string)
    tokens = categorize(tokens, now)
    tokens = build_tree(tokens, now)
    datetimes = assemble_date(tokens, now)

    if len(datetimes) == 1:  # TODO: bad idea?
        return datetimes[0]
    return datetimes

    # TODO: What if user specifies vernacular AND actual date time. Let
    # specified date time take precedence.


def assemble_date(tokens, now=datetime.datetime.now()):
    """Assemble datetime object optionally using time."""
    return [token.datetime(now) for token in tokens if isinstance(token, Token)]
