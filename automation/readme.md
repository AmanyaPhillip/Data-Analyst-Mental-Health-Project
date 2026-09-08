# ⚙️ Automation & MCP Server Architecture & Implementation Blueprint

This document defines the architecture, technical specifications, and execution roadmap for automating the **Canadian Mental Health Surveillance & Analytics Pipeline** and exposing it via a local **Model Context Protocol (MCP) Server**.

---

## 🏛️ System Architecture

```
                               ┌─────────────────────────────┐
                               │   Raw / Cleaned Datasets    │
                               │  data/processed/02_cleaned/ │
                               └──────────────┬──────────────┘
                                              │
                                              ▼
                               ┌─────────────────────────────┐
                               │ [Module 2-A] Orchestrator   │
                               │  automation/run_pipeline.py │
                               └──────────────┬──────────────┘
                                              │
                       ┌──────────────────────┴──────────────────────┐
                       ▼                                             ▼
        ┌─────────────────────────────┐               ┌─────────────────────────────┐
        │ [Module 2-C] Relational DB  │               │    Optional Notebook Sync   │
        │   automation/build_db.py    │               │  --run-notebooks (nbconvert)│
        └──────────────┬──────────────┘               └─────────────────────────────┘
                       │
       ┌───────────────┴───────────────┐
       ▼                               ▼
┌───────────────────────────────┐  ┌───────────────────────────────┐
│ SQLite Database               │  │ Automated KPI Scorecard       │
│ data/processed/               │  │ data/processed/               │
│ mental_health.db              │  │ 04_kpi_summary.csv            │
└──────────────┬────────────────┘  └───────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────────────────────────┐
│ [Module 5] Model Context Protocol (MCP) Server                   │
│ mcp/server.py  (FastMCP / Python MCP SDK - stdio JSON-RPC)       │
├────────────────────────────────┬─────────────────────────────────┤
│ • execute_sql (read-only guard)│ • get_provincial_stats          │
│ • get_kpi_scorecard            │ • get_youth_crisis_data         │
│ • describe_schema              │ • get_disparity_analysis        │
└────────────────────────────────┴─────────────────────────────────┘
                                 │
                 ┌───────────────┴───────────────┐
                 ▼                               ▼
       ┌──────────────────┐            ┌──────────────────┐
       │  Claude Desktop  │            │ Antigravity IDE  │
       └──────────────────┘            └──────────────────┘
```

---

## 📁 Repository Structure & File Manifest

```
Data-Analyst-Mental-Health-Project/
├── automation/
│   ├── readme.md                      # Architecture & blueprint (this file)
│   ├── run_pipeline.py                # Master CLI orchestrator (Module 2-A)
│   ├── build_db.py                    # SQLite DB builder & KPI exporter (Module 2-C)
│   ├── validate_pipeline.py           # Automated schema & data assertions
│   └── sql/
│       ├── schema.sql                 # Fact and dimension table DDL with indexes
│       ├── views.sql                  # Analytical SQL views (Gender Paradox, Trends, etc.)
│       └── kpi_scorecard.sql          # 10 core executive KPI queries
│
├── mcp/
│   ├── server.py                      # FastMCP server entry point (Module 5)
│   ├── db_client.py                   # Thread-safe read-only SQLite connector & query guard
│   ├── tools.py                       # High-level domain analysis tool implementations
│   └── mcp_config.json                # Ready-to-use client config for Claude Desktop / Antigravity
│
└── data/
    └── processed/
        ├── mental_health.db           # Persistent SQLite database file
        ├── mh_long.csv                # Standardized long StatCan analytical table
        ├── cihi_children.csv          # Reshaped pediatric emergency & hospitalization table
        └── 04_kpi_summary.csv         # Master KPI summary scorecard
```

---

## 🧩 Technical Specifications

### 1. [Module 2-A] Master Pipeline Orchestrator (`automation/run_pipeline.py`)
Executes the analytical pipeline headlessly and deterministically.

* **CLI Interface:**
  ```bash
  # Run full pipeline: validate data, rebuild SQLite database, and regenerate KPIs
  python automation/run_pipeline.py

  # Run specific stage
  python automation/run_pipeline.py --stage db
  python automation/run_pipeline.py --stage validate

  # Optionally execute and refresh Jupyter Notebook outputs
  python automation/run_pipeline.py --run-notebooks
  ```
* **Execution Flow:**
  1. `validate_pipeline.py`: Confirms source CSV existence, checks column types, bounds, and suppression codes.
  2. `build_db.py`: Ingests cleaned data, compiles `mental_health.db`, executes `automation/sql/views.sql`, and generates `data/processed/04_kpi_summary.csv`.
  3. (Optional) Executes `02_data_cleaning.ipynb` and `04_analysis.ipynb` via `nbconvert` if `--run-notebooks` is passed.

---

### 2. [Module 2-C] Relational SQLite Database Engine (`automation/build_db.py`)
Builds a persistent, single-source-of-truth database file at `data/processed/mental_health.db`.

* **Tables & Indexing (`automation/sql/schema.sql`):**
  * `statcan_facts`: Ingested from `data/processed/mh_long.csv`
    * Indexed on: `(geo, ref_date, indicator, sex)`
  * `cihi_pediatric_facts`: Ingested from `data/processed/cihi_children.csv`
    * Indexed on: `(fiscal_year, diagnosis_group, sheet_type)`
* **Pre-built Analytical Views (`automation/sql/views.sql`):**
  * `vw_gender_paradox`: Mood disorder prevalence vs. suicide mortality by gender.
  * `vw_provincial_burden`: Fair/poor mental health rankings and coping deficits across Canadian provinces.
  * `vw_pediatric_triage`: ED presentation rates vs. inpatient hospitalization conversion ratios.
* **Automated KPI Exporter:**
  * Executes the 10 KPI queries from `automation/sql/kpi_scorecard.sql` and writes `data/processed/04_kpi_summary.csv`.

---

### 3. [Module 5] Model Context Protocol (MCP) Server (`mcp/server.py`)
Provides an AI interface for Claude Desktop, Antigravity IDE, or any MCP-compatible agent to interrogate the Canadian mental health database safely.

* **Technology:** Official Python MCP SDK / FastMCP via `stdio` transport.
* **Security & Safety Guard (`mcp/db_client.py`):**
  * SQLite opened in read-only mode: `PRAGMA query_only = ON`.
  * Queries restricted strictly to `SELECT` and `WITH ... SELECT` statements.
  * Statement timeouts and maximum row caps (default 500 rows) prevent memory exhaustion.
* **Tool Specifications:**
  1. `describe_schema()`: Returns tables, views, columns, and permitted values.
  2. `execute_sql(query: str)`: Executes read-only SQL queries with syntax validation.
  3. `get_kpi_scorecard()`: Returns the latest executive KPIs from `04_kpi_summary.csv`.
  4. `get_provincial_stats(province: str, indicator: str)`: Returns longitudinal trends for a specific province.
  5. `get_youth_crisis_data(fiscal_year: str)`: Returns pediatric ED and hospitalization rates with conversion ratios.
  6. `get_gender_paradox_stats()`: Returns comparative morbidity, ideation, care consultation, and mortality rates by gender.

---

## 💻 Client Configuration Snippet (`mcp/mcp_config.json`)

To connect the server to **Claude Desktop** (`%APPDATA%\Claude\claude_desktop_config.json`) or **Antigravity IDE**:

```json
{
  "mcpServers": {
    "canadian-mental-health": {
      "command": "python",
      "args": [
        "c:/Dev/Temp/Npower/Data-Analyst-Mental-Health-Project/mcp/server.py"
      ],
      "env": {
        "PYTHONPATH": "c:/Dev/Temp/Npower/Data-Analyst-Mental-Health-Project"
      }
    }
  }
}
```

---

## 🚀 Implementation Roadmap

1. **Step 1: SQL Modules Creation**
   * Create `automation/sql/schema.sql`, `automation/sql/views.sql`, and `automation/sql/kpi_scorecard.sql`.
2. **Step 2: Database Builder & Quality Validator**
   * Implement `automation/build_db.py` to create `mental_health.db` and export `04_kpi_summary.csv`.
   * Implement `automation/validate_pipeline.py`.
3. **Step 3: Master CLI Orchestrator**
   * Implement `automation/run_pipeline.py`.
4. **Step 4: MCP Server & Tools Implementation**
   * Build `mcp/db_client.py`, `mcp/tools.py`, and `mcp/server.py`.
   * Test the MCP server via standard stdio JSON-RPC.
