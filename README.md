# timefhuman

[![Coverage Status](https://coveralls.io/repos/github/alvinwan/timefhuman/badge.svg?branch=master)](https://coveralls.io/github/alvinwan/timefhuman?branch=master)
[![Build Status](https://travis-ci.org/alvinwan/timefhuman.svg?branch=master)](https://travis-ci.org/alvinwan/timefhuman)

Convert human-readable, date-like strings written in natural language to Python objects. Describe specific datetimes or ranges of datetimes.

To start, describe days of the week or times of day in the vernacular.

```
>>> from timefhuman import timefhuman
>>> timefhuman('upcoming Monday noon')
datetime.datetime(2018, 8, 6, 12, 0)
```

Use any human-readable format with a time range, choices of times, or choices of time ranges.

```
>>> timefhuman('7/17 3-4 PM')
(datetime.datetime(2018, 7, 17, 15, 0), datetime.datetime(2018, 7, 17, 16, 0))
>>> timefhuman('7/17 3 p.m. - 4 p.m.')
(datetime.datetime(2018, 7, 17, 15, 30), datetime.datetime(2018, 7, 17, 16, 0))
>>> timefhuman('Monday 3 pm or Tu noon')
[datetime.datetime(2018, 8, 6, 15, 0), datetime.datetime(2018, 8, 7, 12, 0)]
>>> timefhuman('7/17 4 or 5 PM')
[datetime.datetime(2018, 7, 17, 16, 0), datetime.datetime(2018, 7, 17, 17, 0)]
>>> timefhuman('7/17 4-5 or 5-6 PM')
[(datetime.datetime(2018, 7, 17, 16, 0), datetime.datetime(2018, 7, 17, 17, 0)),
 (datetime.datetime(2018, 7, 17, 17, 0), datetime.datetime(2018, 7, 17, 18, 0))]
```

Parse lists of dates and times with more complex relationships.

```
>>> timefhuman('7/17, 7/18, 7/19 at 2')
[datetime.datetime(2018, 7, 17, 2, 0), datetime.datetime(2018, 7, 18, 2, 0), datetime.datetime(2018, 7, 19, 2, 0)]
>>> timefhuman('2 PM on 7/17 or 7/19')
[datetime.datetime(2018, 7, 17, 14, 0), datetime.datetime(2018, 7, 19, 14, 0)]
```

Use the vernacular to describe ranges or days.

```
>>> timefhuman('noon next week')  # coming soon

>>> timefhuman('today or tomorrow noon')  # when run on August 4, 2018
[datetime.datetime(2018, 8, 4, 12, 0), datetime.datetime(2018, 8, 5, 12, 0)]
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

Use a variety of different formats, even with days of the week, months, and times with everyday speech. These are structured formats. [`dateparser`](https://github.com/scrapinghub/dateparser) supports structured formats across languages, customs etc.

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

# Why

[`dateparser`](https://github.com/scrapinghub/dateparser) is the current king of human-readable-date parsing--it supports most common structured dates by trying each one sequentially ([see code](https://github.com/scrapinghub/dateparser/blob/a01a4d2071a8f1d4b368543e5e09cde5eb880799/dateparser/date.py#L220)). However, this isn't optimal for understanding natural language:

```
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
