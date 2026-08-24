# Team Roles & Project Milestones

## Core Team & Ownership
| Member | Core Tasks |
| :--- | :--- |
| **Fatima** |  EDA, Power BI |
| **Misa** | Power BI,  |
| **Jyothi** | tasks placeholder |
| **Phillip** |  Scoping , Wrangling and EDA, KPI |
| **Rebal** | tasks placeholder |
| **Danny** | Data Wrangler, |
| **Samir.AI** |  Documentation,  |

## Sprint Milestones

## Phase 1: Project Scoping & Foundation
*Goal: Ensure the entire team agrees on the dataset, business problem, and variable definitions before writing any code.*
- [ ] Lock in the final dataset(s)
- [ ] Review dataset structure (or schema mapping if joining multiple tables)
- [ ] Draft `docs/data_dictionary.md` to define every column, data type, and permitted value
- [ ] Define the core business problem and target audience

## Phase 2: Data Wrangling & Pipeline
*Goal: Transform raw data into a clean, analytical dataset.*
- [ ] Ingest raw data into a Python environment (e.g., Pandas) or SQL database
- [ ] Handle missing values (imputation or removal) and outliers
- [ ] Standardize text data and clean categorical variables
- [ ] Remove duplicates and irrelevant columns
- [ ] Export the final cleaned dataset to `data/processed/`

## Phase 3: Exploratory Data Analysis (EDA)
*Goal: Discover the "story" in the data and identify trends before defining rigid metrics.*
- [ ] Generate univariate visualizations (histograms, box plots) to understand distributions
- [ ] Perform bivariate/multivariate analysis (scatter plots, correlation matrices)
- [ ] Document key insights, anomalies, and relationships (e.g., in a Jupyter Notebook)

## Phase 4: KPI Definition & Storyboarding
*Goal: Base business metrics on actual data realities discovered during EDA.*
- [ ] Define 5–7 core business KPIs based on EDA findings
- [ ] Document the mathematical formulas and business logic for each KPI
- [ ] Sketch/wireframe the Power BI dashboard layout on a whiteboard or paper

## Phase 5: Power BI Dashboarding
*Goal: Build the interactive visual layer for stakeholders.*
- [ ] Import the cleaned dataset (`data/processed/`) into Power BI
- [ ] Write necessary DAX measures for the defined KPIs
- [ ] Design interactive visuals (bar charts, line graphs, maps) with proper filtering
- [ ] Format the dashboard for accessibility and a professional aesthetic

## Phase 6: Documentation & Presentation
*Goal: Finalize all deliverables and prepare to communicate findings to a non-technical audience.*
- [ ] Finalize the GitHub repository (clean code, proper `README.md`)
- [ ] Draft `docs/ethics_and_limitations.md` detailing dataset biases and privacy considerations
- [ ] Build the final slide deck focusing on actionable insights
- [ ] Conduct a team dry-run of the presentation
