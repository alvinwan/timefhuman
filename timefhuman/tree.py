from .data import TimeToken
from .data import TimeRange
from .data import DayToken
from .data import DayRange
from .data import DayTimeToken
from .data import DayTimeRange
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
    [7/5/2018 11 am, 'or', 7/7/2018 11 am]
    >>> build_tree([DayToken(7, 5, 2018), TimeToken(3, None), 'or', TimeToken(4, 'pm')])
    [7/5/2018 3 pm, 'or', 7/5/2018 4 pm]
    """
    tokens = combine_ranges(tokens)
    tokens = combine_on_at(tokens)
    tokens = combine_ors(tokens)
    tokens = combine_days_and_times(tokens)
    tokens = combine_ors(tokens)  # TODO: is this the cleanest way to do this?
    return tokens


def areinstance(tokens, classes):
    """
    >>> tokens = (TimeToken(15), TimeToken(16))
    >>> areinstance(tokens, TimeToken)
    True
    >>> tokens = (TimeToken(15), DayToken(7, 5, 2018))
    >>> areinstance(tokens, TimeToken)
    False
    >>> areinstance(tokens, (TimeToken, DayToken))
    True
    """
    assert isinstance(classes, type) or isinstance(classes, tuple), \
        "Classes must either be a tuple or a type."
    if isinstance(classes, type):
        classes = (classes,)
    return all([
        any([isinstance(token, cls) for cls in classes]) for token in tokens])


def ifmatchinstance(tokens, classes):
    """
    >>> tokens = (TimeToken(15), TimeToken(16))
    >>> ifmatchinstance(tokens, (TimeToken, TimeToken))
    1
    >>> ifmatchinstance(tokens, (TimeToken, DayToken))
    0
    >>> both = (DayToken, TimeToken)
    >>> ifmatchinstance(tokens, (both, both))
    1
    >>> tokens = (TimeToken(15), DayToken(5, 7, 2018))
    >>> ifmatchinstance(tokens, (DayToken, TimeToken))
    -1
    >>> ifmatchinstance(tokens, ())
    0
    """
    if len(tokens) != len(classes):
        return 0
    if all([isinstance(token, cls) for token, cls in zip(tokens, classes)]):
        return 1
    if all([isinstance(token, cls) for token, cls in zip(tokens[::-1], classes)]):
        return -1
    return 0


def matchinstance(tokens, classes):
    """
    >>> tokens = (TimeToken(15), TimeToken(16))
    >>> matchinstance(tokens, (TimeToken, TimeToken))
    (3 pm, 4 pm)
    >>> matchinstance(tokens, (TimeToken, DayToken))
    ()
    >>> both = (DayToken, TimeToken)
    >>> matchinstance(tokens, (both, both))
    (3 pm, 4 pm)
    >>> tokens = (TimeToken(15), DayToken(5, 7, 2018))
    >>> day_tokens = (DayToken, DayRange)
    >>> time_tokens = (TimeToken, TimeRange)
    >>> matchinstance(tokens, (day_tokens, time_tokens))
    (5/7/2018, 3 pm)
    >>> matchinstance(tokens, ())
    ()
    """
    if len(tokens) != len(classes):
        return ()
    step = ifmatchinstance(tokens, classes)
    if step == 0:
        return ()
    return tokens[::step]


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

        if areinstance((start, end), TimeToken):
            tokens = tokens[:index-1] + [TimeRange(start, end)] + tokens[index+2:]
        elif areinstance((start, end), DayToken):
            tokens = tokens[:index-1] + [DayRange(start, end)] + tokens[index+2:]
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
            match = matchinstance((tokens[i-1], tokens[i+1]), (TimeToken, DayToken))
            if not match:
                tokens = tokens[:i] + tokens[i+1:]
                continue
            time, day = match
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
    day_tokens = (DayToken, DayRange)
    time_tokens = (TimeToken, TimeRange)
    while cursor + 1 < len(tokens):
        amb_time_match = matchinstance(tokens[cursor:cursor+2], (AmbiguousToken, time_tokens))
        day_time_match = matchinstance(tokens[cursor:cursor+2], (day_tokens, time_tokens))

        if amb_time_match and amb_time_match[0].has_day_token():
            ambiguous, time = amb_time_match
            day = ambiguous.get_day_token()
            day_time_match = (day, time)

        if day_time_match:
            day, time = day_time_match
            token = day.combine(time)
            tokens = tokens[:cursor] + [token] + tokens[cursor+2:]
        cursor += 1
    return tokens


def combine_ors(tokens):
    """Transfer times across days if the other days don't have times.

    >>> combine_ors([DayToken(7, 5, 2018), 'or', DayToken(7, 7, 2018)])
    [7/5/2018, 'or', 7/7/2018]
    >>> combine_ors([TimeToken(3, None), 'or', TimeToken(4, 'pm')])
    [3 pm, 'or', 4 pm]
    >>> combine_ors(['or', TimeToken(4, 'pm')])
    ['or', 4 pm]
    """
    index = 1
    while index + 1 < len(tokens):
        if tokens[index] != 'or':
            index += 1
            continue

        # TODO: too explicit, need generic way to "cast"
        candidates = (tokens[index-1], tokens[index+1])
        day_daytime_step = ifmatchinstance(candidates, (DayToken, DayTimeToken))
        time_daytime_step = ifmatchinstance(candidates, (TimeToken, DayTimeToken))
        time_time_step = ifmatchinstance(candidates, (TimeToken, TimeToken))
        amb_timerange_step = ifmatchinstance(candidates, (AmbiguousToken, TimeRange))
        timerange_daytimerange_step = ifmatchinstance(candidates, (TimeRange, DayTimeRange))
        if day_daytime_step:
            day, daytime = candidates[::day_daytime_step]
            tokens[index-day_daytime_step] = day.combine(daytime.time)
        elif time_daytime_step:
            time, daytime = candidates[::time_daytime_step]
            time.apply(daytime.time)
            tokens[index-time_daytime_step] = daytime.day.combine(time)
        elif time_time_step:
            time1, time2 = candidates[::time_time_step]
            time1.apply(time2)
        elif amb_timerange_step and candidates[::amb_timerange_step][0].has_time_range_token():
            ambiguous, timerange = candidates[::amb_timerange_step]
            tokens[index-amb_timerange_step] = ambiguous.get_time_range_token()
        elif timerange_daytimerange_step:
            timerange, daytimerange = candidates[::timerange_daytimerange_step]
            start = daytimerange.start.day.combine(timerange.start)
            end = daytimerange.end.day.combine(timerange.end)
            daytimerange2 = DayTimeRange(start, end)
            tokens[index-timerange_daytimerange_step] = daytimerange2

        candidates = (tokens[index-1], tokens[index+1])
        timerange_timerange_step = ifmatchinstance(candidates, (TimeRange, TimeRange))
        if timerange_timerange_step:
            timerange1, timerange2 = candidates[::timerange_timerange_step]
            timerange1.start.apply(timerange2.start)
            timerange1.end.apply(timerange2.end)
        index += 1
    return tokens
