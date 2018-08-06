from timefhuman import timefhuman
import datetime


def test_main():
    now = datetime.datetime(year=2018, month=8, day=4)
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


def test_choices():
    now = datetime.datetime(year=2018, month=8, day=4)
    assert timefhuman('7/17 4 or 5 PM', now) == [
        datetime.datetime(2018, 7, 17, 16, 0),
        datetime.datetime(2018, 7, 17, 17, 0),
    ]
    # assert timefhuman('7/17 4-5 or 5-6 PM') == [
    #     (datetime.datetime(2018, 7, 17, 16, 0), datetime.datetime(2018, 7, 17, 17, 0)),
    #     (datetime.datetime(2018, 7, 17, 17, 0), datetime.datetime(2018, 7, 17, 18, 0))
    # ]
