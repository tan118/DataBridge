
from pathlib import Path
import pandas as pd

from extract import extract_csv


# =========================================================
# 1. REMOVE DUPLICATES
# =========================================================

def remove_duplicates(df, subset=None, keep="first"):

    original_rows = len(df)

    cleaned_df = df.drop_duplicates(
        subset=subset,
        keep=keep
    ).copy()

    removed = original_rows - len(cleaned_df)

    report = {
        "duplicates_removed": removed,
        "rows_remaining": len(cleaned_df)
    }

    return cleaned_df, report


# =========================================================
# 2. HANDLE MISSING VALUES
# =========================================================

def handle_missing_values(df, rules=None):

    cleaned_df = df.copy()
    report = {}

    if rules is None:
        return cleaned_df, report

    for column, rule in rules.items():

        if column not in cleaned_df.columns:
            continue

        strategy = rule.get("strategy", "keep")
        missing_before = cleaned_df[column].isna().sum()

        if strategy == "drop":
            cleaned_df = cleaned_df.dropna(subset=[column])

        elif strategy == "mean":
            value = pd.to_numeric(
                cleaned_df[column], errors="coerce"
            ).mean()
            cleaned_df[column] = cleaned_df[column].fillna(value)

        elif strategy == "median":
            value = pd.to_numeric(
                cleaned_df[column], errors="coerce"
            ).median()
            cleaned_df[column] = cleaned_df[column].fillna(value)

        elif strategy == "mode":
            modes = cleaned_df[column].mode()
            if not modes.empty:
                cleaned_df[column] = cleaned_df[column].fillna(
                    modes.iloc[0]
                )

        elif strategy == "constant":
            value = rule.get("value")
            cleaned_df[column] = cleaned_df[column].fillna(value)

        elif strategy == "keep":
            pass

        else:
            raise ValueError(
                f"Unsupported missing-value strategy: {strategy}"
            )

        report[column] = {
            "strategy": strategy,
            "missing_before": int(missing_before),
            "missing_after": int(cleaned_df[column].isna().sum())
        }

    return cleaned_df, report


# =========================================================
# 3. HANDLE NEGATIVE AND ZERO NUMERIC VALUES
# =========================================================

def handle_numeric_values(df, rules=None):

    cleaned_df = df.copy()
    report = {}

    if rules is None:
        return cleaned_df, report

    for column, rule in rules.items():

        if column not in cleaned_df.columns:
            continue

        cleaned_df[column] = pd.to_numeric(
            cleaned_df[column], errors="coerce"
        )

        negative_action = rule.get("negative", "keep")
        zero_action = rule.get("zero", "keep")
        replace_value = rule.get("replace_value", 0)

        negative_count = int((cleaned_df[column] < 0).sum())
        zero_count = int((cleaned_df[column] == 0).sum())

        if negative_action == "drop":
            cleaned_df = cleaned_df[
                cleaned_df[column] >= 0
            ]

        elif negative_action == "replace":
            cleaned_df.loc[
                cleaned_df[column] < 0, column
            ] = replace_value

        elif negative_action != "keep":
            raise ValueError("Invalid negative-value action")

        if zero_action == "drop":
            cleaned_df = cleaned_df[
                cleaned_df[column] != 0
            ]

        elif zero_action == "replace":
            cleaned_df.loc[
                cleaned_df[column] == 0, column
            ] = replace_value

        elif zero_action != "keep":
            raise ValueError("Invalid zero-value action")

        report[column] = {
            "negative_values_found": negative_count,
            "zero_values_found": zero_count,
            "negative_action": negative_action,
            "zero_action": zero_action
        }

    return cleaned_df.copy(), report


# =========================================================
# 4. CONVERT DATA TYPES
# =========================================================

def convert_data_types(df, rules=None):

    cleaned_df = df.copy()
    report = {}

    if rules is None:
        return cleaned_df, report

    for column, data_type in rules.items():

        if column not in cleaned_df.columns:
            continue

        try:
            if data_type == "datetime":
                cleaned_df[column] = pd.to_datetime(
                    cleaned_df[column], errors="coerce"
                )

            elif data_type == "numeric":
                cleaned_df[column] = pd.to_numeric(
                    cleaned_df[column], errors="coerce"
                )

            elif data_type == "string":
                cleaned_df[column] = cleaned_df[column].astype("string")

            elif data_type == "integer":
                cleaned_df[column] = pd.to_numeric(
                    cleaned_df[column], errors="coerce"
                ).astype("Int64")

            else:
                raise ValueError(
                    f"Unsupported data type: {data_type}"
                )

            report[column] = {
                "converted_to": data_type,
                "invalid_values": int(cleaned_df[column].isna().sum())
            }

        except (TypeError, ValueError, OverflowError) as error:
            report[column] = {
                "conversion_error": str(error)
            }

    return cleaned_df, report


# =========================================================
# 5. MASTER TRANSFORMATION FUNCTION
# =========================================================

def transform_dataframe(
    df,
    duplicate_subset=None,
    duplicate_keep="first",
    missing_rules=None,
    numeric_rules=None,
    datatype_rules=None
):

    original_rows = len(df)

    # Step 1: Remove duplicates
    cleaned_df, duplicate_report = remove_duplicates(
        df,
        subset=duplicate_subset,
        keep=duplicate_keep
    )

    # Step 2: Handle missing values
    cleaned_df, missing_report = handle_missing_values(
        cleaned_df,
        rules=missing_rules
    )

    # Step 3: Handle negative and zero values
    cleaned_df, numeric_report = handle_numeric_values(
        cleaned_df,
        rules=numeric_rules
    )

    # Step 4: Convert data types
    cleaned_df, datatype_report = convert_data_types(
        cleaned_df,
        rules=datatype_rules
    )

    # Final report
    cleaning_report = {
        "original_rows": original_rows,
        "final_rows": len(cleaned_df),
        "rows_removed": original_rows - len(cleaned_df),
        "duplicates": duplicate_report,
        "missing_values": missing_report,
        "numeric_values": numeric_report,
        "data_types": datatype_report
    }

    return cleaned_df, cleaning_report


# =========================================================
# 6. MAIN EXECUTION
# =========================================================

if __name__ == "__main__":

    project_root = Path(__file__).resolve().parent.parent

    csv_path = (
        project_root
        / "data"
        / "raw"
        / "online_retail.csv"
    )

    output_path = (
        project_root
        / "data"
        / "processed"
        / "cleaned_online_retail.csv"
    )

    # Extract original CSV
    df = extract_csv(csv_path)

    print("\n========== ORIGINAL DATA ==========")
    print(f"Rows: {len(df)}")
    print(f"Columns: {len(df.columns)}")

    # -----------------------------------------------------
    # CONFIGURATION: CHANGE THESE RULES FOR EACH DATASET
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # RUN MASTER TRANSFORMATION
    # -----------------------------------------------------

    cleaned_df, report = transform_dataframe(
        df,
        duplicate_subset=None,
        duplicate_keep="first",
        missing_rules=missing_rules,
        numeric_rules=numeric_rules,
        datatype_rules=datatype_rules
    )

    # Create output directory if needed
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    # Save cleaned dataset
    cleaned_df.to_csv(
        output_path,
        index=False
    )

    # Display report
    print("\n========== CLEANING REPORT ==========")

    print(f"Original rows: {report['original_rows']}")
    print(f"Final rows: {report['final_rows']}")
    print(f"Rows removed: {report['rows_removed']}")

    print("\nDuplicate Report:")
    print(report["duplicates"])

    print("\nMissing Value Report:")
    print(report["missing_values"])

    print("\nNumeric Value Report:")
    print(report["numeric_values"])

    print("\nData Type Report:")
    print(report["data_types"])

    print("\n========== TRANSFORMATION COMPLETED ==========")
    print(f"Cleaned file saved at: {output_path}")
