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

from lark import Lark

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
    | monthname day ("," year)?

time: hour ":" minute MERIDIEM? 
    | hour (MERIDIEM)?
    | "noon"i

weekday: WEEKDAY
monthname: MONTHNAME

day: INT
month: INT
year: INT

hour: INT
minute: INT
"""


def timefhuman(string, now=None, raw=None):
    parser = Lark(grammar, start="start")
    tree = parser.parse(string)

    transformer = TimeFHumanTransformer(now=now)
    result = transformer.transform(tree)

    if raw:
        return tree

    if isinstance(result, (list, tuple)):
        return result

    return result


from datetime import datetime, time, timedelta
from lark import Transformer

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
        return tuple(children)

    def list(self, children):
        """Handles comma/or lists like '7/17, 7/18, 7/19' or '7/17 or 7/18'."""
        return children

    def datetime(self, children):
        """
        A 'datetime' node can contain:
          - date + time
          - date + 'at' + time
          - just date
          - just time
        We combine them here into a single datetime if both parts are present.
        """
        date_part = next((c for c in children if isinstance(c, datetime)), None)
        time_part = next((c for c in children if isinstance(c, time)), None)

        if date_part and time_part:
            return datetime.combine(date_part, time_part)
        elif date_part:
            return date_part
        elif time_part:
            return datetime.combine(self.now.date(), time_part)
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
                    return datetime(dt.year, dt.month, dt.day)
                elif token.lower() == "today":
                    return datetime(self.now.year, self.now.month, self.now.day)
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

        return datetime(data["year"], data["month"], data["day"])

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
                return time(hour=12, minute=0)

        data = {}
        for child in children:
            # 2) If this is a Tree, it has child.data and child.children
            if hasattr(child, "data"):
                # The grammar says hour -> INT, minute -> INT, so
                # we'd expect something like Tree("hour", [Token("INT","3")])
                if child.data == "hour":
                    data["hour"] = int(child.children[0].value)
                elif child.data == "minute":
                    data["minute"] = int(child.children[0].value)

            # 3) If this is a Token, check child.type and child.value
            elif hasattr(child, "type"):
                # The grammar defines MERIDIEM as a token
                if child.type == "MERIDIEM":
                    # child.value might be 'pm', 'a.m.', etc.
                    data["meridiem"] = child.value.lower().replace(".", "")

            # 4) If it's a plain string (already checked 'noon' above), do nothing
            else:
                pass

        # Extract the final hour/minute/meridiem
        hour = data.get("hour", 0)
        minute = data.get("minute", 0)
        meridiem = data.get("meridiem")  # e.g. 'pm' or 'am'

        # 5) Apply am/pm logic
        if meridiem and meridiem.startswith("p") and hour != 12:
            hour += 12
        elif meridiem and meridiem.startswith("a") and hour == 12:
            hour = 0

        return time(hour=hour, minute=minute)