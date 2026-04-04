# Benchmarks

Benchmarks were run on an Apple M3 MacBook Air with 16 GB RAM, macOS 26.3.1, Python 3.13.3.

`acc` is the correctness score for the dataset immediately to the left.
- Document `acc` is member-level coverage: lists and ranges still count as correct when a baseline finds the individual members separately.
- Document `group` is grouped correctness: lists and ranges only count when they are returned as one grouped result.
- Document `#` is the number of extracted datetimes for the dataset immediately to the left.
- Whole-document rows use a 2-second timeout. `timeout` in an `acc` column means the correctness run hit that cap.

These datasets are taken from datefinder's README: https://github.com/akoumjian/datefinder/blob/master/README.rst#benchmark-snapshot

### Main Results

| parser | short (ms) | acc | core (ms) | # | acc | group | sea_76k (ms) | # | acc | group | sea_560k (ms) | # | acc | group |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| timefhuman | 0.4 | <ins><strong>27/27</strong></ins> | 0.4 | [13](matches/timefhuman/core_corpus.md) | <ins><strong>14/14</strong></ins> | <ins><strong>13/13</strong></ins> | <ins><strong>23.6</strong></ins> | [56](matches/timefhuman/seattle_html_76k.md) | <ins><strong>57/57</strong></ins> | <ins><strong>56/56</strong></ins> | <ins><strong>184.9</strong></ins> | [557](matches/timefhuman/test_data_560k.md) | <ins><strong>94/94</strong></ins> | <ins><strong>74/74</strong></ins> |
| datefinder.find_dates | <ins><strong>0.3</strong></ins> | 10/27 | <ins><strong>0.2</strong></ins> | [11](matches/datefinder.find_dates/core_corpus.md) | 9/14 | 7/13 | 39.3 | [57](matches/datefinder.find_dates/seattle_html_76k.md) | 54/57 | 54/56 | 487.9 | [313](matches/datefinder.find_dates/test_data_560k.md) | 37/94 | 22/74 |
| dateparser* | 52.1 | 15/27 | 112.0 | [14](matches/dateparser/core_corpus.md) | 9/14 | 7/13 | 325.8 | [90](matches/dateparser/seattle_html_76k.md) | 53/57 | 53/56 | >2s | n/a | timeout | timeout |

### Lower-Accuracy Baselines

Seattle accuracy below `50/57`.

| parser | short (ms) | acc | core (ms) | # | acc | group | sea_76k (ms) | # | acc | group | sea_560k (ms) | # | acc | group |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| metadate.parse_date | 0.7 | 10/27 | 0.2 | 10 | 8/14 | 6/13 | 4.3 | 90 | 2/57 | 2/56 | 48.6 | 1538 | 25/94 | 19/74 |
| parsedatetime.parseDT | 0.7 | 13/27 | 2.4 | 1 | 0/14 | 0/13 | 699.0 | 1 | 0/57 | 0/56 | >2s | n/a | timeout | timeout |
| recurrent.parse | 4.7 | 13/27 | 4.8 | 1 | 0/14 | 0/13 | error | n/a | error | error | error | n/a | error | error |
| ctparse.ctparse | 132.2 | 6/27 | 120.8 | 1 | 1/14 | 1/13 | >2s | n/a | timeout | timeout | >2s | n/a | timeout | timeout |

Notes:

- `metadate.parse_date`, `datefinder.find_dates`, and `dateparser*` all pick up extra HTML or metadata false positives on the document corpora, so speed and raw count alone overstate quality.
- `datefinder.find_dates` extras on Seattle include version-like metadata such as `1.3.4` and `1.7.1`, plus `Jan 6 2016` as a smaller substring inside `Wed., Jan 6 2016 at 10:13AM`.
- `dateparser*` extras on Seattle include noisy HTML fragments such as `01'`, `90`, `50%`, `<h1`, and `set`.
- `sea_560k` accuracy is measured against the checked-in broad sampled gold set, not an exhaustive annotation of the whole corpus.
- `dateparser*` uses `dateparser.parse` for short columns and `dateparser.search_dates` for document columns.

## Reproduce

Run tests:

```bash
.venv/bin/python -m pytest -q
```

Download the external corpora if you are not using a local `datefinder` clone at `/tmp/datefinder`.

```bash
.venv/bin/python -m eval.download_corpora
```

Run the combined baseline benchmark.

```bash
.venv/bin/python benchmarks/benchmark_baselines.py
```

Refresh the checked-in whole-document match dumps:

```bash
.venv/bin/python benchmarks/dump_document_matches.py
```
