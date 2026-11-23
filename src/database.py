
import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError


# Load environment variables from project root
project_root = Path(__file__).resolve().parent.parent
load_dotenv(project_root / ".env")


def get_database_engine():

    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT")
    database = os.getenv("DB_NAME")
    username = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")

    if not all([host, port, database, username, password]):
        raise ValueError("Missing database configuration in .env")

    connection_url = (
    f"postgresql+pg8000://{username}:{password}"
    f"@{host}:{port}/{database}"
)

    engine = create_engine(
        connection_url,
        pool_pre_ping=True
    )

    return engine


def test_connection():

    engine = get_database_engine()

    try:
        with engine.connect() as connection:
            result = connection.execute(
                text("SELECT current_database(), version()")
            )

            database_name, version = result.fetchone()

            print("PostgreSQL connection successful!")
            print(f"Database: {database_name}")
            print(f"Version: {version}")

    except SQLAlchemyError as error:
        print(f"Database connection failed: {error}")

    finally:
        engine.dispose()


if __name__ == "__main__":
    test_connection()
