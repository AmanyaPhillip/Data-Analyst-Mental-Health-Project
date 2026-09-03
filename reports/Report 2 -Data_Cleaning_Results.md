# Report — Data Cleaning Findings Across All Datasets  
**Project:** Mental Health & Suicide Prevention Data Analysis (Canada)  
**Pipeline Step:** 02 — Data Cleaning  
**Date:** 2026‑09‑03  
**Prepared by:** Fatima Hafeez  

---

## Overview

This report summarizes all issues identified during the cleaning of eight major datasets used in the Mental Health & Suicide Prevention project. Each section documents:

- Dataset structure  
- Column inventory (analytical vs. metadata)  
- Problems encountered  
- Cleaning decisions and code applied  
- Rationale for each fix  
- Core EDA opportunities unlocked after cleaning  

This report follows the team’s standardized review format and is intended for peer validation before finalizing the cleaned datasets in `data/processed/02_cleaned/`.

---

# 1. perceived_mh_annual.csv  
**Rows:** 936  
**Columns:** 19  

### Column Inventory

- **Time:** `ref_date_raw`, `start_year`, `ref_date`  
- **Demographic:** `geo`, `sex`, `age_group`  
- **Indicator:** `indicator`, `characteristic`, `value`, `metric_type`, `uom` (unit of measure, e.g. Percent — confirms how to read `value`)  
- **Metadata (API-oriented, not analytical):** `quality_flag`, `scalar_applied`, `scalar_factor`, `vector`, `dguid`, `is_percent`, `is_population`, `is_ci`, `is_other`  
- **Minimum EDA set:** `start_year` (trends), `geo` (region), `sex`, `age_group`, `indicator`, `value`

### Key Issues Found

#### 🔴 Critical — Missing Values in `value`
- **Cause:**  
  - Indicators not collected for certain demographic groups  
  - Privacy suppression  
  - Metadata placeholder rows  
- **Impact:**  
  - Breaks trend charts  
  - Incorrect aggregations  
  - Distorts year‑over‑year analysis  
- **Fix:**  
  - Dropped 26 rows with missing `value`  
  - Annual datasets require one numeric value per indicator per year  
- **Rationale:**  
  - Missingness is under 5% of rows, which is within the accepted threshold for row deletion  

#### 🟡 Warning — Incorrect Data Types
- `value` and `REF_DATE` loaded as `object`  
- **Fix:** Converted to numeric (integer)

#### 🟡 Warning — Inconsistent Text Formatting
- Long indicator names  
- Mixed casing  
- Extra whitespace  
- **Fix:** Standardized labels across:  
  - `indicator`  
  - `characteristic`  
  - `sex`  
  - `age_group`  
- **Method:** stripped whitespace, normalized text, enforced consistent casing

### EDA Enabled
- Trend analysis (2019–2024) — e.g. is “very good/excellent mental health” declining, is “fair/poor” rising  
- Sex, age, region comparisons  
- Indicator breakdowns — which indicators improve vs. worsen  
- Year‑over‑year change (e.g. 2021 → 2023 shift in “excellent mental health”)  
- Geographic comparisons  
- Correlation analysis against external datasets (income, unemployment, population)  
- Forecasting (ARIMA/Prophet)  
- Clustering demographic profiles  
- Dashboard work: trend charts, bar charts by sex, heatmaps by age group, KPI cards for % change  

---

# 2. perceived_health_quarterly.csv  
**Rows:** 6,318  
**Columns:** 18  

### Column Inventory

- **Use for EDA:** `ref_date` (quarterly period), `start_year`, `geo`, `sex`, `indicator`, `statistic` (tells you whether `value` is a percent, count or CI), `value`, `metric_type`  
- **Ignore:** `ref_date_raw`, `dguid`, `uom`, `scalar_factor`, `scalar_applied`, `vector`, `is_percent`, `is_population`, `is_ci`, `is_other`

### Key Issues Found

#### 🔴 Critical — Mixed Units in `value`
- Percentages (e.g., 57.1)  
- Population counts (e.g., 17,877,000)  
- CI bounds  
- **Cause:** StatCan stores every measurement type in a single `value` column and uses `statistic` to disambiguate — so the “too high” values are counts and the “too low” values are percentages  
- **Impact:**  
  - Percent lines appear flat when plotted with counts  
  - Misleading charts  
  - Skewed distributions and apparent outliers  
- **Fix:**  
  - Split dataset by `statistic`:  
    - Percentage of persons  
    - Number of persons  
    - CI lower bound  
    - CI upper bound  
  - Dropped CI rows (metadata only)

```python
df_percent  = df[df['statistic'] == 'Percentage of persons']
df_count    = df[df['statistic'] == 'Number of persons']
df_ci_lower = df[df['statistic'].str.contains('Lower bound')]
df_ci_upper = df[df['statistic'].str.contains('Upper bound')]
```

- **Then analyze each subset separately:** percentages for trends and demographic comparison, counts for population-level analysis, CI bounds for reliability checks. Never plot percentages and counts on the same axis.

#### 🟡 Warning — High Missing Values (3,545)
- All missing values came from CI rows  
- **Fix:**  
  - Dropped CI rows (non‑analytical)

#### 🟢 Note — Alternatives Considered and Rejected
- **Splitting statistic types into separate columns:** rejected — would create 75–90% sparsity per column, break tidy-data principles, and produce a structure inconsistent with the other StatCan datasets  
- **Standardizing values into a common unit:** rejected — counts, percentages and CI bounds are fundamentally different measurement types and cannot be converted without population denominators and survey-design metadata  

### EDA Enabled
- Quarterly trend analysis  
- Sex/age/region comparisons  
- Indicator comparisons (“excellent” vs “fair” vs “poor”)  
- Confidence interval / reliability review  
- Distribution and outlier detection  
- Missingness pattern analysis (percent vs CI vs counts)  
- Correlation analysis  

---

# 3. MHACS_2022_PUMF.csv  
**Rows:** 9,845  
**Columns:** 606  

### Column Inventory

**Important for analysis**

- **Demographic (core segmentation):** `GEODVPSZ` (province/region), `DHHGMS` (household membership), `DHHGAGE` (age group), `GENDER`, plus decoded `DHHGMS_LABEL`, `GENDER_LABEL`, `DHHGAGE_LABEL`  
- **Mental health indicators:** `GEN_01` (self-rated mental health), `GEN_02A` (stress), `GEN_02A1` (stress frequency), `GEN_08B` (diagnosed conditions), `GEN_08C` (severity), `GEN_01_LABEL`  
- **Socioeconomic:** `INCDVP19` (personal income), `INCDVP20` (income adequacy), `INCDVHH` (household income)  
- **Survey weight:** `WTS_M` — required for weighted prevalence and population-level estimates  

**Not important**

- Administrative/metadata: `PUMFID`, internal StatCan routing codes, processing flags  
- Skip-pattern variables (always NaN because the section was skipped) — must **not** be imputed  
- Technical variables: single-category columns, >95% missing, internal flags  
- Raw coded variables where a decoded `_LABEL` version already exists  

### Key Issues Found

#### 🔴 Critical — Missing Age Group (DHHGAGE)
- 5,226 missing values (over half the dataset)  
- **Cause:**  
  - Skip patterns and refusals  
  - Privacy suppression  
  - Empty strings / whitespace  
  - Special missing codes (6,7,8,9,96,996,999)  
- **Fix:**  
  - Converted all missing formats → `NaN`  
  - Filled with `"Not stated"`  
- **Rationale:**  
  - Preserves true missingness with no fake imputation  
  - Avoids the bias of dropping 5,226 rows  
  - Charts and cross-tabs no longer break  
- **Outcome:**  
  - `DHHGAGE_LABEL` now has **0 missing values**

#### 🔴 Critical — Missing Gender (GENDER)
- 16 values not recognized as missing — they did not respond to `.isna()` or `.fillna()` and persisted after cleaning  
- **Cause:**  
  - Invisible characters  
  - Empty strings and whitespace  
- **Fix:**  
  - Regex replacement → `NaN`  
  - Filled with `"Not stated"`  

```python
df[col] = df[col].replace(r'^\s*$', np.nan, regex=True)
df[col] = df[col].fillna("Not stated")
```

- **Outcome:**  
  - `GENDER_LABEL` now has **0 missing values**

### EDA Enabled
- Demographic segmentation (`DHHGAGE_LABEL`, `GENDER_LABEL`, `GEODVPSZ`)  
- Mental health status: self-rated health, stress, diagnosed conditions  
- Demographic differences across age, gender and income — identifying vulnerable groups  
- Income vs mental health (`INCDVP19`, `INCDVHH`)  
- Access‑to‑care analysis (`ACC_01`–`ACC_05` series) — barriers to services  
- Weighted prevalence using `WTS_M`, aligned with StatCan standards  

---

# 4. stress_coping.csv  
**Rows:** 14,388  
**Columns:** 19  

### Column Inventory

- **Important:** `ref_date_raw`, `start_year`, `geo`, `sex`, `age_group`, `indicator`, `value`, `ci_low`, `ci_high`  
- **Metadata / ignore:** `metric_type`, `vector`, `ref_date` (duplicate), `dguid`, `uom`, `scalar_factor`, `is_percent`, `is_population`, `is_ci`, `is_other`  
- The `is_*` flags are used for **filtering only**, never as analytical variables

### Key Issues Found

#### 🔴 Critical — Missing CI Values
- `ci_low`: 11,511 missing  
- `ci_high`: 11,511 missing  
- **Cause:** StatCan does not compute CI for many stress-coping indicators  
- **Fix:** Left as `NaN`  
- **Rationale (why not mean/median/mode):**  
  - These are not missing through error — StatCan simply never computed them  
  - CI is a statistical boundary, not a measurement; a boundary cannot be replaced by an average  
  - Imputing would produce fake error bars and statistically invalid results  
  - CI requires sample size, variance and distribution assumptions, none of which exist in the dataset  

#### 🟡 Warning — Missing `metric_type` (5,754)
- **Fix:** Filled with `"unknown"`  
- **Rationale:**  
  - Categorical metadata field, so numeric imputation does not apply  
  - Avoids grouping and filtering errors  
  - Preserves meaning without inventing units  

### EDA Enabled
- Trend analysis  
- Sex/age/region comparisons — which groups cope better or worse  
- Coping strategy and stress-level breakdowns by indicator  
- Distribution analysis of `value`  
- Optional CI review  

---

# 5. suicidal_thoughts.csv  
**Rows:** 14,388  
**Columns:** 19  

### Column Inventory

- **Important:** `ref_date_raw`, `start_year`, `geo`, `sex`, `age_group`, `indicator`, `value`, `ci_low`, `ci_high` (optional)  
- **Metadata / ignore:** `metric_type`, `vector`, `ref_date`, `dguid`, `uom`, `scalar_factor`, `is_percent`, `is_population`, `is_ci`, `is_other`

### Key Issues Found

#### 🔴 Critical — Missing CI Values (11,511)
- **Cause:**  
  - Sensitive indicators  
  - Small sample sizes  
  - Suppression rules  
  - CI not calculated for certain breakdowns  
- **Fix:** Left as `NaN`  
- **Rationale:** identical to §4 — CI represents uncertainty, cannot be imputed, and requires sample size and variance the dataset does not carry

#### 🟡 Warning — Missing `metric_type` (5,754)
- **Cause:** StatCan leaves this blank when the indicator is subjective or categorical, has no numeric unit, or the value is already a proportion  
- **Fix:** Filled with `"unknown"`

### EDA Enabled
- Suicidal ideation trends over time  
- Sex/age/region comparisons — identifying vulnerable groups  
- Indicator‑level analysis: ideation, plans, attempts, related coping  
- Optional CI review  

---

# 6. cchs_mh_disorders.csv  
**Rows:** 74,036  
**Columns:** 19  

### Column Inventory

- **Important:** `ref_date_raw`, `start_year`, `geo`, `sex`, `age_group`, `indicator`, `value`, `ci_low`, `ci_high` (optional)  
- **Metadata / ignore:** `metric_type`, `vector`, `ref_date`, `dguid`, `uom`, `scalar_factor`, `is_percent`, `is_population`, `is_ci`, `is_other`

### Key Issues Found

#### 🔴 Critical — Missing CI Values (61,128)
- **Cause:**  
  - CI not computed for many disorder indicators  
  - Small sample sizes and suppression rules  
  - Disorder data is highly sensitive; CI supplied for some indicators only  
- **Fix:** Left as `NaN`  
- **Rationale:** as in §4 and §5 — imputation would fabricate uncertainty

#### 🟢 Note — `metric_type` Fully Complete
- All indicators had a defined unit of measure and consistent StatCan metadata  
- No cleaning required

### EDA Enabled
- Disorder prevalence trends  
- Sex/age/region comparisons  
- Indicator‑level disorder analysis — diagnosed conditions, prevalence by condition, differences between disorder categories  

---

# 7. cihi_mh_services.csv  
**Rows:** 263  
**Columns:** 6  

### Column Inventory

- **All columns are analytical:** `indicator`, `breakdown`, `group`, `value`, `ci_low`, `ci_high`  
- No metadata columns to ignore — CIHI datasets are already minimal

### Key Issues Found

#### 🔴 Critical — Missing CI Values
- **Cause:**  
  - CIHI does not compute CI for many service-use metrics  
  - CI omitted when sample sizes are small  
  - CI not required for administrative data  
  - CIHI datasets are built for dashboards, not statistical modeling  
- **Fix:** Left as `NaN`

#### 🟢 Note — No Metadata Columns
- Dataset already minimal  
- No `metric_type` column, because CIHI indicators carry their units in the indicator name itself  
- No structural issues  

### EDA Enabled
- Service utilization analysis by indicator — service types, uptake, gaps  
- Breakdown analysis — service use by demographic group, region and service type  
- Group‑level comparisons — disparities in access across age, sex and region  
- Value distribution — utilization rates and intensity of access  

---

# 8. cihi_children_youth.csv  
**Rows:** 4,320  
**Columns:** 8  

### Column Inventory

- **Important:** `Fiscal year` (time), `Diagnosis category` (disorder type), `Sex`, `value` (rate or count), `ci_low`, `ci_high` (optional)  
- **Metadata / ignore:** `fiscal_year` (duplicate of `Fiscal year`), `sheet_type` (used only for filtering and separating report sections)

### Key Issues Found

#### 🔴 Critical — Missing CI Values
- `ci_low`: 2,160 missing  
- `ci_high`: 2,160 missing  
- **Cause:** CIHI does not compute CI for many diagnosis categories  
- **Fix:** Left as `NaN`  
- **Rationale:** CI represents uncertainty, not data, and cannot be imputed with mean/median/mode

#### 🟢 Note — Duplicate Time Column
- `Fiscal year` and `fiscal_year` carry the same information  
- **Fix:** Kept `Fiscal year` for analysis; `fiscal_year` retained but unused

### EDA Enabled
- Time trend analysis — how youth mental-health diagnoses and service use shift year over year  
- Diagnosis category analysis — prevalence per disorder, which are rising or declining  
- Sex breakdown — gender-based disparities in diagnosis  
- Value distribution — prevalence rates and overall distribution of conditions  
- Optional CI review  

---

# Summary of Cleaning Decisions

| Issue Type | Decision | Rationale |
|-----------|----------|-----------|
| Missing CI values | Keep as NaN | CI represents uncertainty; cannot be imputed |
| Mixed units | Split dataset by statistic | Prevents misleading charts |
| Mixed units → separate columns | Rejected | Creates 75–90% sparsity; breaks tidy data |
| Mixed units → unit standardization | Rejected | Needs denominators and survey-design metadata |
| Missing demographic values | Convert whitespace → NaN → “Not stated” | Preserves true missingness |
| Missing categorical metadata | Fill with “unknown” | Avoids grouping errors without inventing units |
| Inconsistent text | Standardize labels | Improves chart readability |
| Object types | Convert to numeric | Enables aggregation & plotting |
| Metadata rows | Drop | Non‑analytical |
| Skip-pattern variables | Leave as NaN, exclude from charts | Structural, not missing data |

---

# Final Outcome

All datasets in `data/processed/02_cleaned/` are now:

- Clean  
- Consistent  
- Ready for EDA, dashboards, and modeling  
- Aligned with StatCan & CIHI best practices  
- Free from misleading imputations  
- Structured for trend, demographic, and indicator‑level analysis  

---
