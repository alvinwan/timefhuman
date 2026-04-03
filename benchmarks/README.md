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
- `sea_560k` accuracy is measured against the checked-in sampled gold set, not an exhaustive annotation of the whole corpus.
- `#` is the extracted count for the dataset immediately to the left.
- `dateparser*` uses `dateparser.parse` for short columns and `dateparser.search_dates` for document columns.
- Whole-document rows use a 2-second timeout. `timeout` in an `acc` column means the correctness run hit that cap.

### Main Results

| parser | short (ms) | acc | core (ms) | # | acc | group | sea_76k (ms) | # | acc | group | sea_560k (ms) | # | acc | group |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| timefhuman | 0.8 | <ins><strong>27/27</strong></ins> | 1.0 | [13](matches/timefhuman/core_corpus.md) | <ins><strong>14/14</strong></ins> | <ins><strong>13/13</strong></ins> | <ins><strong>42.5</strong></ins> | [55](matches/timefhuman/seattle_html_76k.md) | <ins><strong>56/56</strong></ins> | <ins><strong>55/55</strong></ins> | <ins><strong>279.8</strong></ins> | [554](matches/timefhuman/test_data_560k.md) | <ins><strong>26/26</strong></ins> | <ins><strong>12/12</strong></ins> |
| datefinder.find_dates | <ins><strong>0.4</strong></ins> | 10/27 | <ins><strong>0.4</strong></ins> | [11](matches/datefinder.find_dates/core_corpus.md) | 9/14 | 7/13 | 66.5 | [57](matches/datefinder.find_dates/seattle_html_76k.md) | 54/56 | 54/55 | 834.9 | [313](matches/datefinder.find_dates/test_data_560k.md) | 13/26 | 0/12 |
| dateparser* | 77.5 | 15/27 | 183.5 | [14](matches/dateparser/core_corpus.md) | 9/14 | 7/13 | 540.3 | [90](matches/dateparser/seattle_html_76k.md) | 52/56 | 52/55 | >2000ms | n/a | timeout | timeout |

### Lower-Accuracy Baselines

Seattle accuracy below `50/55`.

| parser | short (ms) | acc | core (ms) | # | acc | group | sea_76k (ms) | # | acc | group | sea_560k (ms) | # | acc | group |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| metadate.parse_date | 1.1 | 10/27 | 0.3 | 10 | 8/14 | 6/13 | 6.8 | 90 | 2/56 | 2/55 | 77.8 | 1538 | 4/26 | 1/12 |
| parsedatetime.parseDT | 1.1 | 13/27 | 4.1 | 1 | 0/14 | 0/13 | 1164.8 | 1 | 0/56 | 0/55 | >2000ms | n/a | timeout | timeout |
| recurrent.parse | 7.5 | 13/27 | 6.6 | 1 | 0/14 | 0/13 | error | n/a | error | error | error | n/a | error | error |
| ctparse.ctparse | 211.6 | 6/27 | 207.6 | 1 | 1/14 | 1/13 | >2000ms | n/a | timeout | timeout | >2000ms | n/a | timeout | timeout |

Notes:

- `metadate.parse_date`, `datefinder.find_dates`, and `dateparser*` all pick up extra HTML or metadata false positives on the document corpora, so speed and raw count alone overstate quality.
- `datefinder.find_dates` extras on Seattle include version-like metadata such as `1.3.4` and `1.7.1`, plus `Jan 6 2016` as a smaller substring inside `Wed., Jan 6 2016 at 10:13AM`.
- `dateparser*` extras on Seattle include noisy HTML fragments such as `01'`, `90`, `50%`, `<h1`, and `set`.
- `timefhuman` still has some unresolved standalone-weekday matches in `sea_560k`, such as `Friday`, `Saturday`, and `Monday` inside policy prose. Those are currently left out of the sampled gold set.

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
