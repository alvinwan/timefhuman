"""
timefhuman
===
Convert human-readable date-like string to Python datetime object.

1. Tokenize string
2. Parse possible synctatic categories: "day", "time", "time range" etc.
3. Build parse tree.
4. Use grammar to resolve lexical ambiguities.
5. Impute with default values. Output extracted datetime and/or ranges.

@author: Alvin Wan
@site: alvinwan.com
"""


__all__ = ('timefhuman',)

from lark import Lark, Transformer
from datetime import datetime, date, time, timedelta
from typing import Optional

grammar = """
%import common.WS
%import common.INT
%ignore WS

// ----------------------
// TERMINAL DEFINITIONS
// ----------------------

// Month names as a regex token, case-insensitive
MONTHNAME: /(?i)(january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|jun|jul|aug|sep|oct|nov|dec)/

// For weekdays, also as a single regex token, case-insensitive
WEEKDAY: /(?i)(mon|tue|wed|thu|fri|sat|sun)/

// Meridiem token (am/pm, with optional dots)
MERIDIEM: /(?i)([ap](\.?m\.?)?)/

// ----------------------
// PARSER RULES
// ----------------------
start: expression

expression: range 
          | list 
          | single

range: single ("to" | "-") single

list: single ("," single)+ 
    | single ("or" single)+
    | range ("or" range)+

single: datetime 
       | date 
       | time

datetime: date ("at" time)?
        | date time
        | time "on" date

date: month "/" day ("/" year)?
    | month "-" day ("-" year)?
    | "tomorrow"i 
    | "today"i 
    | weekday
    | monthname day ((",")? year)? // `day` here is read as `year` if invalid day

time: hour ":" minute meridiem? 
    | hour meridiem?
    | "noon"i

weekday: WEEKDAY
monthname: MONTHNAME

day: INT
month: INT
year: INT

hour: INT
minute: INT
meridiem: MERIDIEM
"""


class tfhTime(time):
    meridiem: Optional[str] = None
    
    def __new__(cls, *args, meridiem=None, **kwargs):
        result = time.__new__(cls, *args, **kwargs)
        result.meridiem = meridiem
        return result


class tfhDatetime(datetime):
    _date: Optional[date] = None
    _time: Optional[time] = None
    
    @classmethod
    def combine(cls, date, time):
        result = datetime.combine(date, time)
        result = cls(result.year, result.month, result.day, result.hour, result.minute)
        result._date = date
        result._time = time
        return result
    

def timefhuman(string, now=None, raw=None):
    parser = Lark(grammar, start="start")
    tree = parser.parse(string)

    transformer = TimeFHumanTransformer(now=now)
    result = transformer.transform(tree)

    if raw:
        return tree
    return result


def infer(datetimes):
    # distribute first datetime's date to all datetimes
    if isinstance(datetimes[0], datetime) and datetimes[0]._date:
        for i, dt in enumerate(datetimes[1:], start=1):
            if isinstance(dt, time):
                datetimes[i] = tfhDatetime.combine(datetimes[0]._date, dt)

    # distribute last time's meridiem to all datetimes
    if (
        isinstance(datetimes[-1], datetime) and (meridiem := datetimes[-1]._time.meridiem)
    ) or (
        isinstance(datetimes[-1], time) and (meridiem := datetimes[-1].meridiem)
    ):
        for i, dt in enumerate(datetimes[:-1]):
            # TODO: force all datetimes to have _date and _time
            if meridiem.startswith("a"):
                break
            if isinstance(dt, datetime) and dt._time and not dt._time.meridiem:
                dt._time.meridiem = meridiem
                datetimes[i] = dt + timedelta(hours=12)
            elif isinstance(dt, time) and not dt.meridiem:
                dt.meridiem = meridiem
                datetimes[i] = tfhTime(dt.hour + 12, dt.minute, meridiem=meridiem)
                
    return datetimes


class TimeFHumanTransformer(Transformer):
    def __init__(self, now=None):
        self.now = now

    def start(self, children):
        """Strip the 'start' rule and return child(ren) directly."""
        if len(children) == 1:
            return children[0]
        return children

    def expression(self, children):
        """The top-level expression could be a range, list, or single."""
        if len(children) == 1:
            return children[0]
        return children

    def single(self, children):
        """A single object can be a datetime, a date, or a time."""
        return children[0]

    def range(self, children):
        """Handles expressions like '7/17 3 PM - 7/18 4 PM'."""
        assert len(children) == 2
        return tuple(infer(children))

    def list(self, children):
        """Handles comma/or lists like '7/17, 7/18, 7/19' or '7/17 or 7/18'."""
        return list(infer(children))

    def datetime(self, children):
        """
        A 'datetime' node can contain:
          - date + time
          - date + 'at' + time
          - just date
          - just time
        We combine them here into a single datetime if both parts are present.
        """
        date_part = next((c for c in children if isinstance(c, date)), None)
        time_part = next((c for c in children if isinstance(c, time)), None)

        if date_part and time_part:
            result = tfhDatetime.combine(date_part, time_part)
            result._date = date_part
            result._time = time_part
            return result
        elif date_part:
            return date_part
        elif time_part:
            return time_part
        return None

    def date(self, children):
        """
        A 'date' node can match:
          1) month/day/year (numeric)
          2) 'tomorrow', 'today', or a weekday
          3) monthname day, optional year
        We iterate through tokens, collect info, then build a datetime.
        """
        data = {}

        for child in children:
            if not child.children:
                continue

            val = child.children[0].value
            if child.data == "month":
                data["month"] = int(val)
            elif child.data == "monthname":
                data["monthname"] = val  # e.g. "July", "jul"
            elif child.data == "day":
                data["day"] = int(val)
            elif child.data in ["year", "year4"]:
                data["year"] = int(val)
            elif child.data == "weekday":
                data["weekday"] = val.lower()  # e.g. "mon", "tue"

        # Handle special strings like 'tomorrow', 'today', or a plain weekday
        # Because Lark might return these as literal matches with no children.
        # We find them by checking the raw string in tokens:
        for token in children:
            if isinstance(token, str):
                # Lark might match 'tomorrow' or 'today' as a plain string
                if token.lower() == "tomorrow":
                    dt = self.now + timedelta(days=1)
                    return date(dt.year, dt.month, dt.day)
                elif token.lower() == "today":
                    return date(self.now.year, self.now.month, self.now.day)
                else:
                    # Possibly a weekday (like 'wed')
                    # You could parse next occurrence of that weekday, etc.
                    pass

        # If we have a named month, map it to a numeric month
        month_mapping = {
            "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
            "july": 7, "august": 8, "september": 9, "october": 10, "november": 11, "december": 12,
            "jan": 1, "feb": 2, "mar": 3, "apr": 4, "jun": 6, "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12
        }

        if "monthname" in data and "month" not in data:
            key = data["monthname"].lower().replace(".", "")
            data["month"] = month_mapping.get(key, self.now.month)
            
        if data["day"] > 31 and "year" not in data:
            data["year"] = data.pop("day")

        if "day" not in data:
            data["day"] = 1  # the only exception. just use the first day of the month
        if "year" not in data:
            data["year"] = self.now.year
        if "month" not in data:
            data["month"] = self.now.month
            
        if 50 < data["year"] < 100:
            data["year"] = 1900 + data["year"]
        elif data["year"] < 50:
            data["year"] = 2000 + data["year"]

        return date(data["year"], data["month"], data["day"])

    def time(self, children):
        """
        A 'time' node might contain:
        - hour, minute, optional am/pm (captured by the MERIDIEM token)
        - just hour + am/pm
        - the literal string 'noon'
        We produce a timedelta, which is easier to add to a date.
        """
        # 1) Check for 'noon' as a direct match (often a plain string)
        for child in children:
            if isinstance(child, str) and child.lower() == "noon":
                return tfhTime(hour=12, minute=0, meridiem=None)

        data = {child.data.value: child.children[0].value for child in children}
        
        # Extract the final hour/minute/meridiem
        hour = int(data.get("hour", 0))
        minute = int(data.get("minute", 0))
        meridiem = data.get("meridiem", '').lower()  # e.g. 'pm' or 'am'

        # 5) Apply am/pm logic
        if meridiem and meridiem.startswith("p") and hour != 12:
            hour += 12
        elif meridiem and meridiem.startswith("a") and hour == 12:
            hour = 0

        return tfhTime(hour=hour, minute=minute, meridiem=meridiem)
