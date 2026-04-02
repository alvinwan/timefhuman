# Benchmarks

Status as of April 2, 2026.

## Results

- Runtime path: deterministic whole-string parse first, bounded extraction for noisy text, LALR fallback only on misses. Earley is not used at runtime.
- `extracted`: returned any result on the 37-case short-input benchmark corpus.
- `correctness`: exact match on the 10-case exactness subset.
- `core_s`, `seattle_s`, `test_data_s`: warmed median seconds on the `datefinder` corpora. `n/a` means that parser is not run on full-document extraction in this harness.

| parser | us/input | extracted | correctness | core_s | seattle_s | test_data_s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `timefhuman` | `101.5` | `37/37` | `10/10` | `0.0020` | `0.1304` | `0.4669` |
| `dateparser.parse` | `135984.3` | `20/37` | `6/10` | `n/a` | `n/a` | `n/a` |
| `parsedatetime.parseDT` | `118.5` | `36/37` | `6/10` | `n/a` | `n/a` | `n/a` |
| `datefinder.find_dates` | `74.5` | `23/37` | `5/10` | `0.0007` | `0.1036` | `1.2725` |
| `ctparse.ctparse` | `35208.7` | `37/37` | `3/10` | `n/a` | `n/a` | `n/a` |
| `recurrent.parse` | `571.8` | `36/37` | `6/10` | `n/a` | `n/a` | `n/a` |
| `metadate.parse_date` | `95.0` | `31/37` | `5/10` | `n/a` | `n/a` | `n/a` |

## Reproduce

Run tests:

```bash
/tmp/timefhuman-bench-venv/bin/python -m pytest -q
```

Run the combined baseline benchmark.
This expects a local clone of `datefinder` at `/tmp/datefinder` to populate the document columns.

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
