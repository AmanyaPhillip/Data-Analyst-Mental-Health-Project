📊 Data Analytics Project Activity: From Raw Data to Interactive Dashboard
🎯 Objective
In this activity, you will take a real-world dataset, clean and prepare it (data wrangling), perform exploratory data analysis (EDA), and finally build an interactive dashboard using Python.
This mirrors a real job workflow used by Data Analysts and Business Intelligence professionals.
________________________________________
🧩 Step 1: Dataset Selection (Real-World Data)
📌 Task
Choose one dataset from a public source.
Recommended Sources:
•	Kaggle: https://www.kaggle.com/datasets
•	Google Dataset Search: https://datasetsearch.research.google.com
•	Data.gov (Government datasets)
•	World Bank Data
________________________________________
📊 Suggested Dataset Types (Pick ONE):
•	Retail sales data
•	E-commerce transactions
•	Covid-19 cases or health data
•	Airbnb listings
•	Financial stock data
•	Sports performance data
•	Customer churn data
________________________________________
✅ Requirement
Your dataset must have:
•	At least 100+ rows
•	At least 4 columns
•	A time-based column (date/month/year) preferred
________________________________________
🧹 Step 2: Data Wrangling (Cleaning & Preparation)
📌 Task
Load your dataset using Python (Pandas) and clean it.
You must perform:
1. Load dataset
import pandas as pd
df = pd.read_csv("your_file.csv")
2. Handle missing values
•	Identify missing values
•	Fill or remove them
3. Fix data types
•	Convert dates using pd.to_datetime()
•	Ensure numeric columns are correct
4. Remove duplicates (if any)
5. Create new columns (feature engineering)
Examples:
•	Year, Month, Day from Date
•	Profit margin = Profit / Sales
•	Age groups (if demographic data)
________________________________________
✅ Output Expected:
A clean dataset ready for analysis
________________________________________
📊 Step 3: Exploratory Data Analysis (EDA)
📌 Task
Explore the dataset and answer business questions.
________________________________________
🔍 Required Analysis:
1. Basic statistics
•	Mean, median, min, max
2. Group analysis
•	Sales by category
•	Profit by region
•	Monthly trends
3. Visualizations (Minimum 4 required)
Use Plotly or Matplotlib:
•	Bar chart → Category vs Sales
•	Line chart → Trend over time
•	Pie chart → Distribution
•	Box plot → Spread of values
________________________________________
🧠 Questions to Answer:
•	What category generates the highest revenue?
•	What time period shows peak performance?
•	Are there any unusual patterns or outliers?
•	Which region performs best?
________________________________________
✅ Output Expected:
EDA insights + visual charts
________________________________________
📈 Step 4: Build Interactive Dashboard (Final Project)
📌 Task
Create an interactive dashboard using:
 Must: Dash (Plotly) 
Extra: You can also use Power BI/Looker studio /Cognos
________________________________________
📊 Dashboard Must Include:
1. Filters
•	Year dropdown OR category filter
2. Visualizations (minimum 4–5):
•	Bar chart (Category vs Sales)
•	Line chart (Time trend)
•	Pie chart (Distribution)
•	Box plot (Spread)
•	Optional: Sunburst / Heatmap
________________________________________
🧠 Dashboard Features:
•	Interactive filtering
•	Dynamic charts
•	Clean layout
•	Clear titles and labels
________________________________________
💡 Bonus (Optional but recommended):
•	KPI cards (Total Sales, Profit, Avg Value)
•	YoY comparison
•	Export dataset feature
________________________________________
📦 Final Submission Requirements
You must submit:
1. Python notebook or script
•	Data cleaning + EDA + dashboard code
2. Dataset used
•	Github Portfolio link (individual) or link through Microsoft form 
3. Short report (1–2 pages)
Include:
•	Dataset chosen
•	Key insights
•	Challenges faced
•	What you learned
________________________________________________________________________________
🚀 Learning Outcome
By completing this project, you will understand:
•	Real-world data wrangling
•	Business analysis thinking
•	Data storytelling
•	Building dashboards like industry analysts
________________________________________