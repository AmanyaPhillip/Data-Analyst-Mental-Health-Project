# Data Cleaning Issues Found

**Project:** Mental Health & Suicide Prevention Data Analysis (Canada)  
**Pipeline step:** 02 — Data Cleaning  
**Output directory:** `data/processed/02_cleaned/`  
**Notebook:** `notebooks/02_data_cleaning.ipynb`  
**Date issued:** 2026-09-01  
**Status:** 🔄 Peer review in progress

---

## Purpose

Each team member listed below is assigned one or more cleaned CSV files from `data/processed/02_cleaned/`. Your job is to open your assigned file(s), inspect the data, and fill in your feedback section below before the next team meeting.

You are looking for anything that seems wrong, unexpected, or incomplete — you do not need to diagnose the root cause. Just describe what you see and flag it with a severity level.

**Severity guide**

| Label | Meaning |
|---|---|
| 🔴 Critical | Data is incorrect or missing in a way that would break analysis |
| 🟡 Warning | Suspicious values or quality concerns that need investigation |
| 🟢 Note | Minor observations or questions — low risk |

---

## Assignments

| Reviewer | Cleaned file(s) | Raw source file(s) | Size |
|---|---|---|---|
| **Phillip** | `cchs_mh_disorders.csv` | `data/raw/Catalogue Entry Perceived health, by gender and province.csv` | ~30 MB |
| **Danny** | `mhacs_2022_pumf.csv` | `data/raw/MHACS 2022 Public Use Microdata.csv` | ~24 MB |
| **Samir** | `stress_coping.csv` | `data/raw/Catalogue Entry Mental health characteristics Ability to handle stress and sources of stress.csv` | ~5.5 MB |
| **Samir** | `cihi_mh_services.csv` | `data/raw/health services for mental illness and alcoholdrug induced disorders.csv` | ~16 KB |
| **Misa** | `suicidal_thoughts.csv` | `data/raw/Catalogue Entry Mental health characteristics and suicidal thoughts.csv` | ~1.6 MB |
| **Misa** | `perceived_mh_annual.csv` | `data/raw/StatCan 13-10-0972 – perceived mental health.csv` | ~164 KB |
| **Jyothi** | `perceived_health_quarterly.csv` | `data/raw/Catalogue Entry Mental health indicators.csv` | ~1.1 MB |
| **Rebal** | `cihi_children_youth.csv` | `data/raw/care-children-youth-with-mental-disorders-data-tables-en.xlsx` | ~374 KB |

> **Tip:** For large files (>5 MB), you do not need to inspect every row. Load it in Python or Excel, check the first and last 50 rows, column names, null counts, value ranges, and any obvious outliers.

---

## Raw vs Cleaned Reference

Use this table to locate both files when comparing the cleaned output against its source.

| Cleaned file | Raw source |
|---|---|
| `data/processed/02_cleaned/perceived_mh_annual.csv` | `data/raw/StatCan 13-10-0972 – perceived mental health.csv` |
| `data/processed/02_cleaned/suicidal_thoughts.csv` | `data/raw/Catalogue Entry Mental health characteristics and suicidal thoughts.csv` |
| `data/processed/02_cleaned/stress_coping.csv` | `data/raw/Catalogue Entry Mental health characteristics Ability to handle stress and sources of stress.csv` |
| `data/processed/02_cleaned/perceived_health_quarterly.csv` | `data/raw/Catalogue Entry Mental health indicators.csv` |
| `data/processed/02_cleaned/cchs_mh_disorders.csv` | `data/raw/Catalogue Entry Perceived health, by gender and province.csv` |
| `data/processed/02_cleaned/cihi_mh_services.csv` | `data/raw/health services for mental illness and alcoholdrug induced disorders.csv` |
| `data/processed/02_cleaned/cihi_children_youth.csv` | `data/raw/care-children-youth-with-mental-disorders-data-tables-en.xlsx` |
| `data/processed/02_cleaned/mhacs_2022_pumf.csv` | `data/raw/MHACS 2022 Public Use Microdata.csv` |

---

## Feedback Template

For each issue found, copy and fill in the block below inside your section.

```
File: <filename>
Column(s): <column name(s)>
Row(s) / sample value: <row index or example value>
Severity: 🔴 / 🟡 / 🟢
Description: <what you saw>
Suggested fix (if any): <optional>
```

---

## Phillip — `cchs_mh_disorders.csv`

**Raw source:** `data/raw/Catalogue Entry Perceived health, by gender and province.csv`

*Largest StatCan dataset (160,992 source rows). Focus on: `value` / `ci_low` / `ci_high` pivot correctness, `quality_flag` distribution, `scalar_applied` flag accuracy, and `start_year` parsing.*

<!-- Add your findings below -->

---

## Danny — `mhacs_2022_pumf.csv`

**Raw source:** `data/raw/MHACS 2022 Public Use Microdata.csv`

*MHACS 2022 PUMF microdata (9,861 respondents, 602 columns). Focus on: D-prefix columns for remaining non-response codes that should be NaN, `WTS_M` numeric conversion, and any columns that still contain coded values (6, 7, 8, 9, 96, 996, 999, 99.6).*

<!-- Add your findings below -->

---

## Samir — `stress_coping.csv` & `cihi_mh_services.csv`

*Two files. `stress_coping` is a StatCan long table (focus on tidy structure, CI rows). `cihi_mh_services` is a small chart-config CSV unpivoted to tidy rows (focus on `breakdown`, `group`, `value`, `ci_low`, `ci_high` columns).*

### stress_coping.csv

**Raw source:** `data/raw/Catalogue Entry Mental health characteristics Ability to handle stress and sources of stress.csv`

<!-- Add your findings below -->

### cihi_mh_services.csv

**Raw source:** `data/raw/health services for mental illness and alcoholdrug induced disorders.csv`

<!-- Add your findings below -->

---

## Misa — `suicidal_thoughts.csv` & `perceived_mh_annual.csv`

*Two StatCan long tables. Focus on: `value` / `ci_low` / `ci_high` presence and alignment with `characteristic`, `geo` normalization, `quality_flag` values, and whether the pivot produced the expected wide structure for datasets that contain CI rows.*

### suicidal_thoughts.csv

**Raw source:** `data/raw/Catalogue Entry Mental health characteristics and suicidal thoughts.csv`

<!-- Add your findings below -->

### perceived_mh_annual.csv

**Raw source:** `data/raw/StatCan 13-10-0972 – perceived mental health.csv`

<!-- Add your findings below -->

---

## Jyothi — `perceived_health_quarterly.csv`

**Raw source:** `data/raw/Catalogue Entry Mental health indicators.csv`

*StatCan long table with quarterly data. Focus on: `ref_date_raw` format (should be year-quarter strings), `start_year` extraction accuracy, `geo` values, `value` / `ci_low` / `ci_high` column presence, and any unexpected nulls.*

<!-- Add your findings below -->

---

## Rebal — `cihi_children_youth.csv`

**Raw source:** `data/raw/care-children-youth-with-mental-disorders-data-tables-en.xlsx`

*CIHI children/youth Excel workbook reshaped to long format (two sheets combined). Focus on: `fiscal_year` format, `ci_low` / `ci_high` alignment with `value` (point estimate should be the lower CI bound for CI-formatted rows), `sheet_type` values (`ED` / `Hospitalization`), and any rows where `value` is unexpectedly NaN.*

<!-- Add your findings below -->

---

## Consolidated Issues Log

*This table is filled in by Phillip after all individual reviews are submitted. Do not edit this section directly.*

| # | Reviewer | File | Column(s) | Severity | Summary |
|---|---|---|---|---|---|
| — | — | — | — | — | *(pending reviews)* |

---

*Issued by Phillip · 2026-09-01 · See `reports/Report 3 - Data Cleaning and Bug Fixes.md` for the full audit trail of cleaning decisions*
