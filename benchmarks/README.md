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
- `short_correct`: exact match on the 23 single-datetime cases within that same suite.
- `core_corpus`, `seattle_html_76k` in the correctness table: gold-corpus match counts. Parsers with matched-text APIs are scored on `(matched text, normalized value)`. Parsers without span APIs are scored on normalized value only after running on the full document.
- `short_us/input`: median over 7 full-suite passes of the 23 single-datetime short cases.
- `core_corpus`, `seattle_html_76k`, `test_data_560k` in the performance table: warmed median seconds and extracted count, formatted as `seconds (count)`.
- Whole-document rows are run with a strict 1-second per-call timeout. `>1s` means the parser exceeded that cap.
- Whole-document counts link to checked-in raw match dumps under `benchmarks/matches/`.
- `timefhuman` whole-document extraction uses `infer_datetimes=False`, so linked dumps keep raw dates, times, and timedeltas while explicit datetimes stay datetimes.
- `timefhuman` is pinned first; the remaining rows are ordered by overall score in the correctness table and overall speed in the performance table.

### Correctness

| parser | short_correct | core_corpus | seattle_html_76k |
| --- | ---: | ---: | ---: |
| timefhuman | **23/23** | **10/10** | **55/55** |
| datefinder.find_dates | 9/23 | 1/10 | 53/55 |
| dateparser.search_dates | n/a | 1/10 | 52/55 |
| metadate.parse_date | 9/23 | 5/10 | 2/55 |
| dateparser.parse | 13/23 | 0/10 | >1s |
| parsedatetime.parseDT | 11/23 | 0/10 | 0/55 |
| recurrent.parse | 11/23 | 0/10 | n/a |
| ctparse.ctparse | 5/23 | 0/10 | >1s |

### Performance

| parser | short_us/input | core_corpus | seattle_html_76k | test_data_560k |
| --- | ---: | ---: | ---: | ---: |
| timefhuman | 14.4 | 0.0004 ([10](matches/timefhuman/core_corpus.md)) | 0.0223 ([55](matches/timefhuman/seattle_html_76k.md)) | 0.1351 ([594](matches/timefhuman/test_data_560k.md)) |
| metadate.parse_date | 21.1 | **0.0002** (10) | **0.0042** (90) | **0.0483** (1538) |
| datefinder.find_dates | **10.7** | 0.0003 ([11](matches/datefinder.find_dates/core_corpus.md)) | 0.0396 ([57](matches/datefinder.find_dates/seattle_html_76k.md)) | 0.4977 ([313](matches/datefinder.find_dates/test_data_560k.md)) |
| dateparser.search_dates | n/a | 0.1109 ([14](matches/dateparser.search_dates/core_corpus.md)) | 0.3285 ([90](matches/dateparser.search_dates/seattle_html_76k.md)) | >1s (n/a) |
| parsedatetime.parseDT | 20.3 | 0.0024 (1) | 0.6956 (1) | >1s (n/a) |
| recurrent.parse | 146.4 | 0.0040 (1) | n/a | n/a |
| dateparser.parse | 1290.9 | 0.1215 (0) | >1s (n/a) | >1s (n/a) |
| ctparse.ctparse | 3320.6 | 0.1246 (1) | >1s (n/a) | >1s (n/a) |

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
