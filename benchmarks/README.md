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

| parser | short (ms) | acc | core (ms) | # | acc | [sea_76k (ms)](https://github.com/datefinder/datefinder/blob/main/bench/benchmark_results.md#L6) | # | acc | [sea_560k (ms)](https://github.com/datefinder/datefinder/blob/main/bench/benchmark_results.md#L7) | # |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| timefhuman | 0.8 | <ins><strong>27/27</strong></ins> | 0.9 | [13](matches/timefhuman/core_corpus.md) | <ins><strong>13/13</strong></ins> | <ins><strong>39.9</strong></ins> | [55](matches/timefhuman/seattle_html_76k.md) | <ins><strong>55/55</strong></ins> | <ins><strong>269.8</strong></ins> | [572](matches/timefhuman/test_data_560k.md) |
| datefinder.find_dates | <ins><strong>0.5</strong></ins> | 10/27 | <ins><strong>0.4</strong></ins> | [11](matches/datefinder.find_dates/core_corpus.md) | 7/13 | 66.6 | [57](matches/datefinder.find_dates/seattle_html_76k.md) | 54/55 | 839.1 | [313](matches/datefinder.find_dates/test_data_560k.md) |
| dateparser* | 87.7 | 15/27 | 188.4 | [14](matches/dateparser/core_corpus.md) | timeout | 548.3 | [90](matches/dateparser/seattle_html_76k.md) | 52/55 | >1000ms | n/a |

### Lower-Accuracy Baselines

Seattle accuracy below `50/55`.

| parser | short (ms) | acc | core (ms) | # | acc | [sea_76k (ms)](https://github.com/datefinder/datefinder/blob/main/bench/benchmark_results.md#L6) | # | acc | [sea_560k (ms)](https://github.com/datefinder/datefinder/blob/main/bench/benchmark_results.md#L7) | # |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| metadate.parse_date | <ins><strong>1.1</strong></ins> | 10/27 | <ins><strong>0.3</strong></ins> | 10 | <ins><strong>6/13</strong></ins> | <ins><strong>7.0</strong></ins> | 90 | <ins><strong>2/55</strong></ins> | <ins><strong>83.7</strong></ins> | 1538 |
| parsedatetime.parseDT | <ins><strong>1.1</strong></ins> | <ins><strong>13/27</strong></ins> | 4.2 | 1 | 0/13 | >1000ms | n/a | timeout | >1000ms | n/a |
| recurrent.parse | 7.6 | <ins><strong>13/27</strong></ins> | 6.8 | 1 | 0/13 | error | n/a | error | >1000ms | n/a |
| ctparse.ctparse | 220.3 | 6/27 | 210.0 | 1 | 1/13 | >1000ms | n/a | timeout | >1000ms | n/a |

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
