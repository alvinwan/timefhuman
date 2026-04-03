import datetime

import pytz


def localized_datetime(tz_name, *parts):
    return pytz.timezone(tz_name).localize(datetime.datetime(*parts))
