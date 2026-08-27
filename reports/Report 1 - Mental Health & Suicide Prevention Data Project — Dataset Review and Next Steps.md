# Mental Health & Suicide Prevention Data Project
## Dataset Review, Scope, and Next Steps

### 1. Project Context

Our team is developing a Canadian mental-health analytics project with a focus on understanding mental-health burden, suicidal ideation, and access to mental-health services.

Because suicide is a serious and sensitive subject, we need to be careful about how we define the purpose of the project. The goal should **not** be to build a system that predicts whether an individual will die by suicide.

Instead, our project will focus on using real Canadian data to identify **population-level trends, groups experiencing higher levels of mental-health burden, and areas where prevention resources may be needed**.

The project can therefore support prevention planning and public-health analysis while avoiding individual-level predictions.

---
# 2. Dataset Inventory

| Owner | Dataset | Geographic Scope | Data Type | Fit |
|---|---|---|---|---|
| Misa | Statistics Canada 13-10-0972 – Perceived Mental Health | Canada, by province/age/sex | Aggregated | ✅ Strong |
| Fatima | Statistics Canada mental-health indicators, suicidal thoughts, stress, perceived health | Canada | Aggregated | ✅ Strong |
| Fatima | CIHI Health Infobase – Mental Illness Services | Canada | Aggregated/chart-export | ✅ Good |
| Fatima | Children/youth with mental disorders – CIHI | Canada | Aggregated | ✅ Good |
| Samir | MHACS 2022 Public Use Microdata | Canada | Individual-level survey | ✅ Strong for factor analysis |
| Samir | WHO Mortality Database | Global | Raw | ❌ Outside project scope |
| Samir | OWID population projections | Global | Reference | ⚠️ Possible denominator only |
| Danny | Kaggle Mental Health Dataset | Global/synthetic | Individual-level | ❌ Not suitable for primary analysis |

---

# 3. What We Learned About the Data

The most important finding is that our datasets have **different structures and purposes**.

### Track A — Aggregated Canadian Data

The Statistics Canada and CIHI datasets are already summarized by dimensions such as:

- Province
- Year
- Age
- Sex/gender
- Mental-health indicator
- Service use

These datasets are excellent for:

- Dashboards
- KPIs
- Geographic comparisons
- Time-series trends
- Population-level comparisons
- Identifying groups or regions with increasing burden

However, they are limited when answering questions such as:

> “Why is one person experiencing poorer mental health than another?”

Because the data has already been aggregated, individual-level relationships cannot be investigated directly.

### Track B — MHACS Microdata

The 2022 Mental Health and Access to Care Survey (MHACS) is different.

It contains approximately 9,800 individual survey records and more than 600 coded variables.

This dataset can potentially support analysis of relationships between mental health and factors such as:

- Demographics
- Social characteristics
- Mental-health indicators
- Access to services
- Other survey variables

However, it is significantly more complex. We need to use the accompanying data dictionary to correctly interpret the coded variables.

Therefore, MHACS is potentially our strongest dataset for **factor analysis**, while the aggregated Canadian datasets are stronger for **dashboard and trend analysis**.

---

# 4. Important Scope Correction: Suicide

One important issue was identified during our dataset review.

The current datasets do **not necessarily provide the information required to calculate an actual suicide mortality rate**.

Some datasets contain information about:

- Suicidal thoughts
- Mental-health status
- Mental-health services
- Perceived health

These should not automatically be described as suicide deaths.

If the project requires actual suicide mortality, we need a Canadian mortality dataset containing deaths due to intentional self-harm.

Therefore, we should distinguish between:

**Suicide mortality**

Actual deaths caused by suicide.

**Suicidal ideation**

Self-reported thoughts about suicide.

**Mental-health burden**

Measures such as perceived mental health, mental disorders, stress, and related indicators.

Keeping these concepts separate will make the analysis more accurate and ethically responsible.

---

# 5. What Aggregated Data Can Actually Do

Initially, the project idea was close to:

> “Predict suicide.”

After reviewing the available data, this needs to be refined.

Aggregated data can realistically support:

### A. Trend Analysis

Analyze how mental-health or suicidal-ideation indicators change over time.

For example:

> How has the reported mental-health burden changed in Canada over the last five years?

### B. Geographic Analysis

Compare provinces and territories.

For example:

> Which provinces show the highest or fastest-growing mental-health burden?

### C. Demographic Analysis

Compare available age and sex/gender groups.

For example:

> Which demographic groups report poorer mental health or higher suicidal ideation?

### D. Population-Level Forecasting

If sufficient historical data is available, we could forecast population-level rates for the next 1–2 years.

The objective would be to identify:

> Regions or population groups showing a worsening trajectory.

This is **not individual suicide prediction**.

### E. Ecological Regression

If compatible province-year data is available, we could investigate relationships between population-level mental-health outcomes and variables such as:

- Employment
- Income
- Demographics
- Access to services
- Other socioeconomic indicators

The results would describe **population-level associations**, not individual causation.

---

# 6. How the Project Can Help People

Rather than building a system that attempts to predict whether a specific person will commit suicide, the project can become a:

## Prevention Resource Planning Dashboard

The dashboard could help answer:

> “Where is the mental-health burden increasing, and where might additional prevention resources be needed?”

Possible dashboard features include:

- Canadian map
- Province-level trends
- Age-group comparisons
- Sex/gender comparisons
- Mental-health indicators
- Suicidal-ideation indicators
- Mental-health service utilization
- Changes over time
- Identification of worsening population-level trends

The dashboard should clearly communicate that these indicators are intended for **population-level analysis and prevention planning**, not individual risk prediction.

---

# 7. Questions We Need to Answer

Before defining the final KPIs, the team needs to agree on specific analytical questions.

The following questions are proposed:

### Question 1
**How has mental health in Canada changed over the last five years, and how does this differ by province, age, and sex/gender?**

### Question 2
**Which demographic or geographic groups report the highest mental-health burden or suicidal ideation?**

### Question 3
**Are regions with higher mental-health burden also showing higher use of mental-health services?**

### Question 4
**Which provinces or population groups show a worsening trend that could indicate a need for additional prevention resources?**

These questions give us a clearer foundation for selecting KPIs and designing the dashboard.

---

# 8. Potential KPIs

Depending on the final questions selected by the team, possible KPIs include:

- Percentage reporting good/very good perceived mental health
- Percentage reporting poor/fair mental health
- Suicidal-ideation rate
- Mental-health service utilization rate
- Percentage reporting unmet mental-health needs
- Change in mental-health indicators over time
- Provincial rate
- Difference between provinces
- Age-group differences
- Sex/gender differences
- Change in service access relative to mental-health burden

The final KPIs should only be selected after the analytical questions and datasets are confirmed.

---

# 9. Dataset Decision

The recommended approach is to keep **two analytical tracks**.

### Track A — Dashboard and Population Trends

Use the Canadian aggregated Statistics Canada and CIHI datasets.

Primary purposes:

- KPIs
- Trends
- Provincial comparisons
- Demographic comparisons
- Dashboard visualizations
- Prevention-resource planning

### Track B — Factors and Associations

Use the MHACS 2022 microdata.

Primary purposes:

- Exploratory analysis
- Correlation analysis where appropriate
- Regression
- Investigation of factors associated with mental-health outcomes
- Potential clustering

The two tracks do not need to be directly joined.

They can answer different questions and come together in the final dashboard/report.

---

# 10. Datasets to Remove From the Primary Analysis

### WHO Mortality Database

The current WHO dataset is global and contains all causes of death. It is too broad for our current Canadian project scope.

It could potentially be useful for future comparative research, but it should not be part of the primary Canadian dashboard.

### OWID Population Dataset

This should only be retained if we need population denominators for calculating rates.

Otherwise, it is not a primary mental-health dataset.

### Synthetic Kaggle Dataset

The Kaggle mental-health dataset should not be used as the primary dataset because it is synthetic and not Canadian.

It can potentially be retained separately as an ML practice dataset, but its results should not be presented as evidence about Canadian mental health.

---

# 11. Data Storage Issue

There is currently a data-management issue that needs to be resolved.

The repository contains large files, including approximately:

- 121 MB
- 35 MB

There are also deleted ZIP files and newly added uncompressed directories.

The project's requirements indicate that large datasets should remain local until the team agrees on a storage strategy.

The team should therefore decide:

1. Which raw datasets are required.
2. Which files should remain local.
3. Which metadata should be committed to GitHub.
4. Whether large datasets require Git LFS or another storage solution.
5. Which processed datasets can safely be committed.

We should avoid unnecessarily committing large raw datasets to the repository.

---

# 12. Documentation Responsibilities

The documentation work should include the following files:

### `docs/data_inventory.md`

Document:

- Dataset name
- Owner
- Source
- Source URL
- Geographic scope
- Time coverage
- Granularity
- Number of rows
- Number of columns
- Missing values
- Main variables
- What the dataset can support
- What it cannot support
- Limitations

### `docs/data_dictionary.md`

Document important variables and explain:

- Variable name
- Description
- Data type
- Possible values
- Coding
- Missing-value definitions
- Dataset source

This is especially important for MHACS because many variables are coded.

### `docs/ethics_and_limitations.md`

Document:

- Suicide as a sensitive subject
- Difference between suicide mortality and suicidal ideation
- Population-level versus individual-level prediction
- Data limitations
- Aggregation limitations
- Correlation versus causation
- Privacy considerations
- Appropriate interpretation of results
- Responsible use of the dashboard

---

# 13. Current Pipeline Status

The initial data pipeline has been established.

The current workflow is:

**`data/raw/` → profiling → `data/processed/`**

The profiling process generates:

### `01_data_inventory.csv`

Contains one row per dataset, including:

- Number of rows
- Number of columns
- Time coverage
- Geography
- Missing-value information
- Notes

### `01_column_profiles.csv`

Contains a catalogue of the available columns, including:

- Column name
- Data type
- Missing percentage
- Number of unique values
- Sample values

### `01_pipeline_check.txt`

Provides a timestamped confirmation that the raw-to-processed pipeline is functioning.

The current notebook files `01`–`04` still need to be developed further for cleaning, EDA, analysis, and visualization.

---

# 14. Immediate Next Steps

The recommended order of work is:

1. **Finalize the analytical questions.**
2. **Confirm whether suicide mortality is required or whether the project focuses on suicidal ideation and mental-health burden.**
3. **Finalize the Canadian datasets.**
4. **Complete `docs/data_inventory.md`.**
5. **Create the data dictionary.**
6. **Create the ethics and limitations document.**
7. **Clean the selected datasets.**
8. **Perform exploratory data analysis.**
9. **Develop KPIs based on the agreed analytical questions.**
10. **Build the interactive dashboard.**
11. **Develop population-level forecasting or regression only if the data supports it.**
12. **Document findings, limitations, and recommendations.**

---

# 15. Final Project Direction

The project should move away from the idea of:

> **“Predict whether someone will commit suicide.”**

and toward:

> **“Use real Canadian mental-health data to identify population-level trends, disparities, suicidal ideation, and service-access gaps that can support suicide-prevention planning.”**

This direction is more realistic given our datasets, more appropriate for a data-analytics project, and more responsible given the sensitivity of suicide-related data.

The project can demonstrate the complete data-analytics workflow:

**Real Canadian Data → Data Cleaning → EDA → Statistical Analysis → KPIs → Dashboard → Trend/Forecast Analysis → Prevention Insights**

The goal is not to predict an individual's future.

The goal is to use data to better understand **where the burden is increasing, which populations are affected, and where prevention resources may be needed.**
