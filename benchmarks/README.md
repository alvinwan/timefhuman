# Benchmarks

Status as of April 3, 2026.

## Setup

- Hardware: Apple M3 MacBook Air, 16 GB RAM
- OS: macOS 26.3.1
- Python: 3.13.3 from `/tmp/timefhuman-bench-venv`
- Whole-document corpora: either a local `datefinder` clone at `/tmp/datefinder` or cached downloads under `.eval_corpora/`

## Results

- Milliseconds throughout.
- `acc` is the correctness score for the dataset immediately to the left.
- `#` is the extracted count for the dataset immediately to the left.
- `dateparser*` uses `dateparser.parse` for short columns and `dateparser.search_dates` for document columns.
- Document `acc` prefers exact text+value matches, but still counts value-equivalent matches when a baseline returns a narrower or wider span.
- Whole-document rows use a 1-second timeout. `timeout` in an `acc` column means the correctness run hit that cap.

### Main Results

| parser | short (ms) | acc | core (ms) | # | acc | seattle_76k (ms) | # | acc | test_560k (ms) | # |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| timefhuman | 1.0 | **26/26** | 1.3 | [13](matches/timefhuman/core_corpus.md) | **13/13** | 50.4 | [55](matches/timefhuman/seattle_html_76k.md) | **55/55** | 315.3 | [576](matches/timefhuman/test_data_560k.md) |
| datefinder.find_dates | **0.5** | 10/26 | **0.5** | [11](matches/datefinder.find_dates/core_corpus.md) | 7/13 | 72.7 | [57](matches/datefinder.find_dates/seattle_html_76k.md) | 54/55 | 933.2 | [313](matches/datefinder.find_dates/test_data_560k.md) |
| dateparser* | 88.0 | 15/26 | 215.8 | [14](matches/dateparser/core_corpus.md) | timeout | 653.0 | [90](matches/dateparser/seattle_html_76k.md) | 52/55 | >1000ms | n/a |

### Lower-Accuracy Baselines

Seattle accuracy below `50/55`.

| parser | short (ms) | acc | core (ms) | # | acc | seattle_76k (ms) | # | acc | test_560k (ms) | # |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| metadate.parse_date | 1.5 | 10/26 | **0.4** | 10 | 6/13 | **8.4** | 90 | 2/55 | **97.2** | 1538 |
| parsedatetime.parseDT | 1.2 | 13/26 | 4.1 | 1 | 0/13 | >1000ms | n/a | timeout | >1000ms | n/a |
| recurrent.parse | 8.5 | 13/26 | 8.0 | 1 | 0/13 | error | n/a | error | >1000ms | n/a |
| ctparse.ctparse | 255.2 | 6/26 | 241.1 | 1 | 1/13 | >1000ms | n/a | timeout | >1000ms | n/a |

Notes:

- `metadate.parse_date`, `datefinder.find_dates`, and `dateparser*` all pick up extra HTML or metadata false positives on the document corpora, so speed and raw count alone overstate quality.
- `datefinder.find_dates` extras on Seattle include version-like metadata such as `1.3.4` and `1.7.1`, plus `Jan 6 2016` as a smaller substring inside `Wed., Jan 6 2016 at 10:13AM`.
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
