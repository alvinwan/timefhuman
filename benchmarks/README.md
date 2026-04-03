# Benchmarks

Status as of April 2, 2026.

## Results

- Runtime path: deterministic whole-string parse first, bounded extraction for noisy text, LALR fallback only on misses. Earley is not used at runtime.
- `extracted`: returned any result on the 37-case short-input corpus.
- `correctness`: exact match on the 10-case exactness subset.
- `core_corpus`, `seattle_html_76k`, `test_data_560k`: warmed median seconds and extracted count, formatted as `seconds (count)`.
- `>15s (n/a)`: exceeded the document benchmark timeout for that dataset.
- whole-document counts are raw extracted-match counts, so HTML noise can inflate them.
- `timefhuman` is pinned first; the remaining rows are ordered fastest to slowest.

### Short-Input Parsing

| parser | us/input | extracted | correctness |
| --- | ---: | ---: | ---: |
| timefhuman | 94.6 | **37/37** | **10/10** |
| metadate.parse_date | **83.6** | 31/37 | 5/10 |
| datefinder.find_dates | 114.5 | 23/37 | 5/10 |
| parsedatetime.parseDT | 127.9 | 36/37 | 6/10 |
| recurrent.parse | 521.1 | 36/37 | 6/10 |
| ctparse.ctparse | 35200.4 | **37/37** | 3/10 |
| dateparser.parse | 130539.7 | 20/37 | 6/10 |

### Whole-Document Extraction

Only parsers with a comparable whole-document extraction API are included here.

| parser | core_corpus | seattle_html_76k | test_data_560k |
| --- | ---: | ---: | ---: |
| timefhuman | 0.0032 (11) | 0.1615 (102) | **0.5215 (800)** |
| datefinder.find_dates | **0.0006 (11)** | **0.0877 (57)** | 1.0846 (313) |
| dateparser.search_dates | 0.2444 (14) | 0.8960 (90) | >15s (n/a) |

Notes on what the other baselines found that `timefhuman` still misses:

- `core_corpus`: mostly multilingual relative phrases, such as Spanish `ayer`, `mañana`, and French `dans 2 jours`.
- `seattle_html_76k`: `datefinder.find_dates` is now mostly ahead on a few low-value extras:
  asset version numbers like `1.3.4` and `1.7.1`, plus `Jan 6 2016` as a smaller substring inside the longer `Jan 6 2016 at 10:13AM` timestamp that `timefhuman` already captures.
- `seattle_html_76k`: most of `dateparser.search_dates`'s extra hits are lower-quality HTML false positives like `01'`, `90`, `50%`, `<h1`, and `set`.

## Reproduce

Run tests:

```bash
/tmp/timefhuman-bench-venv/bin/python -m pytest -q
```

Run the combined baseline benchmark.
This expects a local clone of `datefinder` at `/tmp/datefinder` to populate the whole-document table.

```bash
/tmp/timefhuman-bench-venv/bin/python benchmarks/benchmark_baselines.py
```

## Rule Of Thumb

If a change makes the LALR parser or noisy extraction run more often, it is probably a slowdown.

The fastest route is:

1. deterministic whole-string parse for exact expressions
2. bounded noisy extraction for prose-like inputs
3. exact whole-string LALR fallback only when needed
4. LALR extraction rescue only when the fast extractor misses
