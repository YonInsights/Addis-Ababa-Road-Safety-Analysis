# Understanding and Trusting Road Accident Data: An Exploratory Analysis of Addis Ababa

A reproducible, evidence-based exploratory data analysis (EDA) of road traffic accident (RTA) records in Addis Ababa, Ethiopia.

## 1. Project Overview

Traffic accidents represent a critical public health and urban mobility challenge in growing metropolitan areas. This portfolio project investigates the quality, completeness, and observational patterns within the Addis Ababa road traffic accident dataset.

Rather than taking data at face value, this analysis evaluates:
- **Data trustworthiness:** Identifying missingness patterns, inconsistencies, reporting anomalies, and potential recording biases.
- **Exploratory patterns:** Investigating temporal variations (time-of-day, day-of-week) and environmental conditions associated with recorded accident severity.
- **Defensible interpretations:** Clearly distinguishing observed counts, rates, and risk—avoiding unwarranted causal claims without exposure denominators (such as traffic volume or vehicle-kilometres travelled).

## 2. Repository Structure

```text
Addis-Ababa-Road-Safety-Analysis/
├── Data/                 # Raw dataset (kept local and uncommitted until license verification)
├── docs/                 # Data dictionary, column definitions, and methodology
├── notebooks/            # Jupyter notebooks for step-by-step exploratory analysis
├── reports/
│   └── figures/          # Exported publication-ready figures
├── src/                  # Reusable Python scripts and data processing helpers
├── .gitignore            # Git exclusion rules for environments and raw data
├── requirements.txt      # Project dependencies and minimum versions
└── README.md             # Project documentation and reproducibility guide
```

## 3. Environment & Setup

This project uses an isolated Python virtual environment to guarantee reproducibility across systems.

### 3.1. Prerequisites
- Python 3.12+ (Standalone interpreter)
- Git 2.x

### 3.2. Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone https://github.com/YonInsights/Addis-Ababa-Road-Safety-Analysis.git
   cd Addis-Ababa-Road-Safety-Analysis
   ```

2. **Create and activate the virtual environment:**
   ```powershell
   # Windows PowerShell
   python -m venv .venv
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   .\.venv\Scripts\Activate.ps1
   ```

3. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

4. **Register the Jupyter kernel:**
   ```powershell
   python -m ipykernel install --user --name addis-ababa-road-safety --display-name "Python (Addis Ababa Road Safety)"
   ```

## 4. Methodology & Principles

- **Preserve raw data:** The raw CSV is never modified directly.
- **Traceable transformations:** Every cleaning and encoding step is explicitly documented and justified.
- **Scientific rigor:** No invented metrics or conclusions. A higher accident count in a given area or time does not prove higher risk without baseline exposure data.

## 5. Author

- **Author:** YonInsights (`yo2120018@gmail.com`)

