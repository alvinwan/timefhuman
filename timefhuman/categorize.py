from .constants import MONTHS
from .constants import DAYS_OF_WEEK
from .data import DayToken
from .data import TimeToken
from .data import DayRange
from .data import TimeRange
from .data import AmbiguousToken
from .data import Token

import datetime


def categorize(tokens, now):
    """
    >>> now = datetime.datetime(2018, 8, 6, 6, 0)
    >>> categorize(['upcoming', 'Monday', 'noon'], now)
    [8/6/2018, 12 pm]
    >>> categorize(['7/17', '3:30', 'p.m.', '-', '4', 'p.m.'], now)
    [7/17/2018, 3:30 pm, '-', 4 pm]
    >>> categorize(['7/17', 'or', '7/18', '3', 'p.m.'], now)
    [7/17/2018, 'or', 7/18/2018, 3 pm]
    >>> categorize(['today', 'or', 'tomorrow', 'noon'], now)
    [8/6/2018, 'or', 8/7/2018, 12 pm]
    >>> categorize(['7/17', '4', 'or', '5', 'PM'], now)
    [7/17/2018, 4:00, 'or', 5 pm]
    >>> categorize(['7/17', '3', 'pm', '-', '7/19', '2', 'pm'], now)
    [7/17/2018, 3 pm, '-', 7/19/2018, 2 pm]
    """
    tokens = list(tokens)
    tokens = convert_words_to_numbers(tokens)
    tokens = convert_day_of_week(tokens, now)
    tokens = convert_relative_days_ranges(tokens, now)
    tokens = convert_time_of_day(tokens)
    tokens = maybe_substitute_hour_minute(tokens)
    tokens = maybe_substitute_using_date(tokens, now)
    tokens = maybe_substitute_using_month(tokens, now)
    tokens = substitute_hour_minute_in_remaining(tokens, now)
    return tokens


# TODO: add conversions for thirty, fourty-five
# TODO: maybe set default for seven o'clock to 7 pm not am?
def convert_words_to_numbers(tokens):
    """
    Converts numbers in word format into number format
    >>> convert_words_to_numbers(['five', "o'clock"])
    ['5', "o'clock"]
    >>> convert_words_to_numbers(['seven', "o'clock"])
    ['7', "o'clock"]
    """
    number_words = ["zero", "one", "two", "three", "four", "five", "six",
                    "seven", "eight", "nine", "ten", "eleven", "twelve"]
    for index, token in enumerate(tokens):
        if token.lower() in number_words:
            tokens[index] = str(number_words.index(token.lower()))
    return tokens


# TODO: "monday next week"
def convert_day_of_week(tokens, now=datetime.datetime.now()):
    """Convert day-of-week vernacular into date-like string.

    WARNING: assumes that 'upcoming', and (no specification) implies
    the same day. e.g., 'upcoming Monday', and 'Monday' are both
    the same day. However, it assumes that 'next Monday' is the one *after.
    Also assumes that 'last', 'past', and 'previous' are the same.

    >>> now = datetime.datetime(year=2018, month=8, day=4)
    >>> convert_day_of_week(['Monday', 'at', '3'], now)
    [8/6/2018, 'at', '3']
    >>> convert_day_of_week(['next', 'Monday', 'at', '3'], now)
    [8/13/2018, 'at', '3']
    >>> convert_day_of_week(['past', 'Monday', 'at', '3'], now)
    [7/30/2018, 'at', '3']
    >>> convert_day_of_week(['sat', 'at', '5'], now)
    [8/4/2018, 'at', '5']
    >>> convert_day_of_week(['suNday', 'at', '5'], now)
    [8/5/2018, 'at', '5']
    """
    tokens = tokens.copy()
    for i in range(7):
        day = now + datetime.timedelta(i)
        day_of_week = DAYS_OF_WEEK[day.weekday()]

        for string in (day_of_week, day_of_week[:2], day_of_week[:3], day_of_week[:4]):
            for index, token in enumerate(tokens):
                if isinstance(token, str) and string.lower() == token.lower():
                    new_index, tokens, weeks = extract_weeks_offset(tokens, end=index)
                    day = now + datetime.timedelta(weeks*7 + i)
                    tokens[new_index] = DayToken(day.month, day.day, day.year)
                    break
    return tokens


def convert_relative_days_ranges(tokens, now=datetime.datetime.now()):
    """Convert relative days (e.g., "today", "tomorrow") into date-like string.

    Additionally converts known ranges (e.g., "weekend", "weekdays")

    >>> now = datetime.datetime(2018, 8, 6)
    >>> convert_relative_days_ranges(['today', 'or', 'tomorrow', TimeToken(12, 'pm')], now)
    [8/6/2018, 'or', 8/7/2018, 12 pm]
    >>> convert_relative_days_ranges(['next', 'weekend'], now)
    ['next', 8/11/2018 - 8/12/2018]
    >>> convert_relative_days_ranges(['weekdays'], now)
    [8/6/2018 - 8/10/2018]
    """
    # TODO: what if user says 'this weekend' and it is currently the weekend?
    # for weekends, use 'next' as +1 and this weekend is the ranging including
    # today
    # TODO: add support for 'next weekday' (not daterange, conditioinal lookahead)
    (saturday,) = convert_day_of_week(['upcoming', 'Saturday'], now)
    (monday,) = convert_day_of_week(['upcoming', 'Monday'], now)
    month_= (now.replace(day=28)+datetime.timedelta(days=4)).replace(day=1)
    month_end_= (((now.replace(day=28)+datetime.timedelta(days=4)).replace(day=28)+datetime.timedelta(days=4)).replace(day=1)-datetime.timedelta(days=1))
    month=DayToken(month_.month,month_.day,month_.year)
    month_end=DayToken(month_end_.month,month_end_.day,month_end_.year)
    
    for keywords, replacement in (
            (("today",), DayToken.from_datetime(now)),
            (("tomorrow", "tmw"), DayToken.from_datetime(now + datetime.timedelta(1))),
            (("yesterday",), DayToken.from_datetime(now - datetime.timedelta(1))),
            (("weekend",), DayRange(saturday, saturday + 1)),
            (("weekdays",), DayRange(monday, monday + 4)),
            (("week",), DayRange(monday, monday + 6)),
            (("month",), DayRange(month, month_end))):
        for keyword in keywords:
            tokens = [replacement if token == keyword else token \
                        for token in tokens]
    return tokens


# TODO: convert to new token-based system
def extract_weeks_offset(tokens, end=None, key_tokens=(
        'next', 'previous', 'last', 'upcoming', 'past', 'prev')):
    """Extract the number of week offsets needed.

    >>> extract_weeks_offset(['next', 'next', 'week'])
    (0, ['week'], 2)
    >>> extract_weeks_offset(['upcoming', 'Monday'])
    (0, ['Monday'], 0)
    >>> extract_weeks_offset(['last', 'Monday'])
    (0, ['Monday'], -1)
    >>> extract_weeks_offset(['past', 'Tuesday'])
    (0, ['Tuesday'], -1)
    >>> extract_weeks_offset(['past', 'Wed', 'next', 'week'], end=1)
    (0, ['Wed', 'next', 'week'], -1)
    """
    offset = 0
    end = len(tokens) - 1 if end is None else end
    start = end - 1
    if start < 0 or start >= len(tokens):
        return 0, tokens, 0

    while len(tokens) > start >= 0 and \
            tokens[start] in key_tokens:
        candidate = tokens[start]
        if candidate == 'upcoming':
            return start, tokens[:end-1] + tokens[end:], 0
        if candidate == 'next':
            offset += 1
        elif candidate in ('previous', 'prev', 'last', 'past'):
            offset -= 1
        start -= 1
    return start + 1, tokens[:start + 1] + tokens[end:], offset


def convert_time_of_day(tokens):
    """Convert time-of-day vernacular into time-like string.

    >>> convert_time_of_day(['Monday', 'noon', 'huehue'])
    ['Monday', 12 pm, 'huehue']
    >>> convert_time_of_day(['Monday', 'afternoon'])
    ['Monday', 3 pm]
    >>> convert_time_of_day(['Tu', 'evening'])
    ['Tu', 6 pm]
    >>> convert_time_of_day(['Wed', 'morning'])
    ['Wed', 9 am]
    >>> convert_time_of_day(['Thu', 'midnight'])
    ['Thu', 12 am]
    """
    temp_tokens = [token.lower() if isinstance(token, str) else token for token in tokens]
    for keyword, time_tokens in (
            ('morning', [TimeToken(9, 'am')]),
            ('noon', [TimeToken(12, 'pm')]),
            ('afternoon', [TimeToken(3, 'pm')]),
            ('evening', [TimeToken(6, 'pm')]),
            ('night', [TimeToken(9, 'pm')]),
            ('midnight', [TimeToken(12, 'am')])):
        if keyword in temp_tokens:
            index = temp_tokens.index(keyword)
            tokens = tokens[:index] + time_tokens + tokens[index+1:]
    return tokens


def maybe_substitute_using_month(tokens, now=datetime.datetime.now()):
    """

    >>> now = datetime.datetime(year=2018, month=7, day=7)
    >>> maybe_substitute_using_month(['July', '17', ',', '2018', 'at'], now=now)
    [7/17/2018, 'at']
    >>> maybe_substitute_using_month(['Jul', '17', 'at'], now=now)
    [7/17/2018, 'at']
    >>> maybe_substitute_using_month(['July', 'at'], now=now)
    [7/7/2018, 'at']
    >>> maybe_substitute_using_month(['August', '17', ','], now=now)
    [8/17/2018, ',']
    >>> maybe_substitute_using_month(['Aug', 'at'], now=now)
    [8/1/2018, 'at']
    >>> maybe_substitute_using_month(['gibberish'], now=now)
    ['gibberish']
    >>> time_range = TimeRange(TimeToken(3, 'pm'), TimeToken(5, 'pm'))
    >>> day_range = DayRange(DayToken(None, 3, None), DayToken(None, 5, None))
    >>> day = DayToken(3, 5, 2018)
    >>> ambiguous_token = AmbiguousToken(time_range, day, day_range)
    >>> maybe_substitute_using_month(['May', ambiguous_token], now=now)
    [5/3/2018 - 5/5/2018]
    """
    temp_tokens = [token.lower() if isinstance(token, str) else token for token in tokens]
    for mo, month in enumerate(MONTHS, start=1):

        index = None
        month = month.lower()
        if month in temp_tokens:
            index = temp_tokens.index(month)
        if month[:3] in temp_tokens:
            index = temp_tokens.index(month[:3])

        if index is None:
            continue

        next_candidate = tokens[index+1]
        day = 1 if now.month != mo else now.day
        if isinstance(next_candidate, AmbiguousToken):
            if next_candidate.has_day_range_token():
                day_range = next_candidate.get_day_range_token()
                day_range.apply_month(mo)
                day_range.apply_year(now.year)  # TODO: fails on July 3-5, 2018
                return tokens[:index] + [day_range] + tokens[index+2:]
        if not next_candidate.isnumeric():
            day = DayToken(month=mo, day=day, year=now.year)
            return tokens[:index] + [day] + tokens[index+1:]

        # allow formats July 17, 2018. Do not consume comma if July 17, July 18 ...
        next_candidate = int(next_candidate)
        next_next_candidate = tokens[index+2] if len(tokens) > index+2 else ''
        if next_next_candidate == ',':
            next_next_candidate = tokens[index+3] if len(tokens) > index+3 else ''
            if next_next_candidate.isnumeric():
                tokens = tokens[:index+1] + tokens[index+2:]

        if next_candidate > 31:
            day = 1 if now.month != mo else now.day
            day = DayToken(month=mo, day=day, year=next_candidate)
            return tokens[:index] + [day] + tokens[index+2:]
        elif not next_next_candidate.isnumeric():
            day = DayToken(month=mo, day=next_candidate, year=now.year)
            return maybe_substitute_using_month(tokens[:index] + [day] + tokens[index+2:], now)

        next_next_candidate = int(next_next_candidate)
        day = DayToken(month=mo, day=next_candidate, year=next_next_candidate)
        return maybe_substitute_using_month(tokens[:index] + [day] + tokens[index+3:], now)
    return tokens


def maybe_substitute_using_date(tokens, now=datetime.datetime.now()):
    """Attempt to extract dates.

    Look for dates in the form of the following:

    (month)/(day)
    (month).(day)
    (month)-(day)
    (month)/(day)/(year)
    (month).(day).(year)
    (month)-(day)-(year)

    >>> now = datetime.datetime(2018, 8, 18)
    >>> maybe_substitute_using_date(['7/17/18'])
    [7/17/2018]
    >>> maybe_substitute_using_date(['7-17-18'])
    [7/17/2018]
    >>> maybe_substitute_using_date(['3', 'on', '7.17.18'])
    ['3', 'on', 7/17/2018]
    >>> maybe_substitute_using_date(['7-25', '3-4', 'pm'], now=now)
    [7/25/2018, 3/4/2018 OR 3:00 - 4:00, 'pm']
    >>> maybe_substitute_using_date(['7/4', '-', '7/6'], now=now)
    [7/4/2018, '-', 7/6/2018]
    """
    i = 0
    while i < len(tokens):
        token = tokens[i]
        if isinstance(token, Token):
            i += 1
            continue
        for punctuation in ('/', '.', '-'):
            if punctuation == token:  # dash joins other tokens, skip parsing
                continue
            if punctuation not in token:
                continue

            parts = tuple(map(int, token.split(punctuation)))
            if len(parts) == 2:
                day = DayToken(month=parts[0], day=parts[1], year=now.year)
                if punctuation == '-' and parts[1] <= 24:
                    day = AmbiguousToken(
                        day, extract_hour_minute(token))
                tokens = tokens[:i] + [day] + tokens[i+1:]
                continue

            month, day, year = parts
            if year < 1000:
                year = year + 2000 if year < 50 else year + 1000
            day = DayToken(month=month, day=day, year=year)
            tokens = tokens[:i] + [day] + tokens[i+1:]
        i += 1
    return tokens


def extract_hour_minute(string, time_of_day=None):
    """

    >>> extract_hour_minute('3:00')
    3:00
    >>> extract_hour_minute('3:00', 'pm')
    3 pm
    >>> time = extract_hour_minute('3')
    >>> time
    3:00
    >>> time.time_of_day
    >>> extract_hour_minute('3:30-4', 'pm')
    3:30-4 pm
    >>> time_range = TimeRange(TimeToken(3, 'pm'), TimeToken(5, 'pm'))
    >>> day_range = DayRange(DayToken(None, 3, None), DayToken(None, 5, None))
    >>> day = DayToken(3, 5, 2018)
    >>> ambiguous_token = AmbiguousToken(time_range, day, day_range)
    >>> extract_hour_minute(ambiguous_token)
    3-5 pm
    >>> extract_hour_minute(AmbiguousToken(day))
    """
    if isinstance(string, AmbiguousToken):
        if string.has_time_range_token():
            return string.get_time_range_token()
        return None

    if '-' in string:
        times = string.split('-')
        start = extract_hour_minute(times[0], time_of_day)
        end = extract_hour_minute(times[1], time_of_day)
        return TimeRange(start, end)

    parts = string.split(':')
    hour = int(parts[0])
    minute = int(parts[1]) if len(parts) >= 2 else 0
    return TimeToken(relative_hour=hour, minute=minute, time_of_day=time_of_day)


def extract_hour_minute_token(tokens, time_of_day=None):
    """
        Attempt to extract the exact token which contains the hour and minute and convert it into a number.
        This will either be 1 before or 2 before the am/pm token.
        12:00 is the default token to prevent failure
        Tests for this helper function are included in maybe_substitute_hour_minute
        >>> extract_hour_minute_token(["3", "o'clock"])
        (-2, 3:00)
        >>> extract_hour_minute_token(["Gibberish", "twice"])
        (-1, 12)
        >>> extract_hour_minute_token(["only one value"])
        (-1, 12)
    """

    # look at previous n tokens
    n = 2
    for i in range(1, n+1):
        try:
            return -i, extract_hour_minute(tokens[-i], time_of_day)
        # if nothing is returned from extract_hour_minute
        except ValueError:
            pass
        # if the tokens list is only of length 1
        except IndexError:
            pass
    # default return value
    return -1, 12


def maybe_substitute_hour_minute(tokens):
    """Attempt to extract hour and minute.

    If am and pm are found, grab the hour and minute before it. If colon, use
    that as time.

    >>> maybe_substitute_hour_minute(['7/17/18', '3', 'PM'])
    ['7/17/18', 3 pm]
    >>> maybe_substitute_hour_minute(['7/17/18', '3:00', 'p.m.'])
    ['7/17/18', 3 pm]
    >>> maybe_substitute_hour_minute(['July', '17', '2018', 'at', '3', 'p.m.'])
    ['July', '17', '2018', 'at', 3 pm]
    >>> maybe_substitute_hour_minute(['July', '17', '2018', '3', 'p.m.'])
    ['July', '17', '2018', 3 pm]
    >>> maybe_substitute_hour_minute(['3', 'PM', 'on', 'July', '17'])
    [3 pm, 'on', 'July', '17']
    >>> maybe_substitute_hour_minute(['July', 'at', '3'])
    ['July', 'at', '3']
    >>> maybe_substitute_hour_minute(['7/17/18', '15:00'])
    ['7/17/18', 3 pm]
    >>> maybe_substitute_hour_minute(['7/17/18', TimeToken(3, 'pm')])
    ['7/17/18', 3 pm]
    >>> maybe_substitute_hour_minute(['3', 'p.m.', '-', '4', 'p.m.'])
    [3 pm, '-', 4 pm]
    >>> maybe_substitute_hour_minute(['5', "o'clock", 'pm'])
    [5 pm]
    >>> maybe_substitute_hour_minute(['12', "o'clock", 'pm'])
    [12 pm]
    """
    remove_dots = lambda token: token.replace('.', '')
    temp_tokens = clean_tokens(tokens, remove_dots)

    for time_of_day in ('am', 'pm'):
        while time_of_day in temp_tokens:
            index = temp_tokens.index(time_of_day)
            (unchanged_index, time_token) = extract_hour_minute_token(temp_tokens[:index], time_of_day)
            tokens = tokens[:index+unchanged_index] + [time_token] + tokens[index+1:]
            temp_tokens = clean_tokens(tokens, remove_dots)

    tokens = [extract_hour_minute(token, None)
        if isinstance(token, str) and ':' in token else token
        for token in tokens]

    return tokens


def clean_tokens(tokens, callback=lambda token: token):
    """
    >>> clean_tokens(['Hello', '3', 'P.M.'])
    ['hello', '3', 'p.m.']
    >>> clean_tokens(['Hello', '3', 'P.M.'], lambda token: token.replace('.', ''))
    ['hello', '3', 'pm']
    """
    return [callback(token.lower()) if isinstance(token, str)
            else token for token in tokens]


def substitute_hour_minute_in_remaining(tokens, now=datetime.datetime.now()):
    """Sketch collector for leftovers integers.

    >>> substitute_hour_minute_in_remaining(['gibberish'])
    ['gibberish']
    """
    for i, token in enumerate(tokens):
        if isinstance(token, Token):
            continue
        if token.isnumeric():
            time_token = extract_hour_minute(token)
            return tokens[:i] + [time_token] + tokens[i+1:]
    return tokens
