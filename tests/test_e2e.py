from timefhuman import timefhuman
import datetime
import pytest


@pytest.fixture
def now():
    return datetime.datetime(year=2018, month=8, day=4)


def test_main(now):
    assert timefhuman('5p', now) == datetime.time(hour=17, minute=0)
    assert timefhuman('July 17, 2018 at 3p.m.', now) == \
        datetime.datetime(2018, 7, 17, 15, 0)
    assert timefhuman('July 17, 2018 3 p.m.', now) == \
        datetime.datetime(2018, 7, 17, 15, 0)
    assert timefhuman('3PM on July 17', now) == \
        datetime.datetime(2018, 7, 17, 15, 0)
    assert timefhuman('July 17 at 3', now) == \
        datetime.datetime(2018, 7, 17, 3, 0)
    assert timefhuman('July 2019', now) == \
        datetime.date(2019, 7, 1)
    assert timefhuman('7/17/18 3:00 p.m.', now) == \
        datetime.datetime(2018, 7, 17, 15, 0)


def test_ambiguity(now):
    # distribute the meridiem across the range
    assert timefhuman('7-17 3-4 p.m.', now) == (
        datetime.datetime(2018, 7, 17, 15, 0),
        datetime.datetime(2018, 7, 17, 16, 0)
    )


def test_choices(now):
    # distribute meridiem across choices
    assert timefhuman('7/17 4 or 5 PM', now) == [
        datetime.datetime(2018, 7, 17, 16, 0),
        datetime.datetime(2018, 7, 17, 17, 0),
    ]
    assert timefhuman('7/17 4-5 PM or 5-6 PM', now) == [
        (datetime.datetime(2018, 7, 17, 16, 0), datetime.datetime(2018, 7, 17, 17, 0)),
        (datetime.datetime(2018, 7, 17, 17, 0), datetime.datetime(2018, 7, 17, 18, 0))
    ]
    assert timefhuman('7/17 4-5 or 5-6 PM', now) == [
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
    assert timefhuman('3p -4p', now) == (
        datetime.time(15, 0),
        datetime.time(16, 0),)
    assert timefhuman('7/17-7/18', now) == (
        datetime.date(2018, 7, 17),
        datetime.date(2018, 7, 18),)
    assert timefhuman('7/17 3 pm- 7/19 2 pm', now) == (
        datetime.datetime(2018, 7, 17, 15, 0),
        datetime.datetime(2018, 7, 19, 14, 0),)


def test_comma_delimited_combination(now):
    assert timefhuman('tomorrow noon,Wed 3 p.m.,Fri 11 AM', now) == [
        datetime.datetime(2018, 8, 5, 12, 0),
        datetime.datetime(2018, 8, 8, 15, 0),
        datetime.datetime(2018, 8, 10, 11, 0)
    ]

def test_multiple_datetimes(now):
    assert timefhuman('Jun 28 5:00 PM - Aug 02 7:00 PM', now) == \
        (datetime.datetime(2018, 6, 28, 17, 0), datetime.datetime(2018, 8, 2, 19, 0))
    assert timefhuman('Jun 28 2019 5:00 PM - Aug 02 2019 7:00 PM', now) == \
        (datetime.datetime(2019, 6, 28, 17, 0), datetime.datetime(2019, 8, 2, 19, 0))
    assert timefhuman('Jun 28, 2019 5:00 PM - Aug 02, 2019 7:00 PM', now) == \
        (datetime.datetime(2019, 6, 28, 17, 0), datetime.datetime(2019, 8, 2, 19, 0))
    assert timefhuman('6/28 5:00 PM - 8/02 7:00 PM', now) == \
        (datetime.datetime(2018, 6, 28, 17, 0), datetime.datetime(2018, 8, 2, 19, 0))
    assert timefhuman('6/28/2019 5:00 PM - 8/02/2019 7:00 PM', now) == \
        (datetime.datetime(2019, 6, 28, 17, 0), datetime.datetime(2019, 8, 2, 19, 0))