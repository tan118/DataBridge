
import pandas as pd
from pathlib import Path
from extract import extract_csv


def profile_dataframe(df):
    """Generate a comprehensive data quality report."""

    total_rows, total_columns = df.shape

    column_results = []

    for column in df.columns:
        series = df[column]

        null_count = int(series.isna().sum())

        if (
            pd.api.types.is_object_dtype(series)
            or pd.api.types.is_string_dtype(series)
        ):
            blank_count = int(
                series.astype("string").str.strip().eq("").sum()
            )
        else:
            blank_count = 0

        missing_count = null_count + blank_count

        missing_percentage = (
            missing_count / total_rows * 100
            if total_rows else 0
        )

        column_results.append({
            "column": column,
            "data_type": str(series.dtype),
            "total_values": total_rows,
            "missing_values": missing_count,
            "missing_percentage": round(missing_percentage, 2),
            "unique_values": int(series.nunique(dropna=True))
        })

    column_profile = pd.DataFrame(column_results)

    duplicate_count = int(df.duplicated().sum())

    summary = {
        "total_rows": total_rows,
        "total_columns": total_columns,
        "duplicate_rows": duplicate_count,
        "duplicate_percentage": round(
            duplicate_count / total_rows * 100, 2
        ) if total_rows else 0,
        "total_missing_cells": int(
            column_profile["missing_values"].sum()
        )
    }

    return {
        "summary": summary,
        "column_profile": column_profile
    }


def display_profile(report):

    print("\n========== DATABRIDGE DATA QUALITY REPORT ==========")

    print("\n--- DATASET SUMMARY ---")

    for key, value in report["summary"].items():
        print(f"{key}: {value}")

    print("\n--- COLUMN QUALITY REPORT ---")

    print(
        report["column_profile"].to_string(index=False)
    )


def save_profile_report(report, output_path):

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    report["column_profile"].to_csv(
        output_path,
        index=False
    )

    print(f"\nReport saved to: {output_path}")


if __name__ == "__main__":

    project_root = Path(__file__).resolve().parent.parent

    input_file = (
        project_root / "data" / "raw" / "online_retail.csv"
    )

    output_file = (
        project_root / "data" / "processed"
        / "data_quality_report.csv"
    )

    # Extract dataset
    df = extract_csv(input_file)

    # Generate profile
    report = profile_dataframe(df)

    # Display report
    display_profile(report)

    # Save report
    save_profile_report(report, output_file)

    print("\nProfiling completed successfully!")
