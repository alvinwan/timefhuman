import datetime
from zoneinfo import ZoneInfo


def localized_datetime(tz_name, *parts):
    return datetime.datetime(*parts, tzinfo=ZoneInfo(tz_name))


def fixed_offset(minutes: int):
    return datetime.timezone(datetime.timedelta(minutes=minutes))
