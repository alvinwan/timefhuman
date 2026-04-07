#!/usr/bin/env python3
"""Generate the benchmark summary chart for the README.

Usage:
    python3 benchmarks/plot.py
    python3 benchmarks/plot.py --output benchmarks/summary.svg
    python3 benchmarks/plot.py --with-title
"""

from __future__ import annotations

import argparse
import math
from pathlib import Path
from xml.sax.saxutils import escape


SERIES = (
    {
        "name": "timefhuman",
        "color": "#1f7a5a",
        "accuracy": (100.0, 100.0, 100.0, 100.0),
        "latency_ms": (2.5, 2.7, 23.0, 168.0),
    },
    {
        "name": "datefinder",
        "color": "#c06b3e",
        "accuracy": (
            10 / 28 * 100.0,
            9 / 14 * 100.0,
            54 / 57 * 100.0,
            37 / 94 * 100.0,
        ),
        "latency_ms": (18.8, 17.6, 85.8, 915.6),
    },
)
DATASETS = ("short", "core", "sea_76k", "test_data_560k")

WIDTH = 1180
PADDING = 60
PANEL_GAP = 20
FONT = "ui-sans-serif, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif"

BG = "var(--bg)"
PANEL = "var(--panel)"
PANEL_STROKE = "var(--panel-stroke)"
GRID = "var(--grid)"
AXIS = "var(--axis)"
TEXT = "var(--text)"
MUTED = "var(--muted)"

BAR_WIDTH = 28
BAR_GAP = 10


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("benchmarks/summary.svg"),
        help="Where to write the SVG chart.",
    )
    parser.add_argument(
        "--with-title",
        action="store_true",
        help="Include the standalone chart title and subtitle.",
    )
    return parser.parse_args()


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


def fmt_percent(value: float) -> str:
    if value >= 99.95:
        return "100"
    return f"{value:.0f}"


def fmt_ms(value: float) -> str:
    if value >= 100:
        return f"{value:.0f}"
    return f"{value:.1f}"


def layout(with_title: bool) -> dict[str, float]:
    height = 620 if with_title else 500
    title_y = 58 if with_title else 0
    subtitle_y = 86 if with_title else 0
    legend_y = 126 if with_title else 38
    panel_top = 154 if with_title else 66
    panel_height = 380 if with_title else 368
    panel_width = (WIDTH - PADDING * 2 - PANEL_GAP) / 2
    footer_y = height - 24
    return {
        "height": height,
        "title_y": title_y,
        "subtitle_y": subtitle_y,
        "legend_y": legend_y,
        "panel_top": panel_top,
        "panel_height": panel_height,
        "panel_width": panel_width,
        "footer_y": footer_y,
    }


def panel_origin(index: int, spec: dict[str, float]) -> tuple[float, float]:
    return PADDING + index * (spec["panel_width"] + PANEL_GAP), spec["panel_top"]


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


def draw_panel_frame(elements, x, y, width, height, title, subtitle):
    elements.append(svg_rect(x, y, width, height, PANEL, rx=18, stroke=PANEL_STROKE))
    elements.append(svg_text(x + 24, y + 28, title, size=20, weight="700"))
    elements.append(svg_text(x + 24, y + 46, subtitle, size=12, fill=MUTED))


def draw_legend(elements, legend_y: float):
    legend_x = WIDTH - PADDING - 386
    for index, series in enumerate(SERIES):
        x = legend_x + index * 180
        elements.append(svg_rect(x, legend_y - 14, 18, 18, series["color"], rx=4))
        elements.append(svg_text(x + 28, legend_y, series["name"], size=14, weight="700"))


def draw_grouped_bars(elements, values_key, x, y, width, height, subtitle, y_ticks, y_formatter, projector, best_rule):
    draw_panel_frame(elements, x, y, width, height, subtitle[0], subtitle[1])

    axis_left = x + 56
    axis_right = x + width - 24
    axis_top = y + 78
    axis_bottom = y + height - 54
    axis_width = axis_right - axis_left
    axis_height = axis_bottom - axis_top
    group_width = axis_width / len(DATASETS)

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

    for dataset_index, dataset in enumerate(DATASETS):
        center = axis_left + group_width * (dataset_index + 0.5)
        start_x = center - (BAR_WIDTH + BAR_GAP / 2)
        dataset_values = [series[values_key][dataset_index] for series in SERIES]
        winner = best_rule(dataset_values)

        elements.append(svg_text(center, axis_bottom + 26, dataset, size=11, anchor="middle", fill=MUTED))
        for series_index, series in enumerate(SERIES):
            value = series[values_key][dataset_index]
            frac = projector(value)
            bar_height = axis_height * frac
            bar_x = start_x + series_index * (BAR_WIDTH + BAR_GAP)
            bar_y = axis_bottom - bar_height
            elements.append(svg_rect(bar_x, bar_y, BAR_WIDTH, bar_height, series["color"], rx=6))
            label_fill = series["color"] if series_index == winner else MUTED
            elements.append(
                svg_text(
                    bar_x + BAR_WIDTH / 2,
                    bar_y - 8,
                    fmt_percent(value) if values_key == "accuracy" else fmt_ms(value),
                    size=11,
                    weight="700",
                    anchor="middle",
                    fill=label_fill,
                )
            )


def draw_accuracy_panel(elements, spec: dict[str, float]):
    draw_grouped_bars(
        elements,
        "accuracy",
        *panel_origin(0, spec),
        spec["panel_width"],
        spec["panel_height"],
        subtitle=("Accuracy", "Member acc"),
        y_ticks=(0, 25, 50, 75, 100),
        y_formatter=lambda tick: str(int(tick)),
        projector=lambda value: value / 100.0,
        best_rule=lambda values: max(range(len(values)), key=values.__getitem__),
    )


def draw_latency_panel(elements, spec: dict[str, float]):
    log_min = math.log10(1)
    log_max = math.log10(1000)

    def projector(value: float) -> float:
        return (math.log10(value) - log_min) / (log_max - log_min)

    draw_grouped_bars(
        elements,
        "latency_ms",
        *panel_origin(1, spec),
        spec["panel_width"],
        spec["panel_height"],
        subtitle=("Latency", "Cold median ms"),
        y_ticks=(1, 10, 100, 1000),
        y_formatter=lambda tick: f"{int(tick)}",
        projector=projector,
        best_rule=lambda values: min(range(len(values)), key=values.__getitem__),
    )


def build_svg(with_title: bool = False):
    spec = layout(with_title)
    elements = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{spec["height"]}" '
        f'viewBox="0 0 {WIDTH} {spec["height"]}" fill="none">',
        style_block(),
        svg_rect(0, 0, WIDTH, spec["height"], BG, rx=0),
    ]
    if with_title:
        elements.extend(
            [
                svg_text(PADDING, spec["title_y"], "Benchmark Snapshot", size=32, weight="800"),
                svg_text(
                    PADDING,
                    spec["subtitle_y"],
                    "timefhuman vs. datefinder from benchmarks/README.md main results",
                    size=15,
                    fill=MUTED,
                ),
            ]
        )
    draw_legend(elements, spec["legend_y"])
    draw_accuracy_panel(elements, spec)
    draw_latency_panel(elements, spec)
    elements.append(svg_text(PADDING, spec["footer_y"], "Cold medians; log latency axis.", size=12, fill=MUTED))
    elements.append("</svg>")
    return "\n".join(elements)


def main():
    args = parse_args()
    args.output.write_text(build_svg(with_title=args.with_title), encoding="utf-8")
    print(args.output)


if __name__ == "__main__":
    main()
