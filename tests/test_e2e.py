import pytest
from eval.short import CUSTOM_CONFIG_CASES, DEFAULT_CASES, MATCHED_TEXT_CASES, NO_INFERENCE_CASES
from timefhuman import timefhuman
from timefhuman.main import tfhConfig


@pytest.mark.parametrize("case", DEFAULT_CASES, ids=lambda case: case["id"])
def test_default(now, case):
    """Default behavior should be to infer datetimes and times."""
    actual = timefhuman(case["text"], config=tfhConfig(now=now))
    assert actual == case["expected"], f"Expected: {case['expected']}\nGot: {actual}"

@pytest.mark.parametrize("case", NO_INFERENCE_CASES, ids=lambda case: case["id"])
def test_no_inference(now, case):
    """Return exactly the date or time, without inferring the other."""
    config = tfhConfig(infer_datetimes=False, now=now)
    assert timefhuman(case["text"], config=config) == case["expected"]

@pytest.mark.parametrize("case", CUSTOM_CONFIG_CASES, ids=lambda case: case["id"])
def test_custom_config(now, case):
    config = tfhConfig(now=now, **case["config_kwargs"])
    assert timefhuman(case["text"], config=config) == case["expected"]

@pytest.mark.parametrize("case", MATCHED_TEXT_CASES, ids=lambda case: case["id"])
def test_matched_text(now, case):  # gh#9
    assert timefhuman(case["text"], tfhConfig(now=now, return_matched_text=True)) == case["expected"]
