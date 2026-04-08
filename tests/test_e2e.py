import pytest
from datasets.cases.short import CUSTOM_CONFIG_CASES, DEFAULT_CASES, MATCHED_TEXT_CASES, NO_INFERENCE_CASES
from timefhuman import timefhuman
from timefhuman.main import tfhConfig


def case_text(case):
    if len(case) == 2:
        return case[0]
    return case[1]


@pytest.mark.parametrize("case", DEFAULT_CASES, ids=case_text)
def test_default(now, case):
    """Default behavior should be to infer datetimes and times."""
    test_input, expected = case
    actual = timefhuman(test_input, config=tfhConfig(now=now))
    assert actual == expected, f"Expected: {expected}\nGot: {actual}"

@pytest.mark.parametrize("case", NO_INFERENCE_CASES, ids=case_text)
def test_no_inference(now, case):
    """Return exactly the date or time, without inferring the other."""
    test_input, expected = case
    config = tfhConfig(infer_datetimes=False, now=now)
    assert timefhuman(test_input, config=config) == expected

@pytest.mark.parametrize("case", CUSTOM_CONFIG_CASES, ids=case_text)
def test_custom_config(now, case):
    config_kwargs, test_input, expected = case
    config = tfhConfig(now=now, **config_kwargs)
    assert timefhuman(test_input, config=config) == expected

@pytest.mark.parametrize("case", MATCHED_TEXT_CASES, ids=case_text)
def test_matched_text(now, case):  # gh#9
    test_input, expected = case
    assert timefhuman(test_input, tfhConfig(now=now, return_matched_text=True)) == expected
