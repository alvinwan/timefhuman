# timefhuman

[![PyPi Downloads per Month](https://img.shields.io/pypi/dm/timefhuman.svg)](https://pypi.python.org/pypi/timefhuman/)
[![Coverage Status](https://coveralls.io/repos/github/alvinwan/timefhuman/badge.svg?branch=master)](https://coveralls.io/github/alvinwan/timefhuman?branch=master)

Extract datetimes, datetime ranges, and datetime lists from natural language text. Supports Python3+[^1]

[^1]: https://github.com/alvinwan/timefhuman/issues/3

----

## Getting Started

Use any text that contains natural language descriptions of dates and times.

```python
>>> from timefhuman import timefhuman

>>> timefhuman("How does 5p mon sound? Or maybe 4p tu?")
[datetime.datetime(2018, 8, 6, 17, 0), datetime.datetime(2018, 8, 7, 16, 0)]
```

The text can contain not only datetimes but also ranges of datetimes, lists of datetimes, or lists of ranges of datetimes! 

```python
>>> timefhuman('3p-4p')  # time range
(datetime.datetime(2018, 7, 17, 15, 0), datetime.datetime(2018, 7, 17, 16, 0))

>>> timefhuman('7/17 4PM to 7/17 5PM')  # range of datetimes
(datetime.datetime(2018, 7, 17, 16, 0), datetime.datetime(2018, 7, 17, 17, 0))

>>> timefhuman('Monday 3 pm or Tu noon')  # list of datetimes
[datetime.datetime(2018, 8, 6, 15, 0), datetime.datetime(2018, 8, 7, 12, 0)]

>>> timefhuman('7/17 4-5 or 5-6 PM')  # list of ranges of datetimes
[(datetime.datetime(2018, 7, 17, 16, 0), datetime.datetime(2018, 7, 17, 17, 0)),
 (datetime.datetime(2018, 7, 17, 17, 0), datetime.datetime(2018, 7, 17, 18, 0))]
```

You can also parse durations.

```python
>>> timefhuman('30 minutes')  # duration
datetime.timedelta(seconds=1800)

>>> timefhuman('30-40 mins')  # range of durations
(datetime.timedelta(seconds=1800), datetime.timedelta(seconds=2400))

>>> timefhuman('30 or 40m')  # list of durations
[datetime.timedelta(seconds=1800), datetime.timedelta(seconds=2400)]
```

To support natural language, `timefhuman` will infer any missing information, using context from other datetimes.

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

See more examples in [`tests/test_e2e.py`](tests/test_e2e.py).

## Installation

Install with pip using

```python
pip install timefhuman
```

Optionally, clone the repository and run `pip install -e .`.

## Advanced Usage

Use the `tfhConfig` class to configure `timefhuman`. For example, you can pass a `now` datetime to use different default values.

```python
>>> from timefhuman import timefhuman, tfhConfig
>>> import datetime
>>> config = tfhConfig(now=datetime.datetime(2018, 8, 4, 0, 0))

>>> timefhuman('upcoming Monday noon', config=config)
datetime.datetime(2018, 8, 6, 12, 0)
```

Alternatively, you can completely disable date inference by setting `infer_datetimes=False`. Instead of always returning a datetime, `timefhuman` will be able to return date-like or time-like objects for only explicitly-written information.

```python
>>> config = tfhConfig(infer_datetimes=False)

>>> timefhuman('3 PM', config=config)
datetime.time(15, 0)

>>> timefhuman('12/18/18', config=config)
datetime.date(2018, 12, 18)
```

Here is the full set of supported configuration options:

```python
class tfhConfig:
    direction: Direction = Direction.next  # next/previous/none
    infer_datetimes: bool = True  # infer missing information using current datetime
    now: datetime = datetime.now()  # current datetime, only used if infer_datetimes is True
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
