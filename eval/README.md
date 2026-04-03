# Eval Data

Shared correctness data for both `tests/` and `benchmarks/`.

- `short.py`: curated short-input exact, no-inference, custom-config, and matched-text cases.
- `corpora.py`: document-scale corpora metadata plus any checked-in gold annotations.
- `download_corpora.py`: downloader for external corpora that are not checked into the repo.

Current corpus status:

- `core_corpus`: fully gold-annotated matched-text expectations.
- `seattle_html_76k`: fully gold-annotated matched-text expectations; HTML itself stays external. Policy: `eval/seattle_html_76k.policy.md`.
- `test_data_560k`: sampled gold only. Includes checked-in positive matches plus forbidden false positives, but is not exhaustive.
