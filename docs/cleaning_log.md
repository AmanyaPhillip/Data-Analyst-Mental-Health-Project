# Cleaning Log

**Project:** Data Analyst - Mental Health (Canada)
**Pipeline step:** 2 - Data Cleaning
**Implementation:** [`notebooks/02_data_cleaning.ipynb`](../notebooks/02_data_cleaning.ipynb)
**Output directory:** [`data/processed/02_cleaned/`](../data/processed/02_cleaned/)

This log records the cleaning currently implemented in the notebook. Source values are retained unless explicitly identified as non-response codes; suppressed and unreliable observations are not imputed.

## Dataset Outputs

| Dataset | Source type | Cleaner | Intended cleaned shape |
|---|---|---|---|
| `perceived_mh_annual` | StatCan CSV | `clean_statcan_long` | Tidy long format |
| `suicidal_thoughts` | StatCan CSV | `clean_statcan_long` | Tidy long format, with confidence intervals where available |
| `stress_coping` | StatCan CSV | `clean_statcan_long` | Tidy long format, with confidence intervals where available |
| `perceived_health_quarterly` | StatCan CSV | `clean_statcan_long` | Tidy long format |
| `cchs_mh_disorders` | StatCan CSV | `clean_statcan_long` | Tidy long format |
| `cihi_mh_services` | CIHI chart-config CSV | `clean_cihi_vizconfig` | One row per plotted observation |
| `cihi_children_youth` | CIHI Excel workbook | `clean_cihi_children_youth` | Long format by fiscal year and sheet type |
| `mhacs_2022_pumf` | StatCan PUMF CSV | `clean_mhacs_pumf` | Microdata with selected non-response codes set to missing |

### Source Registry

The notebook writes each cleaned filename from the following raw source. The two source filenames are counterintuitive, so these mappings are recorded by their verified dataset contents.

| Cleaned dataset | Raw source path |
|---|---|
| `perceived_mh_annual` | `data/raw/StatCan 13-10-0972 – perceived mental health.csv` |
| `suicidal_thoughts` | `data/raw/Catalogue Entry Mental health characteristics and suicidal thoughts.csv` |
| `stress_coping` | `data/raw/Catalogue Entry Mental health characteristics Ability to handle stress and sources of stress.csv` |
| `perceived_health_quarterly` | `data/raw/Catalogue Entry Mental health indicators.csv` |
| `cchs_mh_disorders` | `data/raw/Catalogue Entry Perceived health, by gender and province.csv` |
| `cihi_mh_services` | `data/raw/health services for mental illness and alcoholdrug induced disorders.csv` |
| `cihi_children_youth` | `data/raw/care-children-youth-with-mental-disorders-data-tables-en.xlsx` |
| `mhacs_2022_pumf` | `data/raw/MHACS 2022 Public Use Microdata.csv` |

## Implemented Cleaning

### StatCan Long Tables

The five StatCan tables receive the following transformations:

| Transformation | Implementation |
|---|---|
| Column names | Strip whitespace and convert names to lowercase; rename dimensions to `age_group`, `indicator`, `characteristic`, `sex`, and `quality_flag`. |
| Text values | Strip whitespace without coercing genuine missing values to the string `"nan"`. |
| Dates | Preserve the original period in `ref_date_raw`; extract its first four-digit year to nullable integer `start_year`. |
| Values | Convert `value` to numeric with invalid or suppressed values retained as missing. |
| Scalar factors | Multiply `value` by 1,000 where `scalar_factor` is `thousands`; record this in `scalar_applied`. |
| Data quality | Preserve StatCan `STATUS` as lowercase `quality_flag`; values flagged `E`, `F`, `x`, or `..` are not imputed or dropped by the cleaner. |
| Units | Copy lowercased `uom` to `metric_type` to distinguish percentage and number measures. |
| Geography and indicators | Trim geography, normalize spaced slashes, and collapse repeated whitespace in indicators. |
| Metadata | Remove unused export fields: `symbol`, `terminated`, `decimals`, `uom_id`, `scalar_id`, and `coordinate`. |
| Confidence intervals | Retain percentage estimates and low/high 95% confidence-interval observations in long format through `characteristic` or `statistic`. They are not pivoted until matching grouping keys are validated. |

The base StatCan output orders dimensions first, then measures, then data-quality fields. StatCan outputs remain in long format and keep their original `characteristic` or `statistic` column, including confidence-interval observations where supplied.

### CIHI Mental-Health Services

`clean_cihi_vizconfig` converts each comma-separated `x_axis_values` and `y_axis_values` pair into one tidy row.

| Output field | Source |
|---|---|
| `indicator` | `indicator` |
| `breakdown` | `vis_option` |
| `group` | Each value in `x_axis_values` |
| `value` | Aligned value from `y_axis_values`, converted to numeric |
| `ci_low` | `confidence_interval_low` |
| `ci_high` | `confidence_interval_high` |

Rows whose plotted value is not numeric are excluded. This prevents labels and unavailable values from being analysed as measurements.

### CIHI Children and Youth

`clean_cihi_children_youth` processes the two machine-readable hidden sheets in the CIHI workbook.

- Identifies year-like columns and reshapes the sheets from wide to long format.
- Produces `fiscal_year` and `value` fields.
- Extracts numerical bounds from hyphen-separated confidence-interval text into `ci_low` and `ci_high` when available.
- Converts the main rate to numeric, leaving unavailable values missing.
- Adds `sheet_type`: `ED` for Table 8 and `Hospitalization` for Table 13.

### MHACS 2022 PUMF

`clean_mhacs_pumf` deliberately avoids applying missing-code replacement to all 602 columns. It replaces the currently configured non-response codes (`6`, `7`, `8`, `9`, `96`, `996`, `999`, and `99.6`) only in selected mental-health and behavioural variables, plus numeric variables whose names begin with `D`. `WTS_M` is converted to numeric.

## Remaining Checks

The following work is not complete and should be resolved before final analysis or publication:

| Area | Required follow-up |
|---|---|
| StatCan CI pivot | Confirm the grouping keys and ensure percentage CI rows can be paired only with their matching unit, population, and indicator before adding a wide-format analysis view. The current cleaner intentionally preserves long-format rows. |
| StatCan geography | Map provinces, territories, and rollups such as Atlantic and Prairies to an agreed canonical geography standard. |
| StatCan analysis window | Define and apply the team-approved reference-period window. |
| CIHI mental-health services | Confirm whether confidence-interval columns contain one value per chart or a comma-separated value per plotted category; split aligned CI values if necessary. |
| CIHI children and youth | Validate year-column detection and confidence-interval parsing against both source sheets, including `n/r` values. |
| MHACS PUMF | Replace the heuristic `D*` variable selection with an explicit variable-to-missing-code map derived from the PUMF codebook. |
| Pipeline validation | Add assertions for row counts, required columns, numeric value ranges, and preservation of source quality flags before exporting CSV files. |
