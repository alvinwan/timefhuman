from __future__ import annotations

import math
from pathlib import Path
from xml.sax.saxutils import escape


OUTPUT_PATH = Path(__file__).resolve().parent / "plots" / "benchmark_snapshot.svg"
FONT = "ui-sans-serif, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif"
TEXT_COLOR = "#1c1f24"
MUTED = "#5d6674"
GRID_COLOR = "#eceef2"
AXIS_COLOR = "#d5d8df"
PAGE_BG = "#ffffff"
PANEL_BG = "#fafbfc"
PANEL_STROKE = "#e4e7ec"

SERIES = (
    {
        "label": "timefhuman",
        "color": "#1f7a5a",
        "accuracy": (100.0, 100.0, 100.0, 100.0),
        "latency_ms": (2.5, 2.7, 23.0, 168.0),
    },
    {
        "label": "datefinder",
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


def fmt_percent(value: float) -> str:
    if value >= 99.95:
        return "100"
    return f"{value:.0f}"


def fmt_ms(value: float) -> str:
    if value >= 100:
        return f"{value:.0f}"
    return f"{value:.1f}"


def draw_text(x: float, y: float, text: str, size: int = 14, weight: int = 400, fill: str = TEXT_COLOR, anchor: str = "start") -> str:
    return (
        f'<text x="{x:.1f}" y="{y:.1f}" fill="{fill}" font-size="{size}" '
        f'font-family="{FONT}" '
        f'font-weight="{weight}" text-anchor="{anchor}">{escape(text)}</text>'
    )


def draw_rect(
    x: float,
    y: float,
    width: float,
    height: float,
    fill: str,
    rx: float = 8,
    opacity: float = 1.0,
    stroke: str = "none",
) -> str:
    return (
        f'<rect x="{x:.1f}" y="{y:.1f}" width="{width:.1f}" height="{height:.1f}" '
        f'fill="{fill}" rx="{rx:.1f}" opacity="{opacity:.3f}" stroke="{stroke}" />'
    )


def build_accuracy_panel(x0: float, y0: float, width: float, height: float) -> list[str]:
    left = x0 + 56
    right = x0 + width - 24
    top = y0 + 78
    bottom = y0 + height - 54
    plot_w = right - left
    plot_h = bottom - top
    group_w = plot_w / len(DATASETS)
    bar_w = 28
    gap = 10

    items = [
        draw_text(x0 + 24, y0 + 28, "Accuracy", size=20, weight=700),
        draw_text(x0 + 24, y0 + 46, "Member-level correctness, higher is better", size=12, fill=MUTED),
    ]

    for tick in range(0, 101, 25):
        y = bottom - plot_h * (tick / 100.0)
        items.append(f'<line x1="{left:.1f}" y1="{y:.1f}" x2="{right:.1f}" y2="{y:.1f}" stroke="{GRID_COLOR}" stroke-width="1" />')
        items.append(draw_text(left - 10, y + 5, str(tick), size=11, fill=MUTED, anchor="end"))

    items.append(f'<line x1="{left:.1f}" y1="{top:.1f}" x2="{left:.1f}" y2="{bottom:.1f}" stroke="{AXIS_COLOR}" stroke-width="1" />')
    items.append(f'<line x1="{left:.1f}" y1="{bottom:.1f}" x2="{right:.1f}" y2="{bottom:.1f}" stroke="{AXIS_COLOR}" stroke-width="1" />')

    for index, dataset in enumerate(DATASETS):
        center = left + group_w * (index + 0.5)
        start_x = center - (bar_w + gap / 2)
        items.append(draw_text(center, bottom + 26, dataset, size=11, fill=MUTED, anchor="middle"))
        for series_index, series in enumerate(SERIES):
            value = series["accuracy"][index]
            bar_h = plot_h * (value / 100.0)
            bar_x = start_x + series_index * (bar_w + gap)
            bar_y = bottom - bar_h
            items.append(draw_rect(bar_x, bar_y, bar_w, bar_h, series["color"], rx=6))
            items.append(draw_text(bar_x + bar_w / 2, bar_y - 8, fmt_percent(value), size=11, weight=700, fill=series["color"], anchor="middle"))

    return items


def build_latency_panel(x0: float, y0: float, width: float, height: float) -> list[str]:
    left = x0 + 56
    right = x0 + width - 24
    top = y0 + 78
    bottom = y0 + height - 54
    plot_w = right - left
    plot_h = bottom - top
    group_w = plot_w / len(DATASETS)
    bar_w = 28
    gap = 10
    tick_values = (1, 10, 100, 1000)
    log_min = math.log10(tick_values[0])
    log_max = math.log10(tick_values[-1])

    def project(value: float) -> float:
        return (math.log10(value) - log_min) / (log_max - log_min)

    items = [
        draw_text(x0 + 24, y0 + 28, "Latency", size=20, weight=700),
        draw_text(x0 + 24, y0 + 46, "Fresh-process cold median (ms), lower is better", size=12, fill=MUTED),
    ]

    for tick in tick_values:
        y = bottom - plot_h * project(tick)
        items.append(f'<line x1="{left:.1f}" y1="{y:.1f}" x2="{right:.1f}" y2="{y:.1f}" stroke="{GRID_COLOR}" stroke-width="1" />')
        items.append(draw_text(left - 10, y + 5, f"{tick:g}", size=11, fill=MUTED, anchor="end"))

    items.append(f'<line x1="{left:.1f}" y1="{top:.1f}" x2="{left:.1f}" y2="{bottom:.1f}" stroke="{AXIS_COLOR}" stroke-width="1" />')
    items.append(f'<line x1="{left:.1f}" y1="{bottom:.1f}" x2="{right:.1f}" y2="{bottom:.1f}" stroke="{AXIS_COLOR}" stroke-width="1" />')

    for index, dataset in enumerate(DATASETS):
        center = left + group_w * (index + 0.5)
        start_x = center - (bar_w + gap / 2)
        items.append(draw_text(center, bottom + 26, dataset, size=11, fill=MUTED, anchor="middle"))
        for series_index, series in enumerate(SERIES):
            value = series["latency_ms"][index]
            bar_h = plot_h * project(value)
            bar_x = start_x + series_index * (bar_w + gap)
            bar_y = bottom - bar_h
            items.append(draw_rect(bar_x, bar_y, bar_w, bar_h, series["color"], rx=6))
            items.append(draw_text(bar_x + bar_w / 2, bar_y - 8, fmt_ms(value), size=11, weight=700, fill=series["color"], anchor="middle"))

    return items


def build_svg() -> str:
    width = 1180
    height = 620
    panel_w = 520
    panel_h = 380
    panel_y = 154
    left_x = 60
    right_x = 600

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" fill="none">',
        draw_rect(0, 0, width, height, PAGE_BG, rx=0),
        draw_text(60, 58, "Benchmark Snapshot", size=32, weight=800),
        draw_text(
            60,
            86,
            "timefhuman vs. datefinder from benchmarks/README.md main results",
            size=15,
            fill=MUTED,
        ),
    ]

    legend_y = 126
    legend_x = 734
    for index, series in enumerate(SERIES):
        x = legend_x + index * 180
        parts.append(draw_rect(x, legend_y - 14, 18, 18, series["color"], rx=4))
        parts.append(draw_text(x + 28, legend_y, series["label"], size=14, weight=700))

    parts.append(draw_rect(left_x, panel_y, panel_w, panel_h, PANEL_BG, rx=18, stroke=PANEL_STROKE))
    parts.append(draw_rect(right_x, panel_y, panel_w, panel_h, PANEL_BG, rx=18, stroke=PANEL_STROKE))
    parts.extend(build_accuracy_panel(left_x, panel_y, panel_w, panel_h))
    parts.extend(build_latency_panel(right_x, panel_y, panel_w, panel_h))
    parts.append(draw_text(60, 580, "Accuracy uses member-level coverage. Latency panel uses a log scale because the corpora span two orders of magnitude.", size=12, fill=MUTED))
    parts.append("</svg>")
    return "\n".join(parts)


def main() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(build_svg(), encoding="utf-8")
    print(OUTPUT_PATH)


if __name__ == "__main__":
    main()
