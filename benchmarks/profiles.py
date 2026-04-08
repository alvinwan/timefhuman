from pathlib import Path


BENCHMARKS_ROOT = Path(__file__).resolve().parent
SNAPSHOTS_DIR = BENCHMARKS_ROOT / "snapshots"
SVG_DIR = BENCHMARKS_ROOT / "svg"

SHORT_SAMPLES = 7
CASE_SAMPLES = 1
DOCUMENT_SAMPLE_GRACE_SECONDS = 60
CASE_SAMPLE_GRACE_SECONDS = 60

DEFAULT_TIMEOUT_SECONDS = 2
DATEPARSER_TIMEOUT_SECONDS = 30

DOCUMENT_DATASETS = (
    ("core_corpus", 7),
    ("seattle_html_76k", 5),
    ("test_data_560k", 3),
)

DOCUMENT_PROFILE = {
    "name": "document",
    "snapshot": SNAPSHOTS_DIR / "document.json",
    "svg": SVG_DIR / "document.svg",
}

CASE_PROFILE = {
    "name": "case",
    "dataset": "enron_emails",
    "snapshot": SNAPSHOTS_DIR / "case.json",
    "svg": SVG_DIR / "case.svg",
}


def timeout_seconds_for(label: str) -> int:
    return DATEPARSER_TIMEOUT_SECONDS if label == "dateparser*" else DEFAULT_TIMEOUT_SECONDS
