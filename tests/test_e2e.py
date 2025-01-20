from timefhuman import timefhuman
import datetime
import pytest
from timefhuman.main import Direction, tfhConfig
import pytz


@pytest.fixture
def now():
    return datetime.datetime(year=2018, month=8, day=4, hour=14)


@pytest.mark.parametrize("test_input, expected", [
    # time only
    ('5p', datetime.datetime(2018, 8, 4, 17, 0)),
    ('3p EST', datetime.datetime(2018, 8, 4, 15, 0, tzinfo=pytz.timezone('US/Michigan'))),  # fixes gh#6
    
    # date only
    ('July 2019', datetime.datetime(2019, 7, 1, 0, 0)),
    ('7-17-18', datetime.datetime(2018, 7, 17, 0, 0)),
    ('2018-7-17', datetime.datetime(2018, 7, 17, 0, 0)),  # support YMD
    ('7/2018', datetime.datetime(2018, 7, 1, 0, 0)),
    
    # datetimes
    ('July 17, 2018 at 3p.m.', datetime.datetime(2018, 7, 17, 15, 0)),
    ('July 17, 2018 3 p.m.', datetime.datetime(2018, 7, 17, 15, 0)),
    ('3PM on July 17', datetime.datetime(2018, 7, 17, 15, 0)),
    ('July 17 at 3', datetime.datetime(2018, 7, 17, 3, 0)),
    ('7/17/18 3:00 p.m.', datetime.datetime(2018, 7, 17, 15, 0)),
    ('3 p.m. today', datetime.datetime(2018, 8, 4, 15, 0)),
    ('Tomorrow 3p', datetime.datetime(2018, 8, 5, 15, 0)), # gh#24
    ('3p tomorrow', datetime.datetime(2018, 8, 5, 15, 0)),
    ('July 3rd', datetime.datetime(2018, 7, 3, 0, 0)),
    
    # date-only ranges
    ('7/17-7/18', (datetime.datetime(2018, 7, 17), datetime.datetime(2018, 7, 18))),
    ('July 17-18', (datetime.datetime(2018, 7, 17), datetime.datetime(2018, 7, 18))), # distribute month
    
    # time-only ranges
    ('3p -4p', (datetime.datetime(2018, 8, 4, 15, 0), datetime.datetime(2018, 8, 4, 16, 0))),
    ('3p -4p PDT', (datetime.datetime(2018, 8, 4, 15, 0, tzinfo=pytz.timezone('US/Pacific')), datetime.datetime(2018, 8, 4, 16, 0, tzinfo=pytz.timezone('US/Pacific')))),
    ('6:00 pm - 12:00 am', (datetime.datetime(2018, 8, 4, 18, 0), datetime.datetime(2018, 8, 5, 0, 0))), # gh#8
    ('8/4 6:00 pm - 8/4 12:00 am', (datetime.datetime(2018, 8, 4, 18, 0), datetime.datetime(2018, 8, 4, 0, 0))), # force date, do not infer
    
    # date and time ranges
    ('7/17 3 pm- 7/19 2 pm', (datetime.datetime(2018, 7, 17, 15, 0), datetime.datetime(2018, 7, 19, 14, 0))),
    ('Jun 28 5:00 PM - Aug 02 7:00 PM', (datetime.datetime(2018, 6, 28, 17, 0), datetime.datetime(2018, 8, 2, 19, 0))),
    ('Jun 28 2019 5:00 PM - Aug 02 2019 7:00 PM', (datetime.datetime(2019, 6, 28, 17, 0), datetime.datetime(2019, 8, 2, 19, 0))),
    ('6/28 5:00 PM - 8/02 7:00 PM', (datetime.datetime(2018, 6, 28, 17, 0), datetime.datetime(2018, 8, 2, 19, 0))),
    ('6/28/2019 5:00 PM - 8/02/2019 7:00 PM', (datetime.datetime(2019, 6, 28, 17, 0), datetime.datetime(2019, 8, 2, 19, 0))),
    
    # choices
    ('July 4th or 5th at 3PM', [datetime.datetime(2018, 7, 4, 15, 0), datetime.datetime(2018, 7, 5, 15, 0)]), # distribute month and time
    ('tomorrow noon,Wed 3 p.m.,Fri 11 AM', [datetime.datetime(2018, 8, 5, 12, 0), datetime.datetime(2018, 8, 8, 15, 0), datetime.datetime(2018, 8, 10, 11, 0)]), # distribute meridiem
    # ('2, 3, or 4p tmw', [datetime.datetime(2018, 8, 4, 2, 0), datetime.datetime(2018, 8, 4, 3, 0), datetime.datetime(2018, 8, 4, 4, 0)]), # multiple ambiguous tokens #TODO (check month?)
    
    # choices of ranges
    ('7/17 4-5 PM or 5-6 PM today', [
        (datetime.datetime(2018, 7, 17, 16, 0), datetime.datetime(2018, 7, 17, 17, 0)),
        (datetime.datetime(2018, 8, 4, 17, 0), datetime.datetime(2018, 8, 4, 18, 0))
    ]),
    
    # readme
    ('Monday noon', datetime.datetime(2018, 8, 6, 12, 0)),
    ('3-4p', (datetime.datetime(2018, 8, 4, 15, 0), datetime.datetime(2018, 8, 4, 16, 0))), # infer meridiem
    ('Monday 3 pm or Tu noon', [datetime.datetime(2018, 8, 6, 15, 0), datetime.datetime(2018, 8, 7, 12, 0)]),
    ('7/17 4 or 5 PM', [datetime.datetime(2018, 7, 17, 16, 0), datetime.datetime(2018, 7, 17, 17, 0)]), # distribute meridiem / date
    ('7/17 4-5 or 5-6 PM', [
        (datetime.datetime(2018, 7, 17, 16, 0), datetime.datetime(2018, 7, 17, 17, 0)),
        (datetime.datetime(2018, 7, 17, 17, 0), datetime.datetime(2018, 7, 17, 18, 0))
    ]),
    
    ('7/17, 7/18, 7/19 at 2', [datetime.datetime(2018, 7, 17, 2, 0), datetime.datetime(2018, 7, 18, 2, 0), datetime.datetime(2018, 7, 19, 2, 0)]), # distribute dates
    ('2 PM on 7/17 or 7/19', [datetime.datetime(2018, 7, 17, 14, 0), datetime.datetime(2018, 7, 19, 14, 0)]), # distribute time across dates
    ('2022-12-27T09:15:01.002', datetime.datetime(2022, 12, 27, 9, 15, 1, 2)),  # fixes gh#31
])
def test_default(now, test_input, expected):
    """Default behavior should be to infer datetimes and times."""
    actual = timefhuman(test_input, config=tfhConfig(now=now))
    assert actual == expected, f"Expected: {expected}\nGot: {actual}"


@pytest.mark.parametrize("test_input, expected", [
    # time only
    ('5p', datetime.time(hour=17, minute=0)),
    ("3 o'clock pm", datetime.time(hour=15, minute=0)), # fixes gh#12
    ('5p Eastern Time', datetime.time(hour=17, minute=0, tzinfo=pytz.timezone('US/Michigan'))),  # fixes gh#6
    
    # date only
    ('July 2019', datetime.date(2019, 7, 1)),
    ('Sunday 7/7/2019', datetime.date(2019, 7, 7)),  # fixes gh#27
    
    # date-only ranges
    ('7/17-7/18', (datetime.date(2018, 7, 17), datetime.date(2018, 7, 18))),
    ('July 17-18', (datetime.date(2018, 7, 17), datetime.date(2018, 7, 18))), # distribute month
    
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
    ('1.5h', datetime.timedelta(hours=1, minutes=30)),
    ('in five minutes', datetime.timedelta(minutes=5)), # gh#25
    ('awk', []),  # should *not become 'a week'
    ('a wk', datetime.timedelta(days=7)),
    ('thirty two hours', datetime.timedelta(hours=32)),
    
    # duration ranges and lists
    ('30-40 mins', (datetime.timedelta(minutes=30), datetime.timedelta(minutes=40))),
    ('1 or 2 days', [datetime.timedelta(days=1), datetime.timedelta(days=2)]),

    # TODO: support "quarter to 3"
    # TODO: support "one and a half hours"
    
    # TODO ('noon next week') <- should be a list of options
    # TODO: support recurrences, like "5pm on thursdays" (see gh#33)
    
    # TODO: support natural language date ranges e.g., this week, next weekend, any weekday gh#18
    # TODO: support natural language time ranges e.g., afternoon, morning, evening, tonight, today night gh#30
    
    # TODO: christmas? new years? eve?
    # TODO: support 'this past July' (e.g., reduce to 'this')
    # TODO: support 'last week of dec'
    
    # support for date and month modifiers
    ('next Monday', datetime.date(2018, 8, 6)),
    ('next next Monday', datetime.date(2018, 8, 13)),
    ('last Monday', datetime.date(2018, 7, 30)),
    ('next July', datetime.date(2019, 7, 1)),
    ('last July', datetime.date(2017, 7, 1)),
    ('last Wednesday of December', datetime.date(2018, 12, 26)), # gh#4
    
    # support for vernacular datetimes
    ('afternoon', datetime.time(hour=12, minute=0)),
    ('morning', datetime.time(hour=6, minute=0)),
    ('evening', datetime.time(hour=18, minute=0)),
    ('night', datetime.time(hour=20, minute=0)),
    ('today night', datetime.datetime(2018, 8, 4, 20, 0)),
    ('tonight', datetime.datetime(2018, 8, 4, 20, 0)), # gh#30
])
def test_no_inference(now, test_input, expected):
    """Return exactly the date or time, without inferring the other."""
    config = tfhConfig(infer_datetimes=False, now=now)
    assert timefhuman(test_input, config=config) == expected


@pytest.mark.parametrize("config, test_input, expected", [
    (tfhConfig(direction=Direction.next, infer_datetimes=False), 'mon', datetime.date(2018, 8, 6)),
    (tfhConfig(direction=Direction.previous, infer_datetimes=False), 'mon', datetime.date(2018, 7, 30)),
    
    (tfhConfig(infer_datetimes=True), '5p', datetime.datetime(2018, 8, 4, 17, 0)),
    (tfhConfig(infer_datetimes=False), '5p', datetime.time(hour=17, minute=0)),
    (tfhConfig(infer_datetimes=True), '1p', datetime.datetime(2018, 8, 5, 13, 0)), # gh#12
])
def test_custom_config(now, config, test_input, expected):
    config.now = now
    assert timefhuman(test_input, config=config) == expected


@pytest.mark.parametrize("test_input, expected", [
    ('September 30, 2019.', [('September 30, 2019', datetime.datetime(2019, 9, 30, 0, 0))]), # gh#26
    ('How does 5p mon sound? Or maybe 4p tu?', [('5p mon', datetime.datetime(2018, 8, 6, 17, 0)), ('4p tu', datetime.datetime(2018, 8, 7, 16, 0))]),
    ('There are 3 ways to do it', []),  # '3' should remain ambiguous and then be ignored
    # TODO: get matched characters gh#9
])
def test_with_random_text(now, test_input, expected):
    assert timefhuman(test_input, tfhConfig(now=now, return_matched_text=True)) == expected