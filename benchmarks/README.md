# Benchmarks

Status as of April 2, 2026.

## Results

- Runtime path: deterministic whole-string parse first, bounded extraction for noisy text, LALR fallback only on misses. Earley is not used at runtime.
- `extracted`: returned any result on the 37-case short-input corpus.
- `correctness`: exact match on the 10-case exactness subset.
- `core_corpus`, `seattle_html_76k`, `test_data_560k`: warmed median seconds and extracted count, formatted as `seconds (count)`.
- whole-document counts link to checked-in raw match dumps under `benchmarks/matches/`.
- `timefhuman` whole-document extraction uses `infer_datetimes=False`, so linked dumps keep raw dates, times, and timedeltas while explicit datetimes stay datetimes.
- `>15s (n/a)`: exceeded the document benchmark timeout for that dataset.
- whole-document counts are raw extracted-match counts, so HTML noise can inflate them.
- `timefhuman` is pinned first; the remaining rows are ordered fastest to slowest.

### Short-Input Parsing

| parser | us/input | extracted | correctness |
| --- | ---: | ---: | ---: |
| timefhuman | 37.9 | **37/37** | **10/10** |
| datefinder.find_dates | **24.7** | 23/37 | 5/10 |
| metadate.parse_date | 33.6 | 31/37 | 5/10 |
| parsedatetime.parseDT | 48.4 | 36/37 | 6/10 |
| recurrent.parse | 188.5 | 36/37 | 6/10 |
| ctparse.ctparse | 12222.2 | **37/37** | 3/10 |
| dateparser.parse | 45066.8 | 20/37 | 6/10 |

### Whole-Document Extraction

Only parsers with a comparable whole-document extraction API are included here.

| parser | core_corpus | seattle_html_76k | test_data_560k |
| --- | ---: | ---: | ---: |
| timefhuman | 0.0011 ([10](matches/timefhuman/core_corpus.md)) | 0.0808 ([59](matches/timefhuman/seattle_html_76k.md)) | **0.3378** ([716](matches/timefhuman/test_data_560k.md)) |
| datefinder.find_dates | **0.0002** ([11](matches/datefinder.find_dates/core_corpus.md)) | **0.0400** ([57](matches/datefinder.find_dates/seattle_html_76k.md)) | 0.4943 ([313](matches/datefinder.find_dates/test_data_560k.md)) |
| dateparser.search_dates | 0.1105 ([14](matches/dateparser.search_dates/core_corpus.md)) | 0.3299 ([90](matches/dateparser.search_dates/seattle_html_76k.md)) | >15s (n/a) |

Notes on what the other baselines found that `timefhuman` still misses:

- `core_corpus`: `datefinder.find_dates`'s extra hits are mainly multilingual relative words such as Spanish `ayer` and `mañana`, plus component-level substring matches like `31/08/2012`, `30/08/2013`, and `23 Apr 1996` instead of the full range or full timestamp.
- `seattle_html_76k`: `datefinder.find_dates`'s extra unique hits are mainly low-value metadata matches, such as asset version numbers like `1.3.4` and `1.7.1`, plus `Jan 6 2016` as a smaller substring inside the longer `Jan 6 2016 at 10:13AM` timestamp that `timefhuman` already captures.
- `seattle_html_76k`: most of `dateparser.search_dates`'s extra hits are low-quality HTML false positives like `01'`, `90`, `50%`, `<h1`, and `set`.

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

Refresh the checked-in whole-document match dumps.

```bash
/tmp/timefhuman-bench-venv/bin/python benchmarks/dump_document_matches.py
```

## Rule Of Thumb

If a change makes the LALR parser or noisy extraction run more often, it is probably a slowdown.

The fastest route is:

1. deterministic whole-string parse for exact expressions
2. bounded noisy extraction for prose-like inputs
3. exact whole-string LALR fallback only when needed
4. LALR extraction rescue only when the fast extractor misses
