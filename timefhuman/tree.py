from .data import TimeToken
from .data import TimeRangeToken
from .data import DayToken
from .data import DayRangeToken
from .data import DayTimeToken
from .data import AmbiguousToken

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
    >>> build_tree([DayToken(7, 5, 2018), 'or', DayToken(7, 7, 2018), TimeToken(11)])
    [7/5/2018 11 am, 7/7/2018 11 am]
    >>> build_tree([DayToken(7, 5, 2018), TimeToken(3, None), 'or', TimeToken(4, 'pm')])
    [7/5/2018 3 pm, 7/5/2018 4 pm]
    """
    tokens = combine_ranges(tokens)
    tokens = combine_on_at(tokens)
    tokens = combine_days_and_times(tokens)
    tokens = combine_ors(tokens)
    return tokens


def combine_ranges(tokens):
    """
    >>> combine_ranges([DayToken(7, 5, 2018), TimeToken(9), '-', TimeToken(11)])
    [7/5/2018, 9-11 am]
    >>> combine_ranges([DayToken(7, 5, 2018), 'to', DayToken(7, 7, 2018),
    ...     TimeToken(9), '-', TimeToken(11)])
    [7/5/2018 - 7/7/2018, 9-11 am]
    >>> combine_ranges([TimeToken(7, 'pm'), 'to', DayToken(7, 7, 2018)])  # ignore meaningless 'to'  # TODO: assert?
    [7 pm, 7/7/2018]
    """
    while '-' in tokens or 'to' in tokens:
        if '-' in tokens:
            index = tokens.index('-')
        elif 'to' in tokens:
            index = tokens.index('to')
        else:
            return tokens  # TODO: incorrect; these returns should skip over this index

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


def combine_on_at(tokens):
    """
    >>> combine_on_at([TimeToken(9), 'on', DayToken(7, 5, 2018)])
    [7/5/2018 9 am]
    >>> combine_on_at([DayToken(7, 5, 2018), 'at', TimeToken(9)])
    [7/5/2018 9 am]
    >>> combine_on_at(['at', TimeToken(9)])
    [9 am]
    >>> combine_on_at([TimeToken(9), 'on'])
    [9 am]
    >>> combine_on_at([TimeToken(9), 'at', TimeToken(9)])  # malformed, ignored at  # TODO: alert?
    [9 am, 9 am]
    """
    for keyword in ('on', 'at'):
        while keyword in tokens:
            i = tokens.index(keyword)
            if i <= 0 or i + 1 >= len(tokens):
                tokens = tokens[:i] + tokens[i+1:]
                continue
            if isinstance(tokens[i-1], TimeToken) and isinstance(tokens[i+1], DayToken):
                day, time = tokens[i+1], tokens[i-1]
            elif isinstance(tokens[i-1], DayToken) and isinstance(tokens[i+1], TimeToken):
                day, time = tokens[i-1], tokens[i+1]
            else:
                tokens = tokens[:i] + tokens[i+1:]
                continue
            daytime = DayTimeToken.from_day_time(day, time)
            tokens = tokens[:i-1] + [daytime] + tokens[i+2:]
    return tokens


def combine_days_and_times(tokens):
    """
    >>> combine_days_and_times([DayToken(7, 5, 2018), 'or', DayToken(7, 7, 2018), TimeToken(11)])
    [7/5/2018, 'or', 7/7/2018 11 am]
    >>> combine_days_and_times(['or', DayToken(7, 7, 2018), TimeToken(11)])
    ['or', 7/7/2018 11 am]
    >>> combine_days_and_times([TimeToken(11), DayToken(7, 7, 2018)])
    [7/7/2018 11 am]
    """
    cursor = 0
    while cursor < len(tokens):
        if cursor+1 < len(tokens) and \
                isinstance(tokens[cursor], (DayToken, DayRangeToken)) and \
                isinstance(tokens[cursor+1], (TimeToken, TimeRangeToken)):
            token = tokens[cursor].combine(tokens[cursor+1])
            tokens = tokens[:cursor] + [token] + tokens[cursor+2:]
        elif cursor-1 >= 0 and \
                isinstance(tokens[cursor], (DayToken, DayRangeToken)) and \
                isinstance(tokens[cursor-1], (TimeToken, TimeRangeToken)):
            token = tokens[cursor].combine(tokens[cursor-1])
            tokens = tokens[:cursor-1] + [token] + tokens[cursor+1:]
        cursor += 1
    return tokens


def combine_ors(tokens):
    """Transfer times across days if the other days don't have times.

    >>> combine_ors([DayToken(7, 5, 2018), 'or', DayToken(7, 7, 2018)])
    [7/5/2018, 7/7/2018]
    >>> combine_ors([TimeToken(3, None), 'or', TimeToken(4, 'pm')])
    [3 pm, 4 pm]
    >>> combine_ors(['or', TimeToken(4, 'pm')])
    ['or', 4 pm]
    """
    while 'or' in tokens:
        index = tokens.index('or')

        if index == len(tokens) - 1 or index == 0:
            return tokens  # TODO: incorrect; these returns should skip over this index; multiple ors

        # TODO: need generic way to impute both ways - simplify first two cases
        # TODO: too explicit, need a generic way to combine, esp. for longer lists
        if isinstance(tokens[index-1], DayToken) and \
                isinstance(tokens[index+1], DayTimeToken):
            tokens[index-1] = DayTimeToken.from_day_time(
                tokens[index-1], tokens[index+1].time)
        elif isinstance(tokens[index-1], DayTimeToken) and \
                isinstance(tokens[index+1], DayToken):
            tokens[index+1] = DayTimeToken.from_day_time(
                tokens[index+1], tokens[index-1].time)
        elif isinstance(tokens[index-1], TimeToken) and \
                isinstance(tokens[index+1], TimeToken):
            tokens[index-1].apply_time(tokens[index+1])
        elif isinstance(tokens[index-1], DayTimeToken) and \
                isinstance(tokens[index+1], TimeToken):
            tokens[index+1] = DayTimeToken.from_day_time(
                tokens[index-1].day, tokens[index+1])
            tokens[index+1].time.apply_time(tokens[index-1].time)
        tokens = tokens[:index] + tokens[index+1:]
    return tokens
