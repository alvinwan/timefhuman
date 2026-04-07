# Eval Data

Shared correctness data for both `tests/` and `benchmarks/`.

- `short.py`: curated short-input exact, no-inference, custom-config, and matched-text cases.
- `corpora.py`: document-scale corpus registry and loader helpers.
- `corpus_data/`: one file per corpus with checked-in gold annotations.
- `download_corpora.py`: downloader for external corpora that are not checked into the repo.

Current corpus status:

- `core_corpus`: fully gold-annotated matched-text expectations.
- `seattle_html_76k`: fully gold-annotated matched-text expectations; HTML itself stays external.
- `test_data_560k`: broad sampled gold. Includes many checked-in positive matches plus forbidden false positives, but is not exhaustive.
- `enron_emails`: broad sampled gold built from 256 evenly sampled `Date:` headers plus curated body-text snippets with per-message send-time context; raw mail stays external and is flattened by the downloader.
