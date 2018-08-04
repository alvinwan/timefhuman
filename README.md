# timefhuman

Convert human-readable date-like string to Python datetime object. Use any
human-readable format.

```
>>> timefhuman('7/17 3 PM', now=now)
datetime.datetime(2018, 7, 17, 15, 0)
```

Describe days of the week or times of day in the vernacular **(coming soon)**.

```
>>> timefhuman('upcoming Monday noon')
datetime.datetime(2018, 8, 6, 12, 0)
```

Parse lists of dates and times, written in the vernacular with more complex
relationships. **(coming soon)**

```
>>> timesfhuman('noon anytime next week')
...
>>> timesfhuman('today or tomorrow noon')
...
```

# Usage

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

# Installation

Install from pip.

```
pip install timefhuman
```
