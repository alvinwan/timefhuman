import os
from pathlib import Path

from datasets.cases.core_corpus import DATA as CORE_CORPUS
from datasets.cases.core_corpus import MATCHED_TEXT as CORE_CORPUS_MATCHED_TEXT
from datasets.cases.core_corpus import TEXT as CORE_CORPUS_TEXT
from datasets.cases.enron import CONTEXT_MATCHED_TEXT_CASES as ENRON_EMAILS_CONTEXT_CASES
from datasets.cases.enron import DATA as ENRON_EMAILS
from datasets.cases.seattle_html_76k import DATA as SEATTLE_HTML_76K
from datasets.cases.seattle_html_76k import MATCHED_TEXT as SEATTLE_HTML_76K_MATCHED_TEXT
from datasets.cases.short import CUSTOM_CONFIG_CASES
from datasets.cases.short import DATA as SHORT
from datasets.cases.short import DEFAULT_CASES
from datasets.cases.short import MATCHED_TEXT_CASES
from datasets.cases.short import NO_INFERENCE_CASES
from datasets.cases.test_data_560k import DATA as TEST_DATA_560K
from datasets.cases.test_data_560k import FORBIDDEN as TEST_DATA_560K_FORBIDDEN
from datasets.cases.test_data_560k import MATCHED_TEXT as TEST_DATA_560K_MATCHED_TEXT


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATASETS_DIR = REPO_ROOT / ".eval_corpora"
DATEFINDER_ROOT = Path(os.environ.get("DATEFINDER_ROOT", "/tmp/datefinder"))

DATASET_FILES = {
    "core_corpus": {
        "cache_name": "core_corpus.txt",
        "datefinder_relpath": ("bench", "corpus_core.txt"),
        "download_url": "https://raw.githubusercontent.com/akoumjian/datefinder/master/bench/corpus_core.txt",
    },
    "seattle_html_76k": {
        "cache_name": "seattle_weekly.html",
        "datefinder_relpath": ("tests", "seattle_weekly.html"),
        "download_url": "https://raw.githubusercontent.com/akoumjian/datefinder/master/tests/seattle_weekly.html",
    },
    "test_data_560k": {
        "cache_name": "test_data.txt",
        "datefinder_relpath": ("tests", "test_data.txt"),
        "download_url": "https://raw.githubusercontent.com/akoumjian/datefinder/master/tests/test_data.txt",
    },
    "enron_emails": {
        "cache_name": "enron_emails.txt",
        "archive_name": "enron_mail_20150507.tar.gz",
        "extracted_dir_name": "enron_mail_20150507",
        "download_url": "https://www.cs.cmu.edu/~enron/enron_mail_20150507.tar.gz",
    },
}

DATASETS = {
    "short": {**SHORT},
    "core_corpus": {**CORE_CORPUS},
    "seattle_html_76k": {**SEATTLE_HTML_76K},
    "test_data_560k": {**TEST_DATA_560K},
    "enron_emails": {**ENRON_EMAILS},
}


def datasets_dir():
    return Path(os.environ.get("TIMEFHUMAN_CORPORA_DIR", DEFAULT_DATASETS_DIR))


def resolve_dataset_path(name: str):
    info = DATASET_FILES[name]
    if "datefinder_relpath" not in info:
        cached_path = datasets_dir() / info["cache_name"]
        if cached_path.exists():
            return cached_path
        return None

    datefinder_path = DATEFINDER_ROOT.joinpath(*info["datefinder_relpath"])
    if datefinder_path.exists():
        return datefinder_path

    cached_path = datasets_dir() / info["cache_name"]
    if cached_path.exists():
        return cached_path

    return None


def load_dataset_text(name: str):
    text = DATASETS[name]["text"]
    if text is not None:
        return text

    path = resolve_dataset_path(name)
    if path is None:
        return None
    return path.read_text(encoding="utf-8", errors="ignore")


load_corpus_text = load_dataset_text
resolve_corpus_path = resolve_dataset_path


def get_dataset(name: str):
    return DATASETS[name]


def _normalized_case(dataset_name: str, dataset: dict, case: dict):
    config = dict(dataset.get("defaults", {}))
    config.update(case.get("config", {}))
    normalized = {
        **case,
        "dataset": dataset_name,
        "config": config,
        "tags": tuple(case.get("tags", ())),
    }
    return normalized


def get_cases(name: str, mode: str | None = None, tags: set[str] | None = None):
    dataset = DATASETS[name]
    cases = [
        _normalized_case(name, dataset, case)
        for case in dataset.get("cases", [])
    ]
    if mode is not None:
        cases = [case for case in cases if case["mode"] == mode]
    if tags is not None:
        cases = [case for case in cases if tags.issubset(set(case["tags"]))]
    return cases


def iter_cases(dataset_names=None, mode: str | None = None, tags: set[str] | None = None):
    names = dataset_names or DATASETS.keys()
    for name in names:
        for case in get_cases(name, mode=mode, tags=tags):
            yield case


def load_case_text(case: dict):
    if "text" in case and case["text"] is not None:
        return case["text"]
    return load_dataset_text(case["dataset"])


CORPORA = {
    "core_corpus": {"text": CORE_CORPUS_TEXT, "expected": CORE_CORPUS_MATCHED_TEXT},
    "seattle_html_76k": {"text": None, "expected": SEATTLE_HTML_76K_MATCHED_TEXT},
    "test_data_560k": {"text": None, "expected": TEST_DATA_560K_MATCHED_TEXT, "forbidden": TEST_DATA_560K_FORBIDDEN},
    "enron_emails": {"text": None, "cases": ENRON_EMAILS_CONTEXT_CASES},
}
