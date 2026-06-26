# Data Dictionary — ApexPlanet Sales Dataset

Dataset: `Sales_Dataset` (1,000 rows, 1 sheet)
Source file: `data/raw/ApexPlanet_DataAnalytics_Dataset.xlsx`
Cleaned output: `data/cleaned/cleaned_sales_dataset.csv` (1,000 rows, 27 columns)

## 1. Original columns (as received)

| # | Column | Type | Description | Sample value | Business relevance |
|---|--------|------|--------------|---------------|---------------------|
| 1 | `Order_ID` | string | Order identifier | `ORD100002` | Order tracking and joins with other systems. **Not guaranteed unique in the raw data** — see Data Quality Report. |
| 2 | `Order_Date` | date (`YYYY-MM-DD`) | Date the order was placed | `2025-02-25` | Time-series and seasonality analysis |
| 3 | `Customer_ID` | string | Identifier of the purchasing customer | `CUST5529` | Customer segmentation, repeat-purchase analysis. Treat as the **authoritative** customer key |
| 4 | `Customer_Name` | string | Display name of the customer | `Customer_227` | Low — only 425 unique values across 1,000 rows, so it should **not** be used as a unique identifier |
| 5 | `Age` | integer | Customer age in years | `30` | Demographic segmentation, age-based targeting |
| 6 | `Gender` | string (`Male`/`Female`) | Customer gender | `Female` | Demographic segmentation |
| 7 | `City` | string | City of the order | `Bengaluru` | Regional sales performance, logistics planning |
| 8 | `Product` | string | Product purchased | `Rice` | Product-level performance |
| 9 | `Category` | string | Product category (1:1 with `Product`) | `Grocery` | Category-level performance, inventory planning |
| 10 | `Quantity` | integer | Units purchased | `7` | Demand volume |
| 11 | `Unit_Price` | float (₹) | Price per unit | `2829.77` | Pricing analysis |
| 12 | `Total_Sales` | float (₹) | `Quantity x Unit_Price` | `19808.39` | Core revenue KPI |

## 2. Data-quality flag columns (added by `scripts/data_cleaning.py`)

These columns don't exist in the raw file — the cleaning script adds them so that every imputed or flagged value stays traceable instead of silently disappearing.

| # | Column | Type | Description | Business relevance |
|---|--------|------|--------------|---------------------|
| 13 | `Duplicate_Order_ID_Flag` | boolean | `True` if this row's `Order_ID` is shared by more than one row in the raw data | Tells analysts which rows need `Row_UID` instead of `Order_ID` for joins |
| 14 | `Row_UID` | string | Guaranteed-unique surrogate key generated during cleaning (`ROW00001`, `ROW00002`, …) | Safe join/primary key when `Order_ID` isn't unique |
| 15 | `Age_Was_Missing` | boolean | `True` if `Age` was null in the raw data and was median-imputed | Lets analysts exclude or weight imputed ages |
| 16 | `City_Was_Missing` | boolean | `True` if `City` was null in the raw data and was filled with `"Unknown"` | Lets analysts exclude or separately treat missing geography |
| 17 | `Customer_Identity_Flag` | boolean | `True` if this `Customer_ID` is linked to more than one `Customer_Name` elsewhere in the dataset | Flags records needing identity verification before customer-level reporting |
| 18 | `Total_Sales_Outlier_Flag` | boolean | `True` if `Total_Sales` falls outside the IQR-based "normal" range | Highlights unusually large/small transactions for review (bulk orders, VIP customers, or possible entry errors) |

## 3. Engineered features (added by `scripts/data_cleaning.py`)

| # | Column | Type | Description | Business relevance |
|---|--------|------|--------------|---------------------|
| 19 | `Order_Year` | integer | Year extracted from `Order_Date` | Year-over-year trend analysis |
| 20 | `Order_Month` | integer (1–12) | Month number | Monthly reporting |
| 21 | `Order_Month_Name` | string | Month name (`January`, …) | Readable monthly reporting / chart labels |
| 22 | `Order_Quarter` | integer (1–4) | Calendar quarter | Quarterly business reviews |
| 23 | `Order_Weekday` | string | Day name the order was placed (`Monday`, …) | Weekday demand patterns |
| 24 | `Is_Weekend` | boolean | `True` if `Order_Weekday` is Saturday or Sunday | Weekday vs. weekend demand comparison |
| 25 | `Age_Group` | categorical (`18-25` … `56-65`) | Age bucketed into 5 bands | Customer segmentation for marketing/analysis |
| 26 | `Customer_Order_Count` | integer | Number of orders this `Customer_ID` has placed in the dataset | Identifies repeat customers / loyalty |
| 27 | `High_Value_Order` | boolean | `True` if `Total_Sales` is in the top 25% of all orders | Flags premium transactions for targeted analysis |

---
See [`reports/data_quality_report.md`](reports/data_quality_report.md) for the full before/after findings behind these columns.
