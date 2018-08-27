from timefhuman import timefhuman
import datetime
import pytest


@pytest.fixture
def now():
    return datetime.datetime(year=2018, month=8, day=4)


def test_main(now):
    assert timefhuman('July 17, 2018 at 3p.m.', now) == \
        datetime.datetime(2018, 7, 17, 15, 0)
    assert timefhuman('July 17, 2018 3 p.m.', now) == \
        datetime.datetime(2018, 7, 17, 15, 0)
    assert timefhuman('3PM on July 17', now) == \
        datetime.datetime(2018, 7, 17, 15, 0)
    assert timefhuman('July 17 at 3', now) == \
        datetime.datetime(2018, 7, 17, 3, 0)
    assert timefhuman('July 2019', now) == \
        datetime.datetime(2019, 7, 1, 0, 0)
    assert timefhuman('7/17/18 3:00 p.m.', now) == \
        datetime.datetime(2018, 7, 17, 15, 0)


def test_ambiguity(now):
    assert timefhuman('7-17 3-4 p.m.', now) == (
        datetime.datetime(2018, 7, 17, 15, 0),
        datetime.datetime(2018, 7, 17, 16, 0)
    )


def test_choices(now):
    assert timefhuman('7/17 4 or 5 PM', now) == [
        datetime.datetime(2018, 7, 17, 16, 0),
        datetime.datetime(2018, 7, 17, 17, 0),
    ]
    assert timefhuman('7/17 4-5 PM or 5-6 PM') == [
        (datetime.datetime(2018, 7, 17, 16, 0), datetime.datetime(2018, 7, 17, 17, 0)),
        (datetime.datetime(2018, 7, 17, 17, 0), datetime.datetime(2018, 7, 17, 18, 0))
    ]
    assert timefhuman('7/17 4-5 or 5-6 PM') == [
        (datetime.datetime(2018, 7, 17, 16, 0), datetime.datetime(2018, 7, 17, 17, 0)),
        (datetime.datetime(2018, 7, 17, 17, 0), datetime.datetime(2018, 7, 17, 18, 0))
    ]


def test_multiple_choices(now):
    print(timefhuman('7/17, 7/18, 7/19 at 2', now, raw=True))
    assert timefhuman('7/17, 7/18, 7/19 at 2', now) == [
        datetime.datetime(2018, 7, 17, 2, 0),
        datetime.datetime(2018, 7, 18, 2, 0),
        datetime.datetime(2018, 7, 19, 2, 0),
    ]


def test_edge_cases_range(now):
    assert timefhuman('3-4 pm', now) == (
        datetime.datetime(2018, 8, 4, 15, 0),
        datetime.datetime(2018, 8, 4, 16, 0),)
    assert timefhuman('7/17-7/18', now) == (
        datetime.datetime(2018, 7, 17, 0, 0),
        datetime.datetime(2018, 7, 18, 0, 0),)
    assert timefhuman('7/17 3 pm- 7/19 2 pm') == (
        datetime.datetime(2018, 7, 17, 15, 0),
        datetime.datetime(2018, 7, 19, 14, 0),)
