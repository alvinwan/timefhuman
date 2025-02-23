from timefhuman import timefhuman, tfhConfig, Direction
import pytz
import datetime


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
