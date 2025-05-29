import datetime
from timefhuman import timefhuman, tfhConfig


def test_time_only(now):
    assert timefhuman('5pm', tfhConfig(now=now)) == [datetime.datetime(2018, 8, 4, 17, 0)]


def test_date_only_numeric(now):
    assert timefhuman('7/17/18', tfhConfig(now=now)) == [datetime.datetime(2018, 7, 17, 0, 0)]


def test_date_only_monthname(now):
    assert timefhuman('July 17, 2018', tfhConfig(now=now)) == [datetime.datetime(2018, 7, 17, 0, 0)]


def test_datetime(now):
    assert timefhuman('July 17, 2018 at 3pm', tfhConfig(now=now)) == [datetime.datetime(2018, 7, 17, 15, 0)]
