import time
from datetime import datetime

from timefhuman import timefhuman
from timefhuman.main import tfhConfig

try:
    import ctparse
except ImportError:
    ctparse = None

try:
    import datefinder
except ImportError:
    datefinder = None

try:
    import dateparser
except ImportError:
    dateparser = None

try:
    import metadate
except ImportError:
    metadate = None

try:
    import parsedatetime
except ImportError:
    parsedatetime = None

try:
    import recurrent
except ImportError:
    recurrent = None


NOW = datetime(2018, 8, 4, 14, 0)
INPUTS = [
    "5p",
    "3p EST",
    "July 2019",
    "7-17-18",
    "2018-7-17",
    "7/2018",
    "July 17, 2018 at 3p.m.",
    "July 17, 2018 3 p.m.",
    "3PM on July 17",
    "July 17 at 3",
    "7/17/18 3:00 p.m.",
    "3 p.m. today",
    "Tomorrow 3p",
    "3p tomorrow",
    "yesterday 3p",
    "July 3rd",
    "7/17-7/18",
    "July 17-18",
    "3p -4p",
    "3p -4p PDT",
    "6:00 pm - 12:00 am",
    "8/4 6:00 pm - 8/4 12:00 am",
    "11PM to 1AM",
    "7/17 3 pm- 7/19 2 pm",
    "Jun 28 5:00 PM - Aug 02 7:00 PM",
    "Jun 28 2019 5:00 PM - Aug 02 2019 7:00 PM",
    "6/28 5:00 PM - 8/02 7:00 PM",
    "6/28/2019 5:00 PM - 8/02/2019 7:00 PM",
    "July 4th or 5th at 3PM",
    "tomorrow noon,Wed 3 p.m.,Fri 11 AM",
    "7/17 4-5 PM or 5-6 PM today",
    "30 minutes",
    "30-40 mins",
    "1 or 2 days",
    "in 1 year",
    "1 year ago",
    "2022-12-27T09:15:01.002",
]
EXACT_CASES = [
    ("July 2019", datetime(2019, 7, 1, 0, 0)),
    ("2018-7-17", datetime(2018, 7, 17, 0, 0)),
    ("July 17, 2018 at 3p.m.", datetime(2018, 7, 17, 15, 0)),
    ("3 p.m. today", datetime(2018, 8, 4, 15, 0)),
    ("Tomorrow 3p", datetime(2018, 8, 5, 15, 0)),
    ("yesterday 3p", datetime(2018, 8, 3, 15, 0)),
    ("July 3rd", datetime(2018, 7, 3, 0, 0)),
    ("in 1 year", datetime(2019, 8, 4, 14, 0)),
    ("1 year ago", datetime(2017, 8, 4, 14, 0)),
    ("2022-12-27T09:15:01.002", datetime(2022, 12, 27, 9, 15, 1, 2)),
]


def build_benches():
    cfg = tfhConfig(now=NOW)
    benches = [("timefhuman", lambda text: timefhuman(text, config=cfg))]

    if dateparser:
        benches.append(("dateparser.parse", lambda text: dateparser.parse(text, settings={"RELATIVE_BASE": NOW})))
    if parsedatetime:
        calendar = parsedatetime.Calendar()
        benches.append(("parsedatetime.parseDT", lambda text: calendar.parseDT(text, NOW)))
    if datefinder:
        benches.append(("datefinder.find_dates", lambda text: list(datefinder.find_dates(text, base_date=NOW))))
    if ctparse:
        benches.append(("ctparse.ctparse", lambda text: ctparse.ctparse(text, ts=NOW)))
    if recurrent:
        benches.append(("recurrent.parse", lambda text: recurrent.parse(text, NOW)))
    if metadate:
        benches.append(
            ("metadate.parse_date", lambda text: metadate.parse_date(text, reference_date=NOW, multi=True, use_c_scanner=True))
        )

    return benches


def has_result(label, result):
    if label == "timefhuman":
        return bool(result)
    if label == "dateparser.parse":
        return result is not None
    if label == "parsedatetime.parseDT":
        return bool(result[1])
    if label == "datefinder.find_dates":
        return bool(result)
    if label == "ctparse.ctparse":
        return result is not None
    if label == "recurrent.parse":
        return result is not None
    if label == "metadate.parse_date":
        return bool(result)
    return False


def normalize_exact_result(label, text, func):
    result = func(text)
    if label == "timefhuman":
        return result[0] if result else None
    if label == "dateparser.parse":
        return result
    if label == "parsedatetime.parseDT":
        value, status = result
        return value if status else None
    if label == "datefinder.find_dates":
        return result[0] if result else None
    if label == "ctparse.ctparse":
        return result.resolution.dt if result else None
    if label == "recurrent.parse":
        return result
    if label == "metadate.parse_date":
        return result[0].start_date if result else None
    return None


def run_benchmark(label, func):
    for text in INPUTS[:5]:
        try:
            func(text)
        except Exception:
            pass

    start = time.perf_counter()
    successes = 0
    errors = 0
    for text in INPUTS:
        try:
            successes += has_result(label, func(text))
        except Exception:
            errors += 1
    elapsed = time.perf_counter() - start

    exact = 0
    for text, expected in EXACT_CASES:
        try:
            exact += normalize_exact_result(label, text, func) == expected
        except Exception:
            pass

    return {
        "label": label,
        "seconds": elapsed,
        "us_per_input": elapsed / len(INPUTS) * 1e6,
        "ok": successes,
        "errors": errors,
        "exact": exact,
    }


def main():
    rows = [run_benchmark(label, func) for label, func in build_benches()]
    print(f"{'parser':24} {'us/input':>10} {'ok':>8} {'exact':>8} {'errors':>8}")
    for row in rows:
        print(
            f"{row['label']:24} "
            f"{row['us_per_input']:10.1f} "
            f"{row['ok']:>2}/{len(INPUTS):<5} "
            f"{row['exact']:>2}/{len(EXACT_CASES):<5} "
            f"{row['errors']:>8}"
        )


if __name__ == "__main__":
    main()
