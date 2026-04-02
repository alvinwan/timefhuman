# Performance

Status as of April 2, 2026.

## Results

- Runtime path: deterministic whole-string parse, extraction-first for noisy text, LALR fallback only on misses. Earley is not used at runtime.
- Test suite: `127 passed in 0.22s`
- Tight loop: `19.52 us/input` at `10000` rounds
- Internal path benchmark:
  - `fast exact`: `6.5 us`
  - `fast collection`: `19.5 us`
  - `extract hit`: `46.1 us`
  - `extract miss`: `13.6 us`
- Cross-library snapshot from `benchmarks/benchmark_baselines.py`:
  - `timefhuman`: `56.1 us/input`, `37/37 ok`, `10/10 exact`
  - `parsedatetime`: `45.0 us/input`, `36/37 ok`, `6/10 exact`
  - `datefinder`: `42.9 us/input`, `23/37 ok`, `5/10 exact`
  - `recurrent`: `195.2 us/input`, `36/37 ok`, `6/10 exact`
  - `ctparse`: `12808.2 us/input`, `37/37 ok`, `3/10 exact`
  - `dateparser`: `49105.3 us/input`, `20/37 ok`, `6/10 exact`

## Reproduce

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

Run the local tight loop:

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

## Rule Of Thumb

If a change makes the LALR parser or noisy extraction run more often, it is probably a slowdown.

The fastest route is:

1. deterministic whole-string parse for exact expressions
2. bounded noisy extraction for prose-like inputs
3. exact whole-string LALR fallback only when needed
4. LALR extraction rescue only when the fast extractor misses
