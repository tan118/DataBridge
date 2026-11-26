
import os
import ssl
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from sqlalchemy.exc import SQLAlchemyError


# Load environment variables from project root
project_root = Path(__file__).resolve().parent.parent
load_dotenv(project_root / ".env")


def get_config_value(key):
    """
    Read configuration from local .env first.
    If unavailable, read from Streamlit Secrets.
    """

    value = os.getenv(key)

    if value:
        return value

    try:
        return st.secrets.get(key)
    except Exception:
        return None


def get_database_engine():

    host = get_config_value("DB_HOST")
    port = get_config_value("DB_PORT")
    database = get_config_value("DB_NAME")
    username = get_config_value("DB_USER")
    password = get_config_value("DB_PASSWORD")

    if not all([host, port, database, username, password]):
        raise ValueError(
            "Missing database configuration. "
            "Check your .env file or Streamlit Secrets."
        )

    # Build connection URL safely, including special characters in passwords
    connection_url = URL.create(
        drivername="postgresql+pg8000",
        username=username,
        password=password,
        host=host,
        port=int(port),
        database=database
    )

    # Neon requires SSL; local PostgreSQL can use its normal connection
    connect_args = {}

    if "neon.tech" in host:
        connect_args["ssl_context"] = ssl.create_default_context()

    engine = create_engine(
        connection_url,
        pool_pre_ping=True,
        connect_args=connect_args
    )

    return engine


def test_connection():

    engine = None

    try:
        engine = get_database_engine()

        with engine.connect() as connection:

            result = connection.execute(
                text("SELECT current_database(), version()")
            )

            database_name, version = result.fetchone()

            print("PostgreSQL connection successful!")
            print(f"Database: {database_name}")
            print(f"Version: {version}")

    except (SQLAlchemyError, ValueError) as error:
        print(f"Database connection failed: {error}")

    finally:
        if engine:
            engine.dispose()


if __name__ == "__main__":
    test_connection()
