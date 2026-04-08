import argparse
import contextlib
import io
import json
import statistics
import sys
import time
from datetime import date, datetime, timedelta
from pathlib import Path

BENCHMARKS_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(BENCHMARKS_ROOT) not in sys.path:
    sys.path.insert(0, str(BENCHMARKS_ROOT))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from benchmark_baselines import BenchmarkTimeout, _timeout_call, canonicalize_value, extract_result_items as baseline_extract_result_items, supports_text_matches
from eval.corpora import ENRON_EMAILS_CONTEXT_CASES
from timefhuman import timefhuman
from timefhuman.main import tfhConfig


CASE_TIMEOUT_SECONDS = 2
DATEPARSER_TIMEOUT_SECONDS = 30


def build_benches():
    benches = []

    benches.append(
        {
            "label": "timefhuman",
            "runner": lambda text, sent_at: timefhuman(
                text,
                config=tfhConfig(now=sent_at, return_matched_text=True),
            ),
        }
    )

    try:
        import dateparser
        from dateparser.search import search_dates as dateparser_search_dates
    except ImportError:
        pass
    else:
        benches.append(
            {
                "label": "dateparser*",
                "runner": lambda text, sent_at: dateparser_search_dates(
                    text,
                    settings={"RELATIVE_BASE": sent_at},
                ),
            }
        )

    try:
        import parsedatetime
    except ImportError:
        pass
    else:
        calendar = parsedatetime.Calendar()
        benches.append(
            {
                "label": "parsedatetime.parseDT",
                "runner": lambda text, sent_at: calendar.parseDT(text, sent_at),
            }
        )

    try:
        import datefinder
    except ImportError:
        pass
    else:
        benches.append(
            {
                "label": "datefinder.find_dates",
                "runner": lambda text, sent_at: list(
                    datefinder.find_dates(text, base_date=sent_at, source=True, index=True)
                ),
            }
        )

    try:
        import ctparse
    except ImportError:
        pass
    else:
        benches.append(
            {
                "label": "ctparse.ctparse",
                "runner": lambda text, sent_at: ctparse.ctparse(text, ts=sent_at),
            }
        )

    try:
        import recurrent
    except ImportError:
        pass
    else:
        benches.append(
            {
                "label": "recurrent.parse",
                "runner": lambda text, sent_at: recurrent.parse(text, sent_at),
            }
        )

    try:
        import metadate
    except ImportError:
        pass
    else:
        benches.append(
            {
                "label": "metadate.parse_date",
                "runner": lambda text, sent_at: metadate.parse_date(
                    text,
                    reference_date=sent_at,
                    multi=True,
                    use_c_scanner=True,
                ),
            }
        )

    return benches


def timeout_seconds_for(label):
    return DATEPARSER_TIMEOUT_SECONDS if label == "dateparser*" else CASE_TIMEOUT_SECONDS


def safe_ctparse_dt(value):
    try:
        return getattr(value, "dt", None)
    except ValueError:
        return None


def extract_result_items(label, result):
    if label == "ctparse.ctparse" and result is not None:
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
    return baseline_extract_result_items(label, result)


def values_equivalent(actual, expected):
    actual = canonicalize_value(actual)
    expected = canonicalize_value(expected)

    if actual == expected:
        return True

    if isinstance(actual, datetime) and isinstance(expected, datetime):
        return actual.replace(tzinfo=None) == expected.replace(tzinfo=None)

    if isinstance(expected, date) and not isinstance(expected, datetime):
        return isinstance(actual, datetime) and actual.date() == expected

    if isinstance(expected, timedelta):
        return isinstance(actual, datetime) and actual == expected

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


def count_group_matches(label, result, expected):
    actual_items = [(matched_text, canonicalize_value(value)) for matched_text, value in extract_result_items(label, result)]
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


def count_member_matches(label, result, expected):
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
            if values_equivalent(actual_value, expected_value):
                remaining_actual.pop(actual_index)
                count += 1
                break

    return count, len(expected_members)


def exact_case_match(label, result, expected):
    actual_items = [(matched_text, canonicalize_value(value)) for matched_text, value in extract_result_items(label, result)]
    if len(actual_items) != len(expected):
        return False

    remaining_actual = list(actual_items)
    for expected_text, _, expected_value in expected:
        matched = False
        for actual_index, (actual_text, actual_value) in enumerate(remaining_actual):
            if supports_text_matches(label) and actual_text != expected_text:
                continue
            if values_equivalent(actual_value, expected_value):
                remaining_actual.pop(actual_index)
                matched = True
                break
        if not matched:
            return False

    return not remaining_actual


def evaluate_bench(bench):
    label = bench["label"]
    runner = bench["runner"]
    timeout_seconds = timeout_seconds_for(label)
    group_total = sum(len(case["expected"]) for case in ENRON_EMAILS_CONTEXT_CASES)
    member_total = 0
    for case in ENRON_EMAILS_CONTEXT_CASES:
        for _, _, value in case["expected"]:
            member_total += len(flatten_value_members(value))
    exact_matched = 0
    group_matched = 0
    member_matched = 0
    samples_ms = []
    timeout_count = 0
    error_counts = {}

    for case in ENRON_EMAILS_CONTEXT_CASES:
        start = time.perf_counter()
        try:
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                result = _timeout_call(timeout_seconds, runner, case["text"], case["sent_at"])
        except BenchmarkTimeout:
            timeout_count += 1
            continue
        except Exception as exc:
            error_name = type(exc).__name__
            error_counts[error_name] = error_counts.get(error_name, 0) + 1
            continue

        samples_ms.append((time.perf_counter() - start) * 1000.0)
        if exact_case_match(label, result, case["expected"]):
            exact_matched += 1

        group_matched += count_group_matches(label, result, case["expected"])

        matched, _ = count_member_matches(label, result, case["expected"])
        member_matched += matched

    return {
        "label": label,
        "exact": {"matched": exact_matched, "total": len(ENRON_EMAILS_CONTEXT_CASES)},
        "group": {"matched": group_matched, "total": group_total},
        "member": {"matched": member_matched, "total": member_total},
        "median_ms": statistics.median(samples_ms) if samples_ms else None,
        "timeouts": timeout_count,
        "errors": error_counts,
    }


def sort_rows(rows):
    def sort_key(row):
        member = row["member"]
        member_ratio = member["matched"] / member["total"] if member["total"] else -1
        median_ms = row["median_ms"] if isinstance(row["median_ms"], (int, float)) else float("inf")
        return (row["label"] != "timefhuman", -member_ratio, median_ms, row["label"])

    return sorted(rows, key=sort_key)


def format_fraction(value):
    return f"{value['matched']}/{value['total']}"


def format_ms(value):
    if isinstance(value, (int, float)):
        if value < 0.1:
            return "<0.1"
        return f"{value:.1f}"
    return "n/a"


def print_text_table(rows):
    print("enron contextual benchmark")
    print(
        f"{'parser':24} {'exact':>10} {'group':>10} {'member':>10} {'median ms':>10}"
    )
    for row in rows:
        print(
            f"{row['label']:24} "
            f"{format_fraction(row['exact']):>10} "
            f"{format_fraction(row['group']):>10} "
            f"{format_fraction(row['member']):>10} "
            f"{format_ms(row['median_ms']):>10}"
        )


def print_markdown_table(rows):
    print("| parser | exact | group | member | median per snippet (ms) |")
    print("| --- | ---: | ---: | ---: | ---: |")
    for row in rows:
        print(
            f"| {row['label']} | {format_fraction(row['exact'])} | {format_fraction(row['group'])} | "
            f"{format_fraction(row['member'])} | {format_ms(row['median_ms'])} |"
        )


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--format", choices=("text", "markdown", "json"), default="text")
    parser.add_argument("--write-json", dest="write_json")
    return parser.parse_args()


def main():
    args = parse_args()
    rows = sort_rows([evaluate_bench(bench) for bench in build_benches()])
    payload = {
        "dataset": "enron_emails",
        "cases": len(ENRON_EMAILS_CONTEXT_CASES),
        "published_metric": "member",
        "rows": rows,
    }

    if args.write_json:
        output_path = Path(args.write_json)
        output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    if args.format == "json":
        print(json.dumps(payload, indent=2))
        return
    if args.format == "markdown":
        print_markdown_table(rows)
        return
    print_text_table(rows)


if __name__ == "__main__":
    main()
