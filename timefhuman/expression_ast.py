from dataclasses import dataclass

from timefhuman.inference import infer
from timefhuman.renderers import tfhAmbiguous, tfhDatelike, tfhList, tfhRange


@dataclass(slots=True)
class ValueExpr:
    value: object


@dataclass(slots=True)
class ListExpr:
    items: list
    tz: object = None


@dataclass(slots=True)
class RangeExpr:
    items: tuple
    tz: object = None


def is_ambiguous_only(expression):
    if isinstance(expression, ValueExpr):
        return isinstance(expression.value, tfhAmbiguous)
    return all(is_ambiguous_only(item) for item in expression.items)


def materialize_expression(expression, default_year: int):
    if isinstance(expression, ValueExpr):
        return expression.value

    items = [materialize_expression(item, default_year) for item in expression.items]
    if isinstance(expression, ListExpr):
        result = tfhList(infer(items))
        if expression.tz:
            result.tz = expression.tz
        return result

    left_missing_year = _datelike_missing_year(items[0])
    right_missing_year = _datelike_missing_year(items[1])
    items = infer(items)
    _adjust_cross_year_range(items, left_missing_year, right_missing_year, default_year)
    result = tfhRange(items)
    if expression.tz:
        result.tz = expression.tz
    return result


def _datelike_missing_year(value):
    if not isinstance(value, tfhDatelike):
        return False
    if isinstance(value, (tfhList, tfhRange)):
        return False
    return value.date is not None and value.year is None and value.month is not None and value.day is not None


def _adjust_cross_year_range(items, left_missing_year: bool, right_missing_year: bool, default_year: int):
    if len(items) != 2:
        return
    left, right = items
    if not (
        left_missing_year
        and right_missing_year
        and isinstance(left, tfhDatelike)
        and isinstance(right, tfhDatelike)
        and left.date
        and right.date
        and left.month is not None
        and left.day is not None
        and right.month is not None
        and right.day is not None
    ):
        return

    if (right.month, right.day) < (left.month, left.day):
        base_year = right.year or left.year or default_year
        right.year = base_year + 1
