from __future__ import annotations

import argparse
import contextlib
import io
import json
import statistics
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from benchmarks.profiles import (  # noqa: E402
    CASE_PROFILE,
    DOCUMENT_DATASETS,
    DOCUMENT_PROFILE,
    DOCUMENT_SAMPLE_GRACE_SECONDS,
    SHORT_SAMPLES,
    timeout_seconds_for,
)
from benchmarks.shared import (  # noqa: E402
    BenchmarkTimeout,
    CASE_BENCH_BUILDERS,
    DOCUMENT_BENCH_BUILDERS,
    NOW,
    build_benches,
    count_group_matches,
    count_member_matches,
    exact_case_match,
    extract_result_items,
    flatten_value_members,
    normalize_exact_result,
    timeout_call,
)
from datasets.registry import get_cases, load_case_text, load_dataset_text  # noqa: E402


SHORT_EXACT_CASES = [
    case
    for case in get_cases("short", tags={"default"})
    if case["assertion"] == "exact"
    and len(case["expected"]) == 1
    and isinstance(case["expected"][0], datetime)
]
SHORT_PERF_INPUTS = [case["text"] for case in SHORT_EXACT_CASES]
ENRON_CASES = list(get_cases(CASE_PROFILE["dataset"], mode="snippet"))
DOCUMENT_CASES = {
    dataset_name: get_cases(dataset_name, mode="document")[0]
    for dataset_name, _ in DOCUMENT_DATASETS
}


def parse_args():
    parser = argparse.ArgumentParser(description="Run timefhuman benchmark profiles.")
    parser.add_argument("--profile", choices=("document", "case"), default="document")
    parser.add_argument("--format", choices=("text", "markdown", "json"), default="text")
    parser.add_argument("--write-json", dest="write_json")
    parser.add_argument("--labels", help="Comma-separated parser labels to include")
    parser.add_argument("--sample", nargs=3, metavar=("LABEL", "KIND", "ARG"))
    return parser.parse_args()


def profile_builders(profile: str):
    if profile == "document":
        return DOCUMENT_BENCH_BUILDERS
    if profile == "case":
        return CASE_BENCH_BUILDERS
    raise ValueError(f"unknown profile: {profile}")


def build_profile_benches(profile: str, labels: set[str] | None = None):
    builders = profile_builders(profile)
    if labels is not None:
        builders = {label: builder for label, builder in builders.items() if label in labels}
    return build_benches(builders)


def find_bench(profile: str, label: str):
    builder = profile_builders(profile).get(label)
    return builder() if builder else None


def get_document_runner(bench: dict):
    return bench.get("document_dump_func") or bench.get("document_func") or bench.get("func")


def count_document_results(label: str, result):
    return len(extract_result_items(label, result))


def run_quietly(func, *args):
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        return func(*args)


def run_process_sample(profile: str, label: str, sample_kind: str, sample_arg: str, timeout_seconds: int):
    cmd = [
        sys.executable,
        str(Path(__file__).resolve()),
        "--profile",
        profile,
        "--sample",
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
            timeout=timeout_seconds + DOCUMENT_SAMPLE_GRACE_SECONDS,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return {"timeout": f">{timeout_seconds}s"}

    output_lines = [line for line in completed.stdout.splitlines() if line.strip()]
    if not output_lines:
        return {"error": "ChildProcessError" if completed.returncode else "NoOutput"}

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


def emit_process_sample(profile: str, label: str, sample_kind: str, sample_arg: str):
    bench = find_bench(profile, label)
    if bench is None:
        print(json.dumps({"status": "error", "error": "UnknownBench"}))
        return

    timeout_seconds = timeout_seconds_for(label)

    try:
        if profile == "document" and sample_kind == "short":
            func = bench["func"]
            if func is None:
                print(json.dumps({"status": "n/a"}))
                return

            def run_batch():
                start = time.perf_counter()
                run_quietly(lambda: [func(text) for text in SHORT_PERF_INPUTS])
                return time.perf_counter() - start

            seconds = timeout_call(timeout_seconds, run_batch)
            print(json.dumps({"status": "ok", "seconds": seconds}))
            return

        if profile == "document" and sample_kind == "document":
            text = load_dataset_text(sample_arg)
            runner = get_document_runner(bench)
            if text is None or runner is None:
                print(json.dumps({"status": "n/a"}))
                return

            start = time.perf_counter()
            result = timeout_call(timeout_seconds, run_quietly, runner, text)
            print(json.dumps({
                "status": "ok",
                "seconds": time.perf_counter() - start,
                "count": count_document_results(label, result),
            }))
            return

        if profile == "case" and sample_kind == "case":
            case = ENRON_CASES[int(sample_arg)]
            runner = bench["runner"]
            reference_now = case["config"]["now"]
            start = time.perf_counter()
            timeout_call(timeout_seconds, run_quietly, runner, case["text"], reference_now)
            print(json.dumps({"status": "ok", "seconds": time.perf_counter() - start}))
            return

        print(json.dumps({"status": "error", "error": "UnknownSampleKind"}))
    except BenchmarkTimeout:
        print(json.dumps({"status": "timeout"}))
    except Exception as exc:
        print(json.dumps({"status": "error", "error": type(exc).__name__}))


def benchmark_short_perf(label: str, func):
    if func is None:
        return None

    timeout_seconds = timeout_seconds_for(label)
    samples_ms = []
    for _ in range(SHORT_SAMPLES):
        sample = run_process_sample("document", label, "short", "", timeout_seconds)
        if "timeout" in sample:
            return {"timeout": sample["timeout"]}
        if "error" in sample:
            return {"error": sample["error"]}
        samples_ms.append(sample["seconds"] * 1000.0 / len(SHORT_PERF_INPUTS))
    return {"median_ms": statistics.median(samples_ms)}


def benchmark_document_perf(label: str, dataset_name: str, iterations: int):
    timeout_seconds = timeout_seconds_for(label)
    samples_ms = []
    count = None
    for _ in range(iterations):
        sample = run_process_sample("document", label, "document", dataset_name, timeout_seconds)
        if "timeout" in sample:
            return {"timeout": sample["timeout"], "count": None}
        if "error" in sample:
            return {"error": sample["error"], "count": None}
        samples_ms.append(sample["seconds"] * 1000.0)
        if count is None:
            count = sample.get("count")
    return {"median_ms": statistics.median(samples_ms), "count": count}


def run_short_correctness(bench: dict):
    label = bench["label"]
    func = bench["func"]
    if func is None:
        return None

    exact = 0
    total = len(SHORT_EXACT_CASES)
    for case in SHORT_EXACT_CASES:
        try:
            exact += normalize_exact_result(label, case["text"], func) == case["expected"][0]
        except Exception:
            pass
    return {"matched": exact, "total": total}


def run_document_correctness(label: str, bench: dict, case: dict):
    runner = get_document_runner(bench)
    text = load_case_text(case)
    expected = case["expected"]
    if runner is None or text is None:
        return {"member": None, "group": None}

    timeout_seconds = timeout_seconds_for(label)
    try:
        matches = timeout_call(timeout_seconds, run_quietly, runner, text)
    except BenchmarkTimeout:
        timeout = f">{timeout_seconds}s"
        return {"member": {"timeout": timeout}, "group": {"timeout": timeout}}
    except Exception as exc:
        error = {"error": type(exc).__name__}
        return {"member": error, "group": error}

    reference_now = case["config"].get("now", NOW)
    return {
        "member": count_member_matches(label, matches, expected, reference_now=reference_now),
        "group": {
            "matched": count_group_matches(label, matches, expected, reference_now=reference_now),
            "total": len(expected),
        },
    }


def evaluate_document_bench(bench: dict):
    label = bench["label"]
    row = {"label": label}
    row["short"] = {
        **(benchmark_short_perf(label, bench["func"]) or {}),
        "correctness": run_short_correctness(bench),
    }

    for dataset_name, iterations in DOCUMENT_DATASETS:
        perf = benchmark_document_perf(label, dataset_name, iterations)
        correctness = run_document_correctness(label, bench, DOCUMENT_CASES[dataset_name])
        row[dataset_name] = {
            **perf,
            "member": correctness["member"],
            "group": correctness["group"],
        }
    return row


def evaluate_case_bench(bench: dict):
    label = bench["label"]
    runner = bench["runner"]
    exact_matched = 0
    group_matched = 0
    member_matched = 0
    samples_ms = []
    group_total = sum(len(case["expected"]) for case in ENRON_CASES)
    member_total = sum(
        len(flatten_value_members(value))
        for case in ENRON_CASES
        for _, _, value in case["expected"]
    )
    correctness_timeout_count = 0
    correctness_errors = {}

    for case in ENRON_CASES:
        reference_now = case["config"]["now"]
        try:
            start = time.perf_counter()
            result = timeout_call(timeout_seconds_for(label), run_quietly, runner, case["text"], reference_now)
        except BenchmarkTimeout:
            correctness_timeout_count += 1
            continue
        except Exception as exc:
            error_name = type(exc).__name__
            correctness_errors[error_name] = correctness_errors.get(error_name, 0) + 1
            continue
        samples_ms.append((time.perf_counter() - start) * 1000.0)

        if exact_case_match(label, result, case["expected"], reference_now=reference_now):
            exact_matched += 1
        group_matched += count_group_matches(label, result, case["expected"], reference_now=reference_now)
        member_matched += count_member_matches(
            label,
            result,
            case["expected"],
            reference_now=reference_now,
        )["matched"]

    return {
        "label": label,
        "exact": {"matched": exact_matched, "total": len(ENRON_CASES)},
        "group": {"matched": group_matched, "total": group_total},
        "member": {"matched": member_matched, "total": member_total},
        "median_ms": statistics.median(samples_ms) if samples_ms else None,
        "timeouts": correctness_timeout_count,
        "errors": correctness_errors,
    }


def sort_document_rows(rows: list[dict]):
    def sort_key(row: dict):
        short_correctness = row["short"]["correctness"]
        short_ratio = (
            short_correctness["matched"] / short_correctness["total"]
            if short_correctness and short_correctness["total"]
            else -1
        )
        short_median = row["short"].get("median_ms")
        short_median = short_median if isinstance(short_median, (int, float)) else float("inf")
        return (row["label"] != "timefhuman", -short_ratio, short_median, row["label"])

    return sorted(rows, key=sort_key)


def sort_case_rows(rows: list[dict]):
    def sort_key(row: dict):
        member_ratio = row["member"]["matched"] / row["member"]["total"] if row["member"]["total"] else -1
        median_ms = row["median_ms"] if isinstance(row["median_ms"], (int, float)) else float("inf")
        return (row["label"] != "timefhuman", -member_ratio, median_ms, row["label"])

    return sorted(rows, key=sort_key)


def build_document_payload(labels: set[str] | None = None):
    rows = sort_document_rows([evaluate_document_bench(bench) for bench in build_profile_benches("document", labels=labels)])
    return {
        "profile": "document",
        "timing": "cold",
        "rows": rows,
        "datasets": [dataset_name for dataset_name, _ in DOCUMENT_DATASETS],
        "short_cases": len(SHORT_EXACT_CASES),
    }


def build_case_payload(labels: set[str] | None = None):
    rows = sort_case_rows([evaluate_case_bench(bench) for bench in build_profile_benches("case", labels=labels)])
    return {
        "profile": "case",
        "timing": "same_process",
        "dataset": CASE_PROFILE["dataset"],
        "cases": len(ENRON_CASES),
        "published_metric": "member",
        "rows": rows,
    }


def format_fraction(value):
    return f"{value['matched']}/{value['total']}"


def format_ms(value):
    if value is None:
        return "n/a"
    if value < 0.1:
        return "<0.1"
    return f"{value:.1f}"


def format_perf_cell(cell: dict):
    if cell is None:
        return "n/a"
    if "timeout" in cell:
        return cell["timeout"]
    if "error" in cell:
        return cell["error"]
    value = cell.get("median_ms")
    return format_ms(value)


def format_correctness_cell(cell: dict):
    if cell is None:
        return "n/a"
    if "timeout" in cell:
        return "timeout"
    if "error" in cell:
        return cell["error"]
    return format_fraction(cell)


def print_document_text(payload: dict):
    print("document benchmark")
    print(
        f"{'parser':24} {'short ms':>10} {'acc':>10} "
        f"{'core ms':>10} {'#':>6} {'acc':>10} {'group':>10} "
        f"{'sea ms':>10} {'#':>6} {'acc':>10} {'group':>10} "
        f"{'560k ms':>10} {'#':>6} {'acc':>10} {'group':>10}"
    )
    for row in payload["rows"]:
        core = row["core_corpus"]
        sea = row["seattle_html_76k"]
        test_data = row["test_data_560k"]
        print(
            f"{row['label']:24} "
            f"{format_perf_cell(row['short']):>10} "
            f"{format_correctness_cell(row['short']['correctness']):>10} "
            f"{format_perf_cell(core):>10} {str(core.get('count', 'n/a')):>6} "
            f"{format_correctness_cell(core['member']):>10} {format_correctness_cell(core['group']):>10} "
            f"{format_perf_cell(sea):>10} {str(sea.get('count', 'n/a')):>6} "
            f"{format_correctness_cell(sea['member']):>10} {format_correctness_cell(sea['group']):>10} "
            f"{format_perf_cell(test_data):>10} {str(test_data.get('count', 'n/a')):>6} "
            f"{format_correctness_cell(test_data['member']):>10} {format_correctness_cell(test_data['group']):>10}"
        )


def print_document_markdown(payload: dict):
    print("| parser | short (ms) | acc | core (ms) | # | acc | group | sea_76k (ms) | # | acc | group | test_data_560k (ms) | # | acc | group |")
    print("| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
    for row in payload["rows"]:
        core = row["core_corpus"]
        sea = row["seattle_html_76k"]
        test_data = row["test_data_560k"]
        print(
            f"| {row['label']} | {format_perf_cell(row['short'])} | {format_correctness_cell(row['short']['correctness'])} | "
            f"{format_perf_cell(core)} | {core.get('count', 'n/a')} | {format_correctness_cell(core['member'])} | {format_correctness_cell(core['group'])} | "
            f"{format_perf_cell(sea)} | {sea.get('count', 'n/a')} | {format_correctness_cell(sea['member'])} | {format_correctness_cell(sea['group'])} | "
            f"{format_perf_cell(test_data)} | {test_data.get('count', 'n/a')} | {format_correctness_cell(test_data['member'])} | {format_correctness_cell(test_data['group'])} |"
        )


def print_case_text(payload: dict):
    print("case benchmark")
    print(f"{'parser':24} {'exact':>10} {'group':>10} {'member':>10} {'median ms':>10}")
    for row in payload["rows"]:
        print(
            f"{row['label']:24} {format_fraction(row['exact']):>10} {format_fraction(row['group']):>10} "
            f"{format_fraction(row['member']):>10} {format_ms(row['median_ms']):>10}"
        )


def print_case_markdown(payload: dict):
    print("| parser | exact | group | member | median per snippet (ms) |")
    print("| --- | ---: | ---: | ---: | ---: |")
    for row in payload["rows"]:
        print(
            f"| {row['label']} | {format_fraction(row['exact'])} | {format_fraction(row['group'])} | "
            f"{format_fraction(row['member'])} | {format_ms(row['median_ms'])} |"
        )


def main():
    args = parse_args()
    if args.sample:
        label, sample_kind, sample_arg = args.sample
        emit_process_sample(args.profile, label, sample_kind, sample_arg)
        return

    labels = set(filter(None, (args.labels or "").split(","))) or None
    payload = build_document_payload(labels=labels) if args.profile == "document" else build_case_payload(labels=labels)

    if args.write_json:
        output_path = Path(args.write_json)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    if args.format == "json":
        print(json.dumps(payload, indent=2))
        return
    if args.format == "markdown":
        if args.profile == "document":
            print_document_markdown(payload)
        else:
            print_case_markdown(payload)
        return
    if args.profile == "document":
        print_document_text(payload)
    else:
        print_case_text(payload)


if __name__ == "__main__":
    main()
