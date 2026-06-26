"""
ApexPlanet Software Pvt Ltd - Data Analytics Internship
Task 1: Data Immersion & Wrangling
---------------------------------------------------------
Dataset : Sales Transactions (ApexPlanet_DataAnalytics_Dataset.xlsx)

This script:
    1. Loads the raw dataset
    2. Profiles it to surface data-quality issues (missing values,
       duplicate keys, inconsistent types, outliers, referential
       inconsistencies)
    3. Cleans and standardizes the data
    4. Engineers a few analysis-ready features
    5. Saves a final, analysis-ready CSV to data/cleaned/

Run from the project root:
    python scripts/data_cleaning.py
"""

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

RAW_PATH = Path("ApexPlanet_DataAnalytics_Dataset.xlsx")
CLEAN_PATH = Path("cleaned_sales_dataset.csv")
SHEET_NAME = "Sales_Dataset"


# --------------------------------------------------------------------------- #
# 1. LOAD
# --------------------------------------------------------------------------- #
def load_data(path: Path) -> pd.DataFrame:
    df = pd.read_excel(path, sheet_name=SHEET_NAME)
    print(f"Loaded {len(df):,} rows x {df.shape[1]} columns from {path.name}")
    return df


# --------------------------------------------------------------------------- #
# 2. PROFILE  (data quality assessment)
# --------------------------------------------------------------------------- #
def profile_data(df: pd.DataFrame, label: str = "RAW") -> dict:
    """Print a data-quality report and return key stats for before/after comparison."""
    print(f"\n{'=' * 60}\nDATA QUALITY PROFILE - {label}\n{'=' * 60}")

    stats = {}

    # Missing values
    missing = df.isnull().sum()
    missing = missing[missing > 0]
    stats["missing"] = missing.to_dict()
    print("\nMissing values:")
    print(missing.to_string() if not missing.empty else "  None")

    # Exact duplicate rows
    exact_dupes = df.duplicated().sum()
    stats["exact_duplicate_rows"] = int(exact_dupes)
    print(f"\nExact duplicate rows: {exact_dupes}")

    # Duplicate primary key (Order_ID should be unique)
    if "Order_ID" in df.columns:
        dup_ids = df["Order_ID"].duplicated().sum()
        stats["duplicate_order_ids"] = int(dup_ids)
        print(f"Duplicate Order_ID values (excluding first occurrence): {dup_ids}")

    # Order_Date stored as text, not a real datetime
    if "Order_Date" in df.columns:
        is_text = df["Order_Date"].apply(lambda x: isinstance(x, str)).all()
        stats["order_date_is_text"] = bool(is_text)
        print(f"Order_Date stored as text (not datetime): {is_text}")

    # Customer_ID <-> Customer_Name referential consistency
    if {"Customer_ID", "Customer_Name"}.issubset(df.columns):
        ids_with_multiple_names = (df.groupby("Customer_ID")["Customer_Name"].nunique() > 1).sum()
        stats["customer_ids_with_multiple_names"] = int(ids_with_multiple_names)
        print(f"Customer_IDs linked to >1 Customer_Name: {ids_with_multiple_names}")
        print(
            f"Unique Customer_ID values: {df['Customer_ID'].nunique()}  |  "
            f"Unique Customer_Name values: {df['Customer_Name'].nunique()}  (out of {len(df)} rows)"
        )

    # Outliers (IQR method) on key numeric fields
    print("\nOutliers (IQR method, 1.5x rule):")
    outlier_counts = {}
    for col in ["Age", "Quantity", "Unit_Price", "Total_Sales"]:
        if col in df.columns:
            q1, q3 = df[col].quantile([0.25, 0.75])
            iqr = q3 - q1
            lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
            n_out = int(((df[col] < lo) | (df[col] > hi)).sum())
            outlier_counts[col] = n_out
            print(f"  {col:<12} bounds=({lo:,.2f}, {hi:,.2f})  outliers={n_out}")
    stats["outliers"] = outlier_counts

    # Total_Sales arithmetic check
    if {"Quantity", "Unit_Price", "Total_Sales"}.issubset(df.columns):
        recomputed = (df["Quantity"] * df["Unit_Price"]).round(2)
        mismatches = int((recomputed - df["Total_Sales"]).abs().gt(0.01).sum())
        stats["total_sales_mismatches"] = mismatches
        print(f"\nTotal_Sales != Quantity * Unit_Price: {mismatches} rows")

    return stats


# --------------------------------------------------------------------------- #
# 3. CLEAN
# --------------------------------------------------------------------------- #
def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # --- Drop exact duplicate rows, if any ---
    before = len(df)
    df = df.drop_duplicates().reset_index(drop=True)
    print(f"Dropped {before - len(df)} exact duplicate row(s)")

    # --- Standardize text columns: trim whitespace, fix casing ---
    text_cols = ["Customer_Name", "City", "Product", "Category", "Gender"]
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
            df.loc[df[col].isin(["nan", "None", ""]), col] = np.nan
    df["City"] = df["City"].str.title()
    df["Product"] = df["Product"].str.title()
    df["Category"] = df["Category"].str.title()
    df["Gender"] = df["Gender"].str.title()

    # --- Convert Order_Date from text to a real datetime dtype ---
    df["Order_Date"] = pd.to_datetime(df["Order_Date"], format="%Y-%m-%d", errors="coerce")

    # --- Flag (don't silently drop) duplicate Order_ID values ---
    # Order_ID is meant to be a unique key but isn't in the raw data.
    # We keep the original ID for traceability and add:
    #   - a flag marking which rows share a non-unique Order_ID
    #   - a guaranteed-unique surrogate key for safe joins/analysis
    df["Duplicate_Order_ID_Flag"] = df["Order_ID"].duplicated(keep=False)
    df["Row_UID"] = ["ROW" + str(i).zfill(5) for i in range(1, len(df) + 1)]
    n_dup_flagged = int(df["Duplicate_Order_ID_Flag"].sum())
    print(f"Flagged {n_dup_flagged} rows sharing a non-unique Order_ID; added Row_UID as a safe unique key")

    # --- Missing Age: median imputation + indicator flag ---
    df["Age_Was_Missing"] = df["Age"].isna()
    median_age = df["Age"].median()
    df["Age"] = df["Age"].fillna(median_age)
    df["Age"] = df["Age"].astype(int)
    print(f"Imputed {int(df['Age_Was_Missing'].sum())} missing Age values with median ({median_age:.0f})")

    # --- Missing City: explicit 'Unknown' category + indicator flag ---
    # Geography can't be safely guessed, so we don't impute with mode -
    # we make the gap explicit instead.
    df["City_Was_Missing"] = df["City"].isna()
    df["City"] = df["City"].fillna("Unknown")
    print(f"Filled {int(df['City_Was_Missing'].sum())} missing City values with 'Unknown'")

    # --- Flag genuine Customer_ID identity conflicts for review ---
    # Same Customer_ID appears against more than one Customer_Name -
    # this field was not validated against a master customer table.
    # We flag rather than guess which name is "correct".
    # (Separately - see the data quality report - Customer_Name has far
    # fewer unique values than Customer_ID overall, so Customer_Name
    # should never be treated as a unique identifier; Customer_ID is the
    # authoritative key.)
    df["Customer_Identity_Flag"] = df.groupby("Customer_ID")["Customer_Name"].transform("nunique") > 1
    print(f"Flagged {int(df['Customer_Identity_Flag'].sum())} rows where Customer_ID maps to more than one Customer_Name")

    # --- Validate / correct Total_Sales arithmetic ---
    recomputed = (df["Quantity"] * df["Unit_Price"]).round(2)
    mismatch = (recomputed - df["Total_Sales"]).abs().gt(0.01)
    if mismatch.any():
        df.loc[mismatch, "Total_Sales"] = recomputed[mismatch]
    print(f"Corrected {int(mismatch.sum())} Total_Sales value(s) that didn't equal Quantity x Unit_Price")

    # --- Flag (don't delete) statistical outliers in Total_Sales ---
    # High-value transactions are business-relevant, not necessarily errors,
    # so we flag them for analyst attention instead of removing them.
    q1, q3 = df["Total_Sales"].quantile([0.25, 0.75])
    iqr = q3 - q1
    lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    df["Total_Sales_Outlier_Flag"] = (df["Total_Sales"] < lo) | (df["Total_Sales"] > hi)
    print(f"Flagged {int(df['Total_Sales_Outlier_Flag'].sum())} Total_Sales outliers (IQR method)")

    return df


# --------------------------------------------------------------------------- #
# 4. FEATURE ENGINEERING
# --------------------------------------------------------------------------- #
def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Date-derived features
    df["Order_Year"] = df["Order_Date"].dt.year
    df["Order_Month"] = df["Order_Date"].dt.month
    df["Order_Month_Name"] = df["Order_Date"].dt.month_name()
    df["Order_Quarter"] = df["Order_Date"].dt.quarter
    df["Order_Weekday"] = df["Order_Date"].dt.day_name()
    df["Is_Weekend"] = df["Order_Date"].dt.dayofweek.isin([5, 6])

    # Age_Group bucket - useful for customer segmentation
    bins = [17, 25, 35, 45, 55, 65]
    labels = ["18-25", "26-35", "36-45", "46-55", "56-65"]
    df["Age_Group"] = pd.cut(df["Age"], bins=bins, labels=labels)

    # Per-customer order frequency
    df["Customer_Order_Count"] = df.groupby("Customer_ID")["Order_ID"].transform("count")

    # High-value order flag (top quartile of Total_Sales)
    threshold = df["Total_Sales"].quantile(0.75)
    df["High_Value_Order"] = df["Total_Sales"] > threshold

    print(f"Engineered 9 new columns (date parts, Age_Group, Customer_Order_Count, High_Value_Order)")
    return df


# --------------------------------------------------------------------------- #
# 5. SAVE
# --------------------------------------------------------------------------- #
def save_data(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    print(f"\nSaved cleaned, analysis-ready dataset -> {path}  ({len(df):,} rows x {df.shape[1]} columns)")


# --------------------------------------------------------------------------- #
# MAIN
# --------------------------------------------------------------------------- #
def main():
    parser = argparse.ArgumentParser(description="Clean and transform the ApexPlanet sales dataset")
    parser.add_argument("--input", type=Path, default=RAW_PATH, help="Path to the raw .xlsx file")
    parser.add_argument("--output", type=Path, default=CLEAN_PATH, help="Path to write the cleaned .csv file")
    args = parser.parse_args()

    df_raw = load_data(args.input)
    profile_data(df_raw, label="RAW (before cleaning)")

    df_clean = clean_data(df_raw)
    df_final = engineer_features(df_clean)

    profile_data(df_final, label="CLEANED (after cleaning)")
    save_data(df_final, args.output)


if __name__ == "__main__":
    main()
