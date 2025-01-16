# timefhuman

[![PyPi Downloads per Month](https://img.shields.io/pypi/dm/timefhuman.svg)](https://pypi.python.org/pypi/timefhuman/)
[![Coverage Status](https://coveralls.io/repos/github/alvinwan/timefhuman/badge.svg?branch=master)](https://coveralls.io/github/alvinwan/timefhuman?branch=master)
[![Build Status](https://travis-ci.org/alvinwan/timefhuman.svg?branch=master)](https://travis-ci.org/alvinwan/timefhuman)

Convert human-readable, date-like strings written in natural language to Python objects. Describe specific datetimes, ranges of datetimes, and lists of datetimes. [Supports Python3+](https://github.com/alvinwan/timefhuman/issues/3)

To start, describe days of the week or times of day in the vernacular.

```shell
>>> from timefhuman import timefhuman
>>> timefhuman('Monday noon')
datetime.datetime(2018, 8, 6, 12, 0)
```

Use any human-readable format to describe a datetime, datetime range, list of datetimes, or a duration. You can also use any combination of the above, such as a list of ranges.

```shell
>>> timefhuman('3p-4p')
(datetime.datetime(2018, 7, 17, 15, 0), datetime.datetime(2018, 7, 17, 16, 0))
>>> timefhuman('7/17 4PM to 7/17 5PM')
(datetime.datetime(2018, 7, 17, 16, 0), datetime.datetime(2018, 7, 17, 17, 0))
>>> timefhuman('Monday 3 pm or Tu noon')
[datetime.datetime(2018, 8, 6, 15, 0), datetime.datetime(2018, 8, 7, 12, 0)]
>>> timefhuman('30 minutes')
datetime.timedelta(seconds=1800)
>>> timefhuman('7/17 4-5 or 5-6 PM')  # list of ranges!
[(datetime.datetime(2018, 7, 17, 16, 0), datetime.datetime(2018, 7, 17, 17, 0)),
 (datetime.datetime(2018, 7, 17, 17, 0), datetime.datetime(2018, 7, 17, 18, 0))]
```

`timefhuman` will also infer any missing information, using context from other datetimes.

```shell
>>> timefhuman('3-4p')  # infer "PM" for "3"
(datetime.datetime(2018, 7, 17, 15, 0), datetime.datetime(2018, 7, 17, 16, 0))
>>> timefhuman('7/17 4 or 5 PM')  # infer "PM" for "4" and infer "7/17" for "5 PM"
[datetime.datetime(2018, 7, 17, 16, 0), datetime.datetime(2018, 7, 17, 17, 0)]
>>> timefhuman('7/17, 7/18, 7/19 at 9')  # infer "9a" for "7/17", "7/18"
[datetime.datetime(2018, 7, 17, 9, 0), datetime.datetime(2018, 7, 18, 9, 0), datetime.datetime(2018, 7, 19, 9, 0)]
```

You can even pass in a massive piece of text and `timefhuman` will return just the datetimes.

```shell
>>> timefhuman("How does 5p mon sound? Or maybe 4p tu?")
[datetime.datetime(2018, 8, 6, 17, 0), datetime.datetime(2018, 8, 7, 16, 0)]
```

# Installation

Install with pip using

```shell
pip install timefhuman
```

Optionally, clone the repository and run `python setup.py install`.

# Advanced Usage

Use the `tfhConfig` class to configure `timefhuman`. For example, you can pass a `now` datetime to use different default values.

```shell
>>> from timefhuman import timefhuman, tfhConfig
>>> import datetime
>>> config = tfhConfig(now=datetime.datetime(2018, 8, 4, 0, 0))
>>> timefhuman('upcoming Monday noon', config=config)
datetime.datetime(2018, 8, 6, 12, 0)
```

Alternatively, you can completely disable date inference by setting `infer_datetimes=False`. Instead of always returning a datetime, `timefhuman` will be able to return date-like or time-like objects for only explicitly-written information.

```shell
>>> config = tfhConfig(infer_datetimes=False)
>>> timefhuman('3 PM', config=config)
datetime.time(15, 0)
>>> timefhuman('12/18/18', config=config)
datetime.date(2018, 12, 18)
```

# Why

[`dateparser`](https://github.com/scrapinghub/dateparser) is the current king of human-readable-date parsing--it supports most common structured dates by trying each one sequentially ([see code](https://github.com/scrapinghub/dateparser/blob/a01a4d2071a8f1d4b368543e5e09cde5eb880799/dateparser/date.py#L220)). However, this isn't optimal for understanding natural language:

```shell
>>> import dateparser
>>> dateparser.parse("7/7/18 3 p.m.")  # yay!
datetime.datetime(2018, 7, 7, 15, 0)
>>> dateparser.parse("7/7/18 at 3")  # :(
>>> dateparser.parse("7/17 12 PM")  # yay!
datetime.datetime(2018, 7, 7, 12, 0)
>>> dateparser.parse("7/17/18 noon")  # :(
>>> dateparser.parse("7/18 3-4 p.m.")  # :((((( Parsed July 18 3-4 p.m. as July 3 4 p.m.
datetime.datetime(2018, 7, 3, 16, 0)
```

To remedy this, we can replace "noon" with "12 p.m.", "next Monday" with "7/17/18", "Tu" with "Tuesday" etc. and pass the cleaned string to `dateparser`. However, consider the number of ways we can say "next Monday at 12 p.m.". Ignoring synonyms, we have a number of different grammars to express this:

- 12 p.m. on Monday
- first Monday of August 12 p.m.
- next week Monday noon

This issue compounds when you consider listing noontimes for several different days.

- first half of next week at noon
- 12 p.m. on Monday Tuesday or Wednesday
- early next week midday

The permutations--even the possible *combinations*--are endless. Instead of enumerating each permutation, `timefhuman` extracts tokens: "anytime" modifies the type from 'date' to 'range', "next week" shifts the range by 7 days, "p.m." means the string right before is a time or a time range etc. Each set of tokens is then combined to produce datetimes, datetime ranges, or datetime lists. This then allows `timefhuman` to handle any permutation of these modifiers. Said another way: `timefhuman` aims to parse *unstructured* dates, written in natural language.
