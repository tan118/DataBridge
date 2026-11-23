
from pathlib import Path
import pandas as pd

from extract import extract_csv
from profile import (
    profile_dataframe,
    display_profile,
    save_profile_report
)
from transform import transform_dataframe
from load import load_dataframe


# =====================================================
# MAIN ETL PIPELINE
# =====================================================

def run_pipeline():

    project_root = Path(__file__).resolve().parent.parent

    raw_file = (
        project_root / "data" / "raw" / "online_retail.csv"
    )

    processed_folder = project_root / "data" / "processed"

    processed_folder.mkdir(parents=True, exist_ok=True)

    cleaned_file = processed_folder / "cleaned_online_retail.csv"

    quality_report_file = (
        processed_folder / "data_quality_report.csv"
    )

    print("\n======================================")
    print("       DATABRIDGE ETL PIPELINE")
    print("======================================")

    # STEP 1: EXTRACT

    print("\n[STEP 1] EXTRACTING DATA")

    df = extract_csv(raw_file)

    print(f"Extracted {len(df):,} records.")

    # STEP 2: PROFILE

    print("\n[STEP 2] PROFILING DATA")

    profile_report = profile_dataframe(df)

    display_profile(profile_report)

    save_profile_report(
        profile_report,
        quality_report_file
    )

    # STEP 3: TRANSFORM

    print("\n[STEP 3] TRANSFORMING DATA")

    missing_rules = {
        "Description": {
            "strategy": "constant",
            "value": "Unknown"
        },
        "CustomerID": {
            "strategy": "keep"
        }
    }

    numeric_rules = {
        "Quantity": {
            "negative": "keep",
            "zero": "keep"
        },
        "UnitPrice": {
            "negative": "keep",
            "zero": "keep"
        }
    }

    datatype_rules = {
        "InvoiceDate": "datetime",
        "Quantity": "integer",
        "UnitPrice": "numeric"
    }

    cleaned_df, cleaning_report = transform_dataframe(
        df,
        duplicate_subset=None,
        duplicate_keep="first",
        missing_rules=missing_rules,
        numeric_rules=numeric_rules,
        datatype_rules=datatype_rules
    )

    cleaned_df.to_csv(cleaned_file, index=False)

    print(f"Cleaned records: {len(cleaned_df):,}")
    print(f"Cleaning report: {cleaning_report}")

    # STEP 4: LOAD

    print("\n[STEP 4] LOADING INTO POSTGRESQL")

    database_report = load_dataframe(
        df=cleaned_df,
        table_name="online_retail",
        chunksize=3000
    )

    print("\nDatabase report:")
    print(database_report)

    # FINAL SUMMARY

    print("\n======================================")
    print("       ETL PIPELINE COMPLETED")
    print("======================================")

    print(f"Extracted rows: {len(df):,}")
    print(f"Cleaned rows: {len(cleaned_df):,}")
    print(f"Database rows: {database_report['database_records']:,}")

    print("\nDataBridge pipeline executed successfully!")


# =====================================================
# EXECUTION
# =====================================================

if __name__ == "__main__":
    run_pipeline()
