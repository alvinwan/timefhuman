# Performance

Status as of April 2, 2026.

## Current Snapshot

- Branch: `codex/fast-path-parser`
- Test suite: `127 passed in 0.22s`
- Runtime parser stack:
  1. handwritten deterministic whole-string parser in [timefhuman/fastpath.py](timefhuman/fastpath.py)
  2. extraction-first routing for noisy text in [timefhuman/extraction.py](timefhuman/extraction.py)
  3. LALR whole-string fallback for exact expressions in [timefhuman/grammar.lark](timefhuman/grammar.lark)
  4. LALR extraction rescue only after fast extraction misses
- Earley is not used in the runtime parser path.

## Why It Is Fast

### 1. Common expressions do not go through a general parser

Standalone inputs like:

- `5p`
- `7/17/18 3:00 p.m.`
- `30 minutes`
- `3p -4p`
- `July 4th or 5th at 3PM`

are handled by the deterministic parser in [timefhuman/fastpath.py](timefhuman/fastpath.py). That avoids parse-table work for the cases that dominate normal usage.

### 2. Noisy input skips straight to extraction

If an input looks like prose instead of a standalone expression, [timefhuman/main.py](timefhuman/main.py) routes directly into [timefhuman/extraction.py](timefhuman/extraction.py) instead of trying to parse the full sentence as one date expression first. That avoids wasting the hot path on strings like:

- `How does 5p mon sound? Or maybe 4p tu?`
- `There are 3 ways to do it`
- `e 6:50PM`

### 3. LALR is a fallback, not the primary path

The exact-expression grammar in [timefhuman/grammar.lark](timefhuman/grammar.lark) is still valuable, but it only runs after the deterministic path misses. That keeps grammar flexibility without paying grammar cost on every input.

### 4. Prose extraction is bounded and selective

For noisy text like:

- `How does 5p mon sound? Or maybe 4p tu?`
- `e 6:50PM`
- `September 30, 2019.`

the extractor in [timefhuman/extraction.py](timefhuman/extraction.py) does not blindly try large windows of prose. It:

- scans for plausible start tokens
- limits candidate spans to contiguous expression-like token runs
- skips duplicate trimmed candidates
- uses the LALR parser only as a rescue path after fast extraction misses

That keeps extraction from exploding into repeated failed parses.

### 5. Expensive lookup data is cached

[timefhuman/utils.py](timefhuman/utils.py) caches timezone mappings, timezone word lengths, timezone words, and month mappings so the hot path is not rebuilding or resorting metadata on every call.

### 6. `raw=True` is cheap

Debug output no longer requires a heavyweight parser pass. [timefhuman/main.py](timefhuman/main.py) builds a lightweight synthetic tree from matched spans plus unknown-token gaps.

## Latest Benchmarks

### Validation

```bash
/tmp/timefhuman-bench-venv/bin/python -m pytest -q
```

Result:

```text
127 passed in 0.22s
```

### Local Tight Loop

This is the best signal for `timefhuman` itself because it removes most cross-library benchmark noise.

Command:

```bash
/tmp/timefhuman-bench-venv/bin/python - <<'PY'
import time
from datetime import datetime
from benchmarks.benchmark_baselines import INPUTS
from timefhuman import timefhuman
from timefhuman.main import tfhConfig

cfg = tfhConfig(now=datetime(2018, 8, 4, 14, 0))
for rounds in [1000, 5000, 10000]:
    start = time.perf_counter()
    for _ in range(rounds):
        for text in INPUTS:
            timefhuman(text, config=cfg)
    us = (time.perf_counter() - start) / (rounds * len(INPUTS)) * 1e6
    print(rounds, f"{us:.2f} us/input")
PY
```

Latest run:

- `1000` rounds: `22.19 us/input`
- `5000` rounds: `20.10 us/input`
- `10000` rounds: `19.52 us/input`

### Path Benchmark

Source: [benchmarks/benchmark_paths.py](benchmarks/benchmark_paths.py)

Latest run:

| Expression Case | `timefhuman` | `parse_fast` | `parse_lalr` |
| --- | ---: | ---: | ---: |
| `fast exact` | `6.5 us` | `3.3 us` | `18.2 us` |
| `fast collection` | `19.5 us` | `16.5 us` | `50.5 us` |
| `prefixed input` | `9.1 us` | `9.7 us` | `11.1 us` |
| `structured` | `5.4 us` | `3.5 us` | `12.7 us` |

| Extract Case | `timefhuman` | `fast extract` | `lalr extract` |
| --- | ---: | ---: | ---: |
| `extract hit` | `46.1 us` | `35.5 us` | `84.4 us` |
| `extract miss` | `13.6 us` | `6.7 us` | `6.6 us` |

Interpretation:

- The handwritten parser is the hot path.
- Extraction-first routing keeps noisy inputs off the expensive whole-string path.
- The LALR parser is materially slower than the handwritten parser, so it should stay a fallback.
- Even after routing improvements, noisy extraction is still slower than exact-expression parsing because it has to scan a larger token stream.

### Cross-Library Snapshot

Source: [benchmarks/benchmark_baselines.py](benchmarks/benchmark_baselines.py)

Latest run:

| Parser | us/input | ok | exact |
| --- | ---: | ---: | ---: |
| `timefhuman` | `56.1` | `37/37` | `10/10` |
| `dateparser.parse` | `49105.3` | `20/37` | `6/10` |
| `parsedatetime.parseDT` | `45.0` | `36/37` | `6/10` |
| `datefinder.find_dates` | `42.9` | `23/37` | `5/10` |
| `ctparse.ctparse` | `12808.2` | `37/37` | `3/10` |
| `recurrent.parse` | `195.2` | `36/37` | `6/10` |
| `metadate.parse_date` | `32.3` | `31/37` | `5/10` |

Notes:

- This table is useful for rough comparison, but it is noisier than the local tight-loop measurement.
- `timefhuman`'s own stable throughput is better represented by the tight-loop numbers above.
- `datefinder` and `metadate` are lighter-weight extractors and are not exact semantic peers for lists, ranges, and durations.

## Commands

Run tests:

```bash
/tmp/timefhuman-bench-venv/bin/python -m pytest -q
```

Run the cross-library benchmark:

```bash
/tmp/timefhuman-bench-venv/bin/python benchmarks/benchmark_baselines.py
```

Run the internal path benchmark:

```bash
/tmp/timefhuman-bench-venv/bin/python benchmarks/benchmark_paths.py
```

Run the older simple parser benchmark:

```bash
/tmp/timefhuman-bench-venv/bin/python benchmarks/benchmark_parsers.py
```

## Rule Of Thumb

If a change makes the exact LALR parser or noisy extraction run more often, it is probably a slowdown.

The fastest route is:

1. deterministic whole-string parse for exact expressions
2. bounded noisy extraction for prose-like inputs
3. exact whole-string LALR fallback only when needed
4. LALR extraction rescue only when the fast extractor misses
