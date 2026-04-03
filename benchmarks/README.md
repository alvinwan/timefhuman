# Benchmarks

Status as of April 2, 2026.

## Setup

- Hardware: Apple M3 MacBook Air, 16 GB RAM
- OS: macOS 26.3.1
- Python: 3.13.3 from `/tmp/timefhuman-bench-venv`
- Whole-document corpora: either a local `datefinder` clone at `/tmp/datefinder` or cached downloads under `.eval_corpora/`

## Results

- `short_ms`: median milliseconds for one full pass over the 23 single-datetime short cases.
- `core_ms`, `seattle_76k_ms`, `test_560k_ms`: warmed median milliseconds for one full dataset run.
- `#`: extracted count for the dataset immediately to the left.
- `acc`: exact match count for the dataset immediately to the left.
- Whole-document rows are run with a strict 1-second per-call timeout. `>1000ms` means the parser exceeded that cap. `timeout` in an `acc` column means the correctness run hit the same cap.
- `timefhuman` is pinned first; the remaining rows are ordered by `core_ms`.

### Combined Scorecard

| parser | short_ms | acc | core_ms | # | acc | seattle_76k_ms | # | acc | test_560k_ms | # |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| timefhuman | 0.3 | **23/23** | 0.4 | [10](matches/timefhuman/core_corpus.md) | **10/10** | 21.6 | [55](matches/timefhuman/seattle_html_76k.md) | **55/55** | 132.6 | [594](matches/timefhuman/test_data_560k.md) |
| metadate.parse_date | 0.6 | 9/23 | **0.2** | 10 | 5/10 | **4.2** | 90 | 2/55 | **48.3** | 1538 |
| datefinder.find_dates | **0.2** | 9/23 | **0.2** | [11](matches/datefinder.find_dates/core_corpus.md) | 1/10 | 39.5 | [57](matches/datefinder.find_dates/seattle_html_76k.md) | 53/55 | 498.7 | [313](matches/datefinder.find_dates/test_data_560k.md) |
| parsedatetime.parseDT | 0.5 | 11/23 | 2.4 | 1 | 0/10 | 696.0 | 1 | 0/55 | >1000ms | n/a |
| recurrent.parse | 3.4 | 11/23 | 4.0 | 1 | 0/10 | error | n/a | error | error | n/a |
| dateparser* | 30.3 | 13/23 | 111.4 | [14](matches/dateparser.search_dates/core_corpus.md) | 1/10 | 327.5 | [90](matches/dateparser.search_dates/seattle_html_76k.md) | 52/55 | >1000ms | n/a |
| ctparse.ctparse | 76.2 | 5/23 | 125.2 | 1 | 0/10 | >1000ms | n/a | timeout | >1000ms | n/a |

Notes:

- `dateparser*` uses `dateparser.parse` for the short columns and `dateparser.search_dates` for the document columns.
- `metadate.parse_date`, `datefinder.find_dates`, and `dateparser*` all pick up extra HTML or metadata false positives on the document corpora, so speed and raw count alone overstate quality.
- `datefinder.find_dates` extras on Seattle include version-like metadata such as `1.3.4` and `1.7.1`, plus `Jan 6 2016` as a smaller substring inside `Jan 6 2016 at 10:13AM`.
- `dateparser*` extras on Seattle include noisy HTML fragments such as `01'`, `90`, `50%`, `<h1`, and `set`.

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
