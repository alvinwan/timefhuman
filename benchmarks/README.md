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
- `short`: median `us/input` over 7 full-suite passes of the 23 single-datetime short cases.
- `acc`: exact match count for the column immediately to the left.
- `core_corpus`, `seattle_html_76k`, `test_data_560k`: warmed median seconds and extracted count, formatted as `seconds (count)`.
- `core_corpus acc`, `seattle_html_76k acc`: gold-corpus match counts. Parsers with matched-text APIs are scored on `(matched text, normalized value)`. Parsers without span APIs are scored on normalized value only after running on the full document.
- Whole-document rows are run with a strict 1-second per-call timeout. `>1s` means the parser exceeded that cap.
- Whole-document counts link to checked-in raw match dumps under `benchmarks/matches/`.
- `timefhuman` whole-document extraction uses `infer_datetimes=False`, so linked dumps keep raw dates, times, and timedeltas while explicit datetimes stay datetimes.
- `timefhuman` is pinned first; the remaining rows are ordered by overall speed.

### Combined Scorecard

| parser | short | acc | core_corpus | acc | seattle_html_76k | acc | test_data_560k |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| timefhuman | 15.9 | **23/23** | 0.0004 ([10](matches/timefhuman/core_corpus.md)) | **10/10** | 0.0218 ([55](matches/timefhuman/seattle_html_76k.md)) | **55/55** | 0.1347 ([594](matches/timefhuman/test_data_560k.md)) |
| metadate.parse_date | 26.1 | 9/23 | **0.0002** (10) | 5/10 | **0.0043** (90) | 2/55 | **0.0496** (1538) |
| datefinder.find_dates | **9.1** | 9/23 | 0.0002 ([11](matches/datefinder.find_dates/core_corpus.md)) | 1/10 | 0.0397 ([57](matches/datefinder.find_dates/seattle_html_76k.md)) | 53/55 | 0.4964 ([313](matches/datefinder.find_dates/test_data_560k.md)) |
| dateparser.search_dates | n/a | n/a | 0.1107 ([14](matches/dateparser.search_dates/core_corpus.md)) | 1/10 | 0.3214 ([90](matches/dateparser.search_dates/seattle_html_76k.md)) | 52/55 | >1s (n/a) |
| parsedatetime.parseDT | 20.2 | 11/23 | 0.0024 (1) | 0/10 | 0.6959 (1) | 0/55 | >1s (n/a) |
| recurrent.parse | 140.0 | 11/23 | 0.0038 (1) | 0/10 | n/a | n/a | n/a |
| dateparser.parse | 1307.0 | 13/23 | 0.1212 (0) | 0/10 | >1s (n/a) | >1s | >1s (n/a) |
| ctparse.ctparse | 3263.8 | 5/23 | 0.1263 (1) | 0/10 | >1s (n/a) | >1s | >1s (n/a) |

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
