# timefhuman

[![Coverage Status](https://coveralls.io/repos/github/alvinwan/timefhuman/badge.svg?branch=travis)](https://coveralls.io/github/alvinwan/timefhuman?branch=travis)
[![Build Status](https://travis-ci.org/alvinwan/timefhuman.svg?branch=master)](https://travis-ci.org/alvinwan/timefhuman)

Convert human-readable date-like string to Python datetime object. Use any
human-readable format.

```
>>> from timefhuman import timefhuman
>>> timefhuman('7/17 3 PM')
datetime.datetime(2018, 7, 17, 15, 0)
```

Describe days of the week or times of day in the vernacular.

```
>>> timefhuman('upcoming Monday noon')  # when run on August 4, 2018
datetime.datetime(2018, 8, 6, 12, 0)
```

Parse lists of dates and times, written in the vernacular with more complex
relationships. **(coming soon)**

```
>>> from timefhuman import timesfhuman  # notice the s!
>>> timesfhuman('noon anytime next week')
...
>>> timesfhuman('today or tomorrow noon')
...
```

# Installation

Install with pip using

```
pip install timefhuman
```

Optionally, clone the repository and run `python setup.py install`.

# Usage

Use the `now` kwarg to use different default values for the parser.

```
>>> import datetime
>>> now = datetime.datetime(2018, 8, 4, 0, 0)
>>> timefhuman('upcoming Monday noon', now=now)
datetime.datetime(2018, 8, 6, 12, 0)
```

Use a variety of different formats, even with days of the week, months, and
times with everyday speech.

```
>>> from timefhuman import timefhuman
>>> now = datetime.datetime(year=2018, month=7, day=7)
>>> timefhuman('July 17, 2018 at 3p.m.')
datetime.datetime(2018, 7, 17, 15, 0)
>>> timefhuman('July 17, 2018 3 p.m.')
datetime.datetime(2018, 7, 17, 15, 0)
>>> timefhuman('3PM on July 17', now=now)
datetime.datetime(2018, 7, 17, 15, 0)
>>> timefhuman('July 17 at 3')
datetime.datetime(2018, 7, 17, 3, 0)
>>> timefhuman('7/17/18 3:00 p.m.')
datetime.datetime(2018, 7, 17, 15, 0)
```
