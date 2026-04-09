#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from xml.sax.saxutils import escape

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from benchmarks.profiles import CASE_PROFILE, DOCUMENT_PROFILE


FONT = "ui-sans-serif, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif"

BG = "var(--bg)"
PANEL = "var(--panel)"
PANEL_STROKE = "var(--panel-stroke)"
GRID = "var(--grid)"
AXIS = "var(--axis)"
TEXT = "var(--text)"
MUTED = "var(--muted)"

TIMEFHUMAN_COLOR = "#1f7a5a"
BASELINE_COLORS = {
    "parsedatetime.parseDT": "#5f6875",
    "recurrent.parse": "#727c89",
    "ctparse.ctparse": "#858f9c",
    "dateparser*": "#98a2af",
    "datefinder.find_dates": "#acb5c1",
}

DOCUMENT_ROWS = ("timefhuman", "datefinder.find_dates")
DOCUMENT_DATASETS = (
    ("short", "short"),
    ("core_corpus", "core"),
    ("seattle_html_76k", "sea_76k"),
    ("test_data_560k", "test_data_560k"),
)
CASE_LABELS = {
    "timefhuman": "timefhuman",
    "ctparse.ctparse": "ctparse",
    "parsedatetime.parseDT": "parsedatetime",
    "recurrent.parse": "recurrent",
    "dateparser*": "dateparser",
    "datefinder.find_dates": "datefinder",
}
CASE_ROWS = (
    "timefhuman",
    "parsedatetime.parseDT",
    "recurrent.parse",
    "ctparse.ctparse",
    "dateparser*",
    "datefinder.find_dates",
)


def parse_args():
    parser = argparse.ArgumentParser(description="Generate benchmark SVG summaries.")
    parser.add_argument("--profile", choices=("case", "document"), default="case")
    parser.add_argument("--input", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--with-title", action="store_true")
    return parser.parse_args()


def default_paths(profile: str):
    if profile == "case":
        return CASE_PROFILE["snapshot"], CASE_PROFILE["svg"]
    return DOCUMENT_PROFILE["snapshot"], DOCUMENT_PROFILE["svg"]


def style_block():
    return """
<style>
  svg {
    color-scheme: light dark;
    --bg: #ffffff;
    --panel: #fafbfc;
    --panel-stroke: #e4e7ec;
    --grid: #eceef2;
    --axis: #d5d8df;
    --text: #1c1f24;
    --muted: #5d6674;
  }

  @media (prefers-color-scheme: dark) {
    svg {
      --bg: #0e1117;
      --panel: #151a23;
      --panel-stroke: #2f3847;
      --grid: #2a3140;
      --axis: #3a4456;
      --text: #f3f5f8;
      --muted: #b7bfcb;
    }
  }
</style>""".strip()


def svg_text(x, y, text, size=14, weight="400", anchor="start", fill=TEXT):
    return (
        f'<text x="{x:.1f}" y="{y:.1f}" fill="{fill}" font-family="{FONT}" '
        f'font-size="{size}" font-weight="{weight}" text-anchor="{anchor}">'
        f"{escape(text)}</text>"
    )


def svg_rect(x, y, width, height, fill, rx=8, stroke="none", stroke_width=1):
    return (
        f'<rect x="{x:.1f}" y="{y:.1f}" width="{width:.1f}" height="{height:.1f}" '
        f'rx="{rx:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width}" />'
    )


def document_label(label: str):
    return "datefinder" if label == "datefinder.find_dates" else label


def parser_color(label: str):
    if label == "timefhuman":
        return TIMEFHUMAN_COLOR
    return BASELINE_COLORS.get(label, "#8a94a3")


def build_document_svg(payload: dict, with_title: bool):
    rows_by_label = {row["label"]: row for row in payload["rows"]}
    series = [rows_by_label[label] for label in DOCUMENT_ROWS if label in rows_by_label]

    width = 1180
    title_padding = 60
    embed_padding = 0
    title_panel_gap = 20
    embed_panel_gap = 8
    outer_pad = title_padding if with_title else embed_padding
    panel_gap = title_panel_gap if with_title else embed_panel_gap
    height = 620 if with_title else 424
    panel_top = 154 if with_title else 40
    panel_height = 380 if with_title else 344
    panel_width = (width - outer_pad * 2 - panel_gap) / 2
    legend_y = 126 if with_title else 18
    title_y = 58 if with_title else 0
    subtitle_y = 86 if with_title else 0

    def panel_origin(index: int):
        return outer_pad + index * (panel_width + panel_gap), panel_top

    def fmt_percent(value: float):
        if value >= 99.95:
            return "100"
        return f"{value:.0f}"

    def fmt_ms(value: float):
        if value >= 100:
            return f"{value:.0f}"
        return f"{value:.1f}"

    def draw_panel_frame(elements, x, y, title, subtitle):
        elements.append(svg_rect(x, y, panel_width, panel_height, PANEL, rx=18, stroke=PANEL_STROKE))
        elements.append(svg_text(x + 24, y + 28, title, size=20, weight="700"))
        elements.append(svg_text(x + 24, y + 46, subtitle, size=12, fill=MUTED))

    def draw_legend(elements):
        legend_x = width - outer_pad - 386
        for index, row in enumerate(series):
            x = legend_x + index * 180
            elements.append(svg_rect(x, legend_y - 14, 18, 18, parser_color(row["label"]), rx=4))
            elements.append(svg_text(x + 28, legend_y, document_label(row["label"]), size=14, weight="700"))

    def draw_grouped_bars(elements, values_key, index, title, subtitle, y_ticks, y_formatter, projector, best_rule):
        x, y = panel_origin(index)
        draw_panel_frame(elements, x, y, title, subtitle)
        axis_left = x + 56
        axis_right = x + panel_width - 24
        axis_top = y + 78
        axis_bottom = y + panel_height - 54
        axis_width = axis_right - axis_left
        axis_height = axis_bottom - axis_top
        group_width = axis_width / len(DOCUMENT_DATASETS)
        bar_width = 28
        bar_gap = 10

        for tick in y_ticks:
            frac = projector(tick)
            tick_y = axis_bottom - axis_height * frac
            elements.append(
                f'<line x1="{axis_left:.1f}" y1="{tick_y:.1f}" x2="{axis_right:.1f}" y2="{tick_y:.1f}" '
                f'stroke="{GRID}" stroke-width="1" />'
            )
            elements.append(svg_text(axis_left - 10, tick_y + 5, y_formatter(tick), size=11, anchor="end", fill=MUTED))

        elements.append(f'<line x1="{axis_left:.1f}" y1="{axis_top:.1f}" x2="{axis_left:.1f}" y2="{axis_bottom:.1f}" stroke="{AXIS}" />')
        elements.append(f'<line x1="{axis_left:.1f}" y1="{axis_bottom:.1f}" x2="{axis_right:.1f}" y2="{axis_bottom:.1f}" stroke="{AXIS}" />')

        for dataset_index, (dataset_key, dataset_label) in enumerate(DOCUMENT_DATASETS):
            center = axis_left + group_width * (dataset_index + 0.5)
            start_x = center - (bar_width + bar_gap / 2)
            dataset_values = [row[values_key][dataset_index] for row in series]
            winner = best_rule(dataset_values)

            elements.append(svg_text(center, axis_bottom + 26, dataset_label, size=11, anchor="middle", fill=MUTED))
            for series_index, row in enumerate(series):
                value = row[values_key][dataset_index]
                frac = projector(value)
                height_value = axis_height * frac
                bar_x = start_x + series_index * (bar_width + bar_gap)
                bar_y = axis_bottom - height_value
                elements.append(svg_rect(bar_x, bar_y, bar_width, height_value, parser_color(row["label"]), rx=6))
                label_fill = parser_color(row["label"]) if series_index == winner else MUTED
                elements.append(
                    svg_text(
                        bar_x + bar_width / 2,
                        bar_y - 8,
                        fmt_percent(value) if values_key == "accuracy" else fmt_ms(value),
                        size=11,
                        weight="700",
                        anchor="middle",
                        fill=label_fill,
                    )
                )

    accuracy_values = [
        [row["short"]["correctness"]["matched"] / row["short"]["correctness"]["total"] * 100.0 for row in series],
        [row["core_corpus"]["member"]["matched"] / row["core_corpus"]["member"]["total"] * 100.0 for row in series],
        [row["seattle_html_76k"]["member"]["matched"] / row["seattle_html_76k"]["member"]["total"] * 100.0 for row in series],
        [row["test_data_560k"]["member"]["matched"] / row["test_data_560k"]["member"]["total"] * 100.0 for row in series],
    ]
    latency_values = [
        [row["short"]["median_ms"] for row in series],
        [row["core_corpus"]["median_ms"] for row in series],
        [row["seattle_html_76k"]["median_ms"] for row in series],
        [row["test_data_560k"]["median_ms"] for row in series],
    ]

    for row_index, row in enumerate(series):
        row["accuracy"] = [column[row_index] for column in accuracy_values]
        row["latency_ms"] = [column[row_index] for column in latency_values]

    log_min = math.log10(1)
    log_max = math.log10(1000)

    elements = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" fill="none" role="img" aria-labelledby="title desc">',
        '<title id="title">Document benchmark summary</title>',
        '<desc id="desc">Cold-start median document latency and member accuracy for timefhuman and datefinder.</desc>',
        style_block(),
        svg_rect(0, 0, width, height, BG, rx=0),
    ]

    if with_title:
        elements.append(svg_text(outer_pad, title_y, "Benchmark Summary", size=28, weight="800"))
        elements.append(svg_text(outer_pad, subtitle_y, "Cold-start median latencies and member accuracy", size=14, fill=MUTED))
    draw_legend(elements)
    draw_grouped_bars(
        elements,
        "accuracy",
        0,
        "Accuracy",
        "Member acc",
        (0, 25, 50, 75, 100),
        lambda tick: str(int(tick)),
        lambda value: value / 100.0,
        lambda values: max(range(len(values)), key=values.__getitem__),
    )
    draw_grouped_bars(
        elements,
        "latency_ms",
        1,
        "Latency",
        "Cold-start median latencies",
        (1, 10, 100, 1000),
        lambda tick: f"{int(tick)}",
        lambda value: (math.log10(value) - log_min) / (log_max - log_min),
        lambda values: min(range(len(values)), key=values.__getitem__),
    )
    elements.append("</svg>")
    return "\n".join(elements) + "\n"


def build_case_svg(payload: dict):
    rows_by_label = {row["label"]: row for row in payload["rows"]}
    rows = [rows_by_label[label] for label in CASE_ROWS if label in rows_by_label]

    width = 980
    height = 344
    panel_gap = 20
    panel_width = (width - panel_gap) / 2
    panel_height = 296
    panel_top = 28
    label_width = 118
    panel_inset_x = 16
    panel_inset_right = 14
    bar_height = 22
    row_gap = 15
    header_height = 56
    axis_bottom_margin = 32
    bar_radius = 6

    def fmt_pct(value):
        return f"{value * 100:.1f}%"

    def fmt_ms(value):
        if value < 0.1:
            return "<0.1 ms"
        return f"{value:.1f} ms"

    def panel_origin(index):
        return index * (panel_width + panel_gap), panel_top

    def draw_panel_frame(elements, x, y, title, subtitle):
        elements.append(svg_rect(x, y, panel_width, panel_height, PANEL, rx=14, stroke=PANEL_STROKE))
        elements.append(svg_text(x + 16, y + 26, title, size=16, weight="600"))
        elements.append(svg_text(x + 16, y + 44, subtitle, size=12, fill=MUTED))

    def draw_accuracy_panel(elements):
        x, y = panel_origin(0)
        axis_left = x + panel_inset_x + label_width
        axis_right = x + panel_width - panel_inset_right
        axis_top = y + header_height
        axis_bottom = y + panel_height - axis_bottom_margin
        axis_width = axis_right - axis_left
        draw_panel_frame(
            elements,
            x,
            y,
            "Enron Email Dataset Accuracy",
            "Member accuracy on reviewed email snippets; higher is better",
        )
        for tick in (0.0, 0.5, 1.0):
            tick_x = axis_left + axis_width * tick
            elements.append(f'<line x1="{tick_x}" y1="{axis_top}" x2="{tick_x}" y2="{axis_bottom}" stroke="{GRID}" />')
            elements.append(svg_text(tick_x, axis_bottom + 18, f"{int(tick * 100)}%", size=11, anchor="middle", fill=MUTED))
        elements.append(f'<line x1="{axis_left}" y1="{axis_bottom}" x2="{axis_right}" y2="{axis_bottom}" stroke="{AXIS}" />')
        for index, row in enumerate(rows):
            ratio = row["member"]["matched"] / row["member"]["total"]
            row_y = axis_top + index * (bar_height + row_gap)
            width_value = axis_width * ratio
            elements.append(svg_text(x + panel_inset_x, row_y + bar_height * 0.72, CASE_LABELS[row["label"]], size=12, fill=MUTED))
            elements.append(svg_rect(axis_left, row_y, axis_width, bar_height, "none", rx=bar_radius, stroke=GRID))
            elements.append(svg_rect(axis_left, row_y, width_value, bar_height, parser_color(row["label"]), rx=bar_radius))
            label_x = axis_left + min(width_value + 8, axis_width - 4)
            elements.append(svg_text(label_x, row_y + bar_height * 0.72, fmt_pct(ratio), size=11, weight="600"))

    def draw_latency_panel(elements):
        x, y = panel_origin(1)
        axis_left = x + panel_inset_x + label_width
        axis_right = x + panel_width - panel_inset_right
        axis_top = y + header_height
        axis_bottom = y + panel_height - axis_bottom_margin
        axis_width = axis_right - axis_left
        min_ms = 0.1
        min_visible_bar_width = 6
        max_ms = 10 ** max(1, math.ceil(math.log10(max(row["median_ms"] for row in rows))))
        log_min = math.log10(min_ms)
        log_max = math.log10(max_ms)
        draw_panel_frame(
            elements,
            x,
            y,
            "Enron Email Dataset Latency",
            "Median same-process per-snippet latency; lower is better",
        )
        tick_value = min_ms
        while tick_value <= max_ms:
            tick_x = axis_left + axis_width * ((math.log10(tick_value) - log_min) / (log_max - log_min))
            tick_label = "0.1" if tick_value < 1 else str(int(tick_value))
            elements.append(f'<line x1="{tick_x}" y1="{axis_top}" x2="{tick_x}" y2="{axis_bottom}" stroke="{GRID}" />')
            elements.append(svg_text(tick_x, axis_bottom + 18, tick_label, size=11, anchor="middle", fill=MUTED))
            tick_value *= 10
        elements.append(f'<line x1="{axis_left}" y1="{axis_bottom}" x2="{axis_right}" y2="{axis_bottom}" stroke="{AXIS}" />')
        for index, row in enumerate(rows):
            value = max(min_ms, row["median_ms"])
            width_value = axis_width * ((math.log10(value) - log_min) / (log_max - log_min))
            if row["median_ms"] < min_ms:
                width_value = min_visible_bar_width
            row_y = axis_top + index * (bar_height + row_gap)
            elements.append(svg_text(x + panel_inset_x, row_y + bar_height * 0.72, CASE_LABELS[row["label"]], size=12, fill=MUTED))
            elements.append(svg_rect(axis_left, row_y, axis_width, bar_height, "none", rx=bar_radius, stroke=GRID))
            elements.append(svg_rect(axis_left, row_y, width_value, bar_height, parser_color(row["label"]), rx=bar_radius))
            label_x = axis_left + min(width_value + 8, axis_width - 4)
            elements.append(svg_text(label_x, row_y + bar_height * 0.72, fmt_ms(row["median_ms"]), size=11, weight="600"))

    elements = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" fill="none" role="img" aria-labelledby="title desc">',
        '<title id="title">Enron contextual benchmark summary</title>',
        '<desc id="desc">Member accuracy and same-process median per-snippet latency across reviewed Enron email snippets.</desc>',
        style_block(),
        svg_rect(0, 0, width, height, BG, rx=0),
    ]
    draw_accuracy_panel(elements)
    draw_latency_panel(elements)
    elements.append("</svg>")
    return "\n".join(elements) + "\n"


def main():
    args = parse_args()
    input_path, output_path = default_paths(args.profile)
    input_path = args.input or input_path
    output_path = args.output or output_path
    payload = json.loads(input_path.read_text(encoding="utf-8"))
    if args.profile == "case":
        svg = build_case_svg(payload)
    else:
        svg = build_document_svg(payload, with_title=args.with_title)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(svg, encoding="utf-8")
    print(output_path)


if __name__ == "__main__":
    main()
