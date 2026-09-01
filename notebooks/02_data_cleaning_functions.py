"""
02_data_cleaning_functions.py
==============================
Fixed versions of all four cleaning functions from 02_data_cleaning.ipynb.

Author  : Phillip
Reviewed: Team (agreed 2026-09-01)
Report  : Report 3 – Data Cleaning and Bug Fixes

HOW TO USE
----------
In 02_data_cleaning.ipynb, after cell §1 (library imports), add a new cell:

    %run 02_data_cleaning_functions.py

This will redefine all four functions with the fixes applied.
Alternatively, copy each function body into its respective notebook cell
and re-run that cell before running the orchestration cell (§ end).

STALE-CELL WARNING
------------------
The original notebook has TWO cells with execution_count=null:
  - clean_statcan_long
  - clean_cihi_children_youth
This means those function definitions were NEVER explicitly re-run in
the last kernel session. The kernel had an older in-memory version.

Risk: If you restart the kernel and run only the orchestration cell,
you will either get a NameError or run a stale version.

Resolution: Always use  Kernel → Restart & Run All  before a full pipeline
run, or %run this file at the top of your session.
"""

import re
import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# §1  clean_statcan_long
# ---------------------------------------------------------------------------
# FIX  §7 (Report 3): The original pivot used a manual itertuples() loop with
# a per-row boolean mask — O(n²) complexity.  For cchs_mh_disorders (160 992
# rows) this took minutes.  Replaced with a three-step vectorised approach:
#   1. np.select() classifies each characteristic label in a single O(n) pass.
#   2. pivot_table() groups by all dimension columns and unstacks the key,
#      giving O(n log n) behaviour.
#   3. quality_flag / metric_type are merged back from the Percent rows only.

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

    # -----------------------------------------------------------------
    # VECTORISED PIVOT  (replaces the O(n²) itertuples loop)
    # -----------------------------------------------------------------
    if "characteristic" in df.columns:
        has_percent  = df["characteristic"].str.contains("Percent",  case=False, na=False).any()
        has_ci_low   = df["characteristic"].str.contains("Low.*95%", case=False, na=False).any()
        has_ci_high  = df["characteristic"].str.contains("High.*95%",case=False, na=False).any()

        if has_percent and (has_ci_low or has_ci_high):
            # Step 1 — classify each characteristic row with a short key (O(n))
            char = df["characteristic"].fillna("")
            df["_char_key"] = np.select(
                [
                    char.str.contains("Percent",  case=False),
                    char.str.contains("Low.*95%", case=False),
                    char.str.contains("High.*95%",case=False),
                ],
                ["value", "ci_low", "ci_high"],
                default="other",
            )

            # Step 2 — identify dimension columns (everything that is not a value/meta column)
            meta_cols = {"value", "characteristic", "_char_key",
                         "metric_type", "quality_flag", "scalar_applied"}
            dim_cols  = [c for c in df.columns if c not in meta_cols]

            # Step 3 — carry quality_flag and metric_type from the Percent rows only
            extra_keep = [c for c in ["quality_flag", "metric_type"] if c in df.columns]
            if extra_keep:
                pct_meta = (
                    df[df["_char_key"] == "value"][dim_cols + extra_keep]
                    .drop_duplicates(subset=dim_cols)
                )
            else:
                pct_meta = None

            # Step 4 — pivot: one column per _char_key value (O(n log n))
            pivot = (
                df[df["_char_key"] != "other"]
                .pivot_table(
                    index=dim_cols,
                    columns="_char_key",
                    values="value",
                    aggfunc="first",
                )
                .reset_index()
            )
            pivot.columns.name = None  # remove the residual MultiIndex name

            # Step 5 — re-attach quality_flag / metric_type
            if pct_meta is not None and not pct_meta.empty:
                merge_cols = [c for c in dim_cols if c in pct_meta.columns]
                merge_extra = [c for c in extra_keep if c in pct_meta.columns]
                pivot = pivot.merge(
                    pct_meta[merge_cols + merge_extra],
                    on=merge_cols,
                    how="left",
                )

            df = pivot

    # Reorder columns for readability
    col_order = [
        "ref_date_raw", "start_year", "geo", "sex", "age_group", "indicator",
        "characteristic", "value", "ci_low", "ci_high", "metric_type",
        "quality_flag", "scalar_applied", "vector",
    ]
    cols_present = [c for c in col_order if c in df.columns]
    other_cols   = [c for c in df.columns if c not in cols_present]
    df = df[cols_present + other_cols]

    return df


# ---------------------------------------------------------------------------
# §2  clean_cihi_vizconfig
# ---------------------------------------------------------------------------
# FIX §8 (Report 3): Added column-existence guard before accessing
# vis_option / confidence_interval_low / confidence_interval_high.
# The actual CSV (confirmed 2026-09-01) does contain all three columns,
# but the guard prevents a silent KeyError if the file changes.

# EXISTING BEHAVIOUR NOTE (confirmed safe):
#   x_axis_values and y_axis_values contain one value per row (not lists),
#   so .str.split(",") creates single-element lists.  The zip+loop handles
#   this correctly.  No data is lost.

def clean_cihi_vizconfig(df: pd.DataFrame) -> pd.DataFrame:
    """Unpivot CIHI chart-config CSV: split x/y axis values into separate rows."""
    df = df.copy()
    df.columns = df.columns.str.strip().str.lower()

    # Guard: confirm required columns exist before proceeding
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
            x     = xs[i].strip()
            y     = ys[i].strip()
            value = pd.to_numeric(y, errors="coerce")
            tidy_rows.append({
                "indicator": indicator,
                # vis_option confirmed present (2026-09-01 data inspection)
                "breakdown": row.get("vis_option", None),
                "group"    : x,
                "value"    : value,
                # confidence_interval_low / _high confirmed present in CSV
                "ci_low" : pd.to_numeric(row.get("confidence_interval_low",  None), errors="coerce"),
                "ci_high": pd.to_numeric(row.get("confidence_interval_high", None), errors="coerce"),
            })

    tidy = pd.DataFrame(tidy_rows)
    tidy = tidy.dropna(subset=["value"])
    return tidy


# ---------------------------------------------------------------------------
# §3  clean_cihi_children_youth
# ---------------------------------------------------------------------------
# FIXES applied (Report 3):
#
#   Bug #1 — .loc / enumerate index mismatch
#     BEFORE: for idx, val in enumerate(long_df["value"]):
#               long_df.loc[idx, "ci_low"] = ...   ← idx is a counter 0,1,2…
#                                                     .loc uses LABEL indexing
#                                                     → wrong rows written
#     AFTER:  for idx, val in long_df["value"].items():
#               long_df.loc[idx, "ci_low"] = ...   ← idx is the actual label
#                                                     → correct rows written
#     (Fix Option B, as agreed by the team)
#
#   Bug #2 — CI-formatted value cells lose their point estimate
#     BEFORE: pd.to_numeric("12.3-14.5") → NaN (the "12.3" is discarded)
#     AFTER:  the left-hand number is written back to long_df.loc[idx,"value"]
#             INSIDE the loop, before the bulk pd.to_numeric() conversion.
#
#   Warning #3 — ASCII hyphen only; en-dash / em-dash from Excel missed
#     BEFORE: ci_pattern = r"([\d.]+)\s*-\s*([\d.]+)"
#             if isinstance(val, str) and "-" in val:
#     AFTER:  ci_pattern = r"([\d.]+)\s*[-\u2013\u2014]\s*([\d.]+)"
#             DASH_CHARS  = {"-", "\u2013", "\u2014"}
#             if isinstance(val, str) and any(d in val for d in DASH_CHARS):
#
#   Warning #4 — is not None doesn't catch NaN
#     BEFORE: if not match.empty and match.iloc[0, 0] is not None:
#     AFTER:  if not match.empty and pd.notna(match.iloc[0, 0]):
#
#   Warning #5 — hardcoded year range 2018-2022
#     BEFORE: any(y in str(c) for y in ["2018","2019","2020","2021","2022"])
#     AFTER:  re.search(r"\b\d{4}\b", str(c))   ← matches any 4-digit year

# STALE-CELL WARNING: This function's notebook cell also had execution_count=null.
# See the module docstring for remediation.

_CI_DASH_CHARS = {"-", "\u2013", "\u2014"}           # hyphen, en-dash, em-dash
_CI_PATTERN    = r"([\d.]+)\s*[-\u2013\u2014]\s*([\d.]+)"


def clean_cihi_children_youth(raw_excel: dict) -> pd.DataFrame:
    """Reshape CIHI children/youth Excel from wide to long, parse CI bounds, add sheet identifier."""
    frames = []

    for sheet, df in raw_excel.items():
        df = df.copy()
        df.columns = df.columns.str.strip().str.replace("\n", " ")

        # FIX Warning #5: dynamic year detection (any 4-digit year)
        # BEFORE: hardcoded ["2018","2019","2020","2021","2022"]
        # AFTER:  regex \b\d{4}\b — survives future data updates automatically
        year_cols  = [c for c in df.columns if re.search(r"\b\d{4}\b", str(c))]
        id_cols    = [c for c in df.columns if c not in year_cols] if year_cols else list(df.columns[:3])
        value_cols = year_cols if year_cols else list(df.columns[3:])

        # Melt to long format
        long_df = df.melt(
            id_vars=id_cols,
            value_vars=value_cols,
            var_name="fiscal_year",
            value_name="value",
        )
        long_df["fiscal_year"] = long_df["fiscal_year"].str.replace(" ", "", regex=False)

        # FIX Bug #1 safety belt: reset_index so labels are 0,1,2,…
        # (required for .loc[idx] inside the loop below to be safe)
        long_df = long_df.reset_index(drop=True)

        long_df["ci_low"]  = None
        long_df["ci_high"] = None

        # FIX Bug #1 (Option B): use .items() to pair real label with value
        # FIX Bug #2: write back the left-hand number as the point estimate
        # FIX Warning #3: support en-dash / em-dash from Excel exports
        # FIX Warning #4: use pd.notna() instead of "is not None"
        for idx, val in long_df["value"].items():                         # Bug #1 fix
            if isinstance(val, str) and any(d in val for d in _CI_DASH_CHARS):  # Warning #3
                match = pd.Series(val).str.extract(_CI_PATTERN, expand=True)
                if not match.empty and pd.notna(match.iloc[0, 0]):        # Warning #4
                    lo = pd.to_numeric(match.iloc[0, 0], errors="coerce")
                    hi = pd.to_numeric(match.iloc[0, 1], errors="coerce")
                    long_df.loc[idx, "ci_low"]  = lo
                    long_df.loc[idx, "ci_high"] = hi
                    long_df.loc[idx, "value"]   = lo   # Bug #2 fix: preserve point estimate

        # Bulk numeric conversion — CI strings already resolved above
        long_df["value"] = pd.to_numeric(long_df["value"], errors="coerce")

        # Add sheet type identifier
        long_df["sheet_type"] = (
            "ED"             if "Table8"  in sheet else
            "Hospitalization" if "Table13" in sheet else
            sheet.replace("_to hide", "")
        )
        frames.append(long_df)

    return pd.concat(frames, ignore_index=True)


# ---------------------------------------------------------------------------
# §4  clean_mhacs_pumf
# ---------------------------------------------------------------------------
# FIX §6 (Report 3): Hardcoded documented_variables set contained variable
# names that DO NOT EXIST in the actual MHACS 2022 PUMF CSV:
#
#   Phantom names (checked 2026-09-01):
#     DMHSTAT, DPHSTAT, DALCOHOL, DDRUGS, DWKDECAL, DWKDISAB
#   → exact=False, case-insensitive=False for ALL six variables
#
# These names likely came from an earlier codebook draft or a different
# StatCan survey release.  Because the function already falls back to
# "all numeric D-prefix columns", the phantom set contributed ZERO target
# columns — it was silently a no-op.
#
# The actual D-prefix numeric columns (43 confirmed) are:
#   DHHGMS, DHHGAGE, DIS_01A–DIS_01N, DISDK6, DISDDSX, DISDCHR,
#   DEP_72, DEP_86, DEP_87, DEPDDPS, DEPGREC, DEPGPER, DEPDDY,
#   DEPFSLT, DEPFSYT, DEPFINT, DEPDINT,
#   DASG01, DASG02, DAS_04–DAS_13, DASGSCR, DABTIPPE, DNBTIPPE
#
# FIX: Remove the phantom set.  Derive target columns directly from the
# DataFrame at runtime so this function is resilient to file changes.
#
# DATA IMPACT: None — the phantom set never matched any column, so output
# was already identical to what this corrected version produces.

def clean_mhacs_pumf(df: pd.DataFrame) -> pd.DataFrame:
    """Clean MHACS 2022 PUMF: replace missing codes for numeric D-prefix variables."""
    df = df.copy()

    # Derive target columns at runtime: all numeric columns whose name starts
    # with "D".  This covers all 43 confirmed D-prefix variables and will
    # automatically include any new D-prefix columns in future data releases.
    #
    # NOTE: Previously the code also maintained a hardcoded `documented_variables`
    # set {DMHSTAT, DPHSTAT, DALCOHOL, DDRUGS, DWKDECAL, DWKDISAB} that did
    # NOT match any column in the actual file.  That set has been removed.
    # See Report 3 §6 for full details.
    target_vars = [
        col for col in df.columns
        if col.startswith("D") and df[col].dtype in ("int64", "float64")
    ]

    # Replace known StatCan missing-value codes with NaN
    # Codes: 6 (not applicable), 7 (don't know), 8 (refused),
    #        9 (not stated), 96 / 996 / 999 (not applicable extended),
    #        99.6 (continuous not stated)
    missing_codes = {6, 7, 8, 9, 96, 996, 999, 99.6}
    for col in target_vars:
        df[col] = df[col].replace(list(missing_codes), np.nan)

    # Ensure survey weight is numeric
    if "WTS_M" in df.columns:
        df["WTS_M"] = pd.to_numeric(df["WTS_M"], errors="coerce")

    return df
