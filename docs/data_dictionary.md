# Data Dictionary

**Project:** Data Analyst – Mental Health (Canada)
**Status:** DRAFT · last updated 2026-08-27 · owner: Samir
**Companion:** [`docs/data_inventory.md`](data_inventory.md) · per-column stats in [`data/processed/01_column_profiles.csv`](../data/processed/01_column_profiles.csv)

This file defines every column, its type, and its permitted values for each dataset used.
Sections marked **TODO** need the source documentation (linked) to complete.

---

## A. Shared schema — StatCan tables

Datasets `perceived_mh_annual`, `suicidal_thoughts`, `stress_coping`,
`perceived_health_quarterly`, `cchs_mh_disorders` all use StatCan's standard
"table download" layout. Columns:

| Column | Type | Description | Permitted values / notes |
|---|---|---|---|
| `REF_DATE` | string | Reference period | Year (`2016`), year range (`2019/2020`), or year-month (`2021-04`). Parse per table. |
| `GEO` | string | Geography | Canada (or "Canada excluding territories"), 10 provinces, 3 territories, and region rollups ("Atlantic", "Prairies"). **Standardise names in cleaning.** |
| `DGUID` | string | Dissemination Geography Unique ID | StatCan geography code; can be dropped for analysis. |
| `Age group` | string | Age band | e.g. `12 to 17 years`, `18 to 34 years`, …, `65 years and over`, `Total, 12 years and over`. Absent in `perceived_health_quarterly`. |
| `Sex` / `Gender` | string | Sex or gender of person | `Both sexes`/`Total` , `Males`/`Men`(+), `Females`/`Women`(+). Newer tables use "Gender" and the "+" suffix. |
| `Indicators` | string | The measure | Table-specific — see section B. |
| `Characteristics` / `Statistics` | string | What the number represents | `Number of persons`, `Percent` / `Percentage of persons`, `Low/High 95% confidence interval, number/percent`, `Coefficient of variation …`, `Statistically different from …`. |
| `UOM` | string | Unit of measure | `Number` or `Percent`. |
| `UOM_ID` | int | Numeric code for `UOM` | — |
| `SCALAR_FACTOR` | string | Scale of `VALUE` | `units` (×1) or `thousands` (×1,000). **Apply before comparing.** |
| `SCALAR_ID` | int | Numeric code for scalar | `0` = units, `3` = thousands. |
| `VECTOR` | string | StatCan series ID | e.g. `v1806947204`. Stable key for a single time series — useful for API refresh. |
| `COORDINATE` | string | Dimension coordinate | dotted index into the cube (e.g. `2.1.1.3.4`). Can be dropped. |
| `VALUE` | float | The data point | May be blank when suppressed (see `STATUS`). |
| `STATUS` | string | Data-quality / availability flag | `E` = use with caution · `F` = too unreliable to be published · `x` = suppressed (confidentiality) · `..` = not available for this reference period. Blank = normal. |
| `SYMBOL` | string | Secondary symbol | Unused in these extracts (all blank). |
| `TERMINATED` | string | Series terminated flag | Unused in these extracts (all blank). |
| `DECIMALS` | int | Decimal places for display | `0` for counts, `1` for percentages. |

**Cleaning rules (for `02_data_cleaning.ipynb`):**
1. Keep rows where `UOM = Percent` as the primary metric; keep `Number` rows for population weighting.
2. Pivot `Characteristics`/`Statistics` so each row has `value`, `ci_low`, `ci_high`, `cv` as columns.
3. Multiply `VALUE` by 1,000 where `SCALAR_FACTOR = thousands`.
4. Keep `STATUS` as a `quality_flag` column; **do not impute** suppressed values.
5. Standardise `GEO` to a canonical province list; map region rollups separately.

### Indicator lists (section B)

**`perceived_mh_annual` (13-10-0972)** — all measured as % of persons 18+:
`Perceived mental health, very good or excellent` · `Perceived mental health, fair or poor` ·
`Perceived life stress, most days quite a bit or extremely stressful` · `Mood disorder` ·
`Anxiety disorder` · `Heavy drinking` · `Cannabis use, past 12 months` ·
`Sense of belonging to local community, somewhat strong or very strong`.

**`suicidal_thoughts` (13-10-0465 subset)**:
`Suicidal thoughts (15 years and over)` · `Consultation with a health professional about emotional or mental health` · `Positive mental health, flourishing`.

**`stress_coping` (13-10-0802)**:
`Ability to handle unexpected and difficult problems, good or excellent` ·
`Ability to handle the day-to-day demands in life, good or excellent` ·
`Main source of stress in day-to-day life, {work | financial concerns | family | school work (12 to 34 years old) | time pressures/ not enough time | health | other | none}`.

**`perceived_health_quarterly` (45-10-0081)** — *general* health, not mental health:
`Excellent or very good perceived health` · `Good perceived health` · `Fair or poor perceived health`.

**`cchs_mh_disorders` (13-10-0465)** — 45 indicators, each typically "life" and "12 months":
mood disorders (any mood disorder, major depressive episode, bipolar) · anxiety disorders
(any anxiety disorder, generalized anxiety disorder, social phobia) · substance use
(alcohol / cannabis / other drug abuse or dependence; any substance use disorder) ·
combined "any selected disorder" · plus current diagnosed conditions (ADHD, eating disorder).
→ Full list: see `data/processed/01_column_profiles.csv` filtered to `dataset = cchs_mh_disorders`.

---

## C. `cihi_mh_services` — CIHI / PHAC Health Infobase export

Each **row is a chart specification**, not an observation.

| Column | Description |
|---|---|
| `indicator` | Topic (e.g. `Self-rated mental health in youth`, `Self-inflicted injuries: Hospitalizations`, `Mortality`). 29 values. |
| `vis_option` | Breakdown dimension the chart uses: `Age` or `Sex`. |
| `vis_title` | Human-readable description of what the numbers mean (contains the population and metric). |
| `vis_type` | Chart type (`bargraph`, …). |
| `grouping`, `group` | Secondary grouping labels (often blank). |
| `x_axis_label`, `y_axis_label` | Axis captions (e.g. `Sex` / `Percentage (%)`). |
| `x_axis_values` | The category labels — a list (e.g. `Males`, `Females`). |
| `y_axis_values` | The measured values aligned to `x_axis_values`. |
| `confidence_interval_level` | e.g. `95%`. |
| `confidence_interval_low`, `confidence_interval_high` | CI bounds aligned to `x_axis_values`. |
| `warning` | Data caveat text, if any. |

**Target tidy shape after cleaning:**
`indicator | vis_title | breakdown (Age/Sex) | group | value | ci_low | ci_high | warning`

---

## D. `cihi_children_youth` — CIHI workbook (hidden data sheets only)

Use sheets **`Table8DATA_to hide`** and **`Table13DATA_to hide`**. Real headers are on the
**second row**; row 1 is a title.

| Column | Description | Values |
|---|---|---|
| `Fiscal year` | Reporting year | `2018–2019` … `2023–2024` |
| `Diagnosis category` | Mental-disorder grouping | `Neurocognitive disorders`, `Substance-related disorders`, `Anxiety disorders`, `Mood disorders`, `Schizophrenic / psychotic disorders`, `Selected disorders usually diagnosed in childhood`, `Other`, `Any mental disorder` (confirm full list on parse) |
| `Sex` | | `Female`, `Male`, `Total` |
| `Age group: 5–9 years – Rate` / `95% CI` | Rate per 100,000 and CI string (`"lo–hi"`) | numeric / `"142–158"` |
| `Age group: 10–14 years – Rate` / `95% CI` | " | " |
| `Age group: 15–17 years – Rate` / `95% CI` | " | " |

- `Table8DATA_to hide` = emergency-department visits per 100,000.
- `Table13DATA_to hide` = hospitalisations per 100,000.
- `n/r` = not reported (suppressed). Split each `95% CI` string into `ci_low` / `ci_high`.

---

## E. `mhacs_2022_pumf` — MHACS 2022 Public Use Microdata

**602 numeric-coded columns.** Full definitions: `2022_MHACS_PUMF_Data_dictionary.pdf` and
`2022_MHACS_PUMF_Derived_Variables.pdf` (in `data/raw/Mental Health-Canada-Stat/CSV/Doc/EN/`).

### Missing-value / non-response codes (apply as NaN before analysis)
| Field width | "Valid skip" | "Don't know" | "Refusal" | "Not stated" |
|---|---|---|---|---|
| 1-digit | 6 | 7 | 8 | 9 |
| 2-digit | 96 | 97 | 98 | 99 |
| 3-digit | 996 | 997 | 998 | 999 |
| 1-decimal | 99.6 | 99.7 | 99.8 | 99.9 |

*(Confirm exact codes per variable against the PDF — some scales legitimately use 6–9.)*

### Priority variables — TODO: confirm every label & category against the PUMF PDF

| Variable | Block | Working meaning | Notes |
|---|---|---|---|
| `PUMFID` | ID | Respondent identifier | not for analysis |
| `WTS_M` | weight | Survey (person) weight | **required** for population estimates |
| `GENDER` | demo | Gender | 1 = Men+, 2 = Women+, 9 = not stated |
| `DHHGAGE` | demo | Age group (grouped) | 1–8 bands · TODO map |
| `GEODVPSZ` | demo | Population centre size | 1–4 (rural → large urban) · TODO map |
| `DHHGMS` | demo | Marital status (grouped) | TODO map |
| `EDU_05` | demo | Highest education | 1–7, 99 = not stated · TODO map |
| `INCDVHH` | income | Household income decile/group | 1–15 · TODO map (deciles + extras) |
| `INCDVP19`, `INCDVP20` | income | Derived income position | TODO |
| `GEN_01` | general | Self-rated general health | 1 = excellent … 5 = poor; 7/8 = DK/refusal |
| `GENDHDI` | general | Derived self-rated health index | 0–4, 9 = not stated |
| `GENGSWL` | general | Satisfaction with life | TODO scale |
| `SCRDDEP` | screen | Depression screen positive | 1 = yes, 2 = no, 9 = not stated |
| `SCRDGAD` | screen | Generalized anxiety screen positive | 1/2/9 |
| `SCRDMIA` | screen | (mania/bipolar screen?) | TODO confirm |
| `SCRDSOP` | screen | Social phobia screen positive | 1/2/9 |
| `SCRDMEN` | screen | Any positive mental-health screen (derived) | TODO |
| `PMHDCLA` | positive MH | Positive mental health classification | 1 = flourishing … 3 …; 9 = not stated |
| `SUI_01` | suicidality | Ever seriously thought about suicide | 1 = yes, 2 = no, 6–9 = skip/DK/ref/NS |
| `SUI_02` | suicidality | Ever made a suicide plan | 1/2/6–9 |
| `SUI_03` | suicidality | Ever attempted suicide | 1/2/6–9 |
| `DEP_*` | depression | MDE symptom / diagnosis module | TODO — `DEPDDPS` derived depression scale |
| `GAD_*` | anxiety | GAD module | TODO — `GADDGDS` derived |
| `MIA_*` | mania | Mania/bipolar module | TODO |
| `DISDK6` | distress | Kessler K6 psychological-distress score | 0–24 (higher = more distress) · TODO confirm range |
| `AUD_*` | alcohol | Alcohol use disorder module | TODO — `AUDDL`/`AUDDY` derived life/12-mo |
| `SUD_*` | drugs | Substance use disorder module | TODO |
| `SMKDSTY` | smoking | Smoking status (derived) | TODO map |
| `SPS_01`–`SPS_10`, `SPSD*` | support | Social Provisions Scale items + derived subscales | higher = more support · TODO scoring |
| `MHPFL`, `MHPFY` | services | Ever / past-year consulted a mental-health professional | TODO |
| `PNCDNEED` | services | Perceived need for mental-health care (derived) | TODO categories |
| `MHE_05A/B`, `MHE_06*` | services | Unmet need / barriers to care | TODO |
| `WSTD*` | work | Derived work-stress indices | TODO |
| `SDCFIMM` | demo | Immigrant status | TODO |
| `SORLGBTS` | demo | Sexual orientation (grouped) | TODO |

> Full 602-column list with dtype, % missing and sample codes:
> `data/processed/01_column_profiles.csv` → filter `dataset = mhacs_2022_pumf`.

---

## F. `mental_health_dataset` — Kaggle synthetic (sandbox only)

| Column | Type | Description |
|---|---|---|
| `age` | int | Age in years |
| `gender` | string | `Male` / `Female` / `Other` |
| `employment_status` | string | `Employed` / `Unemployed` / `Self-employed` / `Student` |
| `work_environment` | string | `On-site` / `Remote` / `Hybrid` |
| `mental_health_history` | string | `Yes` / `No` — prior mental-health condition |
| `seeks_treatment` | string | `Yes` / `No` — target for a classification demo |
| `stress_level` | int | 1–10 self-report |
| `sleep_hours` | float | Average hours per night |
| `physical_activity_days` | int | Active days per week (0–7) |
| `depression_score` | int | Synthetic scale (~0–30) |
| `anxiety_score` | int | Synthetic scale (~0–20) |
| `social_support_score` | int | Synthetic scale (~0–100) |
| `productivity_score` | float | Synthetic scale |
| `mental_health_risk` | string | `Low` / `Medium` / `High` — synthetic target label |

Synthetic and global — **not** a source of real findings.

---

## Change log
- 2026-08-27 — initial draft (Samir), generated alongside `01_data_understanding.ipynb`.
