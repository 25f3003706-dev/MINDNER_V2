"""Database connection management and dynamic SQLite schema inspection utilities."""

import os
import sqlite3
from contextlib import contextmanager
from typing import Any, Dict, Generator, List, Optional
import pandas as pd

from app.core.config import settings
from app.core.logging_config import get_logger

logger = get_logger("database")


def get_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    """Creates a configured SQLite database connection."""
    target_path = str(settings.absolute_db_path if db_path is None else db_path)
    os.makedirs(os.path.dirname(os.path.abspath(target_path)), exist_ok=True)

    conn = sqlite3.connect(
        target_path,
        timeout=20.0,
        detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
    )
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    return conn


@contextmanager
def get_db_connection(db_path: Optional[str] = None) -> Generator[sqlite3.Connection, None, None]:
    """Context manager for safe database connections with automatic commit and rollback."""
    conn = get_connection(db_path)
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Database transaction rollback due to error: {e}")
        raise
    finally:
        conn.close()


def get_db() -> Generator[sqlite3.Connection, None, None]:
    """FastAPI Dependency for database sessions."""
    with get_db_connection() as conn:
        yield conn


# =====================================================================
# AUTOMATIC DATABASE TABLE DISCOVERY & SCHEMA INSPECTION
# =====================================================================

def get_table_names(db_path: Optional[str] = None) -> List[str]:
    """Discovers all non-system user table names in the SQLite database."""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        query = """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
              AND name NOT LIKE 'sqlite_%'
            ORDER BY name;
        """
        cursor.execute(query)
        return [row["name"] for row in cursor.fetchall()]


def get_table_schema(table_name: str, db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Inspects column definitions for a given table using PRAGMA table_info."""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        # Safe table identifier query
        cursor.execute(f"PRAGMA table_info('{table_name}');")
        rows = cursor.fetchall()
        return [
            {
                "cid": row["cid"],
                "name": row["name"],
                "type": row["type"],
                "notnull": bool(row["notnull"]),
                "default_value": row["dflt_value"],
                "pk": bool(row["pk"]),
            }
            for row in rows
        ]


def get_primary_keys(table_name: str, db_path: Optional[str] = None) -> List[str]:
    """Retrieves primary key column names for a given table."""
    columns = get_table_schema(table_name, db_path)
    return [col["name"] for col in columns if col["pk"]]


def get_foreign_keys(table_name: str, db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieves foreign key definitions and relationships for a table using PRAGMA foreign_key_list."""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA foreign_key_list('{table_name}');")
        rows = cursor.fetchall()
        return [
            {
                "id": row["id"],
                "seq": row["seq"],
                "target_table": row["table"],
                "from_column": row["from"],
                "to_column": row["to"],
                "on_update": row["on_update"],
                "on_delete": row["on_delete"],
            }
            for row in rows
        ]


def inspect_database(db_path: Optional[str] = None) -> Dict[str, Any]:
    """Comprehensive inspection of database tables, columns, PKs, FKs, and row counts."""
    tables = get_table_names(db_path)
    report: Dict[str, Any] = {
        "database_path": str(settings.absolute_db_path if db_path is None else db_path),
        "total_tables": len(tables),
        "tables": {},
    }

    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        for tbl in tables:
            cursor.execute(f'SELECT COUNT(*) as cnt FROM "{tbl}"')
            count = cursor.fetchone()["cnt"]
            cols = get_table_schema(tbl, db_path)
            fks = get_foreign_keys(tbl, db_path)
            pks = [c["name"] for c in cols if c["pk"]]

            report["tables"][tbl] = {
                "row_count": count,
                "columns": cols,
                "primary_keys": pks,
                "foreign_keys": fks,
            }

    return report


def load_all_tables(db_path: Optional[str] = None) -> Dict[str, pd.DataFrame]:
    """Automatically loads every table into a dictionary of Pandas DataFrames."""
    target_path = str(settings.absolute_db_path if db_path is None else db_path)
    conn = get_connection(target_path)
    tables = get_table_names(target_path)
    data: Dict[str, pd.DataFrame] = {}

    try:
        for table in tables:
            data[table] = pd.read_sql(f'SELECT * FROM "{table}"', conn)
    finally:
        conn.close()

    return data
