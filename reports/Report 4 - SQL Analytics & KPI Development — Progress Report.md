# SQL Analytics & KPI Development — Progress Report

## Overview

The SQL analytics notebook has been developed to provide a structured analysis layer between the cleaned datasets and the final dashboard.

The notebook is designed to work **even before the real processed datasets are available**. It automatically creates a small sample dataset using the expected schema, allowing all SQL queries to run successfully and demonstrating the expected output structure.

Once the team places the real processed files in `data/processed/`, the notebook will automatically detect and use them without requiring changes to the SQL queries.

---

## 1. Handling "No Data Yet"

The notebook expects the following processed datasets:

- `data/processed/mh_long.csv`
- `data/processed/cihi_children.csv`

Because these files are not available yet, the notebook automatically generates a small sample dataset matching the expected schema.

The sample data allows us to:

- Test every SQL query.
- Validate the expected output structure.
- Develop dashboard KPIs before the real data is finalized.
- Identify SQL or schema issues early.
- Demonstrate the complete analytical workflow to the team.

A `USING_SAMPLE` flag and `data_source` column clearly identify sample results as:

**`SAMPLE (not real)`**

This prevents sample results from being confused with actual mental-health statistics.

When the real files are added to `data/processed/`, the notebook will automatically load them instead.

---

# 2. Data Contract

The opening section documents the expected output from `02_data_cleaning.ipynb`.

The primary `mh_long` dataset should contain:

```text
source
geo
geo_level
period
year
age_group
sex
indicator
measure
value
ci_low
ci_high
quality_flag
```

The `cihi_children` dataset is expected to contain the cleaned CIHI children/youth hospitalization and emergency-department information required for the youth analysis.

This creates a clear **data contract between the cleaning and SQL stages**.

If the team's actual column names differ from the expected names, the notebook provides a `COLS` mapping so the team can update the column references in one place rather than modifying every SQL query.

---

# 3. SQL Analysis

A total of **27 business-oriented SQL questions** have been implemented.

Each question has its own notebook cell and a clear business-question heading, making it easier for team members and reviewers to understand why each query exists.

## Section 3 — Coverage & Data Quality

**Q1–Q5**

These queries establish whether the dataset is suitable for analysis:

- Row counts
- Time-period coverage
- Geographic coverage
- Suppression/quality rates
- Duplicate-grain checks

These queries provide the initial **data-quality and coverage sanity checks**.

---

## Section 4 — Current State

**Q6–Q9**

This section identifies the current mental-health situation using the latest available data.

Questions include:

- What are the national headline numbers?
- Which provinces have the highest and lowest burden?
- How do suicidal-thought indicators differ by sex?
- How does each province compare with the Canadian average?

These outputs support dashboard KPIs focused on the **highest and lowest current burden**.

---

## Section 5 — Geography

**Q10–Q12**

The geographic analysis examines differences across Canadian jurisdictions.

Questions include:

- What is the provincial spread?
- Which province performs best/worst for each indicator?
- How do territories compare with provinces?

The main dashboard KPI from this section is the:

**Provincial Spread**

This helps communicate geographic variation rather than relying only on the national average.

---

## Section 6 — Demographics

**Q13–Q15**

This section investigates demographic differences.

Questions include:

- What is the female–male gap?
- How does the sex gap vary by province?
- Is there an age gradient in the indicators?

The primary KPI is the:

**Sex Gap**

This provides a way to highlight demographic differences in mental-health indicators.

---

## Section 7 — Change Over Time

**Q16–Q20**

The notebook includes several time-series analyses:

- First-to-latest change
- Period-over-period change using `LAG`
- Percentage change relative to baseline
- Number of provinces where the situation worsened
- Biggest positive and negative movers

The main KPIs from this section are:

- **Change over time**
- **Number of worsening provinces**

This section is particularly important for the dashboard because it moves beyond a static snapshot and shows how indicators are changing.

---

## Section 8 — Cross-Indicator Analysis

**Q21–Q23**

This section examines relationships between different mental-health indicators.

Questions include:

- What is the help-seeking gap?
- How does stress relate to poor mental health?
- How does sense of belonging relate to poor mental health?

The primary KPI is the:

**Help-Seeking Ratio**

These analyses help connect individual indicators rather than treating each metric independently.

---

## Section 9 — Children & Youth

**Q24–Q27**

The final analytical section focuses specifically on children and youth.

Questions include:

- How are emergency-department visits changing over time?
- How do hospitalizations differ by diagnosis and sex?
- Which diagnosis is growing the fastest?
- Which age group has the highest rate?

The primary dashboard KPI is the:

**Youth Rate**

This creates a dedicated analytical component for understanding mental-health outcomes among younger populations.

---

# 4. KPI Development

The notebook brings the analytical work together in Section 10.

A total of **10 dashboard KPIs** are calculated and assembled into:

```text
04_kpi_summary.csv
```

This file provides a clean output layer for the dashboard.

The goal is to keep the dashboard focused on validated, reproducible metrics rather than embedding complex SQL calculations directly into the visualization layer.

The SQL notebook therefore acts as the analytical bridge:

```text
Cleaned Data
     ↓
SQL Analysis
     ↓
Business Questions
     ↓
KPI Calculations
     ↓
04_kpi_summary.csv
     ↓
Dashboard
```

---

# 5. SQL Techniques Demonstrated

The notebook intentionally uses SQL techniques that demonstrate practical data-analyst skills.

These include:

- Common Table Expressions (CTEs)
- `RANK()`
- `ROW_NUMBER()`
- `LAG()`
- `FIRST_VALUE()`
- Conditional aggregation
- Self-joins
- Grouping and aggregation
- Filtering and comparison logic
- Time-period analysis
- Geographic comparisons

The queries are structured around **business questions**, rather than simply demonstrating SQL syntax.

---

# 6. Team Adjustment Notes

Section 11 contains guidance for adapting the notebook once the real datasets are available.

The team may need to adjust:

- Indicator names/strings
- Column mappings
- Age-group labels
- Geographic labels
- Sex/category values
- CIHI diagnosis labels

The intention is to keep these adjustments centralized so that the core SQL analysis remains stable.

---

# 7. Current Status

### Completed

- SQL notebook structure
- Data contract
- Automatic sample-data fallback
- SQLite in-memory database
- 27 business questions
- Coverage and quality checks
- Current-state analysis
- Geographic analysis
- Demographic analysis
- Time-series analysis
- Cross-indicator analysis
- Children/youth analysis
- 10 KPI calculations
- `04_kpi_summary.csv` output
- Team adjustment documentation

### Pending

The main remaining step is to replace the generated sample data with the finalized processed datasets:

```text
data/processed/mh_long.csv
data/processed/cihi_children.csv
```

Once those files are available, the notebook can be re-run to validate the SQL logic against the real data.

---

## Key Takeaways

1. The SQL analytics layer is now structured and testable before the real data is available.
2. Sample data allows the complete pipeline to run without blocking development.
3. Sample outputs are explicitly labelled to prevent accidental interpretation as real findings.
4. A formal data contract has been established between the cleaning and SQL stages.
5. **27 business questions** have been translated into SQL analyses.
6. The notebook demonstrates advanced SQL techniques including window functions, CTEs, conditional aggregation, and self-joins.
7. **10 KPIs** have been assembled into `04_kpi_summary.csv` for dashboard consumption.
8. The notebook is designed to transition to the real datasets with minimal changes.
9. The next major validation step is running the notebook against the finalized `data/processed/` files.