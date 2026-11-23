
from pathlib import Path
import re
import pandas as pd

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

try:
    from .database import get_database_engine
except ImportError:
    from database import get_database_engine


def load_dataframe(
    df,
    table_name,
    if_exists="replace",
    chunksize=1000
):
    """
    Load a DataFrame into PostgreSQL.

    if_exists:
        replace = Replace existing table.
        append  = Add records to existing table.
    """

    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", table_name):
        raise ValueError("Invalid PostgreSQL table name.")

    if if_exists not in ("replace", "append"):
        raise ValueError("Choose replace or append.")

    if df.empty:
        raise ValueError("Cannot load an empty dataset.")

    engine = get_database_engine()

    total_rows = len(df)
    loaded_rows = 0

    try:
        print("\nConnecting to PostgreSQL...")

        with engine.begin() as connection:

            print("Connection successful!")

            for start in range(0, total_rows, chunksize):

                end = min(start + chunksize, total_rows)
                batch = df.iloc[start:end]

                batch.to_sql(
                    name=table_name,
                    con=connection,
                    if_exists=(
                        "replace"
                        if if_exists == "replace" and start == 0
                        else "append"
                    ),
                    index=False,
                    method="multi"
                )

                loaded_rows += len(batch)

                print(
                    f"Loaded {loaded_rows:,}/{total_rows:,} records"
                )

            result = connection.execute(
                text(f'SELECT COUNT(*) FROM "{table_name}"')
            )

            database_rows = result.scalar_one()

        return {
            "table_name": table_name,
            "records_submitted": loaded_rows,
            "database_records": database_rows,
            "status": "Success"
        }

    except SQLAlchemyError as error:
        print(f"Database loading failed: {error}")
        raise

    finally:
        engine.dispose()


if __name__ == "__main__":

    project_root = Path(__file__).resolve().parent.parent

    cleaned_csv = (
        project_root
        / "data"
        / "processed"
        / "cleaned_online_retail.csv"
    )

    df = pd.read_csv(cleaned_csv)

    report = load_dataframe(
        df,
        table_name="online_retail",
        if_exists="replace"
    )

    print("\nDATABASE LOADING REPORT")
    print(report)
