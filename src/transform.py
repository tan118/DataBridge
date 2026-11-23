
import pandas as pd


# =====================================================
# 1. DUPLICATE REMOVAL
# =====================================================

def remove_duplicates(df, subset=None, keep="first"):

    before = len(df)

    cleaned_df = df.drop_duplicates(
        subset=subset,
        keep=keep
    ).copy()

    return cleaned_df, {
        "duplicates_removed": before - len(cleaned_df),
        "rows_remaining": len(cleaned_df),
        "keep": keep
    }


# =====================================================
# 2. MISSING VALUE HANDLING
# =====================================================

def handle_missing_values(df, rules=None):

    cleaned_df = df.copy()
    report = {}

    for column, rule in (rules or {}).items():

        if column not in cleaned_df.columns:
            continue

        strategy = rule.get("strategy", "keep")
        before = int(cleaned_df[column].isna().sum())
        rows_before = len(cleaned_df)

        if strategy == "drop":

            cleaned_df = cleaned_df.dropna(
                subset=[column]
            )

        elif strategy in ("mean", "median"):

            values = pd.to_numeric(
                cleaned_df[column],
                errors="coerce"
            )

            fill_value = (
                values.mean()
                if strategy == "mean"
                else values.median()
            )

            if pd.notna(fill_value):
                cleaned_df[column] = values.fillna(fill_value)

        elif strategy == "mode":

            modes = cleaned_df[column].mode()

            if not modes.empty:
                cleaned_df[column] = cleaned_df[column].fillna(
                    modes.iloc[0]
                )

        elif strategy == "constant":

            cleaned_df[column] = cleaned_df[column].fillna(
                rule.get("value", "Unknown")
            )

        elif strategy != "keep":

            raise ValueError(
                f"Unsupported missing-value strategy: {strategy}"
            )

        report[column] = {
            "strategy": strategy,
            "missing_before": before,
            "missing_after": int(
                cleaned_df[column].isna().sum()
            ),
            "rows_removed": rows_before - len(cleaned_df)
        }

    return cleaned_df, report


# =====================================================
# 3. TEXT STANDARDIZATION
# =====================================================

def standardize_text(df, rules=None):

    cleaned_df = df.copy()
    report = {}

    for column, operations in (rules or {}).items():

        if column not in cleaned_df.columns:
            continue

        series = cleaned_df[column].astype("string")
        before = series.copy()

        if "trim" in operations:
            series = series.str.strip()

        if "lowercase" in operations:
            series = series.str.lower()

        if "uppercase" in operations:
            series = series.str.upper()

        if "titlecase" in operations:
            series = series.str.title()

        cleaned_df[column] = series

        changed = int(
            (before.fillna("") != series.fillna("")).sum()
        )

        report[column] = {
            "operations": ", ".join(operations),
            "values_changed": changed
        }

    return cleaned_df, report


# =====================================================
# 4. NUMERIC VALUE HANDLING
# =====================================================

def handle_numeric_values(df, rules=None):

    cleaned_df = df.copy()
    report = {}

    for column, rule in (rules or {}).items():

        if column not in cleaned_df.columns:
            continue

        values = pd.to_numeric(
            cleaned_df[column],
            errors="coerce"
        )

        negative_action = rule.get("negative", "keep")
        zero_action = rule.get("zero", "keep")

        negative_replacement = rule.get(
            "negative_replace_value", 0
        )

        zero_replacement = rule.get(
            "zero_replace_value", 1
        )

        negative_count = int((values < 0).sum())
        zero_count = int((values == 0).sum())

        # Handle negative values

        rows_before_negative = len(cleaned_df)

        if negative_action == "drop":

            cleaned_df = cleaned_df.loc[
                values.isna() | (values >= 0)
            ].copy()

        elif negative_action == "replace":

            values = values.mask(
                values < 0,
                negative_replacement
            )

            # IMPORTANT: Save replacements to the DataFrame.
            cleaned_df[column] = values

        elif negative_action != "keep":

            raise ValueError("Invalid negative-value action")

        negative_rows_removed = (
            rows_before_negative - len(cleaned_df)
        )

        # Read the UPDATED column, not the original values.

        values = pd.to_numeric(
            cleaned_df[column],
            errors="coerce"
        )

        # Handle zero values

        rows_before_zero = len(cleaned_df)

        if zero_action == "drop":

            cleaned_df = cleaned_df.loc[
                values.isna() | (values != 0)
            ].copy()

        elif zero_action == "replace":

            values = values.mask(
                values == 0,
                zero_replacement
            )

            cleaned_df[column] = values

        elif zero_action != "keep":

            raise ValueError("Invalid zero-value action")

        zero_rows_removed = rows_before_zero - len(cleaned_df)

        report[column] = {
            "negative_values_found": negative_count,
            "negative_action": negative_action,
            "negative_replacement": negative_replacement,
            "negative_rows_removed": negative_rows_removed,
            "zero_values_found": zero_count,
            "zero_action": zero_action,
            "zero_replacement": zero_replacement,
            "zero_rows_removed": zero_rows_removed
        }

    return cleaned_df, report


# =====================================================
# 5. DATE STANDARDIZATION
# =====================================================

def standardize_dates(df, rules=None):

    cleaned_df = df.copy()
    report = {}

    for column, rule in (rules or {}).items():

        if column not in cleaned_df.columns:
            continue

        original_missing = int(
            cleaned_df[column].isna().sum()
        )

        dates = pd.to_datetime(
            cleaned_df[column],
            errors="coerce",
            dayfirst=rule.get("dayfirst", False)
        )

        invalid_count = int(
            (
                dates.isna()
                & cleaned_df[column].notna()
            ).sum()
        )

        action = rule.get("invalid", "keep")
        rows_before = len(cleaned_df)

        cleaned_df[column] = dates

        if action == "drop":

            cleaned_df = cleaned_df.dropna(
                subset=[column]
            )

        elif action != "keep":

            raise ValueError("Invalid date handling action")

        report[column] = {
            "invalid_dates_found": invalid_count,
            "original_missing": original_missing,
            "invalid_action": action,
            "rows_removed": rows_before - len(cleaned_df)
        }

    return cleaned_df, report


# =====================================================
# 6. COLUMN NAME STANDARDIZATION
# =====================================================

def standardize_column_names(df):

    cleaned_df = df.copy()

    cleaned_df.columns = (
        cleaned_df.columns
        .str.strip()
        .str.lower()
        .str.replace(r"\s+", "_", regex=True)
        .str.replace(r"[^a-z0-9_]", "", regex=True)
    )

    if not cleaned_df.columns.is_unique:
        raise ValueError(
            "Column standardization created duplicate column names."
        )

    return cleaned_df


# =====================================================
# 7. MASTER TRANSFORMATION ENGINE
# =====================================================

def transform_dataframe(
    df,
    duplicate_subset=None,
    duplicate_keep="first",
    missing_rules=None,
    numeric_rules=None,
    datatype_rules=None,
    text_rules=None,
    date_rules=None,
    remove_duplicates_enabled=True,
    standardize_columns=False
):

    original_rows = len(df)
    cleaned_df = df.copy()

    report = {}
    removal_details = []

    # Step 1: Duplicate removal

    if remove_duplicates_enabled:

        cleaned_df, duplicate_report = remove_duplicates(
            cleaned_df,
            subset=duplicate_subset,
            keep=duplicate_keep
        )

        report["duplicates"] = duplicate_report

        removal_details.append({
            "Transformation": "Duplicate removal",
            "Column": ", ".join(duplicate_subset)
            if duplicate_subset else "All columns",
            "Rows removed": duplicate_report["duplicates_removed"],
            "Action": f"Keep {duplicate_keep}"
        })

    # Step 2: Missing values

    cleaned_df, missing_report = handle_missing_values(
        cleaned_df,
        missing_rules
    )

    report["missing_values"] = missing_report

    for column, details in missing_report.items():

        if details["rows_removed"] > 0:

            removal_details.append({
                "Transformation": "Missing-value handling",
                "Column": column,
                "Rows removed": details["rows_removed"],
                "Action": details["strategy"]
            })

    # Step 3: Text standardization

    cleaned_df, text_report = standardize_text(
        cleaned_df,
        text_rules
    )

    report["text_standardization"] = text_report

    # Step 4: Numeric handling

    cleaned_df, numeric_report = handle_numeric_values(
        cleaned_df,
        numeric_rules
    )

    report["numeric_values"] = numeric_report

    for column, details in numeric_report.items():

        if details["negative_rows_removed"] > 0:

            removal_details.append({
                "Transformation": "Negative-value handling",
                "Column": column,
                "Rows removed": details["negative_rows_removed"],
                "Action": details["negative_action"]
            })

        if details["zero_rows_removed"] > 0:

            removal_details.append({
                "Transformation": "Zero-value handling",
                "Column": column,
                "Rows removed": details["zero_rows_removed"],
                "Action": details["zero_action"]
            })

    # Step 5: Date standardization

    cleaned_df, date_report = standardize_dates(
        cleaned_df,
        date_rules
    )

    report["date_standardization"] = date_report

    for column, details in date_report.items():

        if details["rows_removed"] > 0:

            removal_details.append({
                "Transformation": "Date handling",
                "Column": column,
                "Rows removed": details["rows_removed"],
                "Action": details["invalid_action"]
            })

    # Step 6: Data type conversion

    if datatype_rules:

        for column, data_type in datatype_rules.items():

            if column not in cleaned_df.columns:
                continue

            if data_type == "numeric":

                cleaned_df[column] = pd.to_numeric(
                    cleaned_df[column],
                    errors="coerce"
                )

            elif data_type == "string":

                cleaned_df[column] = cleaned_df[column].astype(
                    "string"
                )

            elif data_type == "integer":

                cleaned_df[column] = pd.to_numeric(
                    cleaned_df[column],
                    errors="coerce"
                ).astype("Int64")

            elif data_type == "datetime":

                cleaned_df[column] = pd.to_datetime(
                    cleaned_df[column],
                    errors="coerce"
                )

            else:

                raise ValueError(
                    f"Unsupported data type: {data_type}"
                )

    # Step 7: Column names

    if standardize_columns:

        cleaned_df = standardize_column_names(cleaned_df)

    # Step 8: Summary

    report["summary"] = {
        "original_rows": original_rows,
        "final_rows": len(cleaned_df),
        "rows_removed": original_rows - len(cleaned_df),
        "original_columns": len(df.columns),
        "final_columns": len(cleaned_df.columns)
    }

    report["row_removal_details"] = removal_details

    return cleaned_df, report
