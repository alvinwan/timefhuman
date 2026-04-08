import signal
from datetime import date, datetime, timedelta

from timefhuman import timefhuman
from timefhuman.main import tfhConfig


NOW = datetime(2018, 8, 4, 14, 0)


def build_timefhuman_document_bench():
    cfg = tfhConfig(now=NOW)
    document_cfg = tfhConfig(now=NOW, infer_datetimes=False)
    match_cfg = tfhConfig(now=NOW, infer_datetimes=False, return_matched_text=True)
    return {
        "label": "timefhuman",
        "func": lambda text: timefhuman(text, config=cfg),
        "document_func": lambda text: timefhuman(text, config=document_cfg),
        "document_dump_func": lambda text: timefhuman(text, config=match_cfg),
    }


def build_dateparser_document_bench():
    try:
        import dateparser
    except ImportError:
        return None

    try:
        from dateparser.search import search_dates as dateparser_search_dates
    except ImportError:
        dateparser_search_dates = None

    bench = {
        "label": "dateparser*",
        "func": lambda text: dateparser.parse(text, settings={"RELATIVE_BASE": NOW}),
        "document_func": None,
    }
    if dateparser_search_dates:
        bench["document_func"] = lambda text: dateparser_search_dates(text, settings={"RELATIVE_BASE": NOW})
        bench["document_dump_func"] = lambda text: dateparser_search_dates(text, settings={"RELATIVE_BASE": NOW})
    return bench


def build_parsedatetime_document_bench():
    try:
        import parsedatetime
    except ImportError:
        return None

    calendar = parsedatetime.Calendar()
    return {
        "label": "parsedatetime.parseDT",
        "func": lambda text: calendar.parseDT(text, NOW),
        "document_func": None,
    }


def build_datefinder_document_bench():
    try:
        import datefinder
    except ImportError:
        return None

    return {
        "label": "datefinder.find_dates",
        "func": lambda text: list(datefinder.find_dates(text, base_date=NOW)),
        "document_func": lambda text: list(datefinder.find_dates(text, base_date=NOW)),
        "document_dump_func": lambda text: list(datefinder.find_dates(text, base_date=NOW, source=True, index=True)),
    }


def build_ctparse_document_bench():
    try:
        import ctparse
    except ImportError:
        return None

    return {
        "label": "ctparse.ctparse",
        "func": lambda text: ctparse.ctparse(text, ts=NOW),
        "document_func": None,
    }


def build_recurrent_document_bench():
    try:
        import recurrent
    except ImportError:
        return None

    return {
        "label": "recurrent.parse",
        "func": lambda text: recurrent.parse(text, NOW),
        "document_func": lambda text: recurrent.parse(text, NOW),
    }


def build_metadate_document_bench():
    try:
        import metadate
    except ImportError:
        return None

    return {
        "label": "metadate.parse_date",
        "func": lambda text: metadate.parse_date(text, reference_date=NOW, multi=True, use_c_scanner=True),
        "document_func": None,
    }


DOCUMENT_BENCH_BUILDERS = {
    "timefhuman": build_timefhuman_document_bench,
    "dateparser*": build_dateparser_document_bench,
    "parsedatetime.parseDT": build_parsedatetime_document_bench,
    "datefinder.find_dates": build_datefinder_document_bench,
    "ctparse.ctparse": build_ctparse_document_bench,
    "recurrent.parse": build_recurrent_document_bench,
    "metadate.parse_date": build_metadate_document_bench,
}


def build_timefhuman_case_bench():
    return {
        "label": "timefhuman",
        "runner": lambda text, sent_at: timefhuman(
            text,
            config=tfhConfig(now=sent_at, return_matched_text=True),
        ),
    }


def build_dateparser_case_bench():
    try:
        from dateparser.search import search_dates as dateparser_search_dates
    except ImportError:
        return None

    return {
        "label": "dateparser*",
        "runner": lambda text, sent_at: dateparser_search_dates(
            text,
            settings={"RELATIVE_BASE": sent_at},
        ),
    }


def build_parsedatetime_case_bench():
    try:
        import parsedatetime
    except ImportError:
        return None

    calendar = parsedatetime.Calendar()
    return {
        "label": "parsedatetime.parseDT",
        "runner": lambda text, sent_at: calendar.parseDT(text, sent_at),
    }


def build_datefinder_case_bench():
    try:
        import datefinder
    except ImportError:
        return None

    return {
        "label": "datefinder.find_dates",
        "runner": lambda text, sent_at: list(
            datefinder.find_dates(text, base_date=sent_at, source=True, index=True)
        ),
    }


def build_ctparse_case_bench():
    try:
        import ctparse
    except ImportError:
        return None

    return {
        "label": "ctparse.ctparse",
        "runner": lambda text, sent_at: ctparse.ctparse(text, ts=sent_at),
    }


def build_recurrent_case_bench():
    try:
        import recurrent
    except ImportError:
        return None

    return {
        "label": "recurrent.parse",
        "runner": lambda text, sent_at: recurrent.parse(text, sent_at),
    }


def build_metadate_case_bench():
    try:
        import metadate
    except ImportError:
        return None

    return {
        "label": "metadate.parse_date",
        "runner": lambda text, sent_at: metadate.parse_date(
            text,
            reference_date=sent_at,
            multi=True,
            use_c_scanner=True,
        ),
    }


CASE_BENCH_BUILDERS = {
    "timefhuman": build_timefhuman_case_bench,
    "dateparser*": build_dateparser_case_bench,
    "parsedatetime.parseDT": build_parsedatetime_case_bench,
    "datefinder.find_dates": build_datefinder_case_bench,
    "ctparse.ctparse": build_ctparse_case_bench,
    "recurrent.parse": build_recurrent_case_bench,
    "metadate.parse_date": build_metadate_case_bench,
}


def build_benches(builders):
    benches = []
    for label in builders:
        bench = builders[label]()
        if bench is not None:
            benches.append(bench)
    return benches


def normalize_exact_result(label, text, func):
    result = func(text)
    if label == "timefhuman":
        return result[0] if result else None
    if label == "dateparser*":
        return result
    if label == "parsedatetime.parseDT":
        value, status = result
        return value if status else None
    if label == "datefinder.find_dates":
        return result[0] if result else None
    if label == "ctparse.ctparse":
        return safe_ctparse_dt(result.resolution) if result else None
    if label == "recurrent.parse":
        return result
    if label == "metadate.parse_date":
        return result[0].start_date if result else None
    return None


def safe_ctparse_dt(value):
    try:
        return getattr(value, "dt", None)
    except ValueError:
        return None


def extract_result_items(label, result):
    if label == "timefhuman":
        if not result:
            return []
        if isinstance(result[0], tuple) and len(result[0]) == 3:
            return [(matched_text, value) for matched_text, _, value in result]
        return [(None, value) for value in result]
    if label == "datefinder.find_dates":
        if not result:
            return []
        if isinstance(result[0], tuple) and len(result[0]) == 3:
            return [(matched_text, value) for value, matched_text, _ in result]
        return [(None, value) for value in result]
    if label == "dateparser*":
        if not result:
            return []
        return [(matched_text, value) for matched_text, value in result]
    if label == "parsedatetime.parseDT":
        value, status = result
        return [] if not status else [(None, value)]
    if label == "ctparse.ctparse":
        if result is None:
            return []
        resolution = result.resolution
        dt_value = safe_ctparse_dt(resolution)
        if dt_value is not None:
            return [(None, dt_value)]
        if hasattr(resolution, "start") and hasattr(resolution, "end"):
            start = safe_ctparse_dt(resolution.start)
            end = safe_ctparse_dt(resolution.end)
            if start is not None and end is not None:
                return [(None, (start, end))]
        return []
    if label == "recurrent.parse":
        return [] if result is None else [(None, result)]
    if label == "metadate.parse_date":
        if not result:
            return []
        return [(None, match.start_date) for match in result]
    return []


def supports_text_matches(label):
    return label in {"timefhuman", "datefinder.find_dates", "dateparser*"}


def canonicalize_value(value):
    if isinstance(value, datetime):
        if (
            value.tzinfo is None
            and value.hour == 0
            and value.minute == 0
            and value.second == 0
            and value.microsecond == 0
        ):
            return value.date()
        return value
    if isinstance(value, tuple):
        return tuple(canonicalize_value(item) for item in value)
    if isinstance(value, list):
        return tuple(canonicalize_value(item) for item in value)
    return value


def values_equivalent(actual, expected, reference_now=NOW):
    actual = canonicalize_value(actual)
    expected = canonicalize_value(expected)

    if actual == expected:
        return True

    if isinstance(actual, datetime) and isinstance(expected, datetime):
        return actual.replace(tzinfo=None) == expected.replace(tzinfo=None)

    if isinstance(expected, date) and not isinstance(expected, datetime):
        return isinstance(actual, datetime) and actual.date() == expected

    if isinstance(expected, timedelta):
        return isinstance(actual, datetime) and actual == reference_now + expected

    if isinstance(expected, tuple):
        return (
            isinstance(actual, tuple)
            and len(actual) == len(expected)
            and all(
                values_equivalent(actual_item, expected_item, reference_now=reference_now)
                for actual_item, expected_item in zip(actual, expected)
            )
        )

    return False


def flatten_value_members(value):
    value = canonicalize_value(value)
    if isinstance(value, tuple):
        members = []
        for item in value:
            members.extend(flatten_value_members(item))
        return members
    return [value]


def count_group_matches(label, result, expected, reference_now=NOW):
    actual_items = [
        (matched_text, canonicalize_value(value))
        for matched_text, value in extract_result_items(label, result)
    ]
    remaining_actual = list(actual_items)
    matched_expected = [False] * len(expected)
    count = 0

    if supports_text_matches(label):
        for expected_index, (expected_text, _, expected_value) in enumerate(expected):
            for actual_index, (actual_text, actual_value) in enumerate(remaining_actual):
                if actual_text == expected_text and values_equivalent(
                    actual_value,
                    expected_value,
                    reference_now=reference_now,
                ):
                    matched_expected[expected_index] = True
                    remaining_actual.pop(actual_index)
                    count += 1
                    break

    for expected_index, (_, _, expected_value) in enumerate(expected):
        if matched_expected[expected_index]:
            continue
        for actual_index, (_, actual_value) in enumerate(remaining_actual):
            if values_equivalent(actual_value, expected_value, reference_now=reference_now):
                remaining_actual.pop(actual_index)
                count += 1
                break

    return count


def count_member_matches(label, result, expected, reference_now=NOW):
    actual_members = []
    for _, value in extract_result_items(label, result):
        actual_members.extend(flatten_value_members(value))

    expected_members = []
    for _, _, value in expected:
        expected_members.extend(flatten_value_members(value))

    remaining_actual = list(actual_members)
    count = 0
    for expected_value in expected_members:
        for actual_index, actual_value in enumerate(remaining_actual):
            if values_equivalent(actual_value, expected_value, reference_now=reference_now):
                remaining_actual.pop(actual_index)
                count += 1
                break

    return {
        "matched": count,
        "total": len(expected_members),
    }


def exact_case_match(label, result, expected, reference_now=NOW):
    actual_items = [
        (matched_text, canonicalize_value(value))
        for matched_text, value in extract_result_items(label, result)
    ]
    if len(actual_items) != len(expected):
        return False

    remaining_actual = list(actual_items)
    for expected_text, _, expected_value in expected:
        matched = False
        for actual_index, (actual_text, actual_value) in enumerate(remaining_actual):
            if supports_text_matches(label) and actual_text != expected_text:
                continue
            if values_equivalent(actual_value, expected_value, reference_now=reference_now):
                remaining_actual.pop(actual_index)
                matched = True
                break
        if not matched:
            return False

    return not remaining_actual


class BenchmarkTimeout(Exception):
    pass


def timeout_call(timeout_seconds, func, *args):
    def alarm_handler(signum, frame):
        raise BenchmarkTimeout()

    previous_handler = signal.getsignal(signal.SIGALRM) if timeout_seconds else None
    if timeout_seconds:
        signal.signal(signal.SIGALRM, alarm_handler)
        signal.alarm(timeout_seconds)
    try:
        return func(*args)
    finally:
        if timeout_seconds:
            signal.alarm(0)
            signal.signal(signal.SIGALRM, previous_handler)
