# Benchmarks

Status as of April 2, 2026.

## Results

- Runtime path: deterministic whole-string parse first, bounded extraction for noisy text, LALR fallback only on misses. Earley is not used at runtime.
- `extracted`: returned any result on the 37-case short-input corpus.
- `correctness`: exact match on the 10-case exactness subset.
- `core_corpus`, `seattle_html_76k`, `test_data_560k`: warmed median seconds and extracted count, formatted as `seconds (count)`.
- `>15s (n/a)`: exceeded the document benchmark timeout for that dataset.
- `timefhuman` is pinned first; the remaining rows are ordered fastest to slowest.

### Short-Input Parsing

| parser | us/input | extracted | correctness |
| --- | ---: | ---: | ---: |
| timefhuman | 72.6 | **37/37** | **10/10** |
| metadate.parse_date | **57.6** | 31/37 | 5/10 |
| datefinder.find_dates | 63.5 | 23/37 | 5/10 |
| parsedatetime.parseDT | 87.0 | 36/37 | 6/10 |
| recurrent.parse | 408.0 | 36/37 | 6/10 |
| ctparse.ctparse | 27077.0 | **37/37** | 3/10 |
| dateparser.parse | 99538.1 | 20/37 | 6/10 |

### Whole-Document Extraction

Only parsers with a comparable whole-document extraction API are included here.

| parser | core_corpus | seattle_html_76k | test_data_560k |
| --- | ---: | ---: | ---: |
| timefhuman | 0.0019 (10) | 0.1004 (49) | **0.3802 (645)** |
| datefinder.find_dates | **0.0005 (11)** | **0.0770 (57)** | 0.9598 (313) |
| dateparser.search_dates | 0.2306 (14) | 0.7279 (90) | >15s (n/a) |

Notes on what the other baselines found that `timefhuman` still misses:

- `core_corpus`: mostly multilingual relative phrases, such as Spanish `ayer`, `mañana`, and French `dans 2 jours`.
- `seattle_html_76k`: most of `datefinder.find_dates`'s extra hits are HTML/CMS noise rather than user-visible dates:
  version numbers like `1.3.4` and `1.7.1`, maintenance-comment dates like `REMOVED 08-07-2013`, and URL slug dates like `2013-01-23`.
- `seattle_html_76k`: most of `dateparser.search_dates`'s extra hits are lower-quality HTML false positives like `01'`, `90`, `50%`, `<h1`, and `set`.
- `seattle_html_76k`: the real prose miss we found was `7-11pm`; that is now handled by `timefhuman`, which is why the Seattle count increased from `48` to `49`.

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
