
import sqlite3
from pathlib import Path

# Teste 1: Verifica se as tabelas company e financial_record existem na base de dados


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

# Teste 2: Verifica se initialize_database() cria as tabelas necessárias numa base de dados temporária


def test_initialize_database_creates_tables(tmp_path):
    from src.database import initialize_database

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

# Teste 3: Verifica se é possível inserir uma empresa, associar-lhe um registo financeiro e consultar os dados


def test_insert_company_and_financial_record(tmp_path):
    from src.database import initialize_database

    database_path = tmp_path / "test_insert.db"
    initialize_database(database_path)

    with sqlite3.connect(database_path) as connection:
        cursor = connection.execute(
            """
            INSERT INTO company (name, sector, currency)
            VALUES (?, ?, ?)
            """,
            ("LVMH", "Luxury", "EUR")
        )

        company_id = cursor.lastrowid

        connection.execute(
            """
            INSERT INTO financial_record (
                company_id,
                fiscal_year,
                revenue,
                operating_income,
                net_income
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (company_id, 2025, 80000, 15000, 10000)
        )

        record = connection.execute(
            """
            SELECT company_id, fiscal_year, revenue
            FROM financial_record
            """
        ).fetchone()

    assert record == (company_id, 2025, 80000)

# Teste 4: Verifica se a base de dados impede a criação de dois registos financeiros da mesma empresa no mesmo ano fiscal


def test_cannot_insert_duplicate_financial_record(tmp_path):
    from src.database import initialize_database

    database_path = tmp_path / "test_duplicate.db"
    initialize_database(database_path)

    with sqlite3.connect(database_path) as connection:
        cursor = connection.execute(
            """
            INSERT INTO company (name, sector, currency)
            VALUES (?, ?, ?)
            """,
            ("LVMH", "Luxury", "EUR")
        )

        company_id = cursor.lastrowid

        connection.execute(
            """
            INSERT INTO financial_record (company_id, fiscal_year)
            VALUES (?, ?)
            """,
            (company_id, 2025)
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

# Teste 5: Verifica se a chave estrangeira impede a inserção de um registo financeiro associado a uma empresa inexistente


def test_cannot_insert_record_for_nonexistent_company(tmp_path):
    from src.database import get_connection, initialize_database

    database_path = tmp_path / "test_foreign_key,db"
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


def test_get_all_companies_returns_registered_companies(tmp_path):
    from src.companies import get_all_companies
    from src.database import get_connection, initialize_database

    database_path = tmp_path / "test_companies.db"
    initialize_database(database_path)

    with get_connection(database_path) as connection:
        connection.execute(
            """
            INSERT INTO company (name, sector, currency)
            VALUES (?, ?, ?)
            """,
            ("LVMH", "Luxury", "EUR")
        )

    companies = get_all_companies(database_path)

    assert len(companies) == 1
    assert companies[0][1:] == ("LVMH", "Luxury", "EUR")
