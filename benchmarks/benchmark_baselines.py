import statistics
import sys
import time
from collections import Counter
from datetime import datetime
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
            "label": "dateparser.parse",
            "func": lambda text: dateparser.parse(text, settings={"RELATIVE_BASE": NOW}),
            "document_func": None,
        })
    if dateparser_search_dates:
        benches.append({
            "label": "dateparser.search_dates",
            "func": None,
            "document_func": lambda text: dateparser_search_dates(text, settings={"RELATIVE_BASE": NOW}),
            "document_dump_func": lambda text: dateparser_search_dates(text, settings={"RELATIVE_BASE": NOW}),
        })
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
            "document_func": None,
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
    if label == "dateparser.search_dates":
        if not result:
            return []
        return [(matched_text, value) for matched_text, value in result]
    if label == "dateparser.parse":
        return [] if result is None else [(None, result)]
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
    return label in {"timefhuman", "datefinder.find_dates", "dateparser.search_dates"}


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
    except Exception:
        return None


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


def run_document_correctness(bench, document_datasets):
    row = {"label": bench["label"]}
    document_runner = bench.get("document_dump_func") or get_document_runner(bench)
    for dataset_name in GOLD_DOCUMENT_DATASETS:
        key = f"{dataset_name}_correctness"
        text = document_datasets.get(dataset_name)
        expected = CORPORA[dataset_name]["expected"]
        if document_runner is None or text is None or expected is None:
            row[key] = None
            continue
        try:
            matches = _timeout_call(DOCUMENT_TIMEOUT_SECONDS, document_runner, text)
        except BenchmarkTimeout:
            row[key] = {"timeout": f">{DOCUMENT_TIMEOUT_SECONDS}s"}
            continue
        except Exception:
            row[key] = None
            continue

        items = [normalize_gold_match(bench["label"], match) for match in extract_result_items(bench["label"], matches)]
        if supports_text_matches(bench["label"]):
            actual_counts = Counter(items)
            expected_counts = Counter((match_text, canonicalize_value(value)) for match_text, _, value in expected)
        else:
            actual_counts = Counter(value for _, value in items)
            expected_counts = Counter(canonicalize_value(value) for _, _, value in expected)
        matched = sum((actual_counts & expected_counts).values())
        row[key] = {"matched": matched, "total": len(expected)}
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
        values = []
        short = row.get("short_us_per_input")
        if isinstance(short, (int, float)):
            values.append(short)
        elif isinstance(short, str) and short.startswith(">"):
            values.append(float("inf"))
        for dataset_name, _, _ in DOCUMENT_DATASETS:
            value = row.get(dataset_name)
            if isinstance(value, dict) and "seconds" in value:
                values.append(value["seconds"])
            elif isinstance(value, dict) and "timeout" in value:
                values.append(float("inf"))
        aggregate = statistics.median(values) if values else float("inf")
        return (row["label"] != "timefhuman", aggregate)

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

        perf_row = {"label": bench["label"], "short_us_per_input": benchmark_short_perf(bench["func"])}
        perf_row.update(run_document_perf(bench, document_datasets))
        perf_rows.append(perf_row)

    rows = merge_rows(correctness_rows, perf_rows)

    print("benchmarks")
    print(
        f"{'parser':24} "
        f"{'short':>14} {'acc':>8} "
        f"{'core_corpus':>14} {'acc':>8} "
        f"{'seattle_html_76k':>18} {'acc':>8} "
        f"{'test_data_560k':>16}"
    )

    def format_correctness(value):
        if isinstance(value, dict) and "matched" in value:
            return f"{value['matched']}/{value['total']}"
        if isinstance(value, dict) and "timeout" in value:
            return value["timeout"]
        if value is None:
            return "n/a"
        return str(value)

    def format_short_count(value, total):
        if value is None:
            return "n/a"
        return f"{value}/{total}"

    def format_perf_short(value):
        if isinstance(value, (int, float)):
            return f"{value:.1f}"
        if isinstance(value, str):
            return value
        return "n/a"

    def format_doc(value):
        if isinstance(value, dict) and "seconds" in value:
            return f"{value['seconds']:.4f} ({value['count']})"
        if isinstance(value, dict) and "timeout" in value:
            return f"{value['timeout']} (n/a)"
        if value is None:
            return "n/a"
        return str(value)

    for row in rows:
        print(
            f"{row['label']:24} "
            f"{format_perf_short(row['short_us_per_input']):>14} "
            f"{format_short_count(row['short_correctness'], len(EXACT_CASES)):>8} "
            f"{format_doc(row['core_corpus']):>14} "
            f"{format_correctness(row['core_corpus_correctness']):>8} "
            f"{format_doc(row['seattle_html_76k']):>18} "
            f"{format_correctness(row['seattle_html_76k_correctness']):>8} "
            f"{format_doc(row['test_data_560k']):>16}"
        )


if __name__ == "__main__":
    main()
