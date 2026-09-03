# Report — Data Cleaning Findings Across All Datasets  
**Project:** Mental Health & Suicide Prevention Data Analysis (Canada)  
**Pipeline Step:** 02 — Data Cleaning  
**Date:** 2026‑09‑03  
**Prepared by:** Fatima Hafeez  

---

## Overview

This report summarizes all issues identified during the cleaning of seven major datasets used in the Mental Health & Suicide Prevention project. Each section documents:

- Dataset structure  
- Problems encountered  
- Cleaning decisions  
- Rationale for each fix  
- Core EDA opportunities unlocked after cleaning  

This report follows the team’s standardized review format and is intended for peer validation before finalizing the cleaned datasets in `data/processed/02_cleaned/`.

---

# 1. perceived_mh_annual.csv  
**Rows:** 936  
**Columns:** 19  

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

### EDA Enabled
- Trend analysis (2019–2024)  
- Sex, age, region comparisons  
- Indicator breakdowns  
- Year‑over‑year change  
- Geographic comparisons  
- Forecasting (ARIMA/Prophet)  
- Clustering demographic profiles  

---

# 2. perceived_health_quarterly.csv  
**Rows:** 6,318  
**Columns:** 18  

### Key Issues Found

#### 🔴 Critical — Mixed Units in `value`
- Percentages (e.g., 57.1)  
- Population counts (e.g., 17,877,000)  
- CI bounds  
- **Impact:**  
  - Percent lines appear flat when plotted with counts  
  - Misleading charts  
- **Fix:**  
  - Split dataset by `statistic`:  
    - Percentage of persons  
    - Number of persons  
    - CI lower bound  
    - CI upper bound  
  - Dropped CI rows (metadata only)

#### 🟡 Warning — High Missing Values (3,545)
- All missing values came from CI rows  
- **Fix:**  
  - Dropped CI rows (non‑analytical)

### EDA Enabled
- Quarterly trend analysis  
- Sex/age/region comparisons  
- Indicator comparisons  
- Outlier detection  
- Correlation analysis  

---

# 3. MHACS_2022_PUMF.csv  
**Rows:** 9,845  
**Columns:** 606  

### Key Issues Found

#### 🔴 Critical — Missing Age Group (DHHGAGE)
- 5,226 missing values  
- **Cause:**  
  - Skip patterns  
  - Privacy suppression  
  - Empty strings / whitespace  
  - Special missing codes (6,7,8,9,96,996,999)  
- **Fix:**  
  - Converted all missing formats → `NaN`  
  - Filled with `"Not stated"`  
- **Outcome:**  
  - `DHHGAGE_LABEL` now has **0 missing values**

#### 🔴 Critical — Missing Gender (GENDER)
- 16 values not recognized as missing  
- **Cause:**  
  - Invisible characters  
  - Whitespace  
- **Fix:**  
  - Regex replacement → `NaN`  
  - Filled with `"Not stated"`  
- **Outcome:**  
  - `GENDER_LABEL` now has **0 missing values**

### EDA Enabled
- Demographic segmentation  
- Stress, mental health, diagnosed conditions  
- Income vs mental health  
- Weighted prevalence using `WTS_M`  
- Access‑to‑care analysis  

---

# 4. stress_coping.csv  
**Rows:** 14,388  
**Columns:** 19  

### Key Issues Found

#### 🔴 Critical — Missing CI Values
- `ci_low`: 11,511 missing  
- `ci_high`: 11,511 missing  
- **Cause:** StatCan does not compute CI for many indicators  
- **Fix:** Left as `NaN`  
- **Rationale:**  
  - CI is uncertainty, not a data point  
  - Cannot impute without sample size/variance  

#### 🟡 Warning — Missing `metric_type` (5,754)
- **Fix:** Filled with `"unknown"`  
- **Rationale:**  
  - Avoids grouping errors  
  - Preserves meaning  

### EDA Enabled
- Trend analysis  
- Sex/age/region comparisons  
- Coping strategy breakdowns  
- Distribution analysis  
- Optional CI review  

---

# 5. suicidal_thoughts.csv  
**Rows:** 14,388  
**Columns:** 19  

### Key Issues Found

#### 🔴 Critical — Missing CI Values (11,511)
- **Cause:**  
  - Sensitive indicators  
  - Small sample sizes  
  - Suppression rules  
- **Fix:** Left as `NaN`

#### 🟡 Warning — Missing `metric_type` (5,754)
- **Fix:** Filled with `"unknown"`

### EDA Enabled
- Suicidal ideation trends  
- Sex/age/region comparisons  
- Indicator‑level analysis  
- Optional CI review  

---

# 6. cchs_mh_disorders.csv  
**Rows:** 74,036  
**Columns:** 19  

### Key Issues Found

#### 🔴 Critical — Missing CI Values (61,128)
- **Cause:**  
  - CI not computed for many disorder indicators  
  - Suppression rules  
- **Fix:** Left as `NaN`

#### 🟢 Note — `metric_type` Fully Complete
- No cleaning required

### EDA Enabled
- Disorder prevalence trends  
- Sex/age/region comparisons  
- Indicator‑level disorder analysis  

---

# 7. cihi_mh_services.csv  
**Rows:** 263  
**Columns:** 6  

### Key Issues Found

#### 🔴 Critical — Missing CI Values
- CIHI does not compute CI for many service indicators  
- **Fix:** Left as `NaN`

#### 🟢 Note — No Metadata Columns
- Dataset already minimal  
- No structural issues  

### EDA Enabled
- Service utilization analysis  
- Demographic breakdowns  
- Group‑level comparisons  

---

# Summary of Cleaning Decisions

| Issue Type | Decision | Rationale |
|-----------|----------|-----------|
| Missing CI values | Keep as NaN | CI represents uncertainty; cannot be imputed |
| Mixed units | Split dataset by statistic | Prevents misleading charts |
| Missing demographic values | Convert whitespace → NaN → “Not stated” | Preserves true missingness |
| Inconsistent text | Standardize labels | Improves chart readability |
| Object types | Convert to numeric | Enables aggregation & plotting |
| Metadata rows | Drop | Non‑analytical |

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

