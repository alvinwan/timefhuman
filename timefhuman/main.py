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
from .data import TimeRange
from .data import DayRange
import datetime
import string


__all__ = ('timefhuman',)


def timefhuman(string, now=None, raw=None):
    """A simple parsing function for date-related strings.

    :param string: date-like string to parse
    :param now: datetime for now, will default to datetime.datetime.now()

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
    >>> timefhuman('2 PM on 7/17 or 7/19', now=now)  # time applies to both dates
    [datetime.datetime(2018, 7, 17, 14, 0), datetime.datetime(2018, 7, 19, 14, 0)]
    >>> timefhuman('2 PM on 7/17 or 7/19', raw=True, now=now)
    [[7/17/2018 2 pm, 7/19/2018 2 pm]]
    """
    if now is None:
        now = datetime.datetime.now()

    tokens = timefhuman_tokens(string, now)
    #print(isinstance(tokens[1], Token))

    if raw:
        return tokens
    datetimes = [tok.datetime(now) for tok in tokens if isinstance(tok, Token)]

    if len(datetimes) == 1:  # TODO: bad idea?
        return datetimes[0]
    return datetimes

    # TODO: What if user specifies vernacular AND actual date time. Let
    # specified date time take precedence.


def timefhuman_tokens(string, now):
    """Convert string into timefhuman parsed, imputed, combined tokens"""
    tokens = tokenize(string)
    tokens = categorize(tokens, now)
    tokens = build_tree(tokens, now)
    return tokens
if __name__ == '__main__':
    print(timefhuman('next month'))