# timefhuman

[![PyPi Downloads per Month](https://img.shields.io/pypi/dm/timefhuman.svg)](https://pypi.python.org/pypi/timefhuman/)
[![Coverage Status](https://coveralls.io/repos/github/alvinwan/timefhuman/badge.svg?branch=master)](https://coveralls.io/github/alvinwan/timefhuman?branch=master)

Extract datetimes, datetime ranges, and datetime lists from natural language text. Supports Python3+[^1]

[^1]: https://github.com/alvinwan/timefhuman/issues/3

----

## Getting Started

Install with pip using

```python
pip install timefhuman
```

Then, find natural language dates and times in any text.

```python
>>> from timefhuman import timefhuman

>>> timefhuman("How does 5p mon sound? Or maybe 4p tu?")
[datetime.datetime(2018, 8, 6, 17, 0), datetime.datetime(2018, 8, 7, 16, 0)]
```

The text can contain not only datetimes but also ranges of datetimes or lists of datetimes.

```python
>>> timefhuman('3p-4p')  # time range
(datetime.datetime(2018, 7, 17, 15, 0), datetime.datetime(2018, 7, 17, 16, 0))

>>> timefhuman('7/17 4PM to 7/17 5PM')  # range of datetimes
(datetime.datetime(2018, 7, 17, 16, 0), datetime.datetime(2018, 7, 17, 17, 0))

>>> timefhuman('Monday 3 pm or Tu noon')  # list of datetimes
[datetime.datetime(2018, 8, 6, 15, 0), datetime.datetime(2018, 8, 7, 12, 0)]

>>> timefhuman('7/17 4-5 or 5-6 PM')  # list of ranges of datetimes!
[(datetime.datetime(2018, 7, 17, 16, 0), datetime.datetime(2018, 7, 17, 17, 0)),
 (datetime.datetime(2018, 7, 17, 17, 0), datetime.datetime(2018, 7, 17, 18, 0))]
```

Durations are also supported.

```python
>>> timefhuman('30 minutes')  # duration
datetime.timedelta(seconds=1800)

>>> timefhuman('30-40 mins')  # range of durations
(datetime.timedelta(seconds=1800), datetime.timedelta(seconds=2400))

>>> timefhuman('30 or 40m')  # list of durations
[datetime.timedelta(seconds=1800), datetime.timedelta(seconds=2400)]
```

When possible, timefhuman will infer any missing information, using context from other datetimes.

```python
>>> timefhuman('3-4p')  # infer "PM" for "3"
(datetime.datetime(2018, 7, 17, 15, 0), datetime.datetime(2018, 7, 17, 16, 0))

>>> timefhuman('7/17 4 or 5 PM')  # infer "PM" for "4" and infer "7/17" for "5 PM"
[datetime.datetime(2018, 7, 17, 16, 0), datetime.datetime(2018, 7, 17, 17, 0)]

>>> timefhuman('7/17, 7/18, 7/19 at 9')  # infer "9a" for "7/17", "7/18"
[datetime.datetime(2018, 7, 17, 9, 0), datetime.datetime(2018, 7, 18, 9, 0),
 datetime.datetime(2018, 7, 19, 9, 0)]

>>> timefhuman('3p -4p PDT')  # infer timezone "PDT" for "3p"
(datetime.datetime(2018, 8, 4, 15, 0, tzinfo=pytz.timezone('US/Pacific')),
 datetime.datetime(2018, 8, 4, 16, 0, tzinfo=pytz.timezone('US/Pacific')))
```

You can also use natural language descriptions of dates and times.

```python
>>> timefhuman('next Monday')
datetime.datetime(2018, 8, 6, 0, 0)

>>> timefhuman('next next Monday')
datetime.datetime(2018, 8, 13, 0, 0)

>>> timefhuman('last Wednesday of December')
datetime.datetime(2018, 12, 26, 0, 0)

>>> timefhuman('afternoon')
datetime.datetime(2018, 8, 4, 15, 0)
```

See more examples in [`tests/test_e2e.py`](tests/test_e2e.py).

## Advanced Usage

For more configuration options, simply create a `tfhConfig` object.

```python
from timefhuman import tfhConfig
config = tfhConfig()
```

**Return matched text**: You can additionally grab the matched text from the input string. This is useful for modifying the input string, for example.

```python
>>> config = tfhConfig(return_matched_text=True)

>>> timefhuman('We could maybe do 3 PM, if you still have time', config=config)
[('3 PM', datetime.datetime(2018, 8, 4, 15, 0))]
```

**Change 'Now'**: You can configure the default date that timefhuman uses to fill in missing information. This would be useful if you're extracting dates from an email sent a year ago.

```python
>>> config = tfhConfig(now=datetime.datetime(2018, 8, 4, 0, 0))

>>> timefhuman('upcoming Monday noon', config=config)
datetime.datetime(2018, 8, 6, 12, 0)
```

**Don't infer**: Alternatively, say you want to extract only the time from a text -- perhaps it's a festival's schedule. You can disable date inference by setting `infer_datetimes=False`. Instead of always returning a datetime, timefhuman will be able to return time-like objects for only explicitly-written information.

```python
>>> config = tfhConfig(infer_datetimes=False)

>>> timefhuman('3 PM', config=config)
datetime.time(15, 0)

>>> timefhuman('12/18/18', config=config)
datetime.date(2018, 12, 18)
```

Here is the full set of supported configuration options:

```python
@dataclass
class tfhConfig:
    # Default to the next valid datetime or the previous one
    direction: Direction = Direction.next
    
    # Always produce datetime objects. If no date, use the current date. If no time, use midnight.
    infer_datetimes: bool = True
    
    # The 'current' datetime, used if infer_datetimes is True
    now: datetime = datetime.now()    
    
    # Return the matched text from the input string
    return_matched_text: bool = False
    
    # Return a single object instead of a list when there's only one match
    return_single_object: bool = True
```

## Development

Install the development version.

```shell
$ pip install .e .[test]  # for bash
$ pip install -e .\[test\]  # for zsh
```

To run tests and simultaneously generate a coverage report, use the following commands:

```shell
$ py.test --cov
$ coverage html
$ open htmlcov/index.html
```
