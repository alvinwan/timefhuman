import statistics
import time
from datetime import datetime
import os
from pathlib import Path
import signal

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
DATEFINDER_ROOT = Path(os.environ.get("DATEFINDER_ROOT", "/tmp/datefinder"))
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
DOCUMENT_DATASETS = (
    ("core_corpus", "core_corpus", 10),
    ("seattle_html_76k", "seattle_html_76k", 7),
    ("test_data_560k", "test_data_560k", 3),
)


def build_benches():
    cfg = tfhConfig(now=NOW)
    match_cfg = tfhConfig(now=NOW, return_matched_text=True)
    benches = [{
        "label": "timefhuman",
        "func": lambda text: timefhuman(text, config=cfg),
        "document_func": lambda text: timefhuman(text, config=cfg),
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
            "document_timeout_seconds": 15,
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
    if not DATEFINDER_ROOT.exists():
        return {}

    core_path = DATEFINDER_ROOT / "bench" / "corpus_core.txt"
    seattle_path = DATEFINDER_ROOT / "tests" / "seattle_weekly.html"
    test_data_path = DATEFINDER_ROOT / "tests" / "test_data.txt"
    if not (core_path.exists() and seattle_path.exists() and test_data_path.exists()):
        return {}

    core_lines = [
        line.strip()
        for line in core_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    return {
        "core_corpus": "\n".join(core_lines),
        "seattle_html_76k": seattle_path.read_text(errors="ignore"),
        "test_data_560k": test_data_path.read_text(errors="ignore"),
    }


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


def count_document_results(label, result):
    if label in {"timefhuman", "datefinder.find_dates", "dateparser.search_dates"}:
        return 0 if not result else len(result)
    return 0


def benchmark_document(label, document_func, text, iterations, timeout_seconds=None):
    if document_func is None:
        return None

    class DocumentTimeout(Exception):
        pass

    def alarm_handler(signum, frame):
        raise DocumentTimeout()

    previous_handler = signal.getsignal(signal.SIGALRM) if timeout_seconds else None

    def run_once():
        if timeout_seconds:
            signal.alarm(timeout_seconds)
        start = time.perf_counter()
        try:
            result = document_func(text)
            return {
                "seconds": time.perf_counter() - start,
                "count": count_document_results(label, result),
            }
        except DocumentTimeout:
            return {"timeout": f">{timeout_seconds}s", "count": None}
        except Exception:
            return None
        finally:
            if timeout_seconds:
                signal.alarm(0)

    if timeout_seconds:
        signal.signal(signal.SIGALRM, alarm_handler)

    try:
        warmup = run_once()
        if not isinstance(warmup, dict) or "seconds" not in warmup:
            return warmup

        times = []
        for _ in range(iterations):
            result = run_once()
            if not isinstance(result, dict) or "seconds" not in result:
                return result
            times.append(result["seconds"])
        return {
            "seconds": statistics.median(times),
            "count": warmup["count"],
        }
    finally:
        if previous_handler is not None:
            signal.signal(signal.SIGALRM, previous_handler)


def run_short_benchmark(bench):
    label = bench["label"]
    func = bench["func"]
    if func is None:
        return None
    for text in INPUTS[:5]:
        try:
            func(text)
        except Exception:
            pass

    start = time.perf_counter()
    successes = 0
    for text in INPUTS:
        try:
            successes += has_result(label, func(text))
        except Exception:
            pass
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
        "extracted": successes,
        "correctness": exact,
    }


def run_document_benchmark(bench, document_datasets):
    document_results = {"label": bench["label"]}
    for dataset_name, key, iterations in DOCUMENT_DATASETS:
        text = document_datasets.get(dataset_name)
        document_results[key] = (
            benchmark_document(
                bench["label"],
                bench["document_func"],
                text,
                iterations,
                bench.get("document_timeout_seconds"),
            ) if text is not None else None
        )
    return document_results


def sort_short_rows(rows):
    return sorted(rows, key=lambda row: (row["label"] != "timefhuman", row["us_per_input"]))


def sort_document_rows(rows):
    def sort_key(row):
        values = []
        for _, key, _ in DOCUMENT_DATASETS:
            value = row.get(key)
            if isinstance(value, dict) and "seconds" in value:
                values.append(value["seconds"])
            elif isinstance(value, dict) and "timeout" in value:
                values.append(float("inf"))
        aggregate = statistics.median(values) if values else float("inf")
        return (row["label"] != "timefhuman", aggregate)

    return sorted(rows, key=sort_key)


def main():
    benches = build_benches()
    document_datasets = load_document_datasets()
    short_rows = sort_short_rows([row for row in (run_short_benchmark(bench) for bench in benches) if row is not None])
    document_rows = sort_document_rows([run_document_benchmark(bench, document_datasets) for bench in benches if bench["document_func"] is not None])

    print("short-input parsing")
    print(
        f"{'parser':24} {'us/input':>10} {'extracted':>12} {'correctness':>13}"
    )
    for row in short_rows:
        print(
            f"{row['label']:24} "
            f"{row['us_per_input']:10.1f} "
            f"{row['extracted']:>2}/{len(INPUTS):<9} "
            f"{row['correctness']:>2}/{len(EXACT_CASES):<10}"
        )

    if document_rows:
        print()
        print("whole-document extraction")
        print(f"{'parser':24} {'core_corpus':>14} {'seattle_html_76k':>18} {'test_data_560k':>16}")

        def format_doc(value):
            if isinstance(value, dict) and "seconds" in value:
                return f"{value['seconds']:.4f} ({value['count']})"
            if isinstance(value, dict) and "timeout" in value:
                return f"{value['timeout']} (n/a)"
            if value is None:
                return "n/a"
            return str(value)

        for row in document_rows:
            print(
                f"{row['label']:24} "
                f"{format_doc(row['core_corpus']):>14} "
                f"{format_doc(row['seattle_html_76k']):>18} "
                f"{format_doc(row['test_data_560k']):>16}"
            )


if __name__ == "__main__":
    main()
