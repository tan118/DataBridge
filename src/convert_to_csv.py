
import pandas as pd
from pathlib import Path

# Project root directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Input and output paths
input_file = BASE_DIR / "data" / "raw" / "Online Retail.xlsx"
output_file = BASE_DIR / "data" / "raw" / "online_retail.csv"

print("Starting Excel to CSV conversion...")

# Read Excel file
df = pd.read_excel(input_file, engine="openpyxl")

# Convert and save as CSV
df.to_csv(output_file, index=False, encoding="utf-8")

print("\nConversion completed successfully!")
print("Output file:", output_file.name)
print("Total records:", len(df))
print("Total columns:", len(df.columns))
print("CSV file size:", round(output_file.stat().st_size / (1024 * 1024), 2), "MB")
