import datetime


class Token:

    def share(self, property, other, setter=setattr):
        """
        >>> t1 = Token()
        >>> t2 = Token()
        >>> t1.is_special = True
        >>> t1.share('is_special', t2)
        >>> t2.is_special
        True
        """
        mine = getattr(self, property, None)
        others = getattr(other, property, None)
        if mine is None and others is not None:
            setter(self, property, others)
        elif others is None and mine is not None:
            setter(other, property, mine)
    
    def isnumeric(self):
        return False


class ListToken(Token):

    def __init__(self, *tokens):
        self.tokens = list(tokens)

    def append(self, other):
        self.tokens.append(other)

    def extend(self, others):
        self.tokens.extend(others)

    def datetime(self, now):
        return [token.datetime(now) for token in self.tokens]

    def __getitem__(self, i):
        return self.tokens[i]

    def __repr__(self):
        tokens = list(map(repr, self.tokens))
        return '[{}]'.format(', '.join(tokens))


class DayTimeToken(Token):

    def __init__(self, year, month, day, relative_hour, minute=0, time_of_day=None):
        self.day = DayToken(month, day, year)
        self.time = TimeToken(relative_hour, time_of_day, minute)

    def combine(self, other):
        """

        >>> dt = DayTimeToken(2018, 8, 18, 3, 0, 'pm')
        >>> day = DayToken(8, 20, 2018)
        >>> dt.combine(day)
        8/20/2018 3 pm
        >>> time = TimeToken(5, 'pm')
        >>> dt.combine(time)
        8/18/2018 5 pm
        """
        assert isinstance(other, (DayToken, TimeToken))
        if isinstance(other, DayToken):
            return other.combine(self.time)
        elif isinstance(other, TimeToken):
            self.time.apply(other)
            return self.day.combine(other)

    def datetime(self, now):
        # TODO: handle Nones
        return datetime.datetime(
            self.day.year, self.day.month, self.day.day, self.time.hour, self.time.minute)

    @staticmethod
    def from_day_time(day, time):
        return DayTimeToken(
            day.year, day.month, day.day, time.relative_hour, time.minute,
            time.time_of_day)

    def __repr__(self):
        return '{} {}'.format(repr(self.day), repr(self.time))


class DayTimeRange(Token):
    """
    >>> dt1 = DayTimeToken(2018, 8, 1, 10)
    >>> dt2 = DayTimeToken(2018, 8, 1, 11)
    >>> dt3 = DayTimeToken(2018, 8, 1, 1, time_of_day='pm')
    >>> dt4 = DayTimeToken(2018, 8, 3, 11)
    >>> DayTimeRange(dt1, dt2)
    8/1/2018 10:00 - 11:00
    >>> DayTimeRange(dt1, dt3)
    8/1/2018 10:00 - 1 pm
    >>> DayTimeRange(dt1, dt4)
    8/1/2018 10:00 - 8/3/2018 11:00
    """

    def __init__(self, start, end):
        self.start = start
        self.end = end

    def datetime(self, now):
        return (self.start.datetime(now), self.end.datetime(now))

    def __repr__(self):
        if self.start.day == self.end.day:
            time_range = TimeRange(self.start.time, self.end.time)
            return '{} {}'.format(repr(self.start.day), repr(time_range))
        return '{} - {}'.format(repr(self.start), repr(self.end))


class DayTimeList(ListToken):
    """
    >>> now = datetime.datetime(2018, 7, 5)
    >>> dt1 = DayTimeToken(2018, 8, 1, 10)
    >>> dt2 = DayTimeToken(2018, 8, 1, 11)
    >>> dts = DayTimeList(dt1, dt2)
    >>> dts
    [8/1/2018 10:00, 8/1/2018 11:00]
    >>> dts.datetime(now)
    [datetime.datetime(2018, 8, 1, 10, 0), datetime.datetime(2018, 8, 1, 11, 0)]
    """
    pass


class DayToken(Token):

    def __init__(self, month, day, year):   # TODO: default Nones?
        self.month = month
        self.day = day
        self.year = year

        assert month is None or 1 <= month <= 12
        assert day is None or 1 <= day <= 31

    def combine(self, time):
        """
        >>> day = DayToken(8, 5, 2018)
        >>> time = TimeToken(3, 'pm')
        >>> time_range = TimeRange(TimeToken(3, 'pm'), TimeToken(5, 'pm'))
        >>> day.combine(time)
        8/5/2018 3 pm
        >>> day.combine(time_range)
        8/5/2018 3-5 pm
        """
        assert isinstance(time, (TimeRange, TimeToken, DayTimeToken))
        if isinstance(time, TimeToken):
            return DayTimeToken.from_day_time(self, time)
        if isinstance(time, DayTimeToken):
            return self.combine(time.time)
        return DayTimeRange(
            DayTimeToken.from_day_time(self, time.start),
            DayTimeToken.from_day_time(self, time.end))

    def apply(self, other):
        """
        >>> d1 = DayToken(3, 2, None)
        >>> d2 = DayToken(4, 1, 2018)
        >>> d1.apply(d2)
        >>> d2.year
        2018
        >>> d3 = DayToken(None, 3, None)
        >>> d2.apply(d3)
        >>> d3
        4/3/2018
        """
        assert isinstance(other, DayToken)
        for attr in ('year', 'month'):
            self.share(attr, other)

    def __add__(self, other):
        """
        >>> d1 = DayToken(3, 2, None)
        >>> d1 + 3
        3/5
        """
        assert isinstance(other, int)
        return DayToken(self.month, self.day + other, self.year)

    def __radd__(self, other):
        """
        >>> d1 = DayToken(3, 2, None)
        >>> 3 + d1
        3/5
        """
        assert isinstance(other, int)
        return DayToken(self.month, self.day + other, self.year)

    def datetime(self, now):
        return datetime.datetime(self.year, self.month, self.day)

    @staticmethod
    def from_datetime(datetime):
        return DayToken(datetime.month, datetime.day, datetime.year)

    def __eq__(self, other):
        """
        >>> DayToken(5, 7, 2018) == DayToken(5, 7, 2018)
        True
        >>> DayToken(7, 4, 2018) == DayToken(7, 6, 2018)
        False
        """
        if not isinstance(other, DayToken):
            return False
        return self.month == other.month and self.day == other.day and \
            self.year == other.year

    def __repr__(self):
        if not self.year:
            return '{}/{}'.format(self.month, self.day)
        if not self.day:
            return '{}/{}'.format(self.month, self.year)
        # either all fields populated or would be confusing w/o null fields
        # (e.g., only month is non-null)
        return '{}/{}/{}'.format(
            self.month, self.day, self.year)


class DayRange(Token):

    def __init__(self, start, end):
        self.start = start
        self.end = end

    def apply_month(self, month):
        self.start.month = month
        self.end.month = month

    def apply_year(self, year):
        self.start.year = year
        self.end.year = year

    def datetime(self, now):
        return (self.start.datetime(now), self.end.datetime(now))

    def combine(self, time):
        assert isinstance(time, (TimeRange, TimeToken))
        if isinstance(time, TimeToken):
            return DayTimeRange(
                DayTimeToken.from_day_time(self.start, time),
                DayTimeToken.from_day_time(self.end, time))
        raise NotImplementedError()  # return list of two ranges

    def __repr__(self):
        return '{} - {}'.format(repr(self.start), repr(self.end))


class DayList(ListToken):
    """
    >>> now = datetime.datetime(2018, 7, 5)
    >>> dt1 = DayToken(8, 1, 2018)
    >>> dt2 = DayToken(8, 2, 2018)
    >>> dts = DayList(dt1, dt2)
    >>> dts
    [8/1/2018, 8/2/2018]
    >>> dts.datetime(now)
    [datetime.datetime(2018, 8, 1, 0, 0), datetime.datetime(2018, 8, 2, 0, 0)]
    >>> dts.combine(TimeToken(15))
    [8/1/2018 3 pm, 8/2/2018 3 pm]
    >>> dts2 = DayList(dt1)
    >>> dts3 = DayList()
    >>> dts.extend(dts3) == dts
    True
    >>> dts.extend(dts2)
    [8/1/2018, 8/2/2018, 8/1/2018]
    >>> dts.combine(AmbiguousToken()) == dts
    True
    """

    def combine(self, other):
        if isinstance(other, (TimeRange, TimeToken, DayTimeToken)):
            return DayTimeList(*[token.combine(other) for token in self.tokens])
        return self

    def extend(self, other):
        assert isinstance(other, DayList)
        if other.tokens:
            tokens = self.tokens + other.tokens
            return DayList(*tokens)
        return self


class TimeToken(Token):
    """
    >>> TimeToken(3, 'pm')
    3 pm
    >>> TimeToken(3, None)
    3:00
    >>> TimeToken(3)
    3:00
    >>> TimeToken(12, 'pm')
    12 pm
    >>> TimeToken(12, 'am')
    12 am
    >>> TimeToken(12)
    12 pm
    """

    def __init__(self, relative_hour, time_of_day=None, minute=0):
        self.relative_hour = relative_hour
        self.minute = minute
        self.time_of_day = time_of_day

        if relative_hour > 12:
            assert time_of_day != 'pm'
            self.relative_hour = relative_hour - 12
            self.hour = relative_hour
            self.time_of_day = 'pm'
        elif time_of_day == 'pm' and relative_hour == 12:
            self.hour = 12
        elif time_of_day == 'pm' and relative_hour != 12:
            self.hour = self.relative_hour + 12
        elif time_of_day == 'am' and relative_hour == 12:
            self.hour = 0
        elif relative_hour == 12:
            self.hour = 12
            self.time_of_day = 'pm'
        else:
            self.hour = self.relative_hour

        assert 0 <= self.hour < 24
        assert 0 <= self.minute < 60

    def datetime(self, now):
        return datetime.datetime(now.year, now.month, now.day, self.hour, self.minute)

    def string(self, with_time_of_day=True):
        if self.time_of_day is None:
            return '{}:{:02d}'.format(self.hour, self.minute)
        if self.minute == 0:
            if with_time_of_day:
                return '{} {}'.format(self.relative_hour, self.time_of_day)
            else:
                return str(self.relative_hour)
        if not with_time_of_day:
            return '{}:{:02d}'.format(self.relative_hour, self.minute)
        return '{}:{:02d} {}'.format(
            self.relative_hour, self.minute, self.time_of_day)

    @staticmethod
    def update_time_of_day(self, _, time_of_day):
        """
        >>> time = TimeToken(3)
        >>> TimeToken.update_time_of_day(time, None, 'pm')
        >>> time
        3 pm
        >>> time.hour
        15
        >>> TimeToken.update_time_of_day(time, None, 'am')
        >>> time
        3 am
        >>> time.hour
        3
        """
        if time_of_day != self.time_of_day:
            if time_of_day == 'pm':
                self.hour += 12
            else:
                self.hour -= 12
            self.time_of_day = time_of_day

    def apply(self, other):
        assert isinstance(other, TimeToken)
        self.share('time_of_day', other, setter=TimeToken.update_time_of_day)

    def __repr__(self):
        return self.string()


class TimeRange(Token):

    def __init__(self, start, end):
        self.start = start
        self.end = end

    def datetime(self, now):
        return (self.start.datetime(now), self.end.datetime(now))

    def __repr__(self):
        if self.start.time_of_day == self.end.time_of_day != None:
            return '{}-{}'.format(self.start.string(False), self.end.string())
        return '{} - {}'.format(repr(self.start), repr(self.end))


class TimeList(ListToken):
    """
    >>> t1 = TimeToken(15)
    >>> t2 = TimeToken(17)
    >>> t3 = TimeToken(3, None)
    >>> ts = TimeList(t1, t2)
    >>> dt = DayToken(8, 1, 2018)
    >>> ts.combine(dt)
    [8/1/2018 3 pm, 8/1/2018 5 pm]
    >>> ts2 = TimeList(t3)
    >>> ts3 = TimeList()
    >>> ts.extend(ts3) == ts
    True
    >>> t3.time_of_day
    >>> ts.extend(ts2)
    [3 pm, 5 pm, 3 pm]
    >>> ts.combine(AmbiguousToken()) == ts
    True
    """

    def combine(self, other):
        if isinstance(other, (DayRange, DayToken)):
            return DayTimeList(*[other.combine(token) for token in self.tokens])
        return self

    def extend(self, other):
        assert isinstance(other, TimeList)
        if len(other.tokens) > 0:
            for token in self.tokens:
                token.apply(other.tokens[0])
            tokens = self.tokens + other.tokens
            return TimeList(*tokens)
        return self


class AmbiguousToken(Token):
    """
    >>> now = datetime.datetime(2018, 1, 1)
    >>> amb = AmbiguousToken(TimeToken(15))
    >>> amb.datetime(now)
    datetime.datetime(2018, 1, 1, 15, 0)
    """

    def __init__(self, *tokens):
        self.tokens = tokens

    def has_time_range_token(self):
        return any([isinstance(token, TimeRange) for token in self.tokens])

    def get_time_range_token(self):
        for token in self.tokens:
            if isinstance(token, TimeRange):
                return token

    def has_day_range_token(self):
        return any([isinstance(token, DayRange) for token in self.tokens])

    def get_day_range_token(self):
        for token in self.tokens:
            if isinstance(token, DayRange):
                return token

    def has_day_token(self):
        return any([isinstance(token, DayToken) for token in self.tokens])

    def get_day_token(self):
        for token in self.tokens:
            if isinstance(token, DayToken):
                return token

    def datetime(self, now):
        return self.tokens[0].datetime(now=now)

    def __repr__(self):
        return ' OR '.join(map(repr, self.tokens))
