from datetime import datetime
import pytz
from babel.dates import get_timezone_name


def generate_timezone_mapping():
    text_to_timezone = {}

    for tz_name in pytz.all_timezones:
        timezone = pytz.timezone(tz_name)
        abbreviation1 = timezone.localize(datetime(2025, 1, 15)).strftime('%Z')
        abbreviation2 = timezone.localize(datetime(2025, 7, 15)).strftime('%Z')
        name = get_timezone_name(timezone)
        text_to_timezone[abbreviation1] = tz_name
        text_to_timezone[abbreviation2] = tz_name
        text_to_timezone[name] = tz_name

    return {
        key: value for key, value in text_to_timezone.items()
        if key[0] not in ('+', '-') and not key.startswith('Unknown')
    }