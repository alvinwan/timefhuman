# Performance Progress

Status as of March 30, 2026.

## Current State

- Branch: `codex/fast-path-parser`
- Tests: `124 passed`
- Deterministic fast path for common dates, times, durations, ranges, lists, and timezone suffixes in [timefhuman/fastpath.py](timefhuman/fastpath.py)
- Exact-expression LALR fallback for non-extraction parses in [timefhuman/exact_grammar.lark](timefhuman/exact_grammar.lark)
- Synthetic raw parse tree builder for `raw=True` in [timefhuman/main.py](timefhuman/main.py)
- Shared inference logic in [timefhuman/inference.py](timefhuman/inference.py)
- Cached month/timezone helpers in [timefhuman/utils.py](timefhuman/utils.py)
- Earley has been removed from the runtime parser path.

## What Changed

1. Added a fast deterministic parser for the common structured and semi-structured cases.
2. Added a token-window extractor so noisy text no longer forces full Earley parsing in common cases.
3. Moved matched-text extraction onto the fast path when possible.
4. Split inference into a shared module so fast-path and grammar-path behavior stay aligned.
5. Cached expensive lookup data and removed repeated timezone candidate sorting.
6. Added an accuracy-aware benchmark harness in [benchmarks/benchmark_baselines.py](benchmarks/benchmark_baselines.py).
7. Added an exact-expression LALR grammar so whole-string fallback no longer jumps straight to Earley.
8. Moved modifier-based weekdays/months, numeric dates, and ISO datetimes into the LALR layer to shrink the Earley-only surface.
9. Removed the Earley parser entirely and replaced `raw=True` with a lightweight synthetic tree built from matched spans plus tokenized unknown gaps.

## Latest Numbers

Benchmark source: [benchmarks/benchmark_baselines.py](benchmarks/benchmark_baselines.py)

Latest run snapshot:

| Parser | us/input | ok | exact |
| --- | ---: | ---: | ---: |
| `timefhuman` | `32.7` | `37/37` | `10/10` |
| `dateparser.parse` | `47488.5` | `20/37` | `6/10` |
| `parsedatetime.parseDT` | `42.9` | `36/37` | `6/10` |
| `datefinder.find_dates` | `35.1` | `23/37` | `5/10` |
| `ctparse.ctparse` | `12806.8` | `37/37` | `3/10` |
| `recurrent.parse` | `201.8` | `36/37` | `6/10` |
| `metadate.parse_date` | `34.0` | `31/37` | `5/10` |

Additional local tight-loop measurement for the current 37-input suite:

- `timefhuman`: roughly `24-25 us/input`

Notes:

- Raw microbench timings vary from run to run.
- `datefinder` and `metadate` are lighter-weight extractors and are not exact semantic peers for lists, ranges, and durations.
- The current target is not just raw speed. It is speed with correctness preserved on the repo’s intended behavior.
- On the local exact-parser audit across test strings, the Earley-only set dropped from `37` strings to `22` before the final Earley removal. Those remaining cases are now handled by the fast path, the LALR parser, or the synthetic raw tree.

## Fast Enough Check

Use this as the quick acceptance gate for future changes:

1. Run `pytest` and require the full test suite to stay green.
2. Run `benchmarks/benchmark_baselines.py`.
3. Confirm `timefhuman` stays faster than `dateparser`, `ctparse`, and `recurrent`.
4. Confirm `timefhuman` stays competitive with `parsedatetime`, `datefinder`, and `metadate` while preserving higher exactness on the checked cases.

If a change speeds up microbenchmarks but drops exactness or pushes more cases out of the deterministic fast path and LALR parser, it is not a win.

## Validation Commands

Run tests:

```bash
/tmp/timefhuman-bench-venv/bin/python -m pytest -q
```

Run baseline comparison:

```bash
/tmp/timefhuman-bench-venv/bin/python benchmarks/benchmark_baselines.py
```

Run the older simple parser benchmark:

```bash
/tmp/timefhuman-bench-venv/bin/python benchmarks/benchmark_parsers.py
```

## Remaining Work

- Identify which real-world inputs still miss the exact LALR grammar and document them.
- Move more natural-language exact parses from the fast path into the LALR grammar where that simplifies maintenance without regressing speed.
- Keep reducing the cost of complex list/range expressions, which are still the slowest fast-path cases.
- Expand the benchmark corpus beyond the current 37-case suite into a more realistic extraction corpus.
- Add a lightweight performance regression check so major slowdowns are visible before release.

## Guiding Rule

Prefer deterministic parsing first, then exact-expression LALR parsing, and use the synthetic raw tree only for debug output.
