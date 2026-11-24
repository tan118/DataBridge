
import json
from pathlib import Path

import pandas as pd


# --------------------------------------------------
# SUPPORTED INPUT FORMATS
# --------------------------------------------------

SUPPORTED_FORMATS = {".json", ".xlsx", ".xls"}


# --------------------------------------------------
# GET EXCEL SHEET NAMES
# --------------------------------------------------

def get_excel_sheet_names(uploaded_file):
    """
    Return all sheet names from an Excel file.
    """

    uploaded_file.seek(0)

    try:
        excel_file = pd.ExcelFile(uploaded_file)
        return excel_file.sheet_names

    finally:
        uploaded_file.seek(0)


# --------------------------------------------------
# READ JSON DATA
# --------------------------------------------------

def read_json_file(uploaded_file):
    """
    Read JSON data and convert it into a DataFrame.

    Supports:
    - JSON arrays containing records
    - JSON objects
    - Nested JSON objects
    """

    uploaded_file.seek(0)

    data = json.load(uploaded_file)

    if isinstance(data, list):
        if not data:
            raise ValueError("The JSON file is empty.")

        if all(isinstance(item, dict) for item in data):
            df = pd.json_normalize(data)
        else:
            df = pd.DataFrame(data)

    elif isinstance(data, dict):
        if not data:
            raise ValueError("The JSON file is empty.")

        # Handle objects containing equally sized lists
        if all(isinstance(value, list) for value in data.values()):
            try:
                df = pd.DataFrame(data)
            except ValueError:
                df = pd.json_normalize(data)
        else:
            df = pd.json_normalize(data)

    else:
        raise ValueError(
            "Unsupported JSON structure. "
            "Expected a JSON object or array."
        )

    if df.empty:
        raise ValueError("No tabular records found in JSON.")

    return df


# --------------------------------------------------
# READ EXCEL DATA
# --------------------------------------------------

def read_excel_file(uploaded_file, sheet_name=0):
    """
    Read an Excel file.

    sheet_name can be:
    - Sheet name
    - Sheet index
    """

    uploaded_file.seek(0)

    try:
        df = pd.read_excel(
            uploaded_file,
            sheet_name=sheet_name
        )

    except ImportError as error:
        raise ImportError(
            "Excel engine missing. Install the required "
            "package using: python -m pip install xlrd"
        ) from error

    if df.empty:
        raise ValueError("The selected Excel sheet is empty.")

    return df


# --------------------------------------------------
# MAIN CONVERSION FUNCTION
# --------------------------------------------------

def convert_to_csv(uploaded_file, file_name, sheet_name=0):
    """
    Convert JSON or Excel input into CSV.

    Parameters:
        uploaded_file: Uploaded file or file-like object
        file_name: Original filename
        sheet_name: Excel sheet name or index

    Returns:
        df: Converted pandas DataFrame
        csv_data: CSV file as bytes
    """

    extension = Path(file_name).suffix.lower()

    if extension not in SUPPORTED_FORMATS:
        raise ValueError(
            f"Unsupported format: {extension}. "
            "Upload a JSON or Excel file."
        )

    if extension == ".json":
        df = read_json_file(uploaded_file)

    elif extension in {".xlsx", ".xls"}:
        df = read_excel_file(
            uploaded_file,
            sheet_name=sheet_name
        )

    if df.empty:
        raise ValueError("The converted dataset is empty.")

    csv_data = df.to_csv(
        index=False,
        encoding="utf-8-sig"
    ).encode("utf-8-sig")

    return df, csv_data


# --------------------------------------------------
# STANDALONE FILE CONVERSION
# --------------------------------------------------

def convert_file_to_csv(input_path, output_path, sheet_name=0):
    """
    Convert a local JSON or Excel file into a CSV file.
    """

    input_path = Path(input_path)
    output_path = Path(output_path)

    if not input_path.exists():
        raise FileNotFoundError(
            f"Input file not found: {input_path}"
        )

    with input_path.open("rb") as file:
        df, csv_data = convert_to_csv(
            file,
            input_path.name,
            sheet_name
        )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    output_path.write_bytes(csv_data)

    return {
        "output_file": output_path,
        "records": len(df),
        "columns": len(df.columns),
        "file_size_mb": round(
            output_path.stat().st_size / (1024 * 1024),
            2
        )
    }
