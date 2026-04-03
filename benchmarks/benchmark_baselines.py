import statistics
import sys
import time
from datetime import date, datetime, timedelta
from pathlib import Path
import signal

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from eval.corpora import CORPORA, load_corpus_text
from eval.short import DEFAULT_CASES
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
    from dateparser.search import search_dates as dateparser_search_dates
except ImportError:
    dateparser_search_dates = None

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
EXACT_CASES = [
    (text, expected[0])
    for text, expected in DEFAULT_CASES
    if len(expected) == 1 and isinstance(expected[0], datetime)
]
SHORT_PERF_INPUTS = [text for text, _ in EXACT_CASES]
SHORT_SAMPLES = 7
SHORT_TIMEOUT_SECONDS = 1
DOCUMENT_TIMEOUT_SECONDS = 1
DOCUMENT_DATASETS = (
    ("core_corpus", "core_corpus", 7),
    ("seattle_html_76k", "seattle_html_76k", 5),
    ("test_data_560k", "test_data_560k", 3),
)
GOLD_DOCUMENT_DATASETS = ("core_corpus", "seattle_html_76k")


def build_benches():
    cfg = tfhConfig(now=NOW)
    document_cfg = tfhConfig(now=NOW, infer_datetimes=False)
    match_cfg = tfhConfig(now=NOW, infer_datetimes=False, return_matched_text=True)
    benches = [{
        "label": "timefhuman",
        "func": lambda text: timefhuman(text, config=cfg),
        "document_func": lambda text: timefhuman(text, config=document_cfg),
        "document_dump_func": lambda text: timefhuman(text, config=match_cfg),
    }]

    if dateparser:
        benches.append({
            "label": "dateparser*",
            "func": None,
            "document_func": None,
        })
        benches[-1]["func"] = lambda text: dateparser.parse(text, settings={"RELATIVE_BASE": NOW})
        if dateparser_search_dates:
            benches[-1]["document_func"] = lambda text: dateparser_search_dates(text, settings={"RELATIVE_BASE": NOW})
            benches[-1]["document_dump_func"] = lambda text: dateparser_search_dates(text, settings={"RELATIVE_BASE": NOW})
    if parsedatetime:
        calendar = parsedatetime.Calendar()
        benches.append({
            "label": "parsedatetime.parseDT",
            "func": lambda text: calendar.parseDT(text, NOW),
            "document_func": None,
        })
    if datefinder:
        benches.append({
            "label": "datefinder.find_dates",
            "func": lambda text: list(datefinder.find_dates(text, base_date=NOW)),
            "document_func": lambda text: list(datefinder.find_dates(text, base_date=NOW)),
            "document_dump_func": lambda text: list(datefinder.find_dates(text, base_date=NOW, source=True, index=True)),
        })
    if ctparse:
        benches.append({
            "label": "ctparse.ctparse",
            "func": lambda text: ctparse.ctparse(text, ts=NOW),
            "document_func": None,
        })
    if recurrent:
        benches.append({
            "label": "recurrent.parse",
            "func": lambda text: recurrent.parse(text, NOW),
            "document_func": lambda text: recurrent.parse(text, NOW),
        })
    if metadate:
        benches.append({
            "label": "metadate.parse_date",
            "func": lambda text: metadate.parse_date(text, reference_date=NOW, multi=True, use_c_scanner=True),
            "document_func": None,
        })

    return benches


def load_document_datasets():
    datasets = {}
    for dataset_name, _, _ in DOCUMENT_DATASETS:
        text = load_corpus_text(dataset_name)
        if text is not None:
            datasets[dataset_name] = text
    return datasets


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
        return result.resolution.dt if result else None
    if label == "recurrent.parse":
        return result
    if label == "metadate.parse_date":
        return result[0].start_date if result else None
    return None


def count_document_results(label, result):
    return len(extract_result_items(label, result))


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
        return [] if result is None else [(None, result.resolution.dt)]
    if label == "recurrent.parse":
        return [] if result is None else [(None, result)]
    if label == "metadate.parse_date":
        if not result:
            return []
        return [(None, match.start_date) for match in result]
    return []


def supports_text_matches(label):
    return label in {"timefhuman", "datefinder.find_dates", "dateparser*"}


def get_document_runner(bench):
    return bench.get("document_func") or bench.get("func")


class BenchmarkTimeout(Exception):
    pass


def _timeout_call(timeout_seconds, func, *args):
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


def benchmark_document(label, document_func, text, iterations, timeout_seconds=DOCUMENT_TIMEOUT_SECONDS):
    if document_func is None or text is None:
        return None

    def run_once():
        start = time.perf_counter()
        result = _timeout_call(timeout_seconds, document_func, text)
        return {
            "seconds": time.perf_counter() - start,
            "count": count_document_results(label, result),
        }

    try:
        warmup = run_once()
        times = []
        for _ in range(iterations):
            times.append(run_once()["seconds"])
        return {
            "seconds": statistics.median(times),
            "count": warmup["count"],
        }
    except BenchmarkTimeout:
        return {"timeout": f">{timeout_seconds}s", "count": None}
    except Exception as exc:
        return {"error": type(exc).__name__, "count": None}


def benchmark_short_perf(func, timeout_seconds=SHORT_TIMEOUT_SECONDS, samples=SHORT_SAMPLES):
    if func is None:
        return None

    def run_once():
        start = time.perf_counter()
        for text in SHORT_PERF_INPUTS:
            func(text)
        return time.perf_counter() - start

    try:
        _timeout_call(timeout_seconds, run_once)
        samples_seconds = [_timeout_call(timeout_seconds, run_once) for _ in range(samples)]
        return statistics.median(samples_seconds) / len(SHORT_PERF_INPUTS) * 1e6
    except BenchmarkTimeout:
        return f">{timeout_seconds}s"
    except Exception:
        return None


def run_short_correctness(bench):
    label = bench["label"]
    func = bench["func"]
    if func is None:
        return {
            "label": label,
            "short_correctness": None,
        }

    exact = 0
    for text, expected in EXACT_CASES:
        try:
            exact += normalize_exact_result(label, text, func) == expected
        except Exception:
            pass

    return {
        "label": label,
        "short_correctness": exact,
    }


def normalize_gold_match(label, match):
    matched_text, value = match
    return matched_text, canonicalize_value(value)


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


def values_equivalent(actual, expected):
    actual = canonicalize_value(actual)
    expected = canonicalize_value(expected)

    if actual == expected:
        return True

    if isinstance(expected, date) and not isinstance(expected, datetime):
        return isinstance(actual, datetime) and actual.date() == expected

    if isinstance(expected, timedelta):
        return isinstance(actual, datetime) and actual == NOW + expected

    if isinstance(expected, tuple):
        return (
            isinstance(actual, tuple)
            and len(actual) == len(expected)
            and all(values_equivalent(actual_item, expected_item) for actual_item, expected_item in zip(actual, expected))
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


def count_document_group_matches(label, matches, expected):
    actual_items = [normalize_gold_match(label, match) for match in extract_result_items(label, matches)]
    remaining_actual = list(actual_items)
    matched_expected = [False] * len(expected)
    count = 0

    if supports_text_matches(label):
        for expected_index, (expected_text, _, expected_value) in enumerate(expected):
            for actual_index, (actual_text, actual_value) in enumerate(remaining_actual):
                if actual_text == expected_text and values_equivalent(actual_value, expected_value):
                    matched_expected[expected_index] = True
                    remaining_actual.pop(actual_index)
                    count += 1
                    break

    for expected_index, (_, _, expected_value) in enumerate(expected):
        if matched_expected[expected_index]:
            continue
        for actual_index, (_, actual_value) in enumerate(remaining_actual):
            if values_equivalent(actual_value, expected_value):
                remaining_actual.pop(actual_index)
                count += 1
                break

    return count


def count_document_member_matches(label, matches, expected):
    actual_members = []
    for _, value in extract_result_items(label, matches):
        actual_members.extend(flatten_value_members(value))

    expected_members = []
    for _, _, value in expected:
        expected_members.extend(flatten_value_members(value))

    remaining_actual = list(actual_members)
    count = 0
    for expected_value in expected_members:
        for actual_index, actual_value in enumerate(remaining_actual):
            if values_equivalent(actual_value, expected_value):
                remaining_actual.pop(actual_index)
                count += 1
                break

    return {
        "matched": count,
        "total": len(expected_members),
    }


def run_document_correctness(bench, document_datasets):
    row = {"label": bench["label"]}
    document_runner = bench.get("document_dump_func") or get_document_runner(bench)
    for dataset_name in GOLD_DOCUMENT_DATASETS:
        key = f"{dataset_name}_correctness"
        group_key = f"{dataset_name}_group_correctness"
        text = document_datasets.get(dataset_name)
        expected = CORPORA[dataset_name]["expected"]
        if document_runner is None or text is None or expected is None:
            row[key] = None
            row[group_key] = None
            continue
        try:
            matches = _timeout_call(DOCUMENT_TIMEOUT_SECONDS, document_runner, text)
        except BenchmarkTimeout:
            row[key] = {"timeout": f">{DOCUMENT_TIMEOUT_SECONDS}s"}
            row[group_key] = {"timeout": f">{DOCUMENT_TIMEOUT_SECONDS}s"}
            continue
        except Exception as exc:
            row[key] = {"error": type(exc).__name__}
            row[group_key] = {"error": type(exc).__name__}
            continue

        row[key] = count_document_member_matches(bench["label"], matches, expected)
        row[group_key] = {
            "matched": count_document_group_matches(bench["label"], matches, expected),
            "total": len(expected),
        }
    return row


def run_document_perf(bench, document_datasets):
    document_results = {"label": bench["label"]}
    document_runner = get_document_runner(bench)
    for dataset_name, key, iterations in DOCUMENT_DATASETS:
        text = document_datasets.get(dataset_name)
        document_results[key] = (
            benchmark_document(
                bench["label"],
                document_runner,
                text,
                iterations,
            ) if text is not None else None
        )
    return document_results


def sort_perf_rows(rows):
    def sort_key(row):
        core = row.get("core_corpus")
        if isinstance(core, dict) and "seconds" in core:
            key = core["seconds"]
        elif isinstance(core, dict) and "timeout" in core:
            key = float("inf")
        elif isinstance(core, dict) and "error" in core:
            key = float("inf")
        else:
            short = row.get("short_ms")
            if isinstance(short, (int, float)):
                key = short / 1000.0
            elif isinstance(row.get("short_timeout"), str):
                key = float("inf")
            else:
                key = float("inf")
        return (row["label"] != "timefhuman", key)

    return sorted(rows, key=sort_key)


def merge_rows(correctness_rows, perf_rows):
    correctness_by_label = {row["label"]: row for row in correctness_rows}
    perf_by_label = {row["label"]: row for row in perf_rows}
    labels = [row["label"] for row in sort_perf_rows(perf_rows)]
    merged = []
    for label in labels:
        row = {"label": label}
        row.update(correctness_by_label.get(label, {}))
        row.update(perf_by_label.get(label, {}))
        merged.append(row)
    return merged


def main():
    benches = build_benches()
    document_datasets = load_document_datasets()
    correctness_rows = []
    perf_rows = []

    for bench in benches:
        correctness_row = run_short_correctness(bench)
        correctness_row.update(run_document_correctness(bench, document_datasets))
        correctness_rows.append(correctness_row)

        short_perf = benchmark_short_perf(bench["func"])
        perf_row = {
            "label": bench["label"],
            "short_ms": None if not isinstance(short_perf, (int, float)) else short_perf * len(SHORT_PERF_INPUTS) / 1000.0,
            "short_timeout": short_perf if isinstance(short_perf, str) else None,
        }
        perf_row.update(run_document_perf(bench, document_datasets))
        perf_rows.append(perf_row)

    rows = merge_rows(correctness_rows, perf_rows)

    print("benchmarks")
    print(
        f"{'parser':24} "
        f"{'short (ms)':>10} {'acc':>8} "
        f"{'core (ms)':>10} {'#':>6} {'acc':>8} {'group':>8} "
        f"{'seattle_76k (ms)':>15} {'#':>6} {'acc':>8} {'group':>8} "
        f"{'test_560k (ms)':>15} {'#':>6}"
    )

    def format_correctness(value):
        if isinstance(value, dict) and "matched" in value:
            return f"{value['matched']}/{value['total']}"
        if isinstance(value, dict) and "timeout" in value:
            return "timeout"
        if isinstance(value, dict) and "error" in value:
            return "error"
        if value is None:
            return "n/a"
        return str(value)

    def format_short_count(value, total):
        if value is None:
            return "n/a"
        return f"{value}/{total}"

    def format_perf_short(row):
        value = row["short_ms"]
        if isinstance(value, (int, float)):
            return f"{value:.1f}"
        if isinstance(row["short_timeout"], str):
            return row["short_timeout"].replace(">1s", ">1000ms")
        return "n/a"

    def format_doc_ms(value):
        if isinstance(value, dict) and "seconds" in value:
            return f"{value['seconds'] * 1000.0:.1f}"
        if isinstance(value, dict) and "timeout" in value:
            return value["timeout"].replace(">1s", ">1000ms")
        if isinstance(value, dict) and "error" in value:
            return "error"
        if value is None:
            return "n/a"
        return str(value)

    def format_doc_count(value):
        if isinstance(value, dict) and "seconds" in value:
            return str(value["count"])
        return "n/a"

    for row in rows:
        print(
            f"{row['label']:24} "
            f"{format_perf_short(row):>10} "
            f"{format_short_count(row['short_correctness'], len(EXACT_CASES)):>8} "
            f"{format_doc_ms(row['core_corpus']):>10} "
            f"{format_doc_count(row['core_corpus']):>6} "
            f"{format_correctness(row['core_corpus_correctness']):>8} "
            f"{format_correctness(row['core_corpus_group_correctness']):>8} "
            f"{format_doc_ms(row['seattle_html_76k']):>15} "
            f"{format_doc_count(row['seattle_html_76k']):>6} "
            f"{format_correctness(row['seattle_html_76k_correctness']):>8} "
            f"{format_correctness(row['seattle_html_76k_group_correctness']):>8} "
            f"{format_doc_ms(row['test_data_560k']):>12} "
            f"{format_doc_count(row['test_data_560k']):>6}"
        )


if __name__ == "__main__":
    main()
