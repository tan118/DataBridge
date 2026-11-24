
import re
import streamlit as st
import pandas as pd

from src.transform import transform_dataframe
from src.load import load_dataframe
from src.convert_to_csv import convert_to_csv, get_excel_sheet_names


# =====================================================
# PAGE CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="DataBridge",
    page_icon="🔗",
    layout="wide"
)

st.title("🔗 DataBridge")
st.subheader("CSV Data Integration, Quality & Conversion Platform")
st.caption(
    "Upload, profile, transform and load datasets into PostgreSQL."
)

st.divider()


# =====================================================
# SIDEBAR
# =====================================================

st.sidebar.title("DataBridge")

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Upload Dataset",
        "Data Profiling",
        "Data Transformation",
        "File Conversion",
        "Database Loading"
    ]
)


# =====================================================
# HELPER FUNCTIONS
# =====================================================

def get_current_dataset():

    if "transformed_df" in st.session_state:
        return st.session_state["transformed_df"]

    if "uploaded_df" in st.session_state:
        return st.session_state["uploaded_df"]

    return None


def get_numeric_columns(df):

    return df.select_dtypes(
        include="number"
    ).columns.tolist()


def get_text_columns(df):

    return df.select_dtypes(
        include=["object", "string"]
    ).columns.tolist()



def make_cleaning_report(report):

    rows = []

    duplicate = report.get("duplicates", {})

    if duplicate:

        keep_method = duplicate.get("keep", "first")

        rows.append({
            "Transformation": "Duplicate removal",
            "Column": "Selected columns",
            "Values affected": duplicate.get(
                "duplicates_removed", 0
            ),
            "Rows removed": duplicate.get(
                "duplicates_removed", 0
            ),
            "Method": f"Keep {keep_method}"
        })

    for column, details in report.get(
        "missing_values", {}
    ).items():

        rows.append({
            "Transformation": "Missing-value handling",
            "Column": column,
            "Values affected": (
                details.get("missing_before", 0)
                - details.get("missing_after", 0)
            ),
            "Rows removed": details.get("rows_removed", 0),
            "Method": details.get("strategy", "Unknown")
        })

    for column, details in report.get(
        "text_standardization", {}
    ).items():

        rows.append({
            "Transformation": "Text standardization",
            "Column": column,
            "Values affected": details.get("values_changed", 0),
            "Rows removed": 0,
            "Method": details.get("operations", "None")
        })

    for column, details in report.get(
        "numeric_values", {}
    ).items():

        rows.append({
            "Transformation": "Negative values",
            "Column": column,
            "Values affected": details.get(
                "negative_values_found", 0
            ),
            "Rows removed": details.get(
                "negative_rows_removed", 0
            ),
            "Method": details.get("negative_action", "keep")
        })

        rows.append({
            "Transformation": "Zero values",
            "Column": column,
            "Values affected": details.get(
                "zero_values_found", 0
            ),
            "Rows removed": details.get(
                "zero_rows_removed", 0
            ),
            "Method": details.get("zero_action", "keep")
        })

    for column, details in report.get(
        "date_standardization", {}
    ).items():

        rows.append({
            "Transformation": "Date standardization",
            "Column": column,
            "Values affected": details.get(
                "invalid_dates_found", 0
            ),
            "Rows removed": details.get("rows_removed", 0),
            "Method": details.get("invalid_action", "keep")
        })

    columns = [
        "Transformation",
        "Column",
        "Values affected",
        "Rows removed",
        "Method"
    ]

    return pd.DataFrame(rows, columns=columns)


# =====================================================
# 1. DASHBOARD
# =====================================================

if page == "Dashboard":

    st.header("Dashboard Overview")

    col1, col2, col3 = st.columns(3)

    col1.metric("ETL Platform", "Ready")
    col2.metric("Database", "PostgreSQL")
    col3.metric("Application", "Active")

    st.divider()

    st.subheader("ETL Workflow")

    for step in [
        "1. Extract CSV Data",
        "2. Profile Dataset",
        "3. Transform & Clean",
        "4. Load into PostgreSQL"
    ]:
        st.success(step)

    if "uploaded_df" in st.session_state:

        df = st.session_state["uploaded_df"]

        st.info(
            f"Current dataset: {len(df):,} rows, "
            f"{len(df.columns)} columns"
        )


# =====================================================
# 2. UPLOAD DATASET
# =====================================================

elif page == "Upload Dataset":

    st.header("Upload CSV Dataset")

    uploaded_file = st.file_uploader(
        "Choose a CSV file",
        type=["csv"]
    )

    if uploaded_file is not None:

        try:

            df = pd.read_csv(uploaded_file)

            st.session_state["uploaded_df"] = df
            st.session_state["transformed_df"] = df.copy()
            st.session_state["uploaded_filename"] = uploaded_file.name

            st.session_state.pop("cleaning_report", None)

            st.success("Dataset uploaded successfully!")

            st.subheader("Dataset Preview")

            st.dataframe(
                df.head(10),
                use_container_width=True
            )

            col1, col2, col3 = st.columns(3)

            col1.metric("Total Rows", f"{len(df):,}")
            col2.metric("Total Columns", len(df.columns))
            col3.metric(
                "Missing Cells",
                f"{df.isna().sum().sum():,}"
            )

        except Exception as error:

            st.error(f"Unable to read CSV: {error}")


# =====================================================
# 3. DATA PROFILING
# =====================================================

elif page == "Data Profiling":

    st.header("Data Profiling")

    df = get_current_dataset()

    if df is not None:

        duplicate_rows = int(df.duplicated().sum())
        missing_cells = int(df.isna().sum().sum())
        rows_with_missing = int(df.isna().any(axis=1).sum())

        unique_values = sum(
            df[column].nunique(dropna=True)
            for column in df.columns
        )

        st.subheader("Data Quality Overview")

        col1, col2, col3 = st.columns(3)
        col4, col5, col6 = st.columns(3)

        col1.metric("Total Rows", f"{len(df):,}")
        col2.metric("Total Columns", f"{len(df.columns):,}")
        col3.metric("Duplicate Rows", f"{duplicate_rows:,}")

        col4.metric("Missing Cells", f"{missing_cells:,}")
        col5.metric("Rows With Missing Values", f"{rows_with_missing:,}")
        col6.metric("Total Unique Values", f"{unique_values:,}")

        st.divider()

        st.subheader("Column-wise Data Quality")

        profile = pd.DataFrame({
            "Column": df.columns,
            "Data Type": df.dtypes.astype(str).values,
            "Missing Values": df.isna().sum().values,
            "Missing %": (
                df.isna().mean().values * 100
            ).round(2),
            "Unique Values": df.nunique(dropna=True).values
        })

        st.dataframe(
            profile,
            use_container_width=True,
            hide_index=True
        )

        st.subheader("Missing Values by Column")

        st.bar_chart(df.isna().sum())

        numeric_df = df.select_dtypes(include="number")

        if not numeric_df.empty:

            st.subheader("Numerical Statistics")

            st.dataframe(
                numeric_df.describe().T,
                use_container_width=True
            )

        st.subheader("Duplicate Record Preview")

        duplicates = df[df.duplicated(keep=False)]

        if duplicates.empty:

            st.success("No duplicate records found.")

        else:

            st.warning(
                f"{duplicate_rows:,} extra duplicate rows found."
            )

            st.dataframe(
                duplicates.head(20),
                use_container_width=True
            )

    else:

        st.warning("Please upload a dataset first.")


# =====================================================
# 4. DATA TRANSFORMATION
# =====================================================

elif page == "Data Transformation":

    st.header("Data Transformation")

    df = st.session_state.get("uploaded_df")

    if df is None:

        st.warning("Please upload a dataset first.")

    else:

        st.info(
            "Your original uploaded dataset remains unchanged."
        )

        numeric_columns = get_numeric_columns(df)
        text_columns = get_text_columns(df)

        # ---------------------------------------------
        # DUPLICATES
        # ---------------------------------------------

        st.subheader("1. Duplicate Handling")

        remove_dups = st.checkbox(
            "Remove duplicate records",
            value=True
        )

        duplicate_mode = st.radio(
            "Duplicate detection method",
            ["All columns", "Selected columns"],
            horizontal=True
        )

        duplicate_subset = None

        if duplicate_mode == "Selected columns":

            duplicate_subset = st.multiselect(
                "Select columns",
                df.columns.tolist()
            )

        duplicate_keep_option = st.selectbox(
            "Which occurrence should be retained?",
            [
                "First",
                "Last",
                "Remove all duplicate occurrences"
            ]
        )

        duplicate_keep = {
            "First": "first",
            "Last": "last",
            "Remove all duplicate occurrences": False
        }[duplicate_keep_option]

        st.divider()

        # ---------------------------------------------
        # MISSING VALUES
        # ---------------------------------------------

        st.subheader("2. Missing Value Handling")

        missing_columns = st.multiselect(
            "Select columns for missing-value handling",
            df.columns.tolist()
        )

        missing_strategy = st.selectbox(
            "Missing-value strategy",
            [
                "Keep unchanged",
                "Drop rows",
                "Mean",
                "Median",
                "Mode",
                "Custom value"
            ]
        )

        missing_value = None

        if missing_strategy == "Custom value":

            missing_value = st.text_input(
                "Enter replacement value"
            )

        st.divider()

        # ---------------------------------------------
        # TEXT STANDARDIZATION
        # ---------------------------------------------

        st.subheader("3. Text Standardization")

        text_selected = st.multiselect(
            "Select text columns",
            text_columns
        )

        text_operations = st.multiselect(
            "Choose standardization operations",
            [
                "Trim spaces",
                "Lowercase",
                "Uppercase",
                "Title case"
            ]
        )

        st.divider()

        # ---------------------------------------------
        # NUMERIC CLEANING
        # ---------------------------------------------

        st.subheader("4. Numeric Cleaning")

        numeric_selected = st.multiselect(
            "Select numeric columns",
            numeric_columns
        )

        negative_action = st.selectbox(
            "Negative-value handling",
            ["Keep", "Remove rows", "Replace with value"]
        )

        negative_replacement = 0

        if negative_action == "Replace with value":

            negative_replacement = st.number_input(
                "Replace negative values with",
                value=0.0
            )

        zero_action = st.selectbox(
            "Zero-value handling",
            ["Keep", "Remove rows", "Replace with value"]
        )

        zero_replacement = 1

        if zero_action == "Replace with value":

            zero_replacement = st.number_input(
                "Replace zero values with",
                value=1.0
            )

        st.divider()

        # ---------------------------------------------
        # DATE STANDARDIZATION
        # ---------------------------------------------

        st.subheader("5. Date Standardization")

        date_selected = st.multiselect(
            "Select date columns",
            df.columns.tolist()
        )

        day_first = st.checkbox(
            "Interpret dates as day-first (DD/MM/YYYY)",
            value=False
        )

        invalid_date_action = st.selectbox(
            "Invalid-date handling",
            ["Keep as missing values", "Remove rows"]
        )

        st.divider()

        # ---------------------------------------------
        # COLUMN NAMES
        # ---------------------------------------------

        st.subheader("6. Column Name Standardization")

        standardize_columns = st.checkbox(
            "Standardize column names"
        )

        st.divider()

        # ---------------------------------------------
        # APPLY TRANSFORMATIONS
        # ---------------------------------------------

        if st.button(
            "Apply Transformations",
            type="primary",
            use_container_width=True
        ):

            try:

                if duplicate_mode == "Selected columns" and not duplicate_subset:
                    st.error("Select at least one duplicate-detection column.")
                    st.stop()

                missing_rules = {}

                strategy_map = {
                    "Keep unchanged": "keep",
                    "Drop rows": "drop",
                    "Mean": "mean",
                    "Median": "median",
                    "Mode": "mode",
                    "Custom value": "constant"
                }

                for column in missing_columns:

                    strategy = strategy_map[missing_strategy]

                    if strategy in ("mean", "median") and column not in numeric_columns:

                        raise ValueError(
                            f"{strategy.title()} requires a numeric column: {column}"
                        )

                    missing_rules[column] = {
                        "strategy": strategy,
                        "value": missing_value
                    }

                operation_map = {
                    "Trim spaces": "trim",
                    "Lowercase": "lowercase",
                    "Uppercase": "uppercase",
                    "Title case": "titlecase"
                }

                selected_operations = [
                    operation_map[item]
                    for item in text_operations
                ]

                text_rules = {
                    column: selected_operations
                    for column in text_selected
                }

                negative_map = {
                    "Keep": "keep",
                    "Remove rows": "drop",
                    "Replace with value": "replace"
                }

                zero_map = {
                    "Keep": "keep",
                    "Remove rows": "drop",
                    "Replace with value": "replace"
                }

                numeric_rules = {
                    column: {
                        "negative": negative_map[negative_action],
                        "zero": zero_map[zero_action],
                        "negative_replace_value": negative_replacement,
                        "zero_replace_value": zero_replacement
                    }
                    for column in numeric_selected
                }

                date_rules = {
                    column: {
                        "dayfirst": day_first,
                        "invalid": (
                            "drop"
                            if invalid_date_action == "Remove rows"
                            else "keep"
                        )
                    }
                    for column in date_selected
                }

                cleaned_df, report = transform_dataframe(
                    df=df,
                    duplicate_subset=(
                        duplicate_subset
                        if duplicate_mode == "Selected columns"
                        else None
                    ),
                    duplicate_keep=duplicate_keep,
                    missing_rules=missing_rules,
                    numeric_rules=numeric_rules,
                    text_rules=text_rules,
                    date_rules=date_rules,
                    remove_duplicates_enabled=remove_dups,
                    standardize_columns=standardize_columns
                )

                st.session_state["transformed_df"] = cleaned_df
                st.session_state["cleaning_report"] = report

                st.success("Transformations completed successfully!")

            except Exception as error:

                st.error(f"Transformation failed: {error}")

        # ---------------------------------------------
        # RESULTS
        # ---------------------------------------------

        if "cleaning_report" in st.session_state:

            cleaned_df = st.session_state["transformed_df"]
            report = st.session_state["cleaning_report"]

            st.divider()

            st.subheader("Transformation Summary")

            summary = report["summary"]

            col1, col2, col3 = st.columns(3)

            col1.metric(
                "Original Rows",
                f"{summary['original_rows']:,}"
            )

            col2.metric(
                "Final Rows",
                f"{summary['final_rows']:,}"
            )

            col3.metric(
                "Total Rows Removed",
                f"{summary['rows_removed']:,}"
            )

            st.subheader("Before and After Comparison")

            comparison = pd.DataFrame({
                "Metric": [
                    "Total rows",
                    "Total columns",
                    "Duplicate rows",
                    "Missing cells"
                ],
                "Before": [
                    len(df),
                    len(df.columns),
                    int(df.duplicated().sum()),
                    int(df.isna().sum().sum())
                ],
                "After": [
                    len(cleaned_df),
                    len(cleaned_df.columns),
                    int(cleaned_df.duplicated().sum()),
                    int(cleaned_df.isna().sum().sum())
                ]
            })

            st.dataframe(
                comparison,
                use_container_width=True,
                hide_index=True
            )

            st.subheader("Detailed Cleaning Report")

            cleaning_table = make_cleaning_report(report)

            if cleaning_table.empty:

                st.info("No cleaning operations were performed.")

            else:

                st.dataframe(
                    cleaning_table,
                    use_container_width=True,
                    hide_index=True
                )

            st.subheader("Cleaned Dataset Preview")

            st.dataframe(
                cleaned_df.head(20),
                use_container_width=True
            )

            csv_data = cleaned_df.to_csv(
                index=False
            ).encode("utf-8")

            st.download_button(
                "Download Cleaned CSV",
                data=csv_data,
                file_name="cleaned_dataset.csv",
                mime="text/csv",
                use_container_width=True
            )




# =====================================================
# 5. FILE CONVERSION
# =====================================================

elif page == "File Conversion":

    st.header("File Conversion")
    st.caption(
        "Convert JSON and Excel files into standardized CSV files."
    )

    st.info(
        "Supported inputs: JSON (.json), Excel (.xlsx, .xls). "
        "The output format is always CSV."
    )

    uploaded_file = st.file_uploader(
        "Upload a JSON or Excel file",
        type=["json", "xlsx", "xls"],
        key="conversion_uploader"
    )

    if uploaded_file is not None:

        file_extension = uploaded_file.name.rsplit(".", 1)[-1].lower()
        selected_sheet = 0

        st.write(f"**Selected file:** {uploaded_file.name}")

        # Excel workbooks can contain multiple sheets.
        if file_extension in ["xlsx", "xls"]:

            try:
                sheet_names = get_excel_sheet_names(uploaded_file)

                if not sheet_names:
                    st.error("No worksheets were found in this Excel file.")
                    st.stop()

                selected_sheet = st.selectbox(
                    "Select the worksheet to convert",
                    options=sheet_names,
                    key="conversion_sheet_selector"
                )

            except Exception as error:
                st.error(f"Unable to read Excel worksheets: {error}")
                st.stop()

        if st.button(
            "Convert to CSV",
            type="primary",
            use_container_width=True
        ):

            try:
                with st.spinner("Converting file to CSV..."):

                    converted_df, csv_data = convert_to_csv(
                        uploaded_file=uploaded_file,
                        file_name=uploaded_file.name,
                        sheet_name=selected_sheet
                    )

                output_filename = (
                    uploaded_file.name.rsplit(".", 1)[0] + ".csv"
                )

                st.session_state["converted_df"] = converted_df
                st.session_state["converted_csv"] = csv_data
                st.session_state["converted_filename"] = output_filename
                st.session_state["converted_source"] = uploaded_file.name

                st.success("File converted to CSV successfully!")

            except Exception as error:
                st.error(f"File conversion failed: {error}")

        # Show the latest conversion result for the current source file.
        if (
            st.session_state.get("converted_source")
            == uploaded_file.name
            and "converted_csv" in st.session_state
        ):

            converted_df = st.session_state["converted_df"]
            csv_data = st.session_state["converted_csv"]
            output_filename = st.session_state["converted_filename"]

            st.divider()
            st.subheader("Conversion Summary")

            col1, col2, col3 = st.columns(3)

            col1.metric("Total Records", f"{len(converted_df):,}")
            col2.metric("Total Columns", f"{len(converted_df.columns):,}")
            col3.metric(
                "CSV File Size",
                f"{len(csv_data) / (1024 * 1024):.2f} MB"
            )

            st.subheader("Converted Dataset Preview")

            st.dataframe(
                converted_df.head(20),
                use_container_width=True,
                hide_index=True
            )

            st.download_button(
                label="Download Converted CSV",
                data=csv_data,
                file_name=output_filename,
                mime="text/csv",
                type="primary",
                use_container_width=True
            )

    else:
        st.caption(
            "Upload a JSON or Excel file to begin. "
            "CSV files can be uploaded through the Upload Dataset page."
        )


# =====================================================
# 6. DATABASE LOADING
# =====================================================


elif page == "Database Loading":

    st.header("PostgreSQL Database Loading")

    df = get_current_dataset()

    if df is None:

        st.warning("Upload a dataset before loading.")

    else:

        col1, col2 = st.columns(2)

        col1.metric("Records", f"{len(df):,}")
        col2.metric("Columns", f"{len(df.columns):,}")

        table_name = st.text_input(
            "Destination table name",
            value="uploaded_dataset"
        )

        loading_mode = st.radio(
            "Loading mode",
            [
                "Replace existing table",
                "Append to existing table"
            ]
        )

        st.warning(
            "Replace mode deletes and recreates the destination table."
        )

        if st.button(
            "Load into PostgreSQL",
            type="primary",
            use_container_width=True
        ):

            if not re.fullmatch(
                r"[A-Za-z_][A-Za-z0-9_]*",
                table_name
            ):

                st.error("Enter a valid table name.")

            else:

                try:

                    with st.spinner(
                        "Loading records into PostgreSQL..."
                    ):

                        database_report = load_dataframe(
                            df=df,
                            table_name=table_name,
                            if_exists=(
                                "replace"
                                if loading_mode == "Replace existing table"
                                else "append"
                            ),
                            chunksize=1000
                        )

                    st.success("Database loading completed!")

                    col1, col2, col3 = st.columns(3)

                    col1.metric(
                        "Records Submitted",
                        f"{database_report['records_submitted']:,}"
                    )

                    col2.metric(
                        "Database Records",
                        f"{database_report['database_records']:,}"
                    )

                    col3.metric(
                        "Status",
                        database_report["status"]
                    )

                except Exception as error:

                    st.error(f"Database loading failed: {error}")
