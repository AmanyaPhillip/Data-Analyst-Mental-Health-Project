# Ethics & Limitations

**Project:** Data Analyst – Mental Health (Canada)
**Status:** DRAFT · last updated 2026-08-27 · owner: Samir

This project analyses mental-health and suicide-related data. This document records the
ethical commitments we work under and the limitations that must be stated wherever we
present results (report, dashboard, presentation).

---

## 1. Ethical commitments

### 1.1 Population-level only — never individual
- All datasets are **aggregate statistics** or an **anonymised public-use survey file**. No record identifies a person.
- We do **not** attempt to predict, score, or flag individuals for suicide or mental-illness risk. Any model built on the MHACS microdata or the synthetic set is used only to identify **population-level factors and patterns**.
- Framing we use: *"this group / region shows a higher burden and may warrant further attention and prevention resources"* — **not** *"this type of person is at risk."*

### 1.2 Association, not causation
- This is observational data. We describe relationships as **"associated with"**, **"correlated with"**, or **"higher/lower burden among"** — never "causes", "leads to", or "drives".
- Ecological data (province-year) carries **ecological-fallacy risk**: a relationship at the province level does not imply the same relationship at the person level. State this wherever province-level correlations appear.

### 1.3 Responsible language and presentation
- Use "died by suicide" / "suicide death", not "committed suicide".
- Do not present method, location, or any content that could function as instruction or that sensationalises suicide (follows established safe-reporting guidance).
- Include help-seeking context where appropriate: in Canada, the **9-8-8 Suicide Crisis Helpline** (call or text, 24/7).
- Avoid charts that could imply a "target" or normalise rising numbers; pair rate charts with clear caveats.

### 1.4 Data handling
- Raw data stays in `data/raw/` (local, gitignored). Only aggregated / derived outputs are committed.
- No attempt to re-identify respondents or to link the MHACS PUMF to any other individual-level source (also prohibited by its licence).
- Sources are public and openly licensed (StatCan, CIHI, PHAC, Our World in Data, Kaggle). Cite each one in the report.

---

## 2. Dataset limitations

### 2.1 Suicide and mental illness are under-measured
- Suicide deaths are **undercounted** in many jurisdictions (misclassification as "undetermined intent", coroner variation).
- Mental illness is **under-reported** in surveys due to stigma and lack of diagnosis; self-report over/under-states true prevalence in ways that differ by group.
- We have **suicidal ideation** (self-reported thoughts), not suicide **mortality**, in the current dataset set. A statement about "suicide" must specify which.

### 2.2 Time coverage is thin and uneven
- Most tables have only 2–3 far-apart cycles (2015/2019, 2016/2019, 2002/2012/2022). A continuous national trend line is **not supported**.
- The one multi-year quarterly table measures *general* perceived health, not mental health.
- Conclusions about "change over time" are limited to **cycle-to-cycle comparisons** unless a longer series is added via the StatCan API.

### 2.3 COVID-19 distortion
- The 2019 → 2021/22 → 2023/24 window spans the pandemic. Changes in this period reflect both real shifts and **survey-mode / collection changes** (CCHS methodology changed in 2020–21). Cross-period comparisons must flag this.

### 2.4 Suppressed and unreliable cells
- StatCan suppresses small cells: `x` (confidentiality), `F` (too unreliable), `E` (use with caution), `..` (not available). Suppression is **not random** — it disproportionately removes small provinces/territories and small demographic groups, biasing any national picture toward larger populations.
- Affected most: `cchs_mh_disorders` (~38% of values), `stress_coping` (~19%).
- We **do not impute** suppressed values. Charts show only publishable cells and note where data is missing.

### 2.5 Coverage gaps
- CCHS excludes people living **on First Nations reserves**, in **institutions**, full-time **military**, and some remote areas — so Indigenous and institutionalised populations (both with elevated mental-health burden) are **under-represented**.
- Territories are missing or partial in several tables ("Canada excluding territories").
- CIHI hospital/ED data covers only people who **reached a service** — it measures service contact, not community prevalence, and varies with local service availability.

### 2.6 Comparability across sources
- StatCan, CIHI and PHAC use different populations, age bands, geographies, and definitions. Numbers from different sources are **not directly comparable** and are not combined into a single metric without explicit reconciliation.
- Region rollups ("Atlantic", "Prairies") and province lists differ between tables.

### 2.7 MHACS microdata (Track B)
- Cross-sectional (2022 only) — associations are point-in-time, no direction of effect.
- Public-use file is **coarsened** (grouped ages, capped incomes, broad geography) to protect privacy — reduces precision.
- Requires **survey weights** (`WTS_M`) for valid population estimates and **bootstrap weights** for correct standard errors; unweighted analysis is biased.
- Non-response and "not stated" codes are informative missingness (they correlate with the outcomes).

### 2.8 Synthetic Kaggle dataset (ML sandbox)
- **Entirely synthetic and global.** It reflects the generator's assumptions, not reality.
- Used only to demonstrate the ML workflow. **No result from it appears in the findings or recommendations.**

---

## 3. What we will and won't claim

| We can say | We won't say |
|---|---|
| "In 2022, reported suicidal ideation was higher among X than Y." | "X causes suicidal ideation." |
| "Provinces with higher unemployment tended to show higher burden in this period." | "Unemployment drives suicide." |
| "This region's indicator worsened between cycles and may warrant attention." | "People in this region are at risk." |
| "The data cannot tell us Z because of suppression / coverage / timing." | (silently omitting the limitation) |

---

## 4. Review checklist before publishing any output
- [ ] Every trend/comparison notes its time limitation and the COVID caveat.
- [ ] Suppressed data is shown as missing, not zero or interpolated.
- [ ] Language is "associated with", not causal.
- [ ] Suicide content follows safe-reporting guidance; 9-8-8 helpline noted where relevant.
- [ ] Coverage gaps (Indigenous, institutional, territories) stated.
- [ ] Sources cited; synthetic data clearly labelled and excluded from conclusions.

---

## Change log
- 2026-08-27 — initial draft (Samir).
