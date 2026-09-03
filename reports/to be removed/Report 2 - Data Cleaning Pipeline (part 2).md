
# Universal Cleaning Orchestrator - ETL Pipeline
Built a modular cleaning pipeline where each dataset type has its own cleaning function. This gives us a consistent, reproducible, and scalable data foundation for dashboards and modeling.



### 🔗 Link

https://github.com/AmanyaPhillip/Data-Analyst-Mental-Health-Project/blob/main/reports/Data_Cleaning_Pipeline.jpeg



### Purpose  
Automatically apply the correct cleaning function to each dataset and save cleaned outputs.

### What it does
- 	Creates a folder: data/processed/02_cleaned/
- 	Loops through every dataset in DATASETS
- 	Selects the correct cleaning function based on spec["kind"]
- 	Saves each cleaned dataset as a CSV
- 	Stores cleaned DataFrames in memory for further analysis
- 	Prints logs for transparency

### Why it’s needed
Even though each dataset has its own cleaning function, the orchestrator:
- 	Ensures every dataset is cleaned consistently
- 	Makes the pipeline reproducible
- 	Allows the team to add new datasets easily
- 	Centralizes all cleaning logic in one place
- 	Guarantees cleaned outputs are stored in a predictable folder
- 	Provides a clear audit trail of what was cleaned

This is standard practice in professional ETL pipelines.
