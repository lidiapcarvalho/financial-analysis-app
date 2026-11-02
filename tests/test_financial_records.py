import pytest

from src.financial_records import (
    get_all_financial_records,
    add_financial_record,
    update_financial_record,
    delete_financial_record
)

from src.companies import add_company
from src.database import initialize_database, get_connection

# Teste 1: Testa a consulta de registos financeiros sem resultados


def test_get_all_financial_records_empty(tmp_path):
    """Testa a consulta quando não existem registos financeiros."""

    database_path = tmp_path / "test_financial_records.db"
    initialize_database(database_path)

    financial_records = get_all_financial_records(database_path)

    assert financial_records == []


# Teste 2: Testa a consulta de registos financeiros com dados das empresas associados

def test_get_all_financial_records_returns_registered_records(tmp_path):
    """Testa a consulta dos registos financeiros com os dados das empresas."""

    database_path = tmp_path / "test_financial_records.db"
    initialize_database(database_path)

    company_id = add_company(
        "LVMH", "Luxury", "EUR", database_path
    )

    with get_connection(database_path) as connection:
        connection.execute(
            """
            INSERT INTO financial_record (
                company_id, fiscal_year, revenue, operating_income,
                net_income, total_assets, total_liabilities, equity
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (company_id, 2025, 1000.0, 250.0, 150.0,
             2000.0, 1200.0, 800.0)
        )

    financial_records = get_all_financial_records(database_path)

    assert len(financial_records) == 1
    assert financial_records[0][1:] == (
        "LVMH", "EUR", 2025,
        1000.0, 250.0, 150.0, 2000.0, 1200.0, 800.0
    )

# Teste 3: Testa a criação de um registo financeiro


def test_add_financial_record(tmp_path):
    """Testa a criação de um registo financeiro."""

    database_path = tmp_path / "test_financial_record.db"
    initialize_database(database_path)

    company_id = add_company(
        "LVMH", "Luxury", "EUR", database_path
    )

    record_id = add_financial_record(
        company_id, 2025, 1000.0, 250.0, 150.0,
        2000.0, 1200.0, 800.0, database_path
    )

    financial_records = get_all_financial_records(database_path)

    assert record_id == 1
    assert len(financial_records) == 1
    assert financial_records[0][3] == 2025
    assert financial_records[0][4] == 1000.0


# Teste 4: Testa a atualização dos dados de um registo financeiro

def test_update_financial_record(tmp_path):
    """Testa a atualização de um registo financeiro."""

    database_path = tmp_path / "test_financial_record.db"
    initialize_database(database_path)

    company_id = add_company(
        "LVMH", "Luxury", "EUR", database_path
    )

    record_id = add_financial_record(
        company_id, 2025, 1000.0, 250.0, 150.0,
        2000.0, 1200.0, 800.0, database_path
    )

    update_financial_record(
        record_id, 2026, 1200.0, 300.0, 180.0,
        2200.0, 1300.0, 900.0, database_path
    )

    financial_records = get_all_financial_records(database_path)

    assert len(financial_records) == 1
    assert financial_records[0] == (
        record_id, "LVMH", "EUR", 2026,
        1200.0, 300.0, 180.0, 2200.0, 1300.0, 900.0
    )

# Teste 5: Testa a eliminação de um registo financeiro


def test_delete_financial_record(tmp_path):
    """Testa a eliminação de um registo financeiro."""

    database_path = tmp_path / "test_financial_record.db"
    initialize_database(database_path)

    company_id = add_company(
        "LVMH", "Luxury", "EUR", database_path
    )

    record_id = add_financial_record(
        company_id, 2025, 1000.0, 250.0, 150.0,
        2000.0, 1200.0, 800.0, database_path
    )

    row_delected = delete_financial_record(
        record_id, database_path
    )

    financial_records = get_all_financial_records(database_path)

    assert row_delected == 1
    assert financial_records == []
