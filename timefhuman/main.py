"""
timefhuman
===
Convert human-readable date-like string to Python datetime object.

@author: Alvin Wan
@site: alvinwan.com
"""


from .constants import MONTHS
from .constants import DAYS_OF_WEEK
import datetime
import string


__all__ = ('timefhuman',)


def timefhuman(string, now=None):
    """A simple parsing function for date-related strings.

    >>> now = datetime.datetime(year=2018, month=7, day=7)
    >>> timefhuman('Monday noon', now=now)
    datetime.datetime(2018, 7, 9, 12, 0)
    >>> timefhuman('7/17 3 PM', now=now)
    datetime.datetime(2018, 7, 17, 15, 0)
    >>> timefhuman('July 17, 2018 at 3p.m.')
    datetime.datetime(2018, 7, 17, 15, 0)
    >>> timefhuman('July 17, 2018 3 p.m.')
    datetime.datetime(2018, 7, 17, 15, 0)
    >>> timefhuman('3PM on July 17', now=now)
    datetime.datetime(2018, 7, 17, 15, 0)
    >>> timefhuman('July 17 at 3')
    datetime.datetime(2018, 7, 17, 15, 0)
    >>> timefhuman('July 2019')
    datetime.datetime(2019, 7, 1, 0, 0)
    >>> timefhuman('7/17/18 3:00 p.m.')
    datetime.datetime(2018, 7, 17, 15, 0)
    """
    if now is None:
        now = datetime.datetime.now()

    tokens = list(tokenize(string))
    tokens = convert_day_of_week(tokens, now)
    tokens = convert_time_of_day(tokens)

    tokens, hour, minute = maybe_extract_hour_minute(tokens)
    tokens, month, day, year = maybe_extract_using_date(tokens, now)

    if not tokens:
        return assemble_date(year, month, day, hour, minute)

    if None in (month, day, year):
        tokens, month, day, year = maybe_extract_using_month(tokens, now)

    if not tokens or hour is not None:
        return assemble_date(year, month, day, hour, minute)

    hour, minute = extract_hour_minute_from_remaining(tokens, now)
    return assemble_date(year, month, day, hour, minute)

    # TODO: What if user specifies vernacular AND actual date time. Let
    # specified date time take precedence.


# TODO: "monday next week"
def convert_day_of_week(tokens, now=datetime.datetime.now()):
    """Convert day-of-week vernacular into date-like string.

    WARNING: assumes that 'upcoming', and (no specification) implies
    the same day. e.g., 'upcoming Monday', and 'Monday' are both
    the same day. However, it assumes that 'next Monday' is the one *after.
    Also assumes that 'last', 'past', and 'previous' are the same.

    >>> now = datetime.datetime(year=2018, month=8, day=4)
    >>> convert_day_of_week(['Monday', 'at', '3'])
    ['08/06/18', 'at', '3']
    >>> convert_day_of_week(['next', 'Monday', 'at', '3'])
    ['08/13/18', 'at', '3']
    >>> convert_day_of_week(['past', 'Monday', 'at', '3'])
    ['07/30/18', 'at', '3']
    """
    tokens = tokens.copy()
    for i in range(7):
        day = now + datetime.timedelta(i)
        day_of_week = DAYS_OF_WEEK[day.weekday()]

        for string in (day_of_week, day_of_week[:3], day_of_week[:2]):
            if string in tokens:
                index = tokens.index(string)
                new_index, tokens, weeks = extract_weeks_offset(tokens, end=index)
                day = now + datetime.timedelta(weeks*7 + i)
                tokens[new_index] = day.strftime("%m/%d/%y")
                break
    return tokens


def convert_time_of_day(tokens):
    """Convert time-of-day vernacular into time-like string.

    >>> convert_time_of_day(['Monday', 'noon', 'huehue'])
    ['Monday', '12', 'pm', 'huehue']
    >>> convert_time_of_day(['Monday', 'afternoon'])
    ['Monday', '3', 'pm']
    >>> convert_time_of_day(['Tu', 'evening'])
    ['Tu', '6', 'pm']
    >>> convert_time_of_day(['Wed', 'morning'])
    ['Wed', '9', 'am']
    >>> convert_time_of_day(['Thu', 'midnight'])
    ['Thu', '12', 'am']
    """
    temp_tokens = [token.lower() for token in tokens]
    for keyword, time_tokens in (
            ('morning', ['9', 'am']),
            ('noon', ['12', 'pm']),
            ('afternoon', ['3', 'pm']),
            ('evening', ['6', 'pm']),
            ('night', ['9', 'pm']),
            ('midnight', ['12', 'am'])):
        if keyword in temp_tokens:
            index = temp_tokens.index(keyword)
            return tokens[:index] + time_tokens + tokens[index+1:]
    return tokens


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


def assemble_date(year, month, day, hour, minute):
    """Assemble datetime object optionally using time.

    >>> assemble_date(2018, 8, 8, 0, 0)
    datetime.datetime(2018, 8, 8, 0, 0)
    >>> assemble_date(2018, 8, 8, None, None)
    datetime.datetime(2018, 8, 8, 0, 0)
    """
    assert None not in (year, month, day), "Could not find year, month, day"
    if hour is None:
        return datetime.datetime(year=year, month=month, day=day)
    return datetime.datetime(
        year=year, month=month, day=day, hour=hour, minute=minute)


def tokenize(characters):
    """Tokenize all characters in the string.

    >>> list(tokenize('7/17/18 3:00 p.m.'))
    ['7/17/18', '3:00', 'p.m.']
    >>> list(tokenize('July 17, 2018 at 3p.m.'))
    ['July', '17', '2018', 'at', '3', 'p.m.']
    >>> list(tokenize('July 17, 2018 3 p.m.'))
    ['July', '17', '2018', '3', 'p.m.']
    >>> list(tokenize('3PM on July 17'))
    ['3', 'PM', 'on', 'July', '17']
    """
    token = ''
    last_type = None
    for character in characters:
        type = get_character_type(character)
        is_different_type = None not in (type, last_type) and type != last_type
        is_break_character = character in string.whitespace + ','

        if is_break_character or is_different_type:
            if token:
                yield token
            token = character if is_different_type else ''
            last_type = type
            continue
        token += character
        last_type = type
    yield token


def get_character_type(character):
    """
    >>> get_character_type('a')
    'alpha'
    >>> get_character_type('1')
    'numeric'
    >>> get_character_type('.')
    """
    if character.isalpha():
        return 'alpha'
    elif character.isnumeric():
        return 'numeric'
    return None


def maybe_extract_using_month(tokens, now=datetime.datetime.now()):
    """

    >>> now = datetime.datetime(year=2018, month=7, day=7)
    >>> maybe_extract_using_month(['July', '17', '2018', 'at'])
    (['at'], 7, 17, 2018)
    >>> maybe_extract_using_month(['Jul', '17', 'at'], now=now)
    (['at'], 7, 17, 2018)
    >>> maybe_extract_using_month(['July', 'at'], now=now)
    (['at'], 7, 7, 2018)
    >>> maybe_extract_using_month(['August', '17'], now=now)
    ([], 8, 17, 2018)
    >>> maybe_extract_using_month(['Aug', 'at'], now=now)
    (['at'], 8, 1, 2018)
    >>> maybe_extract_using_month(['gibberish'], now=now)
    (['gibberish'], None, None, None)
    """
    temp_tokens = [token.lower() for token in tokens]
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
        if not next_candidate.isnumeric():
            return tokens[:index] + tokens[index+1:], mo, day, now.year

        next_candidate = int(next_candidate)
        next_next_candidate = tokens[index+2] if len(tokens) > index+2 else ''
        if next_candidate > 31:
            day = 1 if now.month != mo else now.day
            return tokens[:index] + tokens[index+2:], mo, day, next_candidate
        elif not next_next_candidate.isnumeric():
            return tokens[:index] + tokens[index+2:], mo, next_candidate, now.year

        next_next_candidate = int(next_next_candidate)
        remaining_tokens = tokens[:index] + tokens[index+3:]
        return remaining_tokens, mo, next_candidate, next_next_candidate
    return tokens, None, None, None


def maybe_extract_using_date(tokens, now=datetime.datetime.now()):
    """Attempt to extract dates.

    Look for dates in the form of the following:

    (month)/(day)
    (month).(day)
    (month)-(day)
    (month)/(day)/(year)
    (month).(day).(year)
    (month)-(day)-(year)

    >>> maybe_extract_using_date(['7/17/18'])
    ([], 7, 17, 2018)
    >>> maybe_extract_using_date(['7-17-18'])
    ([], 7, 17, 2018)
    >>> maybe_extract_using_date(['3', 'on', '7.17.18'])
    (['3', 'on'], 7, 17, 2018)
    """
    for token in tokens:
        for punctuation in ('/', '.', '-'):
            if punctuation in token:
                remaining_tokens = [token for token in tokens if punctuation not in token]
                parts = tuple(map(int, token.split(punctuation)))
                if len(parts) == 2:
                    return (remaining_tokens,) + parts + (now.year,)

                month, day, year = parts
                if year < 1000:
                    year = year + 2000 if year < 50 else year + 1000
                return remaining_tokens, month, day, year
    return tokens, None, None, None


def extract_hour_minute_from_time(string, time_of_day='am'):
    """

    >>> extract_hour_minute_from_time('3:00')
    (15, 0)
    >>> extract_hour_minute_from_time('3:00', 'pm')
    (15, 0)
    >>> extract_hour_minute_from_time('3')
    (15, 0)
    """
    parts = string.split(':')
    hour = int(parts[0])
    if time_of_day == 'pm' and hour != 12 or hour < 6:
        hour += 12
    minute = int(parts[1]) if len(parts) >= 2 else 0
    return hour, minute


def maybe_extract_hour_minute(tokens):
    """Attempt to extract hour and minute.

    If am and pm are found, grab the hour and minute before it. If colon, use
    that as time.

    >>> maybe_extract_hour_minute(['7/17/18', '3:00', 'p.m.'])
    (['7/17/18'], 15, 0)
    >>> maybe_extract_hour_minute(['July', '17', '2018', 'at', '3', 'p.m.'])
    (['July', '17', '2018', 'at'], 15, 0)
    >>> maybe_extract_hour_minute(['July', '17', '2018', '3', 'p.m.'])
    (['July', '17', '2018'], 15, 0)
    >>> maybe_extract_hour_minute(['3', 'PM', 'on', 'July', '17'])
    (['on', 'July', '17'], 15, 0)
    >>> maybe_extract_hour_minute(['July', 'at', '3'])
    (['July', 'at', '3'], None, None)
    >>> maybe_extract_hour_minute(['7/17/18', '15:00'])
    (['7/17/18'], 15, 0)
    """
    temp_tokens = [token.replace('.', '').lower() for token in tokens]
    remaining_tokens = tokens

    time = None
    time_of_day = None
    for time_of_day in ('am', 'pm'):
        if time_of_day in temp_tokens:
            index = temp_tokens.index(time_of_day)
            time = temp_tokens[index-1]
            remaining_tokens = tokens[:index-1] + tokens[index+1:]
            break

    if time is not None:
        hour, minute = extract_hour_minute_from_time(time, time_of_day)
        return remaining_tokens, hour, minute

    for token in tokens:
        if ':' in token:
            hour, minute = extract_hour_minute_from_time(token)
            remaining_tokens = [token for token in tokens if ':' not in token]
            return remaining_tokens, hour, minute

    return tokens, None, None


def extract_hour_minute_from_remaining(tokens, now=datetime.datetime.now()):
    """Sketch collector for leftovers integers.

    >>> extract_hour_minute_from_remaining(['gibberish'])
    (0, 0)
    """
    for token in tokens:
        if token.isnumeric():
            return extract_hour_minute_from_time(token)
    return 0, 0
