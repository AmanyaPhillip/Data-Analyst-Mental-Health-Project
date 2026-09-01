# Report 3 — Data Cleaning: Bug Fixes & Performance Improvements

**Project:** Mental Health & Suicide Prevention Data Analysis (Canada)  
**Pipeline Step:** 02 — Data Cleaning  
**Author:** Phillip  
**Status:** ✅ Team reviewed and agreed  
**Date:** 2026-09-01  
**Companion File:** `notebooks/02_data_cleaning_functions.py` (all fixes implemented here)

---

## Overview

During code review of `notebooks/02_data_cleaning.ipynb`, the team identified two confirmed bugs, four active warnings, one O(n²) performance issue, one stale-column-name problem, and a stale-function-definition risk. This report documents each issue: what was wrong, what changed, why the change was made, and what data it affects.

---

## §1 — Bug #1 · `clean_cihi_children_youth` — `.loc` / `enumerate` Index Mismatch

**Severity:** 🔴 Critical Bug  
**Function:** `clean_cihi_children_youth()`  
**Columns affected:** `ci_low`, `ci_high`

### What was wrong

```python
# BEFORE
for idx, val in enumerate(long_df["value"]):   # idx = counter 0, 1, 2 ...
    if isinstance(val, str) and "-" in val:
        ...
        long_df.loc[idx, "ci_low"]  = ...     # .loc uses LABEL indexing
        long_df.loc[idx, "ci_high"] = ...     # wrong row is targeted!
```

`enumerate()` produces a sequential counter `(0, 1, 2, ...)`.
`.loc` uses **label-based** indexing — not the counter.
After `df.melt()`, the index labels are not sequential — they repeat in a tiled pattern. The counter and the label almost never point to the same row.

**Consequence:** `ci_low` and `ci_high` were written to random rows — either the wrong rows or a `KeyError`. Output silently corrupted.

### What was changed

**Fix Option B** (as agreed by the team):

```python
# AFTER — Option B: use .items() to get (label, value) pairs
for idx, val in long_df["value"].items():      # idx = actual label
    ...
    long_df.loc[idx, "ci_low"]  = lo          # correct row targeted
    long_df.loc[idx, "ci_high"] = hi
```

`long_df = long_df.reset_index(drop=True)` is also called after `melt()` as a safety belt.

### Data impact

- Previously: all `ci_low` / `ci_high` values were written to incorrect rows or lost entirely.
- After fix: confidence intervals correctly aligned to their source row.
- **Rows affected:** all CI-formatted cells in Table8DATA_to hide and Table13DATA_to hide.

---

## §2 — Bug #2 · `clean_cihi_children_youth` — Point Estimate Lost on CI Strings

**Severity:** 🔴 Critical Bug  
**Function:** `clean_cihi_children_youth()`  
**Columns affected:** `value`

### What was wrong

```python
# BEFORE
long_df.loc[idx, "ci_low"]  = pd.to_numeric(match.iloc[0, 0], errors="coerce")
long_df.loc[idx, "ci_high"] = pd.to_numeric(match.iloc[0, 1], errors="coerce")
# value column still contains raw string "12.3-14.5"

long_df["value"] = pd.to_numeric(long_df["value"], errors="coerce")
# "12.3-14.5" cannot be coerced → NaN.  Point estimate 12.3 is LOST.
```

### What was changed

```python
# AFTER — inside the loop
lo = pd.to_numeric(match.iloc[0, 0], errors="coerce")
hi = pd.to_numeric(match.iloc[0, 1], errors="coerce")
long_df.loc[idx, "ci_low"]  = lo
long_df.loc[idx, "ci_high"] = hi
long_df.loc[idx, "value"]   = lo   # point estimate preserved
```

### Data impact

- Previously: every CI-formatted cell had `value = NaN`.
- After fix: `value` contains the correct point estimate.
- **Rows affected:** all CI-formatted cells in both CIHI children/youth sheets.

---

## §3 — Warning #3 · `clean_cihi_children_youth` — ASCII Hyphen Only

**Severity:** 🟡 Warning  
**Function:** `clean_cihi_children_youth()`

### What was wrong

Regex and guard only matched ASCII hyphen (`-`). Excel exports often use en-dash (–, U+2013) or em-dash (—, U+2014). Those cells were silently skipped.

### What was changed

```python
# AFTER
_CI_DASH_CHARS = {"-", "\u2013", "\u2014"}
_CI_PATTERN    = r"([\d.]+)\s*[-\u2013\u2014]\s*([\d.]+)"
if isinstance(val, str) and any(d in val for d in _CI_DASH_CHARS):
```

### Data impact

- Previously: en/em-dash CI cells had ci_low=None, ci_high=None, value=NaN.
- After fix: all three dash variants parsed correctly.

---

## §4 — Warning #4 · `clean_cihi_children_youth` — `is not None` Does Not Catch NaN

**Severity:** 🟡 Warning  
**Function:** `clean_cihi_children_youth()`

### What was wrong

```python
if not match.empty and match.iloc[0, 0] is not None:
```

`str.extract()` returns `NaN` (not `None`) on no-match. `NaN is not None` is always `True`, so the guard never blocked. Spurious NaN values were written to ci_low/ci_high for non-CI rows.

### What was changed

```python
if not match.empty and pd.notna(match.iloc[0, 0]):
```

### Data impact

Prevents spurious NaN CI values on non-CI rows. Semantically important for future null-checks.

---

## §5 — Warning #5 · `clean_cihi_children_youth` — Hardcoded Year Range

**Severity:** 🟡 Warning  
**Function:** `clean_cihi_children_youth()`

### What was wrong

```python
# BEFORE
year_cols = [c for c in df.columns if any(y in str(c) for y in ["2018","2019","2020","2021","2022"])]
```

A 2023+ column would be silently classified as an ID column and excluded from the melt.

### What was changed

```python
# AFTER — dynamic: match any 4-digit year
year_cols = [c for c in df.columns if re.search(r"\b\d{4}\b", str(c))]
```

### Data impact

- No change to current data (2018–2022 detected as before).
- Future-proofing: new fiscal year columns automatically included.

---

## §6 — `clean_mhacs_pumf` — Hardcoded Variable Names Not in CSV

**Severity:** 🔴 Silent No-Op  
**Function:** `clean_mhacs_pumf()`

### What was wrong

```python
documented_variables = {"DMHSTAT", "DPHSTAT", "DALCOHOL", "DDRUGS", "DWKDECAL", "DWKDISAB"}
```

**Data inspection confirmed (2026-09-01):** None of these six names exist in the actual `MHACS 2022 Public Use Microdata.csv`.  
- Exact match: False for all six  
- Case-insensitive match: False for all six  

These names likely came from an earlier codebook draft. The function's fallback loop (all numeric D-prefix columns) was already doing the real work. The `documented_variables` block contributed zero target columns.

**Actual D-prefix numeric columns (43 confirmed):**  
DHHGMS, DHHGAGE, DIS_01A–DIS_01N, DISDK6, DISDDSX, DISDCHR, DEP_72, DEP_86, DEP_87, DEPDDPS, DEPGREC, DEPGPER, DEPDDY, DEPFSLT, DEPFSYT, DEPFINT, DEPDINT, DASG01, DASG02, DAS_04–DAS_13, DASGSCR, DABTIPPE, DNBTIPPE

### What was changed

Phantom set removed. Target columns derived at runtime:

```python
target_vars = [
    col for col in df.columns
    if col.startswith("D") and df[col].dtype in ("int64", "float64")
]
```

### Data impact

- **Current run:** identical output (phantom set was always a no-op).
- **Future runs:** automatically picks up new D-prefix columns.
- **Risk removed:** no misleading phantom variable names.

---

## §7 — `clean_statcan_long` — O(n²) Pivot Performance

**Severity:** 🟡 Performance  
**Function:** `clean_statcan_long()`

### What was wrong

Manual `itertuples()` loop + per-row boolean mask. For each of ~53,664 unique dimension combinations in `cchs_mh_disorders` (160,992 rows), a full-length boolean Series was re-allocated and every column compared. Effectively O(n²) — taking minutes.

### What was changed

Vectorised three-step approach:

```python
# Step 1: classify rows — O(n), single pass
df["_char_key"] = np.select([cond_pct, cond_low, cond_high], ["value","ci_low","ci_high"], default="other")

# Step 2: vectorised pivot — O(n log n)
pivot = (
    df[df["_char_key"] != "other"]
    .pivot_table(index=dim_cols, columns="_char_key", values="value", aggfunc="first")
    .reset_index()
)

# Step 3: merge back quality_flag/metric_type — O(n)
pivot = pivot.merge(pct_meta, on=merge_cols, how="left")
```

### Data impact

- Output structurally identical (same rows, columns, values).
- `aggfunc="first"` matches the original `pct["value"].iloc[0]` behaviour.
- Runtime reduced from minutes to seconds for the 160,992-row table.

---

## §8 — `clean_cihi_vizconfig` — Column Name Verification

**Severity:** 🟢 Verified Safe  
**Function:** `clean_cihi_vizconfig()`

### Verification result (2026-09-01 data inspection)

| Column used in code | In actual CSV | Status |
|---|---|---|
| `vis_option` | Yes | ✅ |
| `confidence_interval_low` | Yes | ✅ |
| `confidence_interval_high` | Yes | ✅ |
| `x_axis_values` | Yes | ✅ |
| `y_axis_values` | Yes | ✅ |

The inline `# FIXED` comments in the original code were accurate. A column-existence guard was added to raise a descriptive `ValueError` if the schema changes in future.

---

## §9 — Stale Function Definition Cells

**Severity:** 🟡 Process Risk  
**Cells:** `clean_statcan_long` and `clean_cihi_children_youth` (both `execution_count: null`)

### What was wrong

Both cells were never explicitly re-executed in the last kernel session. The kernel had stale in-memory versions. If any team member restarts the kernel and skips these cells, they either get a `NameError` or silently run the old buggy functions.

### Why it matters and what data it would change

| Scenario | Consequence |
|---|---|
| Kernel restart → run orchestration directly | `NameError: clean_statcan_long is not defined` |
| Stale version in memory | O(n²) pivot runs; Bug #1 and Bug #2 persist in output CSVs |
| New team member first run | `NameError` on orchestration cell |

### Solution

**Immediate:** Use `%run 02_data_cleaning_functions.py` in a cell after §1 to load all fixed functions regardless of cell execution order.

**Team standard:** Always use **Kernel → Restart & Run All** before producing pipeline output.

---

## §10 — Notebook Inlining & Professional Polish

**Date:** 2026-09-01  
**Status:** ✅ Complete

### What was done

After the bug fixes were validated and documented in `02_data_cleaning_functions.py`, the companion notebook `notebooks/02_data_cleaning.ipynb` was updated so the team no longer needs a separate `.py` file or a `%run` magic command to run the pipeline.

#### 10.1 — Functions inlined into the notebook

All four corrected function bodies were copied verbatim from `02_data_cleaning_functions.py` into their respective cells in `02_data_cleaning.ipynb`, replacing the original buggy implementations:

| Cell | Function | Issues incorporated |
|---|---|---|
| §4 cell 1 | `clean_statcan_long` | §7 vectorised pivot (O(n²) → O(n log n)) |
| §4 cell 2 | `clean_cihi_vizconfig` | §8 column-existence guard |
| §4 cell 3 | `clean_cihi_children_youth` | §1 Bug #1, §2 Bug #2, §3–§5 Warnings #3–#5 |
| §4 cell 4 | `clean_mhacs_pumf` | §6 phantom variable set removed |

`import re` was added to the §1 Libraries cell because `clean_cihi_children_youth` now uses `re.search()` for dynamic year-column detection.

#### 10.2 — `%run` dependency removed

The notebook no longer references `02_data_cleaning_functions.py` in any cell. The `%run 02_data_cleaning_functions.py` workaround described in §9 is not needed. The stale-cell risk documented in §9 is eliminated because all function definitions now run in order as part of the normal cell execution sequence.

#### 10.3 — Professional polish applied

| Area | Change |
|---|---|
| Title cell | Replaced the "Skeleton only" blockquote with a metadata table (Project, Author, Status, Date, Audit report) and a full Overview section with dataset and structure tables |
| Section headings | Renamed `## 1 ·` … `## 4 ·` to `## §1 ·` … `## §4 ·`; added new `## §5 · Run pipeline` section with its own markdown header cell |
| Section descriptions | Added prose descriptions under each section heading explaining purpose and key implementation details |
| Function docstrings | All four functions received full NumPy-style docstrings (Steps / Parameters / Returns / Notes) |
| Inline comments | All `# FIX §N`, `# FIX Bug #N`, and `# FIX Warning #N` audit-trail markers removed from code; replaced with clean explanatory comments describing what the code does |
| Orchestration cell | Removed condescending comments ("Same process for rest all", "Creates an empty dictionary", "Prints final msg"); added an `else` branch for unknown dataset kinds; `print` now reports the output file path and shape after each write |
| Stale metadata | `metadata.execution` timestamp blocks from the original 2026-08-27 kernel session removed from all edited cells; all edited cells set to `execution_count: null` |
| `TO-DO` task list | The `## 4 · Cleaning — TO BE COMPLETED BY THE TEAM` list replaced with a function reference table summarising each cleaner, its datasets, and its output schema |

#### 10.4 — Files affected

| File | Change |
|---|---|
| `notebooks/02_data_cleaning.ipynb` | All cells updated as described above |
| `notebooks/02_data_cleaning_functions.py` | No changes — retained as the authoritative audit-trail record of every fix |

---

## Summary Table

| # | Severity | Function | Issue | Fix |
|---|---|---|---|---|
| 1 | 🔴 Bug | `clean_cihi_children_youth` | `.loc`/`enumerate` mismatch → wrong rows written | `.items()` (Option B) + `reset_index()` |
| 2 | 🔴 Bug | `clean_cihi_children_youth` | Point estimate discarded on CI strings | Write left-hand number back inside loop |
| 3 | 🟡 Warning | `clean_cihi_children_youth` | ASCII hyphen only — en/em-dash skipped | Expand guard and regex |
| 4 | 🟡 Warning | `clean_cihi_children_youth` | `is not None` fails for NaN | Use `pd.notna()` |
| 5 | 🟡 Warning | `clean_cihi_children_youth` | Hardcoded years 2018–2022 | Dynamic regex `\b\d{4}\b` |
| 6 | 🔴 Silent no-op | `clean_mhacs_pumf` | 6 phantom variable names absent from CSV | Remove; derive targets from DataFrame |
| 7 | 🟡 Performance | `clean_statcan_long` | O(n²) pivot — minutes on 160k rows | `np.select` + `pivot_table` — O(n log n) |
| 8 | 🟢 Verified | `clean_cihi_vizconfig` | Column name verification | All confirmed; guard added |
| 9 | 🟡 Process | Both stale cells | `execution_count: null` — stale function risk | Functions inlined directly; `%run` eliminated |
| 10 | 🔵 Polish | `02_data_cleaning.ipynb` | Skeleton note, audit-trail comments, missing sections | Full notebook rewrite — inline functions, docstrings, clean comments, §5 section |

---

*All fixes implemented in `notebooks/02_data_cleaning_functions.py` and subsequently inlined into `notebooks/02_data_cleaning.ipynb`*  
*Author: Phillip · Team reviewed and agreed · 2026-09-01*
