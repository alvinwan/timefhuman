import pytest

from eval.corpora import (
    CORE_CORPUS_MATCHED_TEXT,
    CORE_CORPUS_TEXT,
    SEATTLE_HTML_76K_MATCHED_TEXT,
    load_corpus_text,
)
from timefhuman import tfhConfig, timefhuman


def test_core_corpus_gold_matches(now):
    config = tfhConfig(now=now, infer_datetimes=False, return_matched_text=True)
    assert timefhuman(CORE_CORPUS_TEXT, config=config) == CORE_CORPUS_MATCHED_TEXT


def test_seattle_html_gold_matches(now):
    text = load_corpus_text("seattle_html_76k")
    if text is None:
        pytest.skip("seattle_html_76k not available; run python -m eval.download_corpora seattle_html_76k")

    config = tfhConfig(now=now, infer_datetimes=False, return_matched_text=True)
    assert timefhuman(text, config=config) == SEATTLE_HTML_76K_MATCHED_TEXT
