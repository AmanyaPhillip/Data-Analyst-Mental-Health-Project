# Data Cleaning — Checklist & Function Reference

**Status:** reference · last updated 2026-09-02 · owner: Samir
**Source:** extracted from `notebooks/02_data_cleaning_functions.py` (Phillip, team-reviewed 2026-09-01, "Report 3 – Data Cleaning and Bug Fixes")
**Companion:** [`docs/data_dictionary.md`](data_dictionary.md) §A · [`docs/data_inventory.md`](data_inventory.md)

---

## Is that `.py` file useful? — Yes, keep the knowledge (rating: 8/10)

`notebooks/02_data_cleaning_functions.py` contains the team's four cleaning functions **plus a
detailed record of every bug found and fixed in Report 3**. That bug commentary is the valuable
part and is preserved in this document.

| | Verdict |
|---|---|
| **The code** | Already copied into `02_data_cleaning.ipynb` cells §4 (with the same fixes). The `.py` is a duplicate. |
| **The comments / rationale** | Unique — the "why" behind each fix is **not** in the notebook. Captured below. |
| **Recommendation** | Extract to this file (done). Then either **(a)** delete the `.py` and treat the notebook as canonical, or **(b)** keep the `.py` as the single source of truth and have the notebook do `%run 02_data_cleaning_functions.py` instead of holding its own copies. **Do not keep both copies** — they will drift. |

---

## How to run the functions

From the file's own instructions:

```python
# in 02_data_cleaning.ipynb, right after the library-import cell:
%run 02_data_cleaning_functions.py
```

…**or** copy each function into its notebook cell (current state of the repo).

> ⚠️ **Stale-cell warning (Report 3).** Two function cells in the original notebook had
> `execution_count = null` — they were never re-run, so the kernel held an *older* version in
> memory. Always do **Kernel → Restart & Run All** before a full pipeline run, or `%run` the
> module at the top of the session. Never trust a partial re-run.

---

## Master cleaning checklist

Work through this for **every** raw table. Items marked 🅢 are StatCan-specific.

### Before you start
- [ ] Read the source's metadata / data dictionary; note the grain (one row = ?).
- [ ] `df.shape`, `df.dtypes`, `df.head()`, `df.isna().sum()` — know the starting point (that's `01_data_understanding.ipynb`).
- [ ] Decide the **target tidy schema** first (see `docs/data_dictionary.md` §A / `04_analysis.ipynb` contract).
- [ ] `df = df.copy()` at the top of every function — never mutate the caller's frame.

### Column normalisation
- [ ] Strip + lowercase column names: `df.columns = df.columns.str.strip().str.lower()`.
- [ ] Strip whitespace inside every text column.
- [ ] Rename to canonical names via an explicit `rename_map` (don't rely on position).
- [ ] Unify synonyms: `gender` → `sex`, `characteristics` → `characteristic`, `status` → `quality_flag`.

### Type conversion
- [ ] `pd.to_numeric(col, errors="coerce")` for every measure column.
- [ ] Parse dates but **keep the original string** (`ref_date_raw`) and derive a sort key (`start_year`).
- [ ] 🅢 Apply `SCALAR_FACTOR`: multiply `value` by 1000 where it equals `"thousands"`; record that you did (`scalar_applied`).

### Reshaping
- [ ] Melt wide → long where each row should be one observation.
- [ ] 🅢 Pivot the `Characteristic`/`Statistic` dimension so each row has `value`, `ci_low`, `ci_high` as **columns**, not rows.
- [ ] **Never** pivot with a per-row Python loop (`itertuples` + boolean mask = O(n²); 160k rows took minutes). Use `np.select` to classify + `pivot_table` to reshape.
- [ ] After `pivot_table().reset_index()`, clear the residual index name: `pivot.columns.name = None`.

### Text & encoding gotchas
- [ ] Confidence-interval strings use **en-dash / em-dash** from Excel, not just ASCII `-`. Match `[-–—]`.
- [ ] When a value cell is a CI range (`"12.3–14.5"`), extract **both** bounds **and** write the left number back as the point estimate — otherwise `pd.to_numeric` turns the whole thing into `NaN` and the estimate is lost.
- [ ] Collapse internal whitespace in long labels: `.str.replace(r"\s+", " ", regex=True)`.
- [ ] Don't hardcode year lists (`["2018","2019",...]`) — detect with `re.search(r"\b\d{4}\b", col)`.

### Missing values
- [ ] Keep `quality_flag` (`E` / `F` / `x` / `..`) as a column. **Do not impute** suppressed values.
- [ ] 🅢 MHACS microdata: replace non-response codes (`6, 7, 8, 9, 96, 996, 999, 99.6`) with `NaN` — **only for the variables you selected**, never blanket-replace (some scales legitimately use 6–9).
- [ ] Ensure the survey weight (`WTS_M`) is numeric and non-null before any weighted stat.

### Index safety
- [ ] After a `melt`, call `.reset_index(drop=True)`.
- [ ] To iterate a Series and write back by label, use `for idx, val in s.items()` — **not** `enumerate()` (its counter is not the DataFrame label; `.loc[counter]` writes the wrong rows).
- [ ] Test emptiness/NaN with `pd.notna(x)`, not `x is not None` (`NaN is not None` is `True`).

### Validate after cleaning
- [ ] Row count sane vs input; no unexpected explosion from the melt.
- [ ] Grain is unique: `df.groupby(dim_cols).size().max() == 1`.
- [ ] `value` numeric, in a plausible range; `ci_low <= value <= ci_high` where CI present.
- [ ] Geography names match the canonical list used across all tables.
- [ ] Write to `data/processed/…` and log the row count.

---

## Function reference

> The code below is the **fixed** version from Report 3 (matches `02_data_cleaning.ipynb` §4).

### 1 · `clean_statcan_long(df)`

**Purpose** — Normalise a StatCan "table download" CSV into a tidy analytical frame: clean column
names, apply scalar factors, parse dates, and pivot the confidence-interval rows into columns.

**Why use it** — All five StatCan tables share the same awkward layout: 17–18 columns, the
`Characteristic`/`Statistic` dimension stores the point estimate *and* both CI bounds *and* the
metric type as **separate rows**, values may be scaled by 1000, and dates come in three formats
(`2016`, `2019/2020`, `2021-04`). This function makes them all consistent so `04_analysis.ipynb`
can `UNION` them into `mh_long`.

**When to use it** — `perceived_mh_annual`, `suicidal_thoughts`, `stress_coping`,
`perceived_health_quarterly`, `cchs_mh_disorders`. Not for CIHI or MHACS.

**Input** — raw StatCan CSV read with `encoding="utf-8-sig"` (BOM).
**Output** — one row per `geo × period × sex × age_group × indicator`, with columns
`ref_date_raw, start_year, geo, sex, age_group, indicator, value, ci_low, ci_high, metric_type, quality_flag, scalar_applied, vector`.

**Cases handled**
- **Large tables without freezing** — the CI pivot is fully vectorised (`np.select` + `pivot_table`, O(n log n)). The original per-row `itertuples` loop was O(n²) and took minutes on `cchs_mh_disorders` (160,992 rows).
- **Tables with no CI rows** — the pivot block is skipped (guarded by `has_percent and (has_ci_low or has_ci_high)`); the function still returns a clean frame.
- **`thousands` scaling** — counts are multiplied to real units and flagged in `scalar_applied`.
- **Three date formats** — original kept in `ref_date_raw`; leading 4-digit year extracted to `start_year` (nullable `Int64`) for sorting.
- **`gender` vs `sex`, `Status` vs quality flag** — unified via `rename_map`.
- **Residual `MultiIndex` name after pivot** — cleared with `pivot.columns.name = None`.

**Watch out for**
- `quality_flag` / `metric_type` are carried from the **Percent rows only**; if a table has count-only indicators they won't get a flag.
- Indicator label strings must survive exactly — `04_analysis.ipynb` filters on them (`WHERE indicator = '...'`).
- The column rename is lowercase-based; if StatCan changes a header the `rename_map` needs updating.

```python
def clean_statcan_long(df: pd.DataFrame) -> pd.DataFrame:
    """Clean StatCan long-format data: normalize, apply factors, pivot CI where available."""
    df = df.copy()

    # Normalize columns: lowercase, strip whitespace
    df.columns = df.columns.str.strip().str.lower()
    text_cols = df.select_dtypes(include="object").columns
    for col in text_cols:
        df[col] = df[col].str.strip()

    # Standardize column names
    rename_map = {
        "age group": "age_group", "indicators": "indicator", "characteristics": "characteristic",
        "statistics": "statistic", "ref_date": "ref_date", "value": "value", "dguid": "dguid",
        "uom_id": "uom_id", "scalar_factor": "scalar_factor", "scalar_id": "scalar_id",
        "vector": "vector", "coordinate": "coordinate", "status": "quality_flag",
    }
    df.rename(columns=rename_map, inplace=True)
    if "gender" in df.columns:
        df.rename(columns={"gender": "sex"}, inplace=True)

    # Parse reference dates: preserve original format, extract year for sorting
    df["ref_date_raw"] = df["ref_date"].astype(str).str.strip()
    df["start_year"] = pd.to_numeric(
        df["ref_date_raw"].str.extract(r"^(\d{4})")[0], errors="coerce"
    ).astype("Int64")

    # Convert value to numeric, apply scalar factors
    if "value" in df.columns:
        df["value"] = pd.to_numeric(df["value"], errors="coerce")
    if "scalar_factor" in df.columns and "value" in df.columns:
        df.loc[df["scalar_factor"].eq("thousands"), "value"] *= 1000
        df["scalar_applied"] = df["scalar_factor"].eq("thousands")

    # Normalize quality flags and metric types
    if "quality_flag" in df.columns:
        df["quality_flag"] = df["quality_flag"].str.lower().str.strip()
    if "uom" in df.columns:
        df["metric_type"] = df["uom"].str.lower()

    # Drop metadata columns
    drop_cols = ["symbol", "terminated", "decimals", "uom_id", "scalar_id", "coordinate"]
    df = df.drop(columns=[c for c in drop_cols if c in df.columns], errors="ignore")

    # Normalize geography and indicators
    if "geo" in df.columns:
        df["geo"] = df["geo"].str.replace(" / ", "/", regex=False).str.strip()
    if "indicator" in df.columns:
        df["indicator"] = df["indicator"].str.replace(r"\s+", " ", regex=True).str.strip()

    # VECTORISED PIVOT (replaces the O(n^2) itertuples loop)
    if "characteristic" in df.columns:
        has_percent  = df["characteristic"].str.contains("Percent",  case=False, na=False).any()
        has_ci_low   = df["characteristic"].str.contains("Low.*95%", case=False, na=False).any()
        has_ci_high  = df["characteristic"].str.contains("High.*95%", case=False, na=False).any()

        if has_percent and (has_ci_low or has_ci_high):
            char = df["characteristic"].fillna("")
            df["_char_key"] = np.select(
                [
                    char.str.contains("Percent",  case=False),
                    char.str.contains("Low.*95%", case=False),
                    char.str.contains("High.*95%", case=False),
                ],
                ["value", "ci_low", "ci_high"],
                default="other",
            )

            meta_cols = {"value", "characteristic", "_char_key",
                         "metric_type", "quality_flag", "scalar_applied"}
            dim_cols  = [c for c in df.columns if c not in meta_cols]

            extra_keep = [c for c in ["quality_flag", "metric_type"] if c in df.columns]
            if extra_keep:
                pct_meta = (
                    df[df["_char_key"] == "value"][dim_cols + extra_keep]
                    .drop_duplicates(subset=dim_cols)
                )
            else:
                pct_meta = None

            pivot = (
                df[df["_char_key"] != "other"]
                .pivot_table(index=dim_cols, columns="_char_key", values="value", aggfunc="first")
                .reset_index()
            )
            pivot.columns.name = None

            if pct_meta is not None and not pct_meta.empty:
                merge_cols = [c for c in dim_cols if c in pct_meta.columns]
                merge_extra = [c for c in extra_keep if c in pct_meta.columns]
                pivot = pivot.merge(pct_meta[merge_cols + merge_extra], on=merge_cols, how="left")

            df = pivot

    # Reorder columns for readability
    col_order = [
        "ref_date_raw", "start_year", "geo", "sex", "age_group", "indicator",
        "characteristic", "value", "ci_low", "ci_high", "metric_type",
        "quality_flag", "scalar_applied", "vector",
    ]
    cols_present = [c for c in col_order if c in df.columns]
    other_cols   = [c for c in df.columns if c not in cols_present]
    return df[cols_present + other_cols]
```

---

### 2 · `clean_cihi_vizconfig(df)`

**Purpose** — Turn the CIHI Health Infobase export (where each row is a *chart definition*) into
tidy observations.

**Why use it** — `cihi_mh_services` isn't data in the normal sense: `x_axis_values` holds the
category labels and `y_axis_values` holds the measured numbers, aligned positionally. You can't
query it until it's unpivoted into `indicator | breakdown | group | value | ci_low | ci_high`.

**When to use it** — `cihi_mh_services` only.

**Input** — the raw `health services for mental illness and alcoholdrug induced disorders.csv`.
**Output** — one row per `(indicator, breakdown, group)` with a numeric `value`; rows whose value
can't be parsed are dropped.

**Cases handled**
- **Missing columns fail loudly** — a guard raises `ValueError` (listing the columns it did find) instead of a silent `KeyError` if the file layout changes.
- **Single-value cells** — `x_axis_values` / `y_axis_values` often have just one value; `.str.split(",")` yields a 1-element list and the `zip`/loop still works. No data lost.
- **Ragged x/y lengths** — the loop runs `min(len(xs), len(ys))` so a mismatch truncates rather than crashes.
- **`vis_option`, CI columns absent** — read with `row.get(col, None)` so they're optional.

**Watch out for**
- The point estimate comes straight from `y_axis_values`; if CIHI ever nests structure in those strings this needs revisiting.
- `dropna(subset=["value"])` silently removes unparseable rows — check how many before/after.

```python
def clean_cihi_vizconfig(df: pd.DataFrame) -> pd.DataFrame:
    """Unpivot CIHI chart-config CSV: split x/y axis values into separate rows."""
    df = df.copy()
    df.columns = df.columns.str.strip().str.lower()

    required = {"x_axis_values", "y_axis_values"}
    missing  = required - set(df.columns)
    if missing:
        raise ValueError(
            f"clean_cihi_vizconfig: expected columns missing from DataFrame: {missing}. "
            f"Available columns: {list(df.columns)}"
        )

    df["x_axis_values"] = df["x_axis_values"].astype(str).str.split(",")
    df["y_axis_values"] = df["y_axis_values"].astype(str).str.split(",")

    tidy_rows = []
    for _, row in df.iterrows():
        indicator = row.get("indicator", "")
        xs = row["x_axis_values"]
        ys = row["y_axis_values"]
        n  = min(len(xs), len(ys))
        for i in range(n):
            x = xs[i].strip()
            y = ys[i].strip()
            value = pd.to_numeric(y, errors="coerce")
            tidy_rows.append({
                "indicator": indicator,
                "breakdown": row.get("vis_option", None),
                "group"    : x,
                "value"    : value,
                "ci_low" : pd.to_numeric(row.get("confidence_interval_low",  None), errors="coerce"),
                "ci_high": pd.to_numeric(row.get("confidence_interval_high", None), errors="coerce"),
            })

    tidy = pd.DataFrame(tidy_rows)
    tidy = tidy.dropna(subset=["value"])
    return tidy
```

---

### 3 · `clean_cihi_children_youth(raw_excel)`

**Purpose** — Reshape the CIHI children/youth workbook's data sheets from wide (one column per
fiscal year) to long, and split embedded confidence-interval strings.

**Why use it** — Only two sheets (`Table8DATA_to hide`, `Table13DATA_to hide`) are
machine-readable, years are columns, and some cells hold a CI range (`"142–158"`) instead of a
number. Manual handling here is where three separate bugs were found.

**When to use it** — `cihi_children_youth`. Pass the dict of the two hidden sheets (already
header-fixed) from the loader.

**Input** — `dict[sheet_name -> DataFrame]`.
**Output** — long frame: `id cols + fiscal_year + value + ci_low + ci_high + sheet_type` (`ED` / `Hospitalization`).

**Cases handled** *(each of these was a real bug — Report 3)*
- **Bug #1 — wrong rows written.** `for idx, val in enumerate(col)` gives a 0,1,2… counter, but `.loc[idx]` uses the **label**; on a melted frame those differ, so CI values landed on the wrong rows. Fixed with `for idx, val in long_df["value"].items()` + a `reset_index(drop=True)` safety belt.
- **Bug #2 — point estimate destroyed.** `pd.to_numeric("12.3–14.5")` → `NaN`. Now the left number is written back as `value` *inside* the loop, before the bulk numeric conversion.
- **Warning #3 — Excel dashes.** Real cells use en-dash `–` / em-dash `—`, not ASCII `-`. Pattern is `([\d.]+)\s*[-–—]\s*([\d.]+)` and the membership test checks all three dash chars.
- **Warning #4 — `NaN is not None`.** Emptiness check now uses `pd.notna(match.iloc[0, 0])`.
- **Warning #5 — hardcoded years.** Year-column detection is `re.search(r"\b\d{4}\b", col)`, so 2023-2024 data (and later) is picked up automatically.

**Watch out for**
- `sheet_type` is derived from the substring `Table8` / `Table13` in the sheet name — keep those names.
- `id_cols` falls back to "first 3 columns" if no year columns are found — verify that's right for a new sheet.

```python
import re

_CI_DASH_CHARS = {"-", "–", "—"}           # hyphen, en-dash, em-dash
_CI_PATTERN    = r"([\d.]+)\s*[-–—]\s*([\d.]+)"


def clean_cihi_children_youth(raw_excel: dict) -> pd.DataFrame:
    """Reshape CIHI children/youth Excel from wide to long, parse CI bounds, add sheet identifier."""
    frames = []

    for sheet, df in raw_excel.items():
        df = df.copy()
        df.columns = df.columns.str.strip().str.replace("\n", " ")

        year_cols  = [c for c in df.columns if re.search(r"\b\d{4}\b", str(c))]
        id_cols    = [c for c in df.columns if c not in year_cols] if year_cols else list(df.columns[:3])
        value_cols = year_cols if year_cols else list(df.columns[3:])

        long_df = df.melt(id_vars=id_cols, value_vars=value_cols,
                          var_name="fiscal_year", value_name="value")
        long_df["fiscal_year"] = long_df["fiscal_year"].str.replace(" ", "", regex=False)
        long_df = long_df.reset_index(drop=True)          # Bug #1 safety belt

        long_df["ci_low"]  = None
        long_df["ci_high"] = None

        for idx, val in long_df["value"].items():                              # Bug #1 fix
            if isinstance(val, str) and any(d in val for d in _CI_DASH_CHARS): # Warning #3
                match = pd.Series(val).str.extract(_CI_PATTERN, expand=True)
                if not match.empty and pd.notna(match.iloc[0, 0]):             # Warning #4
                    lo = pd.to_numeric(match.iloc[0, 0], errors="coerce")
                    hi = pd.to_numeric(match.iloc[0, 1], errors="coerce")
                    long_df.loc[idx, "ci_low"]  = lo
                    long_df.loc[idx, "ci_high"] = hi
                    long_df.loc[idx, "value"]   = lo                           # Bug #2 fix

        long_df["value"] = pd.to_numeric(long_df["value"], errors="coerce")

        long_df["sheet_type"] = (
            "ED"              if "Table8"  in sheet else
            "Hospitalization" if "Table13" in sheet else
            sheet.replace("_to hide", "")
        )
        frames.append(long_df)

    return pd.concat(frames, ignore_index=True)
```

---

### 4 · `clean_mhacs_pumf(df)`

**Purpose** — Replace StatCan non-response codes with `NaN` for the numeric derived (`D`-prefix)
variables in the MHACS microdata, and ensure the survey weight is numeric.

**Why use it** — MHACS has **no blank cells**: missing is coded (`6/7/8/9`, `96`, `996`, `999`,
`99.6`). Any mean, model, or correlation computed before recoding is wrong.

**When to use it** — `mhacs_2022_pumf` only. It's a first pass — real analysis still needs
per-variable decoding against the PUMF PDF (`docs/data_dictionary.md` §E) and application of
`WTS_M` (and bootstrap weights for variance).

**Input** — the raw 9,861 × 602 PUMF CSV.
**Output** — same shape, with missing codes → `NaN` in the `D`-prefix numeric columns and `WTS_M`
coerced to numeric.

**Cases handled**
- **Phantom variable list removed (Report 3 §6).** An old hardcoded set (`DMHSTAT, DPHSTAT, DALCOHOL, DDRUGS, DWKDECAL, DWKDISAB`) matched **no column** in the real file — a silent no-op from an earlier codebook draft. Target columns are now derived at runtime (`col.startswith("D")` and numeric dtype), so the function survives file changes. Data impact of the fix: none — output was already identical.

**Watch out for**
- **Blanket code replacement is risky.** Some scales legitimately use values 6–9. This function trusts that every `D`-prefix numeric is a coded categorical — verify against the dictionary before using any specific variable, and restrict `missing_codes` per variable where a scale's real range overlaps.
- It only touches `D`-prefix columns. Non-derived question columns (`SUI_01`, `GEN_01`, …) are **not** recoded here — do that explicitly for the variables you select.
- `99.6` in `missing_codes` is a float; make sure the column is float before `.replace`.

```python
def clean_mhacs_pumf(df: pd.DataFrame) -> pd.DataFrame:
    """Clean MHACS 2022 PUMF: replace missing codes for numeric D-prefix variables."""
    df = df.copy()

    # Derive target columns at runtime: all numeric columns whose name starts with "D".
    # (Replaces a hardcoded `documented_variables` set that matched nothing — Report 3 §6.)
    target_vars = [
        col for col in df.columns
        if col.startswith("D") and df[col].dtype in ("int64", "float64")
    ]

    # Replace known StatCan missing-value codes with NaN
    missing_codes = {6, 7, 8, 9, 96, 996, 999, 99.6}
    for col in target_vars:
        df[col] = df[col].replace(list(missing_codes), np.nan)

    if "WTS_M" in df.columns:
        df["WTS_M"] = pd.to_numeric(df["WTS_M"], errors="coerce")

    return df
```

---

## Bug catalogue — reusable lessons (Report 3)

| # | Symptom | Root cause | Rule to add to your checklist |
|---|---|---|---|
| §7 | Pivot took minutes on 160k rows | per-row `itertuples` loop + boolean mask = O(n²) | Reshape with `np.select` + `pivot_table`, never a Python row loop |
| Bug #1 | CI values on the wrong rows | `enumerate()` counter used with `.loc` (label indexing) | Iterate with `.items()`; `reset_index(drop=True)` after `melt` |
| Bug #2 | Point estimates became `NaN` | `pd.to_numeric("12.3–14.5")` fails on a range string | Parse CI ranges first; write the left value back before bulk conversion |
| Warn #3 | Some CI strings not parsed | pattern only matched ASCII `-`; Excel uses `–` / `—` | Match `[-–—]` for any dash from spreadsheet exports |
| Warn #4 | Empty-match guard let `NaN` through | `NaN is not None` evaluates `True` | Use `pd.notna(x)`, never `x is not None`, for missing checks |
| Warn #5 | New fiscal years ignored | hardcoded `["2018"…"2022"]` | Detect years with `re.search(r"\b\d{4}\b", col)` |
| §6 | Recode set was a silent no-op | hardcoded var names from a different survey release | Derive column lists from the DataFrame at runtime |
| — | Stale function definitions | notebook cells never re-run (`execution_count = null`) | **Restart & Run All** before any pipeline run |

---

## Recommendation

1. Fold the four functions into **one** location — keep them in `02_data_cleaning_functions.py` and have the notebook `%run` it, **or** keep them inline in the notebook and delete the `.py`. Not both.
2. This document is the reference; keep it in `docs/`.
3. When cleaning is done, move the "Master cleaning checklist" section (minus the code) into `Report 3` / the final report's methodology as evidence of the QA process.
