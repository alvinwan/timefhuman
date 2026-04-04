from dataclasses import dataclass

@dataclass(slots=True)
class AmbiguousExpr:
    value: int


@dataclass(slots=True)
class ValueExpr:
    value: object


@dataclass(slots=True)
class DatetimeExpr:
    date: object = None
    time: object = None
    tz: object = None


@dataclass(slots=True)
class ListExpr:
    items: list
    tz: object = None


@dataclass(slots=True)
class RangeExpr:
    items: tuple
    tz: object = None
