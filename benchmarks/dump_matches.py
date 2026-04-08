from __future__ import annotations

import signal
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from benchmarks.profiles import DOCUMENT_DATASETS, timeout_seconds_for
from benchmarks.shared import DOCUMENT_BENCH_BUILDERS, build_benches
from datasets.registry import get_dataset, load_dataset_text, resolve_dataset_path


OUTPUT_ROOT = Path(__file__).resolve().parent / "matches"


def output_label(label: str):
    if label == "dateparser*":
        return "dateparser"
    return label


def escape(value):
    text = str(value)
    return " ".join(text.split()).replace("|", "\\|")


def context_snippet(text, start, end, radius=40):
    left = max(0, start - radius)
    right = min(len(text), end + radius)
    return escape(text[left:right])


def format_match(label, match, text):
    if label == "timefhuman":
        matched_text, (start, end), value = match
        return {"match": matched_text, "value": repr(value), "span": f"{start}:{end}", "context": context_snippet(text, start, end)}
    if label == "datefinder.find_dates":
        value, matched_text, (start, end) = match
        return {"match": matched_text, "value": repr(value), "span": f"{start}:{end}", "context": context_snippet(text, start, end)}
    if label == "dateparser*":
        matched_text, value = match
        return {"match": matched_text, "value": repr(value), "span": "n/a", "context": "n/a"}
    raise ValueError(f"unsupported label: {label}")


def write_dump(label, dataset_name, source_path, text, matches):
    output_dir = OUTPUT_ROOT / output_label(label)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{dataset_name}.md"
    rows = [format_match(label, match, text) for match in matches]
    lines = [
        f"# {label} · {dataset_name}",
        "",
        f"- Source: {source_path}",
        f"- Total matches: {len(rows)}",
        "",
        "| # | match | normalized | span | context |",
        "| ---: | --- | --- | --- | --- |",
    ]
    for index, row in enumerate(rows, start=1):
        lines.append(
            f"| {index} | {escape(row['match'])} | {escape(row['value'])} | {escape(row['span'])} | {row['context']} |"
        )
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


class DumpTimeout(Exception):
    pass


def run_with_timeout(timeout_seconds, func, text):
    previous_handler = signal.getsignal(signal.SIGALRM)

    def alarm_handler(signum, frame):
        raise DumpTimeout()

    signal.signal(signal.SIGALRM, alarm_handler)
    signal.alarm(timeout_seconds)
    try:
        return func(text)
    except DumpTimeout:
        return None
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, previous_handler)


def main():
    benches = [bench for bench in build_benches(DOCUMENT_BENCH_BUILDERS) if bench.get("document_dump_func") is not None]
    source_paths = {}
    texts = {}
    for dataset_name, _ in DOCUMENT_DATASETS:
        text = load_dataset_text(dataset_name)
        if text is None:
            continue
        texts[dataset_name] = text
        source_paths[dataset_name] = resolve_dataset_path(dataset_name) or get_dataset(dataset_name)["source_hint"]

    if not texts:
        raise SystemExit("no datasets available; run python -m datasets.download")

    for bench in benches:
        for dataset_name, _ in DOCUMENT_DATASETS:
            text = texts.get(dataset_name)
            if text is None:
                continue
            matches = run_with_timeout(
                timeout_seconds_for(bench["label"]),
                bench["document_dump_func"],
                text,
            )
            if matches is None:
                continue
            write_dump(bench["label"], dataset_name, source_paths[dataset_name], text, matches)


if __name__ == "__main__":
    main()
