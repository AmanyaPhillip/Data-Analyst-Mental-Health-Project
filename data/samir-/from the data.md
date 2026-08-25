Think of your data model like this:

                    SUICIDE OUTCOMES
                          │
        ┌─────────────────┼──────────────────┐
        │                 │                  │
     WHO/IHME          Canada/CDC       Other sources
        │                 │                  │
        ▼                 ▼                  ▼
   Deaths/rates       Demographics       Mental health
   Age                Income             Depression
   Sex                Employment         Anxiety
   Country            Education          Substance use
   Year               Geography          Healthcare access


   7. Potential risk-factor datasets

I would search for data around:

Economic
unemployment rate
poverty
income
inflation
housing affordability
homelessness
Social
social isolation
marital status
education
employment
population density
Mental health
depression
anxiety
psychological distress
mental-health service utilization
substance use
Healthcare
physicians per population
mental-health professionals
healthcare accessibility
treatment availability
Demographics
age
sex
urban/rural
geographic region

The important thing is not to assume these factors cause suicide. Your analysis should use language such as "associated with," "correlated with," or "higher/lower suicide burden."

8. Your project could have 5 data layers

I would divide the team's work like this:

Layer 1 — Suicide

WHO Mortality Database

Country
Year
Age
Sex
ICD code
Deaths
Population
Suicide rate
Layer 2 — Mental health
Country
Year
Depression
Anxiety
Mental-health burden
Substance-use indicators
Layer 3 — Socioeconomic
Country
Year
Unemployment
GDP
Income
Poverty
Education
Layer 4 — Demographic
Country
Year
Age
Sex
Population
Urbanization
Layer 5 — Healthcare
Country
Year
Healthcare access
Mental-health services
Healthcare workers
Treatment indicators

Then create a common key:

Country + Year

and join the datasets.


9. Dashboard structure I recommend

Don't make one giant dashboard.

Make 4 pages.

Page 1 — Global Overview

KPIs:

Total Suicide Deaths
Global Suicide Rate
Highest-Risk Region
Lowest-Risk Region
Year-over-Year Change

Visuals:

world map
trend line
country ranking
male vs female
age distribution
Page 2 — Who is most affected?

Filters:

Country
Year
Sex
Age
Region

Visuals:

suicide rate by age
male vs female
age × sex heatmap
demographic comparison
Page 3 — Risk Factors

This is where your project becomes more interesting.

Example:

Suicide Rate
      ↓
   Compare
      ↓
Unemployment
Income
Mental Health
Substance Use
Healthcare Access

You can create:

correlation matrix
scatter plots
regression analysis
trend comparisons

But clearly label these as associations, not causal relationships.

Page 4 — Prevention Insights

Instead of saying:

"This person is at risk."

Say:

"This region has experienced a sustained increase in suicide mortality and may warrant further investigation and prevention-resource assessment."

Then show:

Region
    ↓
Trend
    ↓
Demographic pattern
    ↓
Associated factors
    ↓
Potential prevention priority

This is much more appropriate for public-health analytics.

10. Add a data-engineering component

Since you want scraping + implementation, don't just download CSVs once.

Build a pipeline:

WHO / IHME / Statistics Canada / CDC
                ↓
           Data ingestion
                ↓
        Raw data storage
                ↓
          Data cleaning
                ↓
          Transformation
                ↓
           PostgreSQL
                ↓
             Python
                ↓
              SQL
                ↓
           Dashboard

For example:

/data
   /raw
      who_mortality.csv
      ihme_gbd.csv
      statcan.csv

   /processed
      suicide_clean.csv
      mental_health_clean.csv
      socioeconomic_clean.csv

Then automate:

Python
   ↓
Download/API/scrape
   ↓
Validate
   ↓
Clean
   ↓
Transform
   ↓
Database
   ↓
Dashboard refresh
11. One particularly good analysis

I would make this one of your team's main questions:

"What demographic and socioeconomic patterns are associated with higher suicide mortality, and how have these patterns changed over time?"

Then you can demonstrate almost everything your JDA program is teaching:

Python

Pandas
NumPy
data cleaning
EDA
statistical analysis

SQL

joins
aggregations
window functions
CTEs
ranking

Visualization

Power BI/Tableau
maps
heatmaps
trends
scatter plots

Automation

Python ETL
scheduled data collection
database refresh

Advanced

regression
clustering
forecasting
anomaly detection
12. One warning about your "prevention" goal

Your project can absolutely be about suicide prevention, but I would frame it as a population-level prevention intelligence dashboard, not a system that predicts whether an individual will commit suicide.

For example:

❌ "Predict whether John will commit suicide."

Much harder to ethically justify and requires sensitive individual-level clinical data.

✅ "Identify regions and demographic groups experiencing elevated suicide mortality and changing trends to support prevention planning."

That's a very strong Data Analyst / Public Health Analytics project.

And there is an important data-quality issue: suicide is underreported in many countries, and WHO, IHME and national sources can produce different estimates. That limitation itself should be prominently documented in your project.

My recommended starting stack

Start with these 4:

WHO Mortality Database → raw suicide mortality
IHME GBD → modeled suicide + broader health factors
Statistics Canada → Canadian socioeconomic/demographic data
Our World in Data → easy-to-use processed datasets and validation

Then add CDC if your team wants a U.S. case study.

If you build it this way, your project isn't just "a suicide dashboard." It becomes a complete ETL → SQL → EDA → statistical analysis → dashboard → automation portfolio project, which is much stronger for a Junior Data Analyst portfolio.

