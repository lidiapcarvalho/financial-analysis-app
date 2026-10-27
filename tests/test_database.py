
import sqlite3
from pathlib import Path


def test_database_tables_exist():
    project_dir = Path(__file__).resolve().parent.parent
    database_path = project_dir / "data" / "financial_analysis.db"

    with sqlite3.connect(database_path) as connection:
        tables = connection.execute(
            "SELECT name FROM sqlite_master "
            "WHERE type = 'table' ORDER BY name"
        ).fetchall()

    table_names = [table[0] for table in tables]

    assert "company" in table_names
    assert "financial_record" in table_names
