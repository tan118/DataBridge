
from pathlib import Path
import pandas as pd


def extract_csv(file_path, encoding="utf-8", **kwargs):
    """
    Extract data from a CSV file using Pandas.

    Parameters:
        file_path: Location of the CSV file.
        encoding: File encoding (default: utf-8).
        kwargs: Additional Pandas read_csv options.

    Returns:
        pandas DataFrame containing extracted data.
    """

    path = Path(file_path)

    # Step 1: Check file existence
    if not path.exists():
        raise FileNotFoundError(
            f"CSV file not found: {path}"
        )

    # Step 2: Check file extension
    if path.suffix.lower() != ".csv":
        raise ValueError(
            "Invalid file format. Please provide a CSV file."
        )

    # Step 3: Read the CSV
    try:
        df = pd.read_csv(
            path,
            encoding=encoding,
            **kwargs
        )

    except UnicodeDecodeError as error:
        raise ValueError(
            "Unable to decode the CSV. Check its encoding."
        ) from error

    except pd.errors.EmptyDataError as error:
        raise ValueError(
            "The CSV file is empty."
        ) from error

    # Step 4: Validate extracted data
    if df.empty:
        raise ValueError(
            "The CSV contains no data records."
        )

    print("CSV extraction successful!")
    print(f"File: {path.name}")
    print(f"Rows extracted: {df.shape[0]}")
    print(f"Columns extracted: {df.shape[1]}")

    return df


# Standalone testing
if __name__ == "__main__":

    project_root = Path(__file__).resolve().parent.parent

    csv_path = project_root / "data" / "raw" / "online_retail.csv"

    extracted_data = extract_csv(csv_path)

    print("\n--- EXTRACTED DATA PREVIEW ---")
    print(extracted_data.head())

    print("\n--- COLUMN INFORMATION ---")
    print(extracted_data.info())
