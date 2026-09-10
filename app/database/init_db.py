"""Database initialization and startup diagnostic inspection."""

import os
import sqlite3
from pathlib import Path

from app.core.config import settings
from app.core.logging_config import get_logger
from app.database.connection import get_table_names

logger = get_logger("init_db")

SCHEMA_FILE = Path(__file__).resolve().parent.parent.parent / "database" / "schema.sql"


def init_database(db_path: str = "") -> None:
    """Initializes the database schema if needed and logs the detected tables."""
    target_path = str(settings.absolute_db_path if db_path is None else db_path)
    os.makedirs(os.path.dirname(os.path.abspath(target_path)), exist_ok=True)

    # Initialize schema
    if os.path.exists(SCHEMA_FILE):
        with open(SCHEMA_FILE, "r", encoding="utf-8") as f:
            ddl = f.read()

        conn = sqlite3.connect(target_path)
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.executescript(ddl)
        conn.commit()
        conn.close()

    # Diagnostic inspection of discovered tables
    tables = get_table_names(target_path)
    
    logger.info(f"Database: {target_path}")
    logger.info(f"Discovered {len(tables)} tables in SQLite database:")
    for tbl in tables:
        logger.info(f"  ✓ {tbl}")


if __name__ == "__main__":
    init_database()
