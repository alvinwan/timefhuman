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
- Document `acc` is member-level coverage: lists and ranges still count as correct when a baseline finds the individual members separately.
- Document `group` is grouped correctness: lists and ranges only count when they are returned as one grouped result.
- `#` is the extracted count for the dataset immediately to the left.
- `dateparser*` uses `dateparser.parse` for short columns and `dateparser.search_dates` for document columns.
- Whole-document rows use a 1-second timeout. `timeout` in an `acc` column means the correctness run hit that cap.

### Main Results

| parser | short (ms) | acc | core (ms) | # | acc | group | sea_76k (ms) | # | acc | group | sea_560k (ms) | # |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| timefhuman | 0.8 | <ins><strong>27/27</strong></ins> | 1.0 | [13](matches/timefhuman/core_corpus.md) | <ins><strong>14/14</strong></ins> | <ins><strong>13/13</strong></ins> | <ins><strong>39.5</strong></ins> | [55](matches/timefhuman/seattle_html_76k.md) | <ins><strong>56/56</strong></ins> | <ins><strong>55/55</strong></ins> | <ins><strong>267.7</strong></ins> | [572](matches/timefhuman/test_data_560k.md) |
| datefinder.find_dates | <ins><strong>0.4</strong></ins> | 10/27 | <ins><strong>0.4</strong></ins> | [11](matches/datefinder.find_dates/core_corpus.md) | 9/14 | 7/13 | 66.7 | [57](matches/datefinder.find_dates/seattle_html_76k.md) | 54/56 | 54/55 | 838.1 | [313](matches/datefinder.find_dates/test_data_560k.md) |
| dateparser* | 87.0 | 15/27 | 186.4 | [14](matches/dateparser/core_corpus.md) | timeout | timeout | 552.1 | [90](matches/dateparser/seattle_html_76k.md) | 52/56 | 52/55 | >1000ms | n/a |

### Lower-Accuracy Baselines

Seattle accuracy below `50/55`.

| parser | short (ms) | acc | core (ms) | # | acc | group | sea_76k (ms) | # | acc | group | sea_560k (ms) | # |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| metadate.parse_date | <ins><strong>1.1</strong></ins> | 10/27 | <ins><strong>0.4</strong></ins> | 10 | <ins><strong>8/14</strong></ins> | <ins><strong>6/13</strong></ins> | <ins><strong>7.2</strong></ins> | 90 | <ins><strong>2/56</strong></ins> | <ins><strong>2/55</strong></ins> | <ins><strong>83.4</strong></ins> | 1538 |
| parsedatetime.parseDT | <ins><strong>1.1</strong></ins> | <ins><strong>13/27</strong></ins> | 4.1 | 1 | 0/14 | 0/13 | >1000ms | n/a | timeout | timeout | >1000ms | n/a |
| recurrent.parse | 7.6 | <ins><strong>13/27</strong></ins> | 6.9 | 1 | 0/14 | 0/13 | error | n/a | error | error | >1000ms | n/a |
| ctparse.ctparse | 219.1 | 6/27 | 208.9 | 1 | 1/14 | 1/13 | >1000ms | n/a | timeout | timeout | >1000ms | n/a |

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
