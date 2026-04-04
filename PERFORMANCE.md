# Performance

Status as of April 2, 2026.

## Results

- Runtime path: deterministic whole-string parse first, bounded extraction for noisy text, LALR fallback only on misses. Earley is not used at runtime.
- Correctness: public `timefhuman(...)` now completes on the `datefinder` `core_corpus` and `seattle_html_76k` datasets without raising conversion errors.
- Test suite: `137 passed in 0.55s`
- Warm whole-document median on this machine:
  - `core_corpus`: `timefhuman 0.00199s` for `10` matches, `datefinder.extract 0.00045s` for `14` matches
  - `seattle_html_76k`: `timefhuman 0.09717s` for `48` matches, `datefinder.extract 0.07821s` for `57` matches

## Reproduce

Run tests:

```bash
/tmp/timefhuman-bench-venv/bin/python -m pytest -q
```

Run the warmed whole-document benchmark used above.
This expects a local clone of `datefinder` at `/tmp/datefinder`.

```bash
/tmp/timefhuman-bench-venv/bin/python - <<'PY'
from datetime import datetime, timezone
import statistics
import time
from pathlib import Path

import datefinder
from timefhuman import timefhuman, tfhConfig

ref = datetime(2026, 3, 18, 12, 0, tzinfo=timezone.utc)
cfg = tfhConfig(now=ref)
docs = [
    ("core_corpus", "\n".join(
        x.strip()
        for x in Path("/tmp/datefinder/bench/corpus_core.txt").read_text(encoding="utf-8").splitlines()
        if x.strip()
    ), 10),
    ("seattle_html_76k", Path("/tmp/datefinder/tests/seattle_weekly.html").read_text(errors="ignore"), 7),
]

def bench(fn, iterations):
    times = []
    count = 0
    for _ in range(iterations):
        start = time.perf_counter()
        count = fn()
        times.append(time.perf_counter() - start)
    return statistics.median(times), count

for name, text, iterations in docs:
    tfh = bench(lambda: len(timefhuman(text, cfg)), iterations)
    df = bench(lambda: len(datefinder.extract(text, reference_dt=ref)), iterations)
    print(name, "timefhuman", tfh, "datefinder", df)
PY
```

## Rule Of Thumb

If a change makes the LALR parser or noisy extraction run more often, it is probably a slowdown.

The fastest route is:

1. deterministic whole-string parse for exact expressions
2. bounded noisy extraction for prose-like inputs
3. exact whole-string LALR fallback only when needed
4. LALR extraction rescue only when the fast extractor misses
