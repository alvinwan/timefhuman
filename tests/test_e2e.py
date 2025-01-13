from timefhuman import timefhuman
import datetime
import pytest
from timefhuman.main import Direction, tfhConfig


@pytest.fixture
def now():
    return datetime.datetime(year=2018, month=8, day=4, hour=14)


@pytest.mark.parametrize("test_input, expected", [
    # time only
    ('5p', datetime.datetime(2018, 8, 4, 17, 0)),
    
    # date only
    ('July 2019', datetime.datetime(2019, 7, 1, 0, 0)),
    # ('7-17-18', datetime.datetime(2018, 7, 17, 0, 0)),
    # ('7/2018', datetime.datetime(2018, 7, 1, 0, 0)),
    
    # datetimes
    ('July 17, 2018 at 3p.m.', datetime.datetime(2018, 7, 17, 15, 0)),
    ('July 17, 2018 3 p.m.', datetime.datetime(2018, 7, 17, 15, 0)),
    ('3PM on July 17', datetime.datetime(2018, 7, 17, 15, 0)),
    ('July 17 at 3', datetime.datetime(2018, 7, 17, 3, 0)),
    ('7/17/18 3:00 p.m.', datetime.datetime(2018, 7, 17, 15, 0)),
    ('3 p.m. today', datetime.datetime(2018, 8, 4, 15, 0)),
    ('Tomorrow 3p', datetime.datetime(2018, 8, 5, 15, 0)), # gh#24
    ('3p tomorrow', datetime.datetime(2018, 8, 5, 15, 0)),
    
    # date-only ranges
    ('7/17-7/18', (datetime.datetime(2018, 7, 17), datetime.datetime(2018, 7, 18))),
    # ('July 17-18', (datetime.datetime(2018, 7, 17), datetime.datetime(2018, 7, 18))), # distribute month
    
    # time-only ranges
    ('3p -4p', (datetime.datetime(2018, 8, 4, 15, 0), datetime.datetime(2018, 8, 4, 16, 0))),
    ('3-4p', (datetime.datetime(2018, 8, 4, 15, 0), datetime.datetime(2018, 8, 4, 16, 0))), # distribute meridiem
    # ('6:00 pm - 12:00 am', (datetime.datetime(2018, 8, 4, 18, 0), datetime.datetime(2018, 8, 4, 0, 0))), # TODO gh#8
    
    # basic date and time ranges
    ('7/17 3 pm- 7/19 2 pm', (datetime.datetime(2018, 7, 17, 15, 0), datetime.datetime(2018, 7, 19, 14, 0))),
    ('Jun 28 5:00 PM - Aug 02 7:00 PM', (datetime.datetime(2018, 6, 28, 17, 0), datetime.datetime(2018, 8, 2, 19, 0))),
    ('Jun 28 2019 5:00 PM - Aug 02 2019 7:00 PM', (datetime.datetime(2019, 6, 28, 17, 0), datetime.datetime(2019, 8, 2, 19, 0))),
    ('6/28 5:00 PM - 8/02 7:00 PM', (datetime.datetime(2018, 6, 28, 17, 0), datetime.datetime(2018, 8, 2, 19, 0))),
    ('6/28/2019 5:00 PM - 8/02/2019 7:00 PM', (datetime.datetime(2019, 6, 28, 17, 0), datetime.datetime(2019, 8, 2, 19, 0))),
    
    # infer date and time ranges
    ('7-17 3-4p', (datetime.datetime(2018, 7, 17, 15, 0), datetime.datetime(2018, 7, 17, 16, 0))), # infer date
    
    # choices
    ('7/17 4 or 5 PM', [datetime.datetime(2018, 7, 17, 16, 0), datetime.datetime(2018, 7, 17, 17, 0)]), # distribute meridiem
    # ('July 4th or 5th at 3PM', [datetime.datetime(2018, 7, 4, 15, 0), datetime.datetime(2018, 7, 5, 15, 0)]), # distribute meridiem
    ('7/17, 7/18, 7/19 at 2', [datetime.datetime(2018, 7, 17, 2, 0), datetime.datetime(2018, 7, 18, 2, 0), datetime.datetime(2018, 7, 19, 2, 0)]), # distribute meridiem
    ('tomorrow noon,Wed 3 p.m.,Fri 11 AM', [datetime.datetime(2018, 8, 5, 12, 0), datetime.datetime(2018, 8, 8, 15, 0), datetime.datetime(2018, 8, 10, 11, 0)]), # distribute meridiem
    
    # choices of ranges
    ('7/17 4-5 PM or 5-6 PM today', [
        (datetime.datetime(2018, 7, 17, 16, 0), datetime.datetime(2018, 7, 17, 17, 0)),
        (datetime.datetime(2018, 8, 4, 17, 0), datetime.datetime(2018, 8, 4, 18, 0))
    ]),
    ('7/17 4-5 or 5-6 PM', [
        (datetime.datetime(2018, 7, 17, 16, 0), datetime.datetime(2018, 7, 17, 17, 0)),
        (datetime.datetime(2018, 7, 17, 17, 0), datetime.datetime(2018, 7, 17, 18, 0))
    ]),
])
def test_default(now, test_input, expected):
    """Default behavior should be to infer datetimes and times."""
    assert timefhuman(test_input, now) == expected


@pytest.mark.parametrize("test_input, expected", [
    # time only
    ('5p', datetime.time(hour=17, minute=0)),
    
    # date only
    ('July 2019', datetime.date(2019, 7, 1)),
    
    # date-only ranges
    ('7/17-7/18', (datetime.date(2018, 7, 17), datetime.date(2018, 7, 18))),
    # ('July 17-18', (datetime.date(2018, 7, 17), datetime.date(2018, 7, 18))), # distribute month # TODO
    
    # time-only ranges
    ('3p -4p', (datetime.time(15, 0), datetime.time(16, 0))),
    ('3-4p', (datetime.time(15, 0), datetime.time(16, 0))), # distribute meridiem
    
    # durations
    ('30 minutes', datetime.timedelta(minutes=30)),
    ('30 mins', datetime.timedelta(minutes=30)),
    ('2 hours', datetime.timedelta(hours=2)),
    ('2 hours 30 minutes', datetime.timedelta(hours=2, minutes=30)),
    ('2 hours and 30 minutes', datetime.timedelta(hours=2, minutes=30)), # gh#22
    ('2h30m', datetime.timedelta(hours=2, minutes=30)),
    ('1 day and an hour', datetime.timedelta(days=1, hours=1)),
    ('1.5 hours', datetime.timedelta(hours=1, minutes=30)),
    ('in five minutes', datetime.timedelta(minutes=5)), # gh#25
    # ('one and a half hour', datetime.timedelta(hours=1, minutes=30)), # TODO
    # ('30-40 mins', (datetime.timedelta(minutes=30), datetime.timedelta(minutes=40))), # TODO
    # ('1 or 2 days', [datetime.timedelta(days=1), datetime.timedelta(days=2)]), # TODO
    # TODO: support duration ranges/lists
    # TODO: support natural language for duration like "three and a half hours"
    # TODO: support natural language times like "3 o'clock" or "quarter to 3"
])
def test_no_inference(now, test_input, expected):
    """Return exactly the date or time, without inferring the other."""
    config = tfhConfig(infer_datetimes=False)
    assert timefhuman(test_input, now, config=config) == expected


@pytest.mark.parametrize("config, test_input, expected", [
    (tfhConfig(direction=Direction.next, infer_datetimes=False), 'mon', datetime.date(2018, 8, 6)),
    (tfhConfig(direction=Direction.previous, infer_datetimes=False), 'mon', datetime.date(2018, 7, 30)),
    
    (tfhConfig(infer_datetimes=True), '5p', datetime.datetime(2018, 8, 4, 17, 0)),
    (tfhConfig(infer_datetimes=False), '5p', datetime.time(hour=17, minute=0)),
    # (tfhConfig(infer_datetimes=True), '1p', datetime.datetime(2018, 8, 5, 13, 0)), # TODO tomorrow, since passed today (gh#12)

    # TODO: add tests for 'next/last'
])      
def test_custom_config(now, config, test_input, expected):
    assert timefhuman(test_input, now, config=config) == expected