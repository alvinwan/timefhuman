# timefhuman

[![Coverage Status](https://coveralls.io/repos/github/alvinwan/timefhuman/badge.svg?branch=travis)](https://coveralls.io/github/alvinwan/timefhuman?branch=travis)
[![Build Status](https://travis-ci.org/alvinwan/timefhuman.svg?branch=master)](https://travis-ci.org/alvinwan/timefhuman)

Convert human-readable, date-like strings written in natural language to Python objects. Describe days of the week or times of day in the vernacular.

```
>>> timefhuman('upcoming Monday noon')  # when run on August 4, 2018
datetime.datetime(2018, 8, 6, 12, 0)
```

Use any human-readable format with a time range, choices of times, or choices of time ranges. **(coming soon)**

```
>>> from timefhuman import timefhuman
>>> timefhuman('7/17 3-4 PM')

>>> timefhuman('7/17 3 p.m. - 4 p.m.')

>>> timefhuman('7/17 3, 4, or 5 PM')

>>> timefhuman('7/17 3-4, 4-5, or 5-6 PM')
```

Parse lists of dates and times with more complex relationships. **(coming soon)**

```
>>> timefhuman('7/17, 7/18, 7/19 at 2')

>>> timefhuman('7/17 to 7/19 at 2')
```

Use the vernacular to describe ranges or days. **(coming soon)**

```
>>> timefhuman('noon next week')

>>> timefhuman('today or tomorrow noon')

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

To remedy this, we can replace "noon" with "12 p.m.", "next Monday" with "7/17/18", "Tu" with "Tuesday" etc. and pass the cleaned string to `dateparser`. However, consider the number of ways we can say "next Monday". Put aside synonyms for "next" for now; there are numerous grammatical structures, too many to list explicitly:

- next Monday
- Monday of next week
- first Monday of August

This issue compounds when you consider a list of possible dates

- anytime next week at noon
- afternoon the next few days
- any Friday this month

Listing all the possible permutations is not sustainable. Instead, `timefhuman` leverages lexical structure and assigns each part of the phrase a different modification: "anytime" modifies the type from 'date' to 'range', "next week" shifts the range by 7 days, "p.m." means the string right before is a time or a time range etc. This then allows `timefhuman` to handle any permutation of these modifiers. Said another way: `timefhuman` aims to parse *unstructured* dates.
