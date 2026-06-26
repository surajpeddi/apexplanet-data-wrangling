# Data Immersion \& Wrangling — ApexPlanet Sales Dataset

**ApexPlanet Software Pvt Ltd — Data Analytics Internship, Task 1**

Acquiring, profiling, cleaning, and transforming a raw 1,000-row sales transactions dataset into an
analysis-ready dataset — with every data-quality issue found, decided on, and documented rather than
silently dropped.

## Objective

To rapidly get acquainted with a real-world-style dataset and practice the foundational first step of
any analysis: identifying data quality issues, cleaning them defensibly, and engineering features that
make the data ready for analysis or dashboarding.

## Dataset

`Sales\\\\\\\_Dataset` — 1,000 rows x 12 columns of e-commerce-style sales transactions (order ID, date,
customer demographics, city, product, category, quantity, unit price, total sales).

## What's in this repo

```
.
├── data/
│   ├── raw/                       # Original, untouched dataset
│   │   └── ApexPlanet\\\\\\\_DataAnalytics\\\\\\\_Dataset.xlsx
│   └── cleaned/                   # Output of the cleaning script
│       └── cleaned\\\\\\\_sales\\\\\\\_dataset.csv
├── scripts/
│   └── data\\\\\\\_cleaning.py           # Profiling + cleaning + feature engineering pipeline
├── reports/
│   └── data\\\\\\\_quality\\\\\\\_report.md     # Every issue found, with before/after numbers and rationale
├── data\\\\\\\_dictionary.md             # Every column in the cleaned dataset: type, meaning, business use
├── linkedin\\\\\\\_video\\\\\\\_script.md       # Talking points + post caption for the task's video walkthrough
├── requirements.txt
└── README.md
```

## Data quality issues found

A full write-up with numbers and rationale is in [`reports/data\\\\\\\_quality\\\\\\\_report.md`](reports/data_quality_report.md).
Short version:

|Issue|Found|Resolution|
|-|-|-|
|Missing `Age`|20 rows|Median-imputed + flagged (`Age\\\\\\\_Was\\\\\\\_Missing`)|
|Missing `City`|13 rows|Filled with `"Unknown"` + flagged (`City\\\\\\\_Was\\\\\\\_Missing`)|
|Non-unique `Order\\\\\\\_ID`|9 rows share one ID|Flagged + given a safe surrogate key (`Row\\\\\\\_UID`)|
|`Order\\\\\\\_Date` stored as text|1,000 rows|Converted to real `datetime`, standardized output format|
|`Customer\\\\\\\_ID` linked to multiple `Customer\\\\\\\_Name`s|105 rows|Flagged (`Customer\\\\\\\_Identity\\\\\\\_Flag`) for manual review|
|`Customer\\\\\\\_Name` unreliable as an identity key|425 unique names for 947 unique IDs|Documented — use `Customer\\\\\\\_ID` instead|
|Statistical outliers in `Total\\\\\\\_Sales`|19 rows|Flagged, not deleted (genuine high-value orders)|

## Feature engineering

From the cleaned data, the script derives: `Order\\\\\\\_Year`, `Order\\\\\\\_Month`, `Order\\\\\\\_Month\\\\\\\_Name`,
`Order\\\\\\\_Quarter`, `Order\\\\\\\_Weekday`, `Is\\\\\\\_Weekend`, `Age\\\\\\\_Group` (5 bands), `Customer\\\\\\\_Order\\\\\\\_Count`, and
`High\\\\\\\_Value\\\\\\\_Order` — see [`data\\\\\\\_dictionary.md`](data_dictionary.md) for the full reference.

## How to run it

```bash
git clone <this-repo-url>
cd ApexPlanet\\\\\\\_Task1\\\\\\\_Data\\\\\\\_Wrangling
pip install -r requirements.txt
python scripts/data\\\\\\\_cleaning.py
```

This reads `data/raw/ApexPlanet\\\\\\\_DataAnalytics\\\\\\\_Dataset.xlsx`, prints a full before/after data-quality
profile to the console, and writes the cleaned dataset to `data/cleaned/cleaned\\\\\\\_sales\\\\\\\_dataset.csv`.

## Tools used

Python, pandas, NumPy, openpyxl

## Author

*PEDDI SURAJ* — Data Analytics Intern, ApexPlanet Software Pvt Ltd

