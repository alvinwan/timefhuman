# Benchmarks

Status as of April 2, 2026.

## Results

- Runtime path: deterministic whole-string parse first, bounded extraction for noisy text, LALR fallback only on misses. Earley is not used at runtime.
- `extracted`: returned any result on the 37-case short-input corpus.
- `correctness`: exact match on the 10-case exactness subset.
- `core_corpus`, `seattle_html_76k`, `test_data_560k`: warmed median seconds on the `datefinder` document corpora.
- `>15s`: exceeded the document benchmark timeout for that dataset.

### Short-Input Parsing

| parser | us/input | extracted | correctness |
| --- | ---: | ---: | ---: |
| `timefhuman` | `67.3` | `37/37` | `10/10` |
| `dateparser.parse` | `105315.5` | `20/37` | `6/10` |
| `parsedatetime.parseDT` | `92.3` | `36/37` | `6/10` |
| `datefinder.find_dates` | `56.2` | `23/37` | `5/10` |
| `ctparse.ctparse` | `29565.8` | `37/37` | `3/10` |
| `recurrent.parse` | `460.9` | `36/37` | `6/10` |
| `metadate.parse_date` | `65.3` | `31/37` | `5/10` |

### Whole-Document Extraction

Only parsers with a comparable whole-document extraction API are included here.

| parser | core_corpus | seattle_html_76k | test_data_560k |
| --- | ---: | ---: | ---: |
| `timefhuman` | `0.0020` | `0.1024` | `0.3860` |
| `dateparser.search_dates` | `0.2506` | `0.8103` | `>15s` |
| `datefinder.find_dates` | `0.0005` | `0.0833` | `1.0325` |

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
