import sqlite3
import pytest

from src.companies import add_company, get_all_companies, update_company
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

# Teste 6: Atualizar os dados de uma empresa existente


def test_update_company(tmp_path):
    """Testa a atualização dos dados de uma empresa"""

    database_path = tmp_path / "test.db"
    initialize_database(database_path)

    company_id = add_company(
        "LVMH", "Luxury", "EUR", database_path
    )

    update_company(
        company_id, "LVMH Group", "Luxury Goods", "EUR", database_path
    )

    companies = get_all_companies(database_path)

    assert companies == [
        (company_id, "LVMH Group", "Luxury Goods", "EUR")
    ]

# Teste 7: Atualização de uma empresa inexistente


def test_update_nonexistent_company(tmp_path):
    """Testa a atualização de uma empresa inexistente"""

    database_path = tmp_path / "test.db"
    initialize_database(database_path)

    with pytest.raises(ValueError, match="A empresa não existe."):
        update_company(
            999, "Empresa Teste", "Luxury", "EUR", database_path
        )

# Teste 8: Testar os campos obrigatórios vazios


@pytest.mark.parametrize(
    "name, sector, currency, expected_error",
    [
        ("", "Luxury", "EUR", "O nome da empresa é obrigatório."),
        ("LVMH", "", "EUR", "O setor da empresa é obrigatório."),
        ("LVMH", "Luxury", "", "A moeda da empresa é obrigatória."),
    ]
)
def test_update_company_empty_fields(
    tmp_path, name, sector, currency, expected_error
):
    """Testa a atualização com campos obrigatórios vazios."""

    database_path = tmp_path / "test.db"
    initialize_database(database_path)

    company_id = add_company(
        "LVMH", "Luxury", "EUR", database_path
    )

    with pytest.raises(ValueError, match=expected_error):
        update_company(
            company_id, name, sector, currency, database_path
        )

# Teste 9: Testar a normalização dos valores

def test_update_company_normalizes_inputs(tmp_path):
    """Testa a normalização dos dados durante a atualização."""

    database_path = tmp_path / "test.db"
    initialize_database(database_path)

    company_id = add_company(
        "LVMH", "Luxury", "EUR", database_path
    )

    update_company(
        company_id, " Kering ", " Luxury ", " eur ", database_path
    )

    companies = get_all_companies(database_path)

    assert companies == [
        (company_id, "Kering", "Luxury", "EUR")
    ]

# Teste 10: Testar a alteração da moeda sem registos financeiros

def test_update_company_currency_without_financial_records(tmp_path):
    """Testa a alteração da moeda sem registos financeiros."""

    database_path = tmp_path / "test.db"
    initialize_database(database_path)

    company_id = add_company(
        "LVMH", "Luxury", "EUR", database_path
    )

    update_company(
        company_id, "LVMH", "Luxury", "USD", database_path
    )

    companies = get_all_companies(database_path)

    assert companies == [
        (company_id, "LVMH", "Luxury", "USD")
    ]

# Testar 11: Impedir a alteração da moeda com registos financeiros

def test_update_company_currency_with_financial_records(tmp_path):
    """Testa o bloqueio da alteração da moeda com registos financeiros."""

    database_path = tmp_path / "test.db"
    initialize_database(database_path)

    company_id = add_company(
        "LVMH", "Luxury", "EUR", database_path
    )

    with get_connection(database_path) as connection:
        connection.execute(
            """
            INSERT INTO financial_record (
                company_id, fiscal_year
            )
            VALUES (?, ?)
            """,
            (company_id, 2025)
        )

    with pytest.raises(
        ValueError,
        match="Não é possível atualizar a moeda de uma empresa com registos financeiros associados."
    ):
        update_company(
            company_id, "LVMH", "Luxury", "USD", database_path
        )