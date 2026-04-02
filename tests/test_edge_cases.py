from timefhuman import timefhuman, tfhConfig, Direction
from timefhuman.renderers import tfhTime
import pytz
import datetime
import timefhuman.main as main


def test_now_changes(now): # gh#53
    """
    The 'now' attribute should not be modified by the function, and if not specified, the
    notion of 'now' should change each time we call the function.
    """
    
    # 'now' should not be modified
    config = tfhConfig(now=now)
    timefhuman('5p', config=config)
    assert config.now == now
    
    # even if not specified, 'now' should not be modified
    config = tfhConfig()
    timefhuman('5p', config=config)
    assert config.now is None
    
    # 'now' should change each time we call the function
    config = tfhConfig()
    assert timefhuman('5p', now=True) != timefhuman('5p', now=True)


def test_timezone(now):  # gh#52
    """
    Support timezones specifications without a specific time.
    1. When a timezone is specified in the original text, honor this first.
    2. Otherwise, if a timezone is specified in `now`, use this.
    """
    now_PST = now.replace(tzinfo=pytz.timezone('US/Pacific'))
    
    # 1. When a timezone is specified in the original text, honor this first.
    assert timefhuman('Wed EST', tfhConfig(now=now_PST)) == [datetime.datetime(2018, 8, 8, 0, 0, tzinfo=pytz.timezone('US/Michigan'))]
    assert timefhuman('Wed 5p EST', tfhConfig(now=now_PST)) == [datetime.datetime(2018, 8, 8, 17, 0, tzinfo=pytz.timezone('US/Michigan'))]
    assert timefhuman('5p EST', tfhConfig(now=now_PST)) == [datetime.datetime(2018, 8, 4, 17, 0, tzinfo=pytz.timezone('US/Michigan'))]
    assert timefhuman('5p EST', tfhConfig(now=now_PST, direction=Direction.previous)) == [datetime.datetime(2018, 8, 3, 17, 0, tzinfo=pytz.timezone('US/Michigan'))]
    assert timefhuman('5p EST', tfhConfig(now=now_PST, direction=Direction.this)) == [datetime.datetime(2018, 8, 4, 17, 0, tzinfo=pytz.timezone('US/Michigan'))]
    assert timefhuman('9a EST', tfhConfig(now=now_PST, direction=Direction.next)) == [datetime.datetime(2018, 8, 5, 9, 0, tzinfo=pytz.timezone('US/Michigan'))]
    assert timefhuman('9a EST', tfhConfig(now=now_PST, infer_datetimes=False)) == [datetime.time(9, 0, tzinfo=pytz.timezone('US/Michigan'))]
    # 2. Otherwise, if a timezone is specified in `now`, use this.
    assert timefhuman('Wed', tfhConfig(now=now_PST)) == [datetime.datetime(2018, 8, 8, 0, 0, tzinfo=pytz.timezone('US/Pacific'))]
    # 3. If no timezone is specified, do not attach one
    assert timefhuman('Wed', tfhConfig(now=now)) == [datetime.datetime(2018, 8, 8, 0, 0)]
    

def test_unk_correctness():
    tree = timefhuman('how does 5p sound?', raw=True)
    assert len(tree.children) > 1, "Should have parsed into many UNK tokens"


def test_lalr_fallback_without_fastpath(now, monkeypatch):
    config = tfhConfig(now=now, infer_datetimes=False)
    infer_config = tfhConfig(now=now)

    monkeypatch.setattr(main, 'parse_fast', lambda *args, **kwargs: None)
    monkeypatch.setattr(main, 'extract_fast', lambda *args, **kwargs: None)

    assert timefhuman('last Wednesday of December', config=config) == [datetime.date(2018, 12, 26)]
    assert timefhuman('next Monday', config=config) == [datetime.date(2018, 8, 6)]
    assert timefhuman('next next Monday', config=config) == [datetime.date(2018, 8, 13)]
    assert timefhuman('1/1/95', config=config) == [datetime.date(1995, 1, 1)]
    assert timefhuman('7/2018', config=config) == [datetime.date(2018, 7, 1)]
    assert timefhuman('Sunday 7/7/2019', config=config) == [datetime.date(2019, 7, 7)]
    assert timefhuman('2022-12-27T09:15:01.002', config=infer_config) == [datetime.datetime(2022, 12, 27, 9, 15, 1, 2)]
    assert timefhuman('July 17, 2018 at 3p.m.', config=infer_config) == [datetime.datetime(2018, 7, 17, 15, 0)]
    assert timefhuman('2 hours and 30 minutes', config=config) == [datetime.timedelta(hours=2, minutes=30)]
    assert timefhuman('30-40 mins', config=config) == [(datetime.timedelta(minutes=30), datetime.timedelta(minutes=40))]
    assert timefhuman('1 or 2 days', config=config) == [[datetime.timedelta(days=1), datetime.timedelta(days=2)]]
    assert timefhuman('3-4p', config=config) == [(datetime.time(15, 0), datetime.time(16, 0))]
    assert timefhuman('July 17-18', config=config) == [(datetime.date(2018, 7, 17), datetime.date(2018, 7, 18))]
    assert timefhuman('July 4th or 5th at 3PM', config=infer_config) == [[
        datetime.datetime(2018, 7, 4, 15, 0),
        datetime.datetime(2018, 7, 5, 15, 0),
    ]]
    assert timefhuman('7/17 4-5 PM or 5-6 PM today', config=infer_config) == [[
        (datetime.datetime(2018, 7, 17, 16, 0), datetime.datetime(2018, 7, 17, 17, 0)),
        (datetime.datetime(2018, 8, 4, 17, 0), datetime.datetime(2018, 8, 4, 18, 0)),
    ]]


def test_time_renderer_does_not_mutate_hour():
    renderer = tfhTime(hour=5, meridiem=tfhTime.Meridiem.PM)
    assert renderer.to_object() == datetime.time(17, 0)
    assert renderer.hour == 5
    assert "tz=" not in repr(renderer)


def test_extraction_avoids_exact_candidate_fallback(now, monkeypatch):
    calls = 0
    real_parse_exact = main._parse_exact

    def wrapped_parse_exact(*args, **kwargs):
        nonlocal calls
        calls += 1
        return real_parse_exact(*args, **kwargs)

    monkeypatch.setattr(main, "_parse_exact", wrapped_parse_exact)

    result = timefhuman(
        "How does 5p mon sound? Or maybe 4p tu?",
        tfhConfig(now=now, return_matched_text=True),
    )

    assert result == [
        ("5p mon", (9, 15), datetime.datetime(2018, 8, 6, 17, 0)),
        ("4p tu", (32, 37), datetime.datetime(2018, 8, 7, 16, 0)),
    ]
    assert calls == 1
