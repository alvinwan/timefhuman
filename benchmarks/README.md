# Benchmarks

Status as of April 2, 2026.

## Setup

- Hardware: Apple M3 MacBook Air, 16 GB RAM
- OS: macOS 26.3.1
- Python: 3.13.3 from `/tmp/timefhuman-bench-venv`
- Whole-document corpora: either a local `datefinder` clone at `/tmp/datefinder` or cached downloads under `.eval_corpora/`

## Results

- Runtime path: deterministic whole-string parse first, bounded extraction for noisy text, LALR fallback only on misses. Earley is not used at runtime.
- Shared benchmark inputs live in `eval/short.py`, and the checked-in fully gold `core_corpus` lives in `eval/corpora.py`.
- `seattle_html_76k` is also a checked-in gold corpus; the HTML stays external and is loaded from `/tmp/datefinder` or `.eval_corpora/`.
- `short_ms`: median milliseconds for one full pass over the 23 single-datetime short cases.
- `core_ms`, `seattle_76k_ms`, `test_560k_ms`: warmed median milliseconds for one full dataset run.
- `#`: extracted count for the dataset immediately to the left.
- `acc`: exact match count for the dataset immediately to the left.
- `core` and `seattle` accuracy are gold-corpus match counts. Parsers with matched-text APIs are scored on `(matched text, normalized value)`. Parsers without span APIs are scored on normalized value only after running on the full document.
- Whole-document rows are run with a strict 1-second per-call timeout. `>1000ms` means the parser exceeded that cap. `timeout` in an `acc` column means the correctness run hit the same cap.
- Whole-document counts link to checked-in raw match dumps under `benchmarks/matches/`.
- `timefhuman` whole-document extraction uses `infer_datetimes=False`, so linked dumps keep raw dates, times, and timedeltas while explicit datetimes stay datetimes.
- `timefhuman` is pinned first; the remaining rows are ordered by `core_ms`.

### Combined Scorecard

| parser | short_ms | acc | core_ms | # | acc | seattle_76k_ms | # | acc | test_560k_ms | # |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| timefhuman | 0.3 | **23/23** | 0.4 | [10](matches/timefhuman/core_corpus.md) | **10/10** | 22.6 | [55](matches/timefhuman/seattle_html_76k.md) | **55/55** | 133.0 | [594](matches/timefhuman/test_data_560k.md) |
| metadate.parse_date | 0.5 | 9/23 | **0.2** | 10 | 5/10 | **4.6** | 90 | 2/55 | **49.5** | 1538 |
| datefinder.find_dates | **0.2** | 9/23 | **0.2** | [11](matches/datefinder.find_dates/core_corpus.md) | 1/10 | 39.8 | [57](matches/datefinder.find_dates/seattle_html_76k.md) | 53/55 | 497.3 | [313](matches/datefinder.find_dates/test_data_560k.md) |
| parsedatetime.parseDT | 0.5 | 11/23 | 2.4 | 1 | 0/10 | 696.9 | 1 | 0/55 | >1000ms | n/a |
| recurrent.parse | 3.4 | 11/23 | 4.0 | 1 | 0/10 | n/a | n/a | n/a | n/a | n/a |
| dateparser.search_dates | n/a | n/a | 111.7 | [14](matches/dateparser.search_dates/core_corpus.md) | 1/10 | 326.6 | [90](matches/dateparser.search_dates/seattle_html_76k.md) | 52/55 | >1000ms | n/a |
| dateparser.parse | 31.5 | 13/23 | 120.8 | 0 | 0/10 | >1000ms | n/a | timeout | >1000ms | n/a |
| ctparse.ctparse | 75.2 | 5/23 | 124.8 | 1 | 0/10 | >1000ms | n/a | timeout | >1000ms | n/a |

Notes:

- `metadate.parse_date`, `datefinder.find_dates`, and `dateparser.search_dates` all pick up extra HTML or metadata false positives on the document corpora, so speed and raw count alone overstate quality.
- `datefinder.find_dates`'s extra unique Seattle hits are mainly low-value metadata matches such as asset version numbers like `1.3.4` and `1.7.1`, plus `Jan 6 2016` as a smaller substring inside the longer `Jan 6 2016 at 10:13AM` timestamp that `timefhuman` already captures.
- `dateparser.search_dates`'s extra Seattle hits are mostly low-quality HTML false positives like `01'`, `90`, `50%`, `<h1`, and `set`.

## Reproduce

Run tests:

```bash
/tmp/timefhuman-bench-venv/bin/python -m pytest -q
```

Download the external corpora if you are not using a local `datefinder` clone at `/tmp/datefinder`.

```bash
/tmp/timefhuman-bench-venv/bin/python -m eval.download_corpora
```

Run the combined baseline benchmark.

```bash
/tmp/timefhuman-bench-venv/bin/python benchmarks/benchmark_baselines.py
```

Refresh the checked-in whole-document match dumps.

```bash
/tmp/timefhuman-bench-venv/bin/python benchmarks/dump_document_matches.py
```

## Rule Of Thumb

If a change makes the LALR parser or noisy extraction run more often, it is probably a slowdown.

The fastest route is:

1. deterministic whole-string parse for exact expressions
2. bounded noisy extraction for prose-like inputs
3. exact whole-string LALR fallback only when needed
4. LALR extraction rescue only when the fast extractor misses
