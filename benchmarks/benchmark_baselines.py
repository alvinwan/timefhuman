import json
import statistics
import subprocess
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


NOW = datetime(2018, 8, 4, 14, 0)
EXACT_CASES = [
    (text, expected[0])
    for text, expected in DEFAULT_CASES
    if len(expected) == 1 and isinstance(expected[0], datetime)
]
SHORT_PERF_INPUTS = [text for text, _ in EXACT_CASES]
SHORT_WARMUP_INPUTS = (
    "review moved to January 9 2026 at 4:45 pm",
    "follow up in 9 days",
    "shipment arrived two weeks later",
    "billing stays open from 6:15 am to 8:45 am",
    "next Tuesday at noon",
    "from March 18 2026 through April 2 2026",
    "three hours ago we sent the revision",
    "meeting on 2026-07-14 18:30",
)
DOCUMENT_WARMUP_TEXT = "\n".join(
    (
        "Operations memo 01: review moved to January 9 2026 at 4:45 pm.",
        "Operations memo 02: follow up in 9 days with the accounting team.",
        "Operations memo 03: shipment arrived two weeks later than planned.",
        "Operations memo 04: billing stays open from 6:15 am to 8:45 am on weekdays.",
        "Operations memo 05: next Tuesday at noon we start the rollout.",
        "Operations memo 06: from March 18 2026 through April 2 2026 the office is under renovation.",
        "Operations memo 07: three hours ago we sent the revised draft to legal.",
        "Operations memo 08: meeting on 2026-07-14 18:30 with the field team.",
    ) * 8
)
SHORT_SAMPLES = 7
SHORT_TIMEOUT_SECONDS = 1
DOCUMENT_TIMEOUT_SECONDS = 2
COLD_SAMPLE_GRACE_SECONDS = 60
PERF_MODES = {"cold", "warmed"}
DOCUMENT_DATASETS = (
    ("core_corpus", "core_corpus", 7),
    ("seattle_html_76k", "seattle_html_76k", 5),
    ("test_data_560k", "test_data_560k", 3),
)
GOLD_DOCUMENT_DATASETS = ("core_corpus", "seattle_html_76k", "test_data_560k")


def _build_timefhuman_bench():
    cfg = tfhConfig(now=NOW)
    document_cfg = tfhConfig(now=NOW, infer_datetimes=False)
    match_cfg = tfhConfig(now=NOW, infer_datetimes=False, return_matched_text=True)
    return {
        "label": "timefhuman",
        "func": lambda text: timefhuman(text, config=cfg),
        "document_func": lambda text: timefhuman(text, config=document_cfg),
        "document_dump_func": lambda text: timefhuman(text, config=match_cfg),
    }


def _build_dateparser_bench():
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


def _build_parsedatetime_bench():
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


def _build_datefinder_bench():
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


def _build_ctparse_bench():
    try:
        import ctparse
    except ImportError:
        return None

    return {
        "label": "ctparse.ctparse",
        "func": lambda text: ctparse.ctparse(text, ts=NOW),
        "document_func": None,
    }


def _build_recurrent_bench():
    try:
        import recurrent
    except ImportError:
        return None

    return {
        "label": "recurrent.parse",
        "func": lambda text: recurrent.parse(text, NOW),
        "document_func": lambda text: recurrent.parse(text, NOW),
    }


def _build_metadate_bench():
    try:
        import metadate
    except ImportError:
        return None

    return {
        "label": "metadate.parse_date",
        "func": lambda text: metadate.parse_date(text, reference_date=NOW, multi=True, use_c_scanner=True),
        "document_func": None,
    }


BENCH_BUILDERS = {
    "timefhuman": _build_timefhuman_bench,
    "dateparser*": _build_dateparser_bench,
    "parsedatetime.parseDT": _build_parsedatetime_bench,
    "datefinder.find_dates": _build_datefinder_bench,
    "ctparse.ctparse": _build_ctparse_bench,
    "recurrent.parse": _build_recurrent_bench,
    "metadate.parse_date": _build_metadate_bench,
}

def build_benches():
    benches = []
    for label in BENCH_BUILDERS:
        bench = BENCH_BUILDERS[label]()
        if bench is not None:
            benches.append(bench)
    return benches


def load_document_datasets():
    datasets = {}
    for dataset_name, _, _ in DOCUMENT_DATASETS:
        text = load_corpus_text(dataset_name)
        if text is not None:
            datasets[dataset_name] = text
    return datasets


def find_bench(label):
    builder = BENCH_BUILDERS.get(label)
    if builder is None:
        return None
    return builder()


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


def benchmark_document(label, dataset_name, document_func, text, iterations, timeout_seconds=DOCUMENT_TIMEOUT_SECONDS, perf_mode="cold"):
    del document_func
    if text is None:
        return None

    try:
        times = []
        count = None
        for _ in range(iterations):
            sample = _run_process_sample(label, perf_mode, "document", dataset_name, timeout_seconds)
            if "timeout" in sample:
                return {"timeout": f">{timeout_seconds}s", "count": None}
            if "error" in sample:
                return {"error": sample["error"], "count": None}
            times.append(sample["seconds"])
            if count is None:
                count = sample["count"]
        return {
            "seconds": statistics.median(times),
            "count": count,
        }
    except Exception as exc:
        return {"error": type(exc).__name__, "count": None}


def benchmark_short_perf(label, func, timeout_seconds=SHORT_TIMEOUT_SECONDS, samples=SHORT_SAMPLES, perf_mode="cold"):
    if func is None:
        return None

    try:
        samples_seconds = []
        for _ in range(samples):
            sample = _run_process_sample(label, perf_mode, "short", "", timeout_seconds)
            if "timeout" in sample:
                return f">{timeout_seconds}s"
            if "error" in sample:
                return None
            samples_seconds.append(sample["seconds"])
        return statistics.median(samples_seconds) / len(SHORT_PERF_INPUTS) * 1e6
    except Exception:
        return None


def _run_process_sample(label, perf_mode, sample_kind, sample_arg, timeout_seconds):
    script_path = Path(__file__).resolve()
    cmd = [
        sys.executable,
        str(script_path),
        "--sample",
        perf_mode,
        label,
        sample_kind,
        sample_arg,
    ]
    try:
        completed = subprocess.run(
            cmd,
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=timeout_seconds + COLD_SAMPLE_GRACE_SECONDS,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return {"timeout": f">{timeout_seconds}s"}

    output_lines = [line for line in completed.stdout.splitlines() if line.strip()]
    if not output_lines:
        error_name = "ChildProcessError" if completed.returncode else "NoOutput"
        return {"error": error_name}

    try:
        payload = json.loads(output_lines[-1])
    except json.JSONDecodeError:
        return {"error": "InvalidChildOutput"}

    if payload.get("status") == "ok":
        return payload
    if payload.get("status") == "timeout":
        return {"timeout": f">{timeout_seconds}s"}
    if payload.get("status") == "n/a":
        return {"error": "NotAvailable"}
    return {"error": payload.get("error", "ChildProcessError")}


def _warmup_short(func):
    for text in SHORT_WARMUP_INPUTS:
        func(text)


def _warmup_document(document_func):
    _timeout_call(DOCUMENT_TIMEOUT_SECONDS, document_func, DOCUMENT_WARMUP_TEXT)


def _emit_process_sample(perf_mode, label, sample_kind, sample_arg):
    if perf_mode not in PERF_MODES:
        print(json.dumps({"status": "error", "error": "UnknownPerfMode"}))
        return

    bench = find_bench(label)
    if bench is None:
        print(json.dumps({"status": "error", "error": "UnknownBench"}))
        return

    try:
        if sample_kind == "short":
            func = bench["func"]
            if func is None:
                print(json.dumps({"status": "n/a"}))
                return
            if perf_mode == "warmed":
                _warmup_short(func)

            def run_short_batch():
                start = time.perf_counter()
                for text in SHORT_PERF_INPUTS:
                    func(text)
                return time.perf_counter() - start

            seconds = _timeout_call(SHORT_TIMEOUT_SECONDS, run_short_batch)
            print(json.dumps({"status": "ok", "seconds": seconds}))
            return

        if sample_kind == "document":
            document_func = get_document_runner(bench)
            text = load_document_datasets().get(sample_arg)
            if document_func is None or text is None:
                print(json.dumps({"status": "n/a"}))
                return
            if perf_mode == "warmed":
                _warmup_document(document_func)
            start = time.perf_counter()
            result = _timeout_call(DOCUMENT_TIMEOUT_SECONDS, document_func, text)
            print(
                json.dumps({
                    "status": "ok",
                    "seconds": time.perf_counter() - start,
                    "count": count_document_results(label, result),
                })
            )
            return

        print(json.dumps({"status": "error", "error": "UnknownSampleKind"}))
    except BenchmarkTimeout:
        print(json.dumps({"status": "timeout"}))
    except Exception as exc:
        print(json.dumps({"status": "error", "error": type(exc).__name__}))


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


def run_document_perf(bench, document_datasets, perf_mode="cold"):
    document_results = {"label": bench["label"]}
    document_runner = get_document_runner(bench)
    for dataset_name, key, iterations in DOCUMENT_DATASETS:
        text = document_datasets.get(dataset_name)
        document_results[key] = (
            benchmark_document(
                bench["label"],
                dataset_name,
                document_runner,
                text,
                iterations,
                perf_mode=perf_mode,
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
    perf_mode = "cold"
    if len(sys.argv) >= 6 and sys.argv[1] == "--sample":
        _emit_process_sample(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
        return
    if len(sys.argv) >= 3 and sys.argv[1] == "--perf-mode":
        perf_mode = sys.argv[2]
        if perf_mode not in PERF_MODES:
            raise SystemExit(f"Unknown perf mode: {perf_mode}")

    benches = build_benches()
    document_datasets = load_document_datasets()
    correctness_rows = []
    perf_rows = []

    for bench in benches:
        correctness_row = run_short_correctness(bench)
        correctness_row.update(run_document_correctness(bench, document_datasets))
        correctness_rows.append(correctness_row)

        short_perf = benchmark_short_perf(bench["label"], bench["func"], perf_mode=perf_mode)
        perf_row = {
            "label": bench["label"],
            "short_ms": None if not isinstance(short_perf, (int, float)) else short_perf * len(SHORT_PERF_INPUTS) / 1000.0,
            "short_timeout": short_perf if isinstance(short_perf, str) else None,
        }
        perf_row.update(run_document_perf(bench, document_datasets, perf_mode=perf_mode))
        perf_rows.append(perf_row)

    rows = merge_rows(correctness_rows, perf_rows)

    print(f"benchmarks ({perf_mode})")
    print(
        f"{'parser':24} "
        f"{'short (ms)':>10} {'acc':>8} "
        f"{'core (ms)':>10} {'#':>6} {'acc':>8} {'group':>8} "
        f"{'sea_76k (ms)':>15} {'#':>6} {'acc':>8} {'group':>8} "
        f"{'sea_560k (ms)':>15} {'#':>6} {'acc':>8} {'group':>8}"
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
            f"{format_doc_count(row['test_data_560k']):>6} "
            f"{format_correctness(row['test_data_560k_correctness']):>8} "
            f"{format_correctness(row['test_data_560k_group_correctness']):>8}"
        )


if __name__ == "__main__":
    main()
