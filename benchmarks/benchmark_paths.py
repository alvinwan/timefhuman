import time
from datetime import datetime

from timefhuman import timefhuman
from timefhuman.fastpath import extract_fast, parse_fast
from timefhuman.main import _parse_exact, tfhConfig
from timefhuman.utils import generate_timezone_mapping


NOW = datetime(2018, 8, 4, 14, 0)
CONFIG = tfhConfig(now=NOW)
TIMEZONE_MAPPING = generate_timezone_mapping()
EXACT_CASES = [
    ("fast exact", "5p"),
    ("fast collection", "July 4th or 5th at 3PM"),
    ("prefixed input", "e 6:50PM"),
    ("structured", "2022-12-27T09:15:01.002"),
]
EXTRACT_CASES = [
    ("extract hit", "How does 5p mon sound? Or maybe 4p tu?"),
    ("extract miss", "There are 3 ways to do it"),
]


def bench(func, iterations=5000):
    for _ in range(200):
        func()

    start = time.perf_counter()
    for _ in range(iterations):
        func()
    return (time.perf_counter() - start) / iterations * 1e6


def main():
    print(f"{'exact case':18} {'timefhuman':>12} {'parse_fast':>12} {'parse_exact':>12}")
    for label, text in EXACT_CASES:
        print(
            f"{label:18} "
            f"{bench(lambda: timefhuman(text, config=CONFIG)):12.1f} "
            f"{bench(lambda: parse_fast(text, CONFIG, TIMEZONE_MAPPING)):12.1f} "
            f"{bench(lambda: _parse_exact(text, CONFIG)):12.1f}"
        )

    print()
    print(f"{'extract case':18} {'timefhuman':>12} {'fast extract':>12} {'exact extract':>12}")
    for label, text in EXTRACT_CASES:
        print(
            f"{label:18} "
            f"{bench(lambda: timefhuman(text, config=CONFIG), iterations=2000):12.1f} "
            f"{bench(lambda: extract_fast(text, lambda candidate, start: parse_fast(candidate, CONFIG, TIMEZONE_MAPPING, start)), iterations=2000):12.1f} "
            f"{bench(lambda: extract_fast(text, lambda candidate, start: _parse_exact(candidate, CONFIG, start)), iterations=2000):12.1f}"
        )


if __name__ == "__main__":
    main()
