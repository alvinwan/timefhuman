import os
from pathlib import Path
from eval.corpus_data.core_corpus import DATA as CORE_CORPUS, MATCHED_TEXT as CORE_CORPUS_MATCHED_TEXT, TEXT as CORE_CORPUS_TEXT
from eval.corpus_data.enron_emails import (
    DATA as ENRON_EMAILS,
    FORBIDDEN as ENRON_EMAILS_FORBIDDEN,
    MATCHED_TEXT as ENRON_EMAILS_MATCHED_TEXT,
)
from eval.corpus_data.seattle_html_76k import DATA as SEATTLE_HTML_76K, MATCHED_TEXT as SEATTLE_HTML_76K_MATCHED_TEXT
from eval.corpus_data.test_data_560k import (
    DATA as TEST_DATA_560K,
    FORBIDDEN as TEST_DATA_560K_FORBIDDEN,
    MATCHED_TEXT as TEST_DATA_560K_MATCHED_TEXT,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CORPORA_DIR = REPO_ROOT / ".eval_corpora"
DATEFINDER_ROOT = Path(os.environ.get("DATEFINDER_ROOT", "/tmp/datefinder"))

CORPUS_FILES = {
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

CORPORA = {
    "core_corpus": {
        **CORE_CORPUS,
    },
    "seattle_html_76k": {
        **SEATTLE_HTML_76K,
    },
    "test_data_560k": {
        **TEST_DATA_560K,
    },
    "enron_emails": {
        **ENRON_EMAILS,
    },
}


def corpora_dir():
    return Path(os.environ.get("TIMEFHUMAN_CORPORA_DIR", DEFAULT_CORPORA_DIR))


def resolve_corpus_path(name: str):
    info = CORPUS_FILES[name]
    if "datefinder_relpath" not in info:
        cached_path = corpora_dir() / info["cache_name"]
        if cached_path.exists():
            return cached_path
        return None

    datefinder_path = DATEFINDER_ROOT.joinpath(*info["datefinder_relpath"])
    if datefinder_path.exists():
        return datefinder_path

    cached_path = corpora_dir() / info["cache_name"]
    if cached_path.exists():
        return cached_path

    return None


def load_corpus_text(name: str):
    text = CORPORA[name]["text"]
    if text is not None:
        return text

    path = resolve_corpus_path(name)
    if path is None:
        return None
    return path.read_text(encoding="utf-8", errors="ignore")
