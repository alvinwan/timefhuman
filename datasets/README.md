# Datasets

Shared evaluation data for both `tests/` and `benchmarks/`.

- `registry.py`: dataset registry, loader helpers, and normalized case access.
- `download.py`: downloader for external datasets that are not checked into the repo.
- `cases/`: checked-in gold cases, with one module per dataset.
- `utils/`: dataset-specific helpers, currently for Enron flattening.

Current dataset status:

- `short`: curated short-input exact, no-inference, custom-config, and matched-text cases.
- `core_corpus`: fully gold-annotated matched-text document cases.
- `seattle_html_76k`: fully gold-annotated matched-text document cases; the HTML stays external.
- `test_data_560k`: broad sampled document gold with positive matches plus forbidden false positives.
- `enron_emails`: 100 curated body-text snippet cases with per-message send-time context; raw mail stays external and is flattened by the downloader.
