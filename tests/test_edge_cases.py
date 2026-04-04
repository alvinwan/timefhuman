from timefhuman import timefhuman, tfhConfig, Direction
from timefhuman.renderers import tfhRange, tfhTimedelta, tfhTime
import pytz
import datetime
import timefhuman.main as main
import timefhuman.utils as utils
from timefhuman.extraction import prefer_extraction


def localized_datetime(tz_name, *parts):
    return pytz.timezone(tz_name).localize(datetime.datetime(*parts))


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
    now_PST = localized_datetime('US/Pacific', 2018, 8, 4, 14, 0)
    
    # 1. When a timezone is specified in the original text, honor this first.
    assert timefhuman('Wed EST', tfhConfig(now=now_PST)) == [localized_datetime('US/Michigan', 2018, 8, 8, 0, 0)]
    assert timefhuman('Wed 5p EST', tfhConfig(now=now_PST)) == [localized_datetime('US/Michigan', 2018, 8, 8, 17, 0)]
    assert timefhuman('5p EST', tfhConfig(now=now_PST)) == [localized_datetime('US/Michigan', 2018, 8, 4, 17, 0)]
    assert timefhuman('5p EST', tfhConfig(now=now_PST, direction=Direction.previous)) == [localized_datetime('US/Michigan', 2018, 8, 3, 17, 0)]
    assert timefhuman('5p EST', tfhConfig(now=now_PST, direction=Direction.this)) == [localized_datetime('US/Michigan', 2018, 8, 4, 17, 0)]
    assert timefhuman('9a EST', tfhConfig(now=now_PST, direction=Direction.next)) == [localized_datetime('US/Michigan', 2018, 8, 5, 9, 0)]
    assert timefhuman('9a EST', tfhConfig(now=now_PST, infer_datetimes=False)) == [datetime.time(9, 0, tzinfo=pytz.timezone('US/Michigan'))]
    # 2. Otherwise, if a timezone is specified in `now`, use this.
    assert timefhuman('Wed', tfhConfig(now=now_PST)) == [localized_datetime('US/Pacific', 2018, 8, 8, 0, 0)]
    # 3. If no timezone is specified, do not attach one
    assert timefhuman('Wed', tfhConfig(now=now)) == [datetime.datetime(2018, 8, 8, 0, 0)]


def test_timezone_datetimes_use_localized_offsets():
    config = tfhConfig(now=localized_datetime('UTC', 2025, 11, 10, 12, 0))
    result = timefhuman("next friday 2 pm CET", config=config)[0]
    assert result.tzname() == "CET"
    assert result.utcoffset() == datetime.timedelta(hours=1)


def test_generate_timezone_mapping_uses_explicit_locale(monkeypatch):
    utils.generate_timezone_mapping.cache_clear()
    real_get_timezone_name = utils.get_timezone_name
    locales = []

    def wrapped_get_timezone_name(timezone, locale=None, **kwargs):
        locales.append(locale)
        if locale is None:
            raise TypeError("Unexpected value for identifier: None")
        return real_get_timezone_name(timezone, locale=locale, **kwargs)

    monkeypatch.setattr(utils, "get_timezone_name", wrapped_get_timezone_name)

    mapping = utils.generate_timezone_mapping()

    assert "pacific time" in mapping
    assert locales
    assert set(locales) == {"en_US"}
    utils.generate_timezone_mapping.cache_clear()
    

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
    assert timefhuman('08.07.2013', config=config) == [datetime.date(2013, 8, 7)]
    assert timefhuman('31/08/2012 to 30/08/2013', config=config) == [(
        datetime.date(2012, 8, 31),
        datetime.date(2013, 8, 30),
    )]
    assert timefhuman('7/2018', config=config) == [datetime.date(2018, 7, 1)]
    assert timefhuman('Sunday 7/7/2019', config=config) == [datetime.date(2019, 7, 7)]
    assert timefhuman('2022-12-27T09:15:01.002', config=infer_config) == [datetime.datetime(2022, 12, 27, 9, 15, 1, 2)]
    assert timefhuman('July 17, 2018 at 3p.m.', config=infer_config) == [datetime.datetime(2018, 7, 17, 15, 0)]
    assert timefhuman('2 hours and 30 minutes', config=config) == [datetime.timedelta(hours=2, minutes=30)]
    assert timefhuman('for 3 days', config=config) == [datetime.timedelta(days=3)]
    assert timefhuman('past 40 minutes', config=config) == [datetime.timedelta(minutes=-40)]
    assert timefhuman('for the past 40 minutes', config=config) == [datetime.timedelta(minutes=-40)]
    assert timefhuman('30-40 mins', config=config) == [(datetime.timedelta(minutes=30), datetime.timedelta(minutes=40))]
    assert timefhuman('1 or 2 days', config=config) == [[datetime.timedelta(days=1), datetime.timedelta(days=2)]]
    assert timefhuman('3-4p', config=config) == [(datetime.time(15, 0), datetime.time(16, 0))]
    assert timefhuman('July 17-18', config=config) == [(datetime.date(2018, 7, 17), datetime.date(2018, 7, 18))]
    assert timefhuman('July 4th or 5th at 3PM', config=infer_config) == [[
        datetime.datetime(2018, 7, 4, 15, 0),
        datetime.datetime(2018, 7, 5, 15, 0),
    ]]
    assert timefhuman('90p', config=config) == []
    assert timefhuman('4906/0', config=config) == []
    assert timefhuman('7/17 4-5 PM or 5-6 PM today', config=infer_config) == [[
        (datetime.datetime(2018, 7, 17, 16, 0), datetime.datetime(2018, 7, 17, 17, 0)),
        (datetime.datetime(2018, 8, 4, 17, 0), datetime.datetime(2018, 8, 4, 18, 0)),
    ]]


def test_time_renderer_does_not_mutate_hour():
    renderer = tfhTime(hour=5, meridiem=tfhTime.Meridiem.PM)
    assert renderer.to_object() == datetime.time(17, 0)
    assert renderer.hour == 5
    assert "tz=" not in repr(renderer)


def test_extraction_avoids_lalr_candidate_fallback(now, monkeypatch):
    calls = 0
    real_parse_lalr = main._parse_lalr

    def wrapped_parse_lalr(*args, **kwargs):
        nonlocal calls
        calls += 1
        return real_parse_lalr(*args, **kwargs)

    monkeypatch.setattr(main, "_parse_lalr", wrapped_parse_lalr)

    result = timefhuman(
        "How does 5p mon sound? Or maybe 4p tu?",
        tfhConfig(now=now, return_matched_text=True),
    )

    assert result == [
        ("5p mon", (9, 15), datetime.datetime(2018, 8, 6, 17, 0)),
        ("4p tu", (32, 37), datetime.datetime(2018, 8, 7, 16, 0)),
    ]
    assert calls == 0


def test_prefixed_or_punctuated_text_skips_lalr_fallback(now, monkeypatch):
    calls = 0
    real_parse_lalr = main._parse_lalr

    def wrapped_parse_lalr(*args, **kwargs):
        nonlocal calls
        calls += 1
        return real_parse_lalr(*args, **kwargs)

    monkeypatch.setattr(main, "_parse_lalr", wrapped_parse_lalr)

    prefixed = timefhuman("e 6:50PM", tfhConfig(now=now, return_matched_text=True))
    punctuated = timefhuman("September 30, 2019.", tfhConfig(now=now, return_matched_text=True))

    assert prefixed == [
        ("6:50PM", (2, 8), datetime.datetime(2018, 8, 4, 18, 50)),
    ]
    assert punctuated == [
        ("September 30, 2019", (0, 18), datetime.datetime(2019, 9, 30, 0, 0)),
    ]
    assert calls == 0


def test_large_multiline_documents_prefer_extraction(now, monkeypatch):
    doc = "1/1/95 header text\n" + ("plain filler line without dates\n" * 1100) + "How does 5p mon sound?\n"
    calls = 0
    real_parse_fast = main.parse_fast

    def wrapped_parse_fast(text, *args, **kwargs):
        nonlocal calls
        if text == doc:
            calls += 1
        return real_parse_fast(text, *args, **kwargs)

    monkeypatch.setattr(main, "parse_fast", wrapped_parse_fast)

    assert prefer_extraction(doc) is True
    assert timefhuman(doc, tfhConfig(now=now, return_matched_text=True)) == [
        ("1/1/95", (0, 6), datetime.datetime(1995, 1, 1, 0, 0)),
        ("5p mon", (doc.index("5p mon"), doc.index("5p mon") + 6), datetime.datetime(2018, 8, 6, 17, 0)),
    ]
    assert calls == 0


def test_timedelta_range_does_not_assume_date(now):
    renderer = tfhRange([
        tfhTimedelta(days=4, unit="days"),
        tfhTimedelta(seconds=10 * 60 * 60, unit="hours"),
    ])
    assert renderer.to_object(tfhConfig(now=now)) == (
        now + datetime.timedelta(days=4),
        now + datetime.timedelta(hours=10),
    )
