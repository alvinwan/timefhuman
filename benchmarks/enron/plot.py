import argparse
import json
import math
from pathlib import Path
from xml.sax.saxutils import escape


SCRIPT_DIR = Path(__file__).resolve().parent
SNAPSHOT_PATH = SCRIPT_DIR / "snapshot.json"
DEFAULT_OUTPUT = SCRIPT_DIR / "summary.svg"

PARSER_LABELS = {
    "timefhuman": "timefhuman",
    "ctparse.ctparse": "ctparse",
    "parsedatetime.parseDT": "parsedatetime",
    "recurrent.parse": "recurrent",
    "dateparser*": "dateparser",
    "datefinder.find_dates": "datefinder",
}
INCLUDED = [
    "timefhuman",
    "parsedatetime.parseDT",
    "recurrent.parse",
    "ctparse.ctparse",
    "dateparser*",
    "datefinder.find_dates",
]

WIDTH = 980
HEIGHT = 344
PADDING = 0
PANEL_GAP = 20
PANEL_TOP = 28
PANEL_HEIGHT = 296
PANEL_WIDTH = (WIDTH - PADDING * 2 - PANEL_GAP) / 2
LABEL_WIDTH = 118
PANEL_INSET_X = 16
PANEL_INSET_RIGHT = 14
BAR_HEIGHT = 22
ROW_GAP = 15
HEADER_HEIGHT = 56
AXIS_BOTTOM_MARGIN = 32
BAR_RADIUS = 6
ACCENT = "#1f7a5a"
BASELINE_COLORS = {
    "parsedatetime.parseDT": "#5f6875",
    "recurrent.parse": "#727c89",
    "ctparse.ctparse": "#858f9c",
    "dateparser*": "#98a2af",
    "datefinder.find_dates": "#acb5c1",
}
BG = "var(--bg)"
PANEL = "var(--panel)"
PANEL_STROKE = "var(--panel-stroke)"
GRID = "var(--grid)"
AXIS = "var(--axis)"
TEXT = "var(--text)"
MUTED = "var(--muted)"
FONT = "ui-sans-serif, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif"


def parse_args():
    parser = argparse.ArgumentParser(description="Generate the Enron benchmark summary SVG.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


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
        f'<text x="{x}" y="{y}" fill="{fill}" font-family="{FONT}" '
        f'font-size="{size}" font-weight="{weight}" text-anchor="{anchor}">'
        f"{escape(text)}</text>"
    )


def svg_rect(x, y, width, height, fill, rx=8, stroke="none", stroke_width=1, dash=None):
    dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
    return (
        f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="{rx}" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width}"{dash_attr} />'
    )


def panel_origin(index):
    return PADDING + index * (PANEL_WIDTH + PANEL_GAP), PANEL_TOP


def load_rows():
    payload = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))
    rows_by_label = {row["label"]: row for row in payload["rows"]}
    return [rows_by_label[label] for label in INCLUDED if label in rows_by_label]


def member_ratio(row):
    return row["member"]["matched"] / row["member"]["total"]


def fmt_pct(value):
    return f"{value * 100:.1f}%"


def fmt_ms(value):
    if value < 0.1:
        return "<0.1 ms"
    return f"{value:.1f} ms"


def parser_color(label):
    if label == "timefhuman":
        return ACCENT
    return BASELINE_COLORS.get(label, "#8a94a3")


def value_text_x(bar_x, width, max_width):
    return bar_x + min(width + 8, max_width - 4)


def draw_panel_frame(elements, x, y, width, height, title, subtitle):
    elements.append(svg_rect(x, y, width, height, PANEL, rx=14, stroke=PANEL_STROKE))
    elements.append(svg_text(x + 16, y + 26, title, size=16, weight="600"))
    elements.append(svg_text(x + 16, y + 44, subtitle, size=12, fill=MUTED))


def left_panel_geometry():
    x, y = panel_origin(0)
    axis_left = x + PANEL_INSET_X + LABEL_WIDTH
    axis_right = x + PANEL_WIDTH - PANEL_INSET_RIGHT
    axis_top = y + HEADER_HEIGHT
    axis_bottom = y + PANEL_HEIGHT - AXIS_BOTTOM_MARGIN
    return x, y, axis_left, axis_right, axis_top, axis_bottom


def right_panel_geometry():
    x, y = panel_origin(1)
    axis_left = x + PANEL_INSET_X + LABEL_WIDTH
    axis_right = x + PANEL_WIDTH - PANEL_INSET_RIGHT
    axis_top = y + HEADER_HEIGHT
    axis_bottom = y + PANEL_HEIGHT - AXIS_BOTTOM_MARGIN
    return x, y, axis_left, axis_right, axis_top, axis_bottom


def draw_accuracy_panel(elements, rows):
    x, y, axis_left, axis_right, axis_top, axis_bottom = left_panel_geometry()
    draw_panel_frame(
        elements,
        x,
        y,
        PANEL_WIDTH,
        PANEL_HEIGHT,
        "Enron Email Dataset Accuracy",
        "Member accuracy on reviewed email snippets; higher is better",
    )
    axis_width = axis_right - axis_left

    for tick in (0.0, 0.5, 1.0):
        tick_x = axis_left + axis_width * tick
        elements.append(f'<line x1="{tick_x}" y1="{axis_top}" x2="{tick_x}" y2="{axis_bottom}" stroke="{GRID}" />')
        elements.append(svg_text(tick_x, axis_bottom + 18, f"{int(tick * 100)}%", size=11, anchor="middle", fill=MUTED))

    elements.append(f'<line x1="{axis_left}" y1="{axis_bottom}" x2="{axis_right}" y2="{axis_bottom}" stroke="{AXIS}" />')

    for index, row in enumerate(rows):
        row_y = axis_top + index * (BAR_HEIGHT + ROW_GAP)
        width = axis_width * member_ratio(row)
        bar_x = axis_left
        color = parser_color(row["label"])
        label = PARSER_LABELS[row["label"]]

        elements.append(svg_text(x + PANEL_INSET_X, row_y + BAR_HEIGHT * 0.72, label, size=12, fill=MUTED))
        elements.append(svg_rect(bar_x, row_y, axis_width, BAR_HEIGHT, "none", rx=BAR_RADIUS, stroke=GRID))
        elements.append(svg_rect(bar_x, row_y, width, BAR_HEIGHT, color, rx=BAR_RADIUS))
        elements.append(
            svg_text(
                value_text_x(bar_x, width, axis_width),
                row_y + BAR_HEIGHT * 0.72,
                fmt_pct(member_ratio(row)),
                size=11,
                weight="600",
            )
        )


def draw_latency_panel(elements, rows):
    x, y, axis_left, axis_right, axis_top, axis_bottom = right_panel_geometry()
    draw_panel_frame(
        elements,
        x,
        y,
        PANEL_WIDTH,
        PANEL_HEIGHT,
        "Enron Email Dataset Latency",
        "Median same-process per-snippet latency; lower is better",
    )
    axis_width = axis_right - axis_left
    min_ms = 0.1
    max_ms = 10 ** max(1, math.ceil(math.log10(max(row["median_ms"] for row in rows))))
    log_min = math.log10(min_ms)
    log_max = math.log10(max_ms)
    tick_values = []
    tick = min_ms
    while tick <= max_ms:
        tick_values.append(tick)
        tick *= 10

    for tick_value in tick_values:
        tick_x = axis_left + axis_width * ((math.log10(tick_value) - log_min) / (log_max - log_min))
        tick_label = "0.1" if tick_value < 1 else str(int(tick_value))
        elements.append(f'<line x1="{tick_x}" y1="{axis_top}" x2="{tick_x}" y2="{axis_bottom}" stroke="{GRID}" />')
        elements.append(svg_text(tick_x, axis_bottom + 18, tick_label, size=11, anchor="middle", fill=MUTED))

    elements.append(f'<line x1="{axis_left}" y1="{axis_bottom}" x2="{axis_right}" y2="{axis_bottom}" stroke="{AXIS}" />')

    for index, row in enumerate(rows):
        row_y = axis_top + index * (BAR_HEIGHT + ROW_GAP)
        value = max(min_ms, row["median_ms"])
        width = axis_width * ((math.log10(value) - log_min) / (log_max - log_min))
        bar_x = axis_left
        color = parser_color(row["label"])
        label = PARSER_LABELS[row["label"]]

        elements.append(svg_text(x + PANEL_INSET_X, row_y + BAR_HEIGHT * 0.72, label, size=12, fill=MUTED))
        elements.append(svg_rect(bar_x, row_y, axis_width, BAR_HEIGHT, "none", rx=BAR_RADIUS, stroke=GRID))
        elements.append(svg_rect(bar_x, row_y, width, BAR_HEIGHT, color, rx=BAR_RADIUS))
        elements.append(
            svg_text(
                value_text_x(bar_x, width, axis_width),
                row_y + BAR_HEIGHT * 0.72,
                fmt_ms(row["median_ms"]),
                size=11,
                weight="600",
            )
        )


def build_svg(rows):
    elements = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" fill="none" role="img" aria-labelledby="title desc">',
        '<title id="title">Enron contextual benchmark summary</title>',
        '<desc id="desc">Member accuracy and median per-snippet latency across reviewed Enron email snippets.</desc>',
        style_block(),
        svg_rect(0, 0, WIDTH, HEIGHT, BG, rx=0),
    ]
    draw_accuracy_panel(elements, rows)
    draw_latency_panel(elements, rows)
    elements.append("</svg>")
    return "\n".join(elements) + "\n"


def main():
    args = parse_args()
    args.output.write_text(build_svg(load_rows()), encoding="utf-8")
    print(args.output)


if __name__ == "__main__":
    main()
