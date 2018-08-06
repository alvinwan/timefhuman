import datetime


class Token:
    pass


class DayTimeToken(Token):

    def __init__(self, year, month, day, relative_hour, minute=0, time_of_day='am'):
        self.day = DayToken(month, day, year)
        self.time = TimeToken(relative_hour, time_of_day, minute)

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
    8/1/2018 10-11 am
    >>> DayTimeRange(dt1, dt3)
    8/1/2018 10 am - 1 pm
    >>> DayTimeRange(dt1, dt4)
    8/1/2018 10 am - 8/3/2018 11 am
    """

    def __init__(self, start, end):
        self.start = start
        self.end = end

    def datetime(self, now):
        return (self.start.datetime(now), self.end.datetime(now))

    def __repr__(self):
        if self.start.day == self.end.day:
            time_range = TimeRangeToken(self.start.time, self.end.time)
            return '{} {}'.format(repr(self.start.day), repr(time_range))
        return '{} - {}'.format(repr(self.start), repr(self.end))


class DayToken(Token):

    def __init__(self, month, day, year):
        self.month = month
        self.day = day
        self.year = year

    def combine(self, time):
        """
        >>> day = DayToken(8, 5, 2018)
        >>> time = TimeToken(3, 'pm')
        >>> time_range = TimeRangeToken(TimeToken(3, 'pm'), TimeToken(5, 'pm'))
        >>> day.combine(time)
        8/5/2018 3 pm
        >>> day.combine(time_range)
        8/5/2018 3-5 pm
        """
        assert isinstance(time, (TimeRangeToken, TimeToken))
        if isinstance(time, TimeToken):
            return DayTimeToken.from_day_time(self, time)
        return DayTimeRange(
            DayTimeToken.from_day_time(self, time.start),
            DayTimeToken.from_day_time(self, time.end))

    def datetime(self, now):
        return datetime.datetime(self.year, self.month, self.day)

    @staticmethod
    def from_datetime(datetime):
        return DayToken(datetime.month, datetime.day, datetime.year)

    def __eq__(self, other):
        """
        >>> DayToken(2018, 5, 7) == DayToken(2018, 5, 7)
        True
        >>> DayToken(2018, 7, 4) == DayToken(2018, 7, 6)
        False
        """
        if not isinstance(other, DayToken):
            return False
        return self.month == other.month and self.day == other.day and \
            self.year == other.year

    def __repr__(self):
        return '{}/{}/{}'.format(
            self.month, self.day, self.year)


class TimeToken(Token):
    """
    >>> TimeToken(3, 'pm')
    3 pm
    >>> TimeToken(3, None)
    3:00
    >>> TimeToken(3)
    3 am
    >>> TimeToken(12, 'pm')
    12 pm
    >>> TimeToken(12, 'am')
    12 am
    """

    def __init__(self, relative_hour, time_of_day='am', minute=0):
        self.relative_hour = relative_hour
        self.minute = minute
        self.time_of_day = time_of_day

        if relative_hour > 12:
            assert time_of_day != 'pm'
            self.relative_hour = relative_hour - 12
            self.hour = relative_hour
            self.time_of_day = 'pm'
        elif time_of_day == 'pm' and relative_hour != 12:
            self.hour = self.relative_hour + 12
        elif time_of_day == 'am' and relative_hour == 12:
            self.hour = 0
        else:
            self.hour = self.relative_hour

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

    def update_time_of_day(self, time_of_day):
        """
        >>> time = TimeToken(3)
        >>> time.update_time_of_day('pm')
        >>> time
        3 pm
        >>> time.hour
        15
        >>> time.update_time_of_day('am')
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

    def apply_time(self, other):
        if self.time_of_day is None and other.time_of_day is not None:
            self.update_time_of_day(other.time_of_day)
        elif self.time_of_day is not None and other.time_of_day is None:
            other.update_time_of_day(self.time_of_day)

    def __repr__(self):
        return self.string()


class DayRangeToken(Token):

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
        assert isinstance(time, (TimeRangeToken, TimeToken))
        if isinstance(time, TimeToken):
            return DayTimeRange(
                DayTimeToken.from_day_time(self.start, time),
                DayTimeToken.from_day_time(self.end, time))
        raise NotImplementedError()  # return list of two ranges

    def __repr__(self):
        return '{} - {}'.format(repr(self.start), repr(self.end))


class TimeRangeToken(Token):

    def __init__(self, start, end):
        self.start = start
        self.end = end

    def datetime(self, now):
        return (self.start.datetime(now), self.end.datetime(now))

    def __repr__(self):
        if self.start.time_of_day == self.end.time_of_day != None:
            return '{}-{}'.format(self.start.string(False), self.end.string())
        return '{} - {}'.format(repr(self.start), repr(self.end))


class AmbiguousToken(Token):

    def __init__(self, *tokens):
        self.tokens = tokens

    def has_time_range_token(self):
        return any([isinstance(token, TimeRangeToken) for token in self.tokens])

    def get_time_range_token(self):
        for token in self.tokens:
            if isinstance(token, TimeRangeToken):
                return token

    def has_day_range_token(self):
        return any([isinstance(token, DayRangeToken) for token in self.tokens])

    def get_day_range_token(self):
        for token in self.tokens:
            if isinstance(token, DayRangeToken):
                return token

    def __repr__(self):
        return ' OR '.join(map(repr, self.tokens))
