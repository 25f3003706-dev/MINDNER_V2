import sqlite3
from pathlib import Path


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

DB_PATH = BASE_DIR / "caregiver.db"

SCHEMA_PATH = BASE_DIR / "schema.sql"


# ============================================================
# CREATE DATABASE
# ============================================================

def create_database():

    print("=" * 70)
    print("MINDNER DATABASE CREATION")
    print("=" * 70)

    # --------------------------------------------------------
    # Delete old database
    # --------------------------------------------------------

    if DB_PATH.exists():

        print("\nRemoving old caregiver.db...")

        DB_PATH.unlink()

        print("✓ Old database deleted")

    # --------------------------------------------------------
    # Check schema
    # --------------------------------------------------------

    if not SCHEMA_PATH.exists():

        print(
            f"\nERROR: schema.sql not found:\n{SCHEMA_PATH}"
        )

        return

    # --------------------------------------------------------
    # Create database
    # --------------------------------------------------------

    print("\nCreating new caregiver.db...")

    connection = sqlite3.connect(DB_PATH)

    connection.execute(
        "PRAGMA foreign_keys = ON;"
    )

    # --------------------------------------------------------
    # Read schema
    # --------------------------------------------------------

    with open(
        SCHEMA_PATH,
        "r",
        encoding="utf-8"
    ) as file:

        schema = file.read()

    # --------------------------------------------------------
    # Execute schema
    # --------------------------------------------------------

    try:

        connection.executescript(schema)

        connection.commit()

        print("✓ All tables created successfully")

    except sqlite3.Error as error:

        connection.rollback()

        print(
            f"\nERROR while creating database:\n{error}"
        )

        connection.close()

        return

    # --------------------------------------------------------
    # Verify tables
    # --------------------------------------------------------

    cursor = connection.cursor()

    cursor.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
        AND name NOT LIKE 'sqlite_%'
        ORDER BY name;
    """)

    tables = [
        row[0]
        for row in cursor.fetchall()
    ]

    print("\n" + "=" * 70)
    print("TABLES CREATED")
    print("=" * 70)

    for number, table in enumerate(
        tables,
        start=1
    ):

        print(
            f"{number:2}. {table}"
        )

    print("=" * 70)

    print(
        f"Total tables created: {len(tables)}"
    )

    connection.close()

    print(
        f"\n✓ Database created at:\n{DB_PATH}"
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    create_database()