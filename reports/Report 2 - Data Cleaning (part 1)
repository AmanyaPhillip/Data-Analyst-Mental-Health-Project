
# 📘 DATA CLEANING PIPELINE 

This project contains multiple raw datasets from StatCan, CIHI, and MHACS. Each dataset has a different structure, format, and quality. To make them usable for analysis and dashboards, we built a universal cleaning pipeline with specialized cleaning functions for each dataset type.

Below is a summary of what each cleaning function does and why it is needed.

## 🧹Cleaning 1 -  StatCan Long Format CSVs
### Purpose
Standardize all StatCan long-format datasets into a consistent, analysis-ready structure.

### What it does
- Strips whitespace from column names and text values
•   Standardizes column names (e.g., REF_DATE → ref_date, GEO → geo)
-   Converts dates (ref_date) into proper datetime format
-   Converts numeric values (value) into floats
-   Removes suppressed rows (marked in STATUS)
-   Drops metadata columns (SYMBOL, TERMINATED, DECIMALS)
-   Normalizes geography names (e.g., "Newfoundland / Labrador" → "Newfoundland/Labrador")
-   Cleans indicator names (removes double spaces)

### Why it’s needed
StatCan files are inconsistent across releases. This function ensures every StatCan dataset has the same structure, making it easy to merge, analyze, and visualize.
## 🧹Cleaning 2 CIHI Visualization Config Files 
### Purpose
Convert CIHI’s chart configuration tables into tidy, row-level data.

### What it does
-   Splits comma-separated x/y values into lists
-   Pairs each x with its corresponding y
-   Converts y values to numeric, safely handling invalid values
-   Extracts indicator, breakdown, CI bounds
-   Builds a tidy dataset with one row per data point
-   Removes rows with invalid numeric values

### Why it’s needed
CIHI vizconfig files are not real datasets — they store chart definitions. This function transforms them into proper analytical data that can be plotted or merged.

## 🧹Cleaning 3 - CIHI Excel Multi Sheet Tables 
### Purpose
Convert CIHI’s multi-sheet Excel workbook into a single long-format dataset.

### What it does
-   Standardizes column headers (removes spaces/newlines)
-   Identifies fiscal year columns (columns containing "20")
-   Melts wide year columns into long format
-   Cleans fiscal year labels
-   Combines all sheets into one DataFrame

### Why it’s needed
CIHI Excel tables are in wide format and split across multiple sheets. This function produces a unified, tidy dataset ready for time-series analysis.

## 🧹Cleaning 4 - MHACS Microdata 
### Purpose
Prepare MHACS survey microdata for statistical analysis.

### What it does
-   Replaces coded missing values (6, 7, 8, 9, 96, 996, 999, 99.6) with NaN
-   Ensures survey weights (WTS_M) are numeric

### Why it’s needed
Microdata uses numeric codes instead of actual missing values. This function standardizes missing data and ensures weights are usable for weighted analysis.
