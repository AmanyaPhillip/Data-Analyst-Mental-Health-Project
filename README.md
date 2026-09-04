# 🔍 Mental Health Analytics — Canada

End-to-end data-analytics project covering the full lifecycle: dataset selection → cleaning →
EDA → KPIs → SQL analysis → visualization → interactive dashboard → automation → insights →
presentation. Built collaboratively as a Junior Data Analyst portfolio piece.

> ### ⚖️ Legal & Medical Disclaimer
> This repository is developed strictly for educational, analytical, and portfolio purposes.
> The code, analyses, and dashboards **do not constitute medical, diagnostic, or clinical advice**.
> All analysis is at the **population level** — it never identifies, scores, or predicts individuals.
> The contributors make no warranties about the accuracy or completeness of the underlying data.
> Use is at your own risk. Licensed MIT (see [`LICENSE`](LICENSE)).
>
> If you or someone you know is in distress, call or text the **9-8-8 Suicide Crisis Helpline** (Canada, 24/7).

---

## Business problem

*What patterns and factors are associated with mental-health challenges across Canadian
populations, and how can data help identify where mental-health support may be most needed?*

Framed as **population-level prevention intelligence**, not individual prediction. Relationships
are reported as *associated with*, never *causes*. See [`docs/ethics_and_limitations.md`](docs/ethics_and_limitations.md).

---

## Learning objectives

End-to-end analytics workflow · data cleaning & transformation · exploratory data analysis ·
KPI design · SQL querying · Python analytics · data visualization · Power BI dashboards ·
automation · Git/GitHub collaboration · communicating findings to a non-technical audience.

---

## Datasets

All real, Canadian, publicly licensed. Raw files are kept **local** (`data/raw/`, gitignored) —
ask a teammate or re-download from the source. Full detail: [`docs/data_inventory.md`](docs/data_inventory.md).

| Dataset | Source | Grain | Use |
|---|---|---|---|
| `perceived_mh_annual` | StatCan 13-10-0972 (CCHS) | province × 2-yr cycle × sex | core KPIs, trend |
| `suicidal_thoughts` | StatCan 13-10-0465 subset | province × 2015/2019 × age × sex | ideation, help-seeking |
| `stress_coping` | StatCan 13-10-0802 | province × 2016/2019 × age × sex | sources of stress |
| `perceived_health_quarterly` | StatCan 45-10-0081 | province × quarter × gender | *general* health context |
| `cchs_mh_disorders` | StatCan 13-10-0465 (CCHS-MH) | province × 2002/2012/2022 | disorder prevalence, comparison |
| `cihi_mh_services` | CIHI / PHAC Health Infobase | indicator × breakdown | service use |
| `cihi_children_youth` | CIHI — Care for Children & Youth With Mental Disorders | fiscal year × diagnosis × age × sex | youth ED / hospitalisation |
| `mhacs_2022_pumf` | StatCan MHACS 2022 PUMF (microdata) | 9,861 respondents × 602 vars | individual-level factor analysis |
| `mental_health_dataset` | Kaggle (synthetic) | 10,000 rows | ML-workflow sandbox only — excluded from findings |

**Two analysis tracks** (they do not join): aggregated StatCan/CIHI → KPIs + dashboard;
MHACS microdata → regression / feature-importance.

---

## Repository structure

```
notebooks/
  01_data_understanding.ipynb   raw profiling → data/processed/01_*
  02_data_cleaning.ipynb        raw → data/processed/02_cleaned/  (+ §4·FIX cell)
  03_eda.ipynb                  exploratory analysis, all 8 datasets
  04_analysis.ipynb             SQL analysis + KPI development (SQLite, real data)
  05_ml_synthetic_sandbox.ipynb ML workflow demo on the synthetic set (+ KPIs mirrored from real data)
  06_trend_direction_model.ipynb real-data model: does a reported % rise or fall next cycle
data/
  raw/                          original downloads — LOCAL ONLY (gitignored)
  processed/02_cleaned/         cleaned analytical tables
  processed/mh_long.csv         unified long table for 04/06 (all StatCan sources)
  synthetic_kaggle/             ML sandbox input
docs/
  data_inventory.md             every dataset: scope, coverage, limits
  data_dictionary.md            column definitions + permitted values
  cleaning_log.md               what the cleaning pipeline does
  data_cleaning_checklist.md    reusable cleaning checklist + function reference
  ethics_and_limitations.md     commitments + dataset limitations
reports/                        point-in-time deliverables (Report 1, 2, 3…)
models/                         trained models + metrics (notebook 05)
dashboard/  automation/  presentation/   later pipeline stages
```

---

## Pipeline status

| # | Step | Status |
|---|---|---|
| 1 | Dataset selection | ✅ |
| 2 | Data cleaning & preparation | ✅ — StatCan `clean_statcan_long` fix pending team sync (`02_data_cleaning.ipynb` §4·FIX) |
| 3 | Exploratory Data Analysis | 🔄 substantial — all 8 datasets covered in `03_eda.ipynb` |
| 4 | KPI definition | 🔄 10 KPIs computed on real data → `data/processed/04_kpi_summary.csv` |
| 5 | SQL analysis | ✅ runs on real `data/processed/mh_long.csv` / `cihi_children.csv` |
| 6 | Data visualization | ⬜ |
| 7 | Interactive dashboard | ⬜ |
| 8 | Automation | ⬜ |
| 9 | Insights & recommendations | ⬜ |
| 10 | Final presentation | ⬜ |
| — | ML sandbox (side track) | ✅ `05_ml_synthetic_sandbox.ipynb` |
| — | Trend-direction model (side track) | ✅ `06_trend_direction_model.ipynb` — real-data Up/Down classifier |

---

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Run a notebook end to end and regenerate its outputs:

```bash
jupyter nbconvert --to notebook --execute --inplace notebooks/02_data_cleaning.ipynb
```

> Always **Kernel → Restart & Run All** before producing pipeline output — see
> `reports/Report 3 - Data Cleaning and Bug Fixes.md` §9.

---

## Team

| Member | Focus | Cleaning file(s) reviewed |
|---|---|---|
| Phillip | Scoping, wrangling, EDA, KPI | `cchs_mh_disorders` |
| Fatima | EDA, Power BI | data-cleaning findings report |
| Misa | Power BI, KPI definition | `suicidal_thoughts`, `perceived_mh_annual` |
| Danny | Data wrangling | `mhacs_2022_pumf` |
| Samir | Documentation, MHACS track | `stress_coping`, `cihi_mh_services` |
| Jyothi | Data wrangling  | `perceived_health_quarterly` |
| Rebal | — | `cihi_children_youth` |

Everyone should be able to explain every phase of the pipeline, not only their own.

### GitHub workflow

Fetch → Pull → Edit → Commit → Push. Pull before editing. Datasets stay local until the
team agrees a storage approach.
