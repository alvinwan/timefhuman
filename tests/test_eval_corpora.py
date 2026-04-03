from eval.corpora import CORE_CORPUS_MATCHED_TEXT, CORE_CORPUS_TEXT
from timefhuman import tfhConfig, timefhuman


def test_core_corpus_gold_matches(now):
    config = tfhConfig(now=now, infer_datetimes=False, return_matched_text=True)
    assert timefhuman(CORE_CORPUS_TEXT, config=config) == CORE_CORPUS_MATCHED_TEXT
