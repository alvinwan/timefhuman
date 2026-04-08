import pytest

from datasets.registry import (
    CORE_CORPUS_MATCHED_TEXT,
    CORE_CORPUS_TEXT,
    ENRON_EMAILS_CONTEXT_CASES,
    SEATTLE_HTML_76K_MATCHED_TEXT,
    TEST_DATA_560K_FORBIDDEN,
    TEST_DATA_560K_MATCHED_TEXT,
    load_corpus_text,
)
from timefhuman import tfhConfig, timefhuman


def test_core_corpus_gold_matches(now):
    config = tfhConfig(now=now, infer_datetimes=False, return_matched_text=True)
    assert timefhuman(CORE_CORPUS_TEXT, config=config) == CORE_CORPUS_MATCHED_TEXT


def test_seattle_html_gold_matches(now):
    text = load_corpus_text("seattle_html_76k")
    if text is None:
        pytest.skip("seattle_html_76k not available; run python -m datasets.download seattle_html_76k")

    config = tfhConfig(now=now, infer_datetimes=False, return_matched_text=True)
    assert timefhuman(text, config=config) == SEATTLE_HTML_76K_MATCHED_TEXT


def test_test_data_gold_matches(now):
    text = load_corpus_text("test_data_560k")
    if text is None:
        pytest.skip("test_data_560k not available; run python -m datasets.download test_data_560k")

    config = tfhConfig(now=now, infer_datetimes=False, return_matched_text=True)
    matches = timefhuman(text, config=config)

    for expected in TEST_DATA_560K_MATCHED_TEXT:
        assert expected in matches

    actual_match_spans = {(matched_text, span) for matched_text, span, _ in matches}
    for forbidden in TEST_DATA_560K_FORBIDDEN:
        assert forbidden not in actual_match_spans


def enron_case_id(case):
    return f"{case['source_path']}:{case['source_span'][0]}"


@pytest.mark.parametrize("case", ENRON_EMAILS_CONTEXT_CASES, ids=enron_case_id)
def test_enron_context_gold_matches(case):
    config = tfhConfig(now=case["sent_at"], return_matched_text=True)
    actual = timefhuman(case["text"], config=config)

    if "known_failure" in case:
        try:
            assert actual == case["expected"]
        except AssertionError:
            pytest.xfail(case["known_failure"])
        return

    assert actual == case["expected"]


def test_enron_context_spans_match_corpus():
    text = load_corpus_text("enron_emails")
    if text is None:
        pytest.skip("enron_emails not available; run python -m datasets.download enron_emails")

    for case in ENRON_EMAILS_CONTEXT_CASES:
        start, end = case["source_span"]
        assert text[start:end] == case["text"]
