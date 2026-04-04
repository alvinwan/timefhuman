# Benchmarks

Benchmarks were run on an Apple M3 MacBook Air with 16 GB RAM, macOS 26.3.1, Python 3.13.3.

`short` is median microseconds per input on the 37-case short-input suite. Whole-document columns are median seconds with extracted counts in parentheses. `dateparser*` uses `dateparser.parse` for short inputs and `dateparser.search_dates` for whole documents.

## Main Results

| parser | short (us/input) | extracted | correctness | core_corpus | seattle_html_76k | test_data_560k |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| timefhuman | 44.5 | <ins><strong>37/37</strong></ins> | <ins><strong>10/10</strong></ins> | 0.0004 ([10](matches/timefhuman/core_corpus.md)) | <ins><strong>0.0223</strong></ins> ([57](matches/timefhuman/seattle_html_76k.md)) | <ins><strong>0.1321</strong></ins> ([594](matches/timefhuman/test_data_560k.md)) |
| datefinder.find_dates | <ins><strong>26.3</strong></ins> | 23/37 | 5/10 | <ins><strong>0.0003</strong></ins> ([11](matches/datefinder.find_dates/core_corpus.md)) | 0.0394 ([57](matches/datefinder.find_dates/seattle_html_76k.md)) | 0.5034 ([313](matches/datefinder.find_dates/test_data_560k.md)) |
| dateparser* | 44039.9 | 20/37 | 6/10 | 0.1155 ([14](matches/dateparser.search_dates/core_corpus.md)) | 0.3135 ([90](matches/dateparser.search_dates/seattle_html_76k.md)) | >15s (n/a) |

## Lower-Accuracy Baselines

These baselines do not support the whole-document task well enough to include in the main table.

| parser | short (us/input) | extracted | correctness |
| --- | ---: | ---: | ---: |
| metadate.parse_date | 32.5 | 31/37 | 5/10 |
| parsedatetime.parseDT | 43.7 | 36/37 | 6/10 |
| recurrent.parse | 193.7 | 36/37 | 6/10 |
| ctparse.ctparse | 12598.5 | 37/37 | 3/10 |

## Notes

- `datefinder.find_dates` and `dateparser*` both pick up extra HTML and metadata false positives on the document corpora, so speed and raw count alone overstate document quality.
- `datefinder.find_dates` extras on Seattle include version-like metadata such as `1.3.4` and `1.7.1`, plus `Jan 6 2016` as a smaller substring inside `Wed., Jan 6 2016 at 10:13AM`.
- `dateparser*` extras on Seattle include noisy HTML fragments such as `01'`, `90`, `50%`, `<h1`, and `set`.

## Reproduce

Run tests:

```bash
/tmp/timefhuman-bench-venv/bin/python -m pytest -q
```

The whole-document benchmark expects a local clone of `datefinder` at `/tmp/datefinder`.

```bash
/tmp/timefhuman-bench-venv/bin/python benchmarks/benchmark_baselines.py
```

Refresh the checked-in whole-document match dumps:

```bash
/tmp/timefhuman-bench-venv/bin/python benchmarks/dump_document_matches.py
```
