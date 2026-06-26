# Data Quality Report — ApexPlanet Sales Dataset

This report documents the profiling done on the raw dataset (`data/raw/ApexPlanet_DataAnalytics_Dataset.xlsx`),
the issues found, and exactly how each one was handled in `scripts/data_cleaning.py`. It's generated from a real
run of the script — every number below is reproducible by running:

```bash
python scripts/data_cleaning.py
```

## Snapshot

| Metric | Raw | Cleaned |
|---|---|---|
| Rows | 1,000 | 1,000 |
| Columns | 12 | 27 |
| Missing values | 33 (`Age`: 20, `City`: 13) | 0 |
| Exact duplicate rows | 0 | 0 |
| `Order_ID` values shared by >1 row | 9 rows (1 ID: `ORD100050`, repeated 9x) | unchanged, but flagged + given a safe surrogate key |
| `Order_Date` data type | text string | proper `datetime` during processing → standardized ISO `YYYY-MM-DD` on output |
| `Total_Sales` arithmetic errors (`≠ Quantity x Unit_Price`) | 0 | 0 (script re-validates and would auto-correct any found) |
| Statistical outliers in `Total_Sales` (IQR method) | 19 | 19 (flagged, not deleted — see rationale below) |

## Issues found, and how each was resolved

### 1. Missing values
- `Age`: 20 of 1,000 rows (2.0%) were blank.
- `City`: 13 of 1,000 rows (1.3%) were blank.

**Resolution:** `Age` was median-imputed (median = 41) rather than mean-imputed, since the median is
less sensitive to the few very young/old customers in the dataset. `City` was filled with the explicit
label `"Unknown"` instead of a guessed city, because geography can't be reliably inferred from the other
fields. Both decisions are fully traceable: the boolean columns `Age_Was_Missing` and `City_Was_Missing`
mark exactly which rows were touched, so any downstream analysis can filter them out if a stricter view
is needed.

### 2. Non-unique primary key (`Order_ID`)
`Order_ID` is meant to behave like a primary key, but the value `ORD100050` appears on **9 different rows**
with completely different customers, dates, and products — i.e. these are genuinely different orders that
happen to share an ID, not accidental duplicate rows (a full-row duplicate check found 0 exact duplicates).

**Resolution:** Rather than overwrite the business-provided `Order_ID` (which could hide the issue from
whoever owns the upstream system generating these IDs), the script:
- Adds `Duplicate_Order_ID_Flag` to mark every affected row.
- Adds `Row_UID` — a guaranteed-unique surrogate key (`ROW00001` … `ROW01000`) — so any join or
  groupby in downstream analysis has a safe key to use.

### 3. `Order_Date` stored as text
All 1,000 values were technically valid `YYYY-MM-DD` strings (no mixed formats, no unparseable dates),
but the column's dtype was plain text, not a real date type — so no date arithmetic, sorting, or
`.dt` accessor methods would work on it directly.

**Resolution:** Converted to a proper `datetime64` during processing (enabling all the date-derived
features below), and written back out in standardized ISO `YYYY-MM-DD` format.

### 4. Customer identity inconsistencies
Two related but distinct findings:
- **52 `Customer_ID` values are each linked to more than one `Customer_Name`** (105 rows affected) —
  the same supposedly-unique customer ID appears with different names on different orders.
- **`Customer_Name` has only 425 unique values across 1,000 rows**, while `Customer_ID` has 947 unique
  values. In other words, customer names repeat far more than customer IDs do — a strong signal that
  `Customer_Name` was never validated against a master customer table and should **not** be treated as
  a unique identifier.

**Resolution:** Rather than guessing which name is "correct" for a given ID, the script flags every
affected row with `Customer_Identity_Flag` (105 rows) so a human can resolve them against a real
customer master table if one exists. The recommendation — documented in the data dictionary — is to
always use `Customer_ID`, never `Customer_Name`, as the customer key.

### 5. Statistical outliers in `Total_Sales`
Using the standard IQR method (1.5x rule), 19 of 1,000 orders (1.9%) fall outside the "normal" range
for `Total_Sales` (high-value end only — no low-value outliers).

**Resolution:** These were **flagged, not deleted**. In a sales dataset, an unusually large order is
very plausibly a genuine bulk purchase or VIP customer rather than a data error — deleting it would
quietly throw away real revenue from the analysis. The `Total_Sales_Outlier_Flag` column lets an
analyst include, exclude, or specifically study these transactions as needed.

### 6. Arithmetic consistency check
Verified that `Total_Sales == Quantity x Unit_Price` for every row. No mismatches were found in this
dataset, but the script still performs and logs this check (and would auto-correct `Total_Sales` from
`Quantity x Unit_Price` if a mismatch ever appeared) so the pipeline stays correct if the raw data
changes.

### 7. Text formatting
Checked `City`, `Gender`, `Product`, `Category`, and `Customer_Name` for leading/trailing whitespace
and inconsistent casing. None was found in this particular file, but the cleaning script still
trims whitespace and title-cases these fields defensively, so the pipeline is robust if a future
data pull isn't as clean.

## Feature engineering performed

| New feature | Derived from | Purpose |
|---|---|---|
| `Order_Year`, `Order_Month`, `Order_Month_Name`, `Order_Quarter`, `Order_Weekday`, `Is_Weekend` | `Order_Date` | Enable time-based trend and seasonality analysis |
| `Age_Group` | `Age` | 5-band customer segmentation (`18-25` … `56-65`) |
| `Customer_Order_Count` | `Customer_ID` | Identify repeat customers / loyalty |
| `High_Value_Order` | `Total_Sales` | Flag the top 25% of orders by revenue |

## Why this matters for the business
- A non-unique `Order_ID` would silently break any reporting tool that assumes one row = one order
  per ID (e.g. a `COUNT(DISTINCT Order_ID)` would undercount actual orders).
- Treating `Customer_Name` as an identity key would massively overstate "repeat customers" because
  names collide across genuinely different people.
- Deleting the 19 high-value outliers instead of flagging them would have erased about
  ₹87.8 lakh in legitimate large-order revenue (~6.3% of total `Total_Sales` in the dataset)
  from any downstream revenue analysis.

These are exactly the kind of issues a one-off `df.dropna()` / `df.drop_duplicates()` would miss or
mishandle — which is the point of doing a proper data quality pass before analysis.
