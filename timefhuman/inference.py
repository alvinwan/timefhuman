from datetime import timedelta

from timefhuman.renderers import tfhAmbiguous, tfhDatelike, tfhDatetime, tfhDate, tfhTime, tfhTimedelta


def infer_from(source: tfhDatelike, target):
    if isinstance(source, tfhAmbiguous):
        return target

    if isinstance(target, tfhAmbiguous) and isinstance(source, tfhDatelike):
        if source.time:
            target = tfhDatetime(time=tfhTime(hour=target.value, meridiem=source.meridiem))
        elif source.year:
            target = tfhDatetime(date=tfhDate(year=target.value))
        elif source.day:
            target = tfhDatetime(date=tfhDate(day=target.value))
        elif source.month:
            target = tfhDatetime(date=tfhDate(month=target.value))
        else:
            raise NotImplementedError(f"Not enough context to infer what {target} is")

    if isinstance(source, tfhDatelike) and isinstance(target, tfhDatelike):
        if source.date and not target.date:
            target.date = source.date
        if source.time and not target.time:
            target.time = source.time
        if source.month and not target.month:
            target.month = source.month
        if source.year and not target.year:
            target.year = source.year
        if source.meridiem and not target.meridiem:
            target.meridiem = source.meridiem
        if source.tz and not target.tz:
            target.tz = source.tz

    if isinstance(source, tfhTimedelta) and isinstance(target, tfhAmbiguous):
        target = tfhTimedelta.from_object(timedelta(**{source.unit: target.value}), unit=source.unit)

    return target


def infer(items):
    for i, item in enumerate(items[1:], start=1):
        items[i] = infer_from(items[0], item)

    for i, item in enumerate(items[:-1]):
        items[i] = infer_from(items[-1], item)

    return items
