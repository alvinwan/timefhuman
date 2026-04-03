# Eval Data

Shared correctness data for both `tests/` and `benchmarks/`.

- `short.py`: curated short-input exact, no-inference, custom-config, and matched-text cases.
- `corpora.py`: document-scale corpora metadata plus any checked-in gold annotations.

Current corpus status:

- `core_corpus`: fully gold-annotated matched-text expectations.
- `seattle_html_76k`: tracked for document perf and raw dump inspection, but not fully gold-annotated yet.
- `test_data_560k`: tracked for document perf and sampled inspection, but not fully gold-annotated yet.
