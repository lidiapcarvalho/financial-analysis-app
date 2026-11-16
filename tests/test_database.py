import sqlite3
from pathlib import Path

import pytest

from src.database import (
    initialize_database,
    get_connection,
    migrate_database
)
from src.companies import add_company, get_all_companies

# Teste 1: Verifica se as tabelas principais existem na base de dados do projeto


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

# Teste 2: Verifica se a inicialização cria a tabelas numa base de dados nova


def test_initialize_database_creates_tables(tmp_path):

    database_path = tmp_path / "test_database.db"

    initialize_database(database_path)

    with sqlite3.connect(database_path) as connection:
        tables = connection.execute(
            "SELECT name FROM sqlite_master "
            "WHERE type = 'table' ORDER BY name"
        ).fetchall()

    table_names = [table[0] for table in tables]

    assert "company" in table_names
    assert "financial_record" in table_names

# Teste 3: Verifica se é possível inserir e consultar um registo financeiro associado a uma empresa


def test_insert_company_and_financial_record(tmp_path):

    database_path = tmp_path / "test_insert.db"
    initialize_database(database_path)

    with sqlite3.connect(database_path) as connection:
        cursor = connection.execute(
            """
            INSERT INTO company (name, sector)
            VALUES (?, ?)
            """,
            ("LVMH", "Luxury")
        )

        company_id = cursor.lastrowid

        connection.execute(
            """
            INSERT INTO financial_record (
                company_id,
                fiscal_year,
                period_end,
                currency,
                unit,
                revenue,
                operating_income,
                net_income,
                total_assets,
                total_liabilities
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (company_id, 2025, "2025-12-31", "EUR",
             "millions", 80000, 15000, 10000, 20000, 10000)
        )

        record = connection.execute(
            """
            SELECT company_id, fiscal_year, revenue
            FROM financial_record
            """
        ).fetchone()

    assert record == (company_id, 2025, 80000)

# Teste 4: Verifica se a base de dados impede registos financeiros duplicados para a mesma empresa e ano fiscal


def test_cannot_insert_duplicate_financial_record(tmp_path):

    database_path = tmp_path / "test_duplicate.db"
    initialize_database(database_path)

    with sqlite3.connect(database_path) as connection:
        cursor = connection.execute(
            """
            INSERT INTO company (name, sector)
            VALUES (?, ?)
            """,
            ("LVMH", "Luxury")
        )

        company_id = cursor.lastrowid

        connection.execute(
            """
            INSERT INTO financial_record (
                company_id,
                fiscal_year,
                period_end,
                currency,
                unit,
                revenue,
                operating_income,
                net_income,
                total_assets,
                total_liabilities
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (company_id, 2025, "2025-12-31", "EUR",
                "millions", 80000, 15000, 10000, 20000, 10000)
        )

        try:
            connection.execute(
                """
                INSERT INTO financial_record (company_id, fiscal_year)
                VALUES (?, ?)
                """,
                (company_id, 2025)
            )
        except sqlite3.IntegrityError:
            pass
        else:
            raise AssertionError(
                "A base de dados permitiu um registo duplicado."
            )

# Teste 5: Verifica se a chave estrangeira impede registos associados a empresas inexistentes


def test_cannot_insert_record_for_nonexistent_company(tmp_path):

    database_path = tmp_path / "test_foreign_key.db"
    initialize_database(database_path)

    with get_connection(database_path) as connection:
        try:
            connection.execute(
                """
                INSERT INTO financial_record (company_id, fiscal_year)
                VALUES (?, ?)
                """,
                (999, 2025)
            )
        except sqlite3.IntegrityError:
            pass
        else:
            raise AssertionError(
                "A base de dados permitiu um registo sem empresa associada."
            )

# Teste 6: Verifica se a inicialização cria a pasta e a base de dados


def test_initialize_database_creates_missing_directory(tmp_path):

    database_path = tmp_path / "new_folder" / "test.db"

    initialize_database(database_path)

    assert database_path.parent.exists()
    assert database_path.exists()


# Teste 7: Verifica se uma nova base de dados é criada na versão 3
# e contém a coluna notes

def test_new_database_has_version_3_and_notes(tmp_path):

    database_path = tmp_path / "test_version_3.db"
    initialize_database(database_path)

    with get_connection(database_path) as connection:

        version = connection.execute(
            "PRAGMA user_version"
        ).fetchone()[0]

        columns = [
            column[1]
            for column in connection.execute(
                "PRAGMA table_info(saved_comparison)"
            ).fetchall()
        ]

    assert version == 3
    assert "notes" in columns


# Teste 8: Verifica se uma base de dados v2 é migrada para v3

def test_migrate_database_v2_to_v3(tmp_path):

    database_path = tmp_path / "test_migration.db"

    # Cria uma estrutura simplificada da versão 2
    with sqlite3.connect(database_path) as connection:

        connection.execute("""
            CREATE TABLE company (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                sector TEXT NOT NULL
            )
        """)

        connection.execute("""
            CREATE TABLE saved_comparison (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)

        connection.execute("PRAGMA user_version = 2")

    # Executa a migração
    migrate_database(database_path)

    with get_connection(database_path) as connection:

        version = connection.execute(
            "PRAGMA user_version"
        ).fetchone()[0]

        columns = [
            column[1]
            for column in connection.execute(
                "PRAGMA table_info(saved_comparison)"
            ).fetchall()
        ]

    assert version == 3
    assert "notes" in columns
