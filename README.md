# DataBridge

**DataBridge** is a Python-based data integration and data-quality application built with Streamlit. It helps users inspect, clean, convert, and load tabular datasets through an interactive interface.

## Features

### 1. CSV Data Upload
- Upload CSV datasets.
- Preview records and inspect basic dataset dimensions.
- Keep the original uploaded dataset unchanged while applying transformations to a working copy.

### 2. Data Profiling
- View row and column counts.
- Identify duplicate records.
- Inspect missing values and missing-value percentages.
- Review column data types and unique-value counts.
- View numerical descriptive statistics.

### 3. Data Transformation
- Remove duplicate records using all columns or selected columns.
- Choose whether to retain the first or last occurrence, or remove all duplicate occurrences.
- Handle missing values using options such as dropping rows, mean, median, mode, a custom constant, or keeping values unchanged.
- Standardize text using trimming, lowercase, uppercase, and title case.
- Handle negative and zero numeric values by keeping, removing, or replacing them.
- Standardize dates and choose how to handle invalid dates.
- Standardize column names.
- Review a before-and-after summary and a detailed cleaning report.
- Download the cleaned dataset as CSV.

> **Important:** Duplicate detection on selected columns treats rows with matching values in those columns as duplicates, even if other columns differ. Use this option carefully. For exact duplicate-row removal, select all columns.

### 4. File Conversion
- Convert JSON files to CSV.
- Convert Excel `.xlsx` and `.xls` files to CSV.
- Select a worksheet when converting a multi-sheet Excel workbook.
- Preview converted data and download the resulting CSV.
- CSV is the output format for this conversion feature.

### 5. PostgreSQL Database Loading
- Connect to a PostgreSQL database.
- Load the current dataset into a destination table.
- Choose whether to replace an existing table or append records.
- Review the number of records submitted and the database record count.

## Technology Stack

- **Language:** Python
- **User Interface:** Streamlit
- **Data Processing:** Pandas, NumPy
- **Database:** PostgreSQL
- **Database Access:** SQLAlchemy, Psycopg
- **Excel Support:** OpenPyXL, xlrd
- **Data Export:** CSV

## Project Structure

```text
DataBridge/
│
├── data/
│   ├── raw/                 # Local input datasets
│   └── processed/           # Local processed outputs
│
├── logs/                    # Application logs
│
├── src/
│   ├── extract.py           # CSV extraction
│   ├── profile.py           # Dataset profiling
│   ├── transform.py         # Data cleaning and transformation
│   ├── convert_to_csv.py    # JSON/Excel-to-CSV conversion
│   ├── database.py          # PostgreSQL connection
│   └── load.py              # Load DataFrames into PostgreSQL
│
├── app.py                   # Streamlit application
├── requirements.txt         # Python dependencies
├── .env                     # Local database credentials
└── .gitignore
```

## Prerequisites

- Python 3.10 or newer
- PostgreSQL installed and running
- Git (optional, for cloning the repository)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/tan118/DataBridge.git
cd DataBridge
```

### 2. Create and Activate a Virtual Environment

**Windows PowerShell:**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks script execution for the current terminal session:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
.\.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```bash
python -m pip install -r requirements.txt
```

If the project dependency file does not already include the Excel reader for legacy `.xls` files, install it with:

```bash
python -m pip install xlrd
```

## Configuration

Create a local `.env` file in the project root for the PostgreSQL connection settings expected by `src/database.py`.

Do not commit `.env` or publish database passwords. Configure the variable names to match those read by your `database.py` implementation.

Before using Database Loading, ensure that:

1. PostgreSQL is running.
2. The target database exists.
3. The connection settings in `.env` are correct.
4. The configured database user has permission to create or modify tables.

## Run the Application

From the project root, with the virtual environment activated:

```bash
python -m streamlit run app.py
```

Streamlit will display a local address in the terminal, usually:

```text
http://localhost:8501
```

Open that address in your browser.

## Typical Workflow

1. Upload a CSV file through **Upload Dataset**.
2. Inspect its quality through **Data Profiling**.
3. Choose cleaning operations through **Data Transformation