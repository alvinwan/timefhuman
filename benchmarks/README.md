# Benchmarks

Status as of April 2, 2026.

## Results

- Runtime path: deterministic whole-string parse first, bounded extraction for noisy text, LALR fallback only on misses. Earley is not used at runtime.
- `extracted`: returned any result on the 37-case short-input corpus.
- `correctness`: exact match on the 10-case exactness subset.
- `core_corpus`, `seattle_html_76k`, `test_data_560k`: warmed median seconds on the `datefinder` document corpora.
- `>15s`: exceeded the document benchmark timeout for that dataset.
- `timefhuman` is pinned first; the remaining rows are ordered fastest to slowest.

### Short-Input Parsing

| parser | us/input | extracted | correctness |
| --- | ---: | ---: | ---: |
| `timefhuman` | `68.3` | **`37/37`** | **`10/10`** |
| `datefinder.find_dates` | **`64.2`** | `23/37` | `5/10` |
| `metadate.parse_date` | `79.4` | `31/37` | `5/10` |
| `parsedatetime.parseDT` | `106.9` | `36/37` | `6/10` |
| `recurrent.parse` | `443.6` | `36/37` | `6/10` |
| `ctparse.ctparse` | `28714.5` | **`37/37`** | `3/10` |
| `dateparser.parse` | `102994.5` | `20/37` | `6/10` |

### Whole-Document Extraction

Only parsers with a comparable whole-document extraction API are included here.

| parser | core_corpus | seattle_html_76k | test_data_560k |
| --- | ---: | ---: | ---: |
| `timefhuman` | `0.0019` | `0.1006` | **`0.3652`** |
| `datefinder.find_dates` | **`0.0006`** | **`0.0790`** | `0.9830` |
| `dateparser.search_dates` | `0.2829` | `0.8582` | `>15s` |

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
