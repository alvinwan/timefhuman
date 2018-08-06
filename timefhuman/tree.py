from .data import TimeToken
from .data import TimeRangeToken
from .data import DayToken
from .data import DayRangeToken

import datetime


def build_tree(tokens, now=datetime.datetime.now()):
    """Assemble datetime object optionally using time.

    >>> build_tree([DayToken(7, 5, 2018), TimeToken(12, 'pm')])
    [7/5/2018 12 pm]
    >>> build_tree([TimeToken(9), 'on', DayToken(7, 5, 2018)])
    [7/5/2018 9 am]
    >>> build_tree([DayToken(7, 5, 2018), TimeToken(9), '-', TimeToken(11)])
    [7/5/2018 9-11 am]
    >>> build_tree([DayToken(7, 5, 2018), 'to', DayToken(7, 7, 2018), TimeToken(11)])
    [7/5/2018 11 am - 7/7/2018 11 am]
    """
    tokens = combine_ranges(tokens)

    datetimes = []
    day = time = None
    for token in tokens:
        if isinstance(token, (DayToken, DayRangeToken)):
            type = 'day'
        elif isinstance(token, (TimeToken, TimeRangeToken)):
            type = 'time'
        else:
            type = 'UNK'

        if type == 'time':
            if time is not None:
                datetimes.append(time)
                time = None
            else:
                time = token
        elif type == 'day':
            if day is not None:
                datetimes.append(day)
                day = None
            else:
                day = token

        if day is not None and time is not None:
            datetimes.append(day.combine(time))
            day = None
            time = None

    if day is not None:
        datetimes.append(day)
    elif time is not None:
        datetimes.append(time)
    return datetimes

def combine_ranges(tokens):
    """
    >>> combine_ranges([DayToken(7, 5, 2018), TimeToken(9), '-', TimeToken(11)])
    [7/5/2018, 9-11 am]
    >>> combine_ranges([DayToken(7, 5, 2018), 'to', DayToken(7, 7, 2018), TimeToken(9), '-', TimeToken(11)])
    [7/5/2018 - 7/7/2018, 9-11 am]
    """
    while '-' in tokens or 'to' in tokens:
        if '-' in tokens:
            index = tokens.index('-')
        elif 'to' in tokens:
            index = tokens.index('to')
        else:
            return tokens

        if index == len(tokens) - 1 or index == 0:  # doesn't have both start, end
            return tokens

        end = tokens[index+1]
        start = tokens[index-1]

        if isinstance(start, TimeToken) and isinstance(end, TimeToken):
            tokens = tokens[:index-1] + [TimeRangeToken(start, end)] + tokens[index+2:]
        elif isinstance(start, DayToken) and isinstance(end, DayToken):
            tokens = tokens[:index-1] + [DayRangeToken(start, end)] + tokens[index+2:]
        else:
            tokens = tokens[:index] + tokens[index+1:]  # ignore meaningless dashes, to
    return tokens
