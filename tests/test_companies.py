import sqlite3
import pytest

from src.companies import add_company, get_all_companies
from src.database import initialize_database, get_connection

# Teste 1: Verifica se a função devolve as empresas registadas, com os respetivos dados


def test_get_all_companies_returns_registered_companies(tmp_path):

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

# Teste 2: Verifica se a o registo de uma empresa devolve o seu identificador e guarda os dados corretamente


def test_add_company_returns_company_id(tmp_path):

    database_path = tmp_path / "test_add_company.db"
    initialize_database(database_path)

    company_id = add_company(
        "LVMH",
        "Luxury",
        "EUR",
        database_path
    )

    companies = get_all_companies(database_path)

    assert company_id == 1
    assert len(companies) == 1
    assert companies[0][1:] == ("LVMH", "Luxury", "EUR")

# Teste 3: Verifica se a função impede o registo de empresas com nomes duplicados


def test_add_company_rejects_duplicate_name(tmp_path):

    database_path = tmp_path / "test_duplicate_company.db"
    initialize_database(database_path)

    add_company("LVMH", "Luxury", "EUR", database_path)

    with pytest.raises(sqlite3.IntegrityError):
        add_company("LVMH", "Luxury", "EUR", database_path)

# Teste 4: Verifica se a função rejeita empresas sem nome, setor ou moeda


def test_add_company_rejects_empty_required_fields(tmp_path):

    database_path = tmp_path / "test_empty_company.db"
    initialize_database(database_path)

    invalid_companies = [
        ("", "Luxury", "EUR"),
        ("LVMH", "", "EUR"),
        ("LVMH", "Luxury", "")
    ]

    for name, sector, currency in invalid_companies:
        with pytest.raises(ValueError):
            add_company(
                name,
                sector,
                currency,
                database_path
            )

# Teste 5: Verifica se a função remove espaços desnecessários e converte a moeda para maiúsculas


def test_add_company_normalizes_input_data(tmp_path):
    database_path = tmp_path / "test.db"
    initialize_database(database_path)

    add_company(
        "  LVMH  ",
        "  Luxury  ",
        " eur ",
        database_path
    )

    companies = get_all_companies(database_path)

    assert companies[0][1:] == ("LVMH", "Luxury", "EUR")
