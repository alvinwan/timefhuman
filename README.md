# timefhuman
Convert human-readable date-like string to Python datetime object.

```
>>> now = datetime.datetime(year=2018, month=7, day=7)
>>> timefhuman('7-17 3 PM', now=now)
datetime.datetime(2018, 7, 17, 15, 0)
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
