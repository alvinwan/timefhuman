# Benchmarks

Status as of April 2, 2026.

## Results

- Runtime path: deterministic whole-string parse first, bounded extraction for noisy text, LALR fallback only on misses. Earley is not used at runtime.
- `extracted`: returned any result on the 37-case short-input corpus.
- `correctness`: exact match on the 10-case exactness subset.
- `core_corpus`, `seattle_html_76k`, `test_data_560k`: warmed median seconds and extracted count, formatted as `seconds/count`.
- `>15s/n/a`: exceeded the document benchmark timeout for that dataset.
- `timefhuman` is pinned first; the remaining rows are ordered fastest to slowest.

### Short-Input Parsing

| parser | us/input | extracted | correctness |
| --- | ---: | ---: | ---: |
| timefhuman | 67.1 | **37/37** | **10/10** |
| datefinder.find_dates | **54.8** | 23/37 | 5/10 |
| metadate.parse_date | 77.5 | 31/37 | 5/10 |
| parsedatetime.parseDT | 86.0 | 36/37 | 6/10 |
| recurrent.parse | 452.5 | 36/37 | 6/10 |
| ctparse.ctparse | 28715.5 | **37/37** | 3/10 |
| dateparser.parse | 110968.9 | 20/37 | 6/10 |

### Whole-Document Extraction

Only parsers with a comparable whole-document extraction API are included here.

| parser | core_corpus | seattle_html_76k | test_data_560k |
| --- | ---: | ---: | ---: |
| timefhuman | 0.0016/10 | 0.0983/48 | **0.3628/637** |
| datefinder.find_dates | **0.0006/11** | **0.0792/57** | 0.9695/313 |
| dateparser.search_dates | 0.2412/14 | 0.7354/90 | >15s/n/a |

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
