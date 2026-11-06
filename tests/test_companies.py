import sqlite3
import pytest

from src.companies import (
    add_company,
    get_all_companies,
    update_company,
    delete_company
)
from src.database import initialize_database, get_connection

# Teste 1: Verifica se a função devolve as empresas registadas, com os respetivos dados


def test_get_all_companies_returns_registered_companies(tmp_path):

    database_path = tmp_path / "test_companies.db"
    initialize_database(database_path)

    with get_connection(database_path) as connection:
        connection.execute(
            """
            INSERT INTO company (name, sector)
            VALUES (?, ?)
            """,
            ("LVMH", "Luxury")
        )

    companies = get_all_companies(database_path)

    assert len(companies) == 1
    assert companies[0][1:] == ("LVMH", "Luxury")

# Teste 2: Verifica se a o registo de uma empresa devolve o seu identificador e guarda os dados corretamente


def test_add_company_returns_company_id(tmp_path):

    database_path = tmp_path / "test_add_company.db"
    initialize_database(database_path)

    company_id = add_company(
        "LVMH",
        "Luxury",
        database_path
    )

    companies = get_all_companies(database_path)

    assert company_id == 1
    assert len(companies) == 1
    assert companies[0][1:] == ("LVMH", "Luxury")

# Teste 3: Verifica se a função impede o registo de empresas com nomes duplicados


def test_add_company_rejects_duplicate_name(tmp_path):

    database_path = tmp_path / "test_duplicate_company.db"
    initialize_database(database_path)

    add_company("LVMH", "Luxury", database_path)

    with pytest.raises(sqlite3.IntegrityError):
        add_company("LVMH", "Luxury", database_path)

# Teste 4: Verifica se a função rejeita empresas sem nome ou setor


def test_add_company_rejects_empty_required_fields(tmp_path):

    database_path = tmp_path / "test_empty_company.db"
    initialize_database(database_path)

    invalid_companies = [
        ("", "Luxury"),
        ("LVMH", "")
    ]

    for name, sector in invalid_companies:
        with pytest.raises(ValueError):
            add_company(
                name,
                sector,
                database_path
            )

# Teste 5: Verifica se a função remove espaços desnecessários


def test_add_company_normalizes_input_data(tmp_path):
    database_path = tmp_path / "test.db"
    initialize_database(database_path)

    add_company(
        "  LVMH  ",
        "  Luxury  ",
        database_path
    )

    companies = get_all_companies(database_path)

    assert companies[0][1:] == ("LVMH", "Luxury")

# Teste 6: Atualizar os dados de uma empresa existente


def test_update_company(tmp_path):
    """Testa a atualização dos dados de uma empresa"""

    database_path = tmp_path / "test.db"
    initialize_database(database_path)

    company_id = add_company(
        "LVMH", "Luxury", database_path
    )

    update_company(
        company_id, "LVMH Group", "Luxury Goods", database_path
    )

    companies = get_all_companies(database_path)

    assert companies == [
        (company_id, "LVMH Group", "Luxury Goods")
    ]

# Teste 7: Atualização de uma empresa inexistente


def test_update_nonexistent_company(tmp_path):
    """Testa a atualização de uma empresa inexistente"""

    database_path = tmp_path / "test.db"
    initialize_database(database_path)

    with pytest.raises(ValueError, match="A empresa não existe."):
        update_company(
            999, "Empresa Teste", "Luxury", database_path
        )

# Teste 8: Testar os campos obrigatórios vazios


@pytest.mark.parametrize(
    "name, sector, expected_error",
    [
        ("", "Luxury", "O nome da empresa é obrigatório."),
        ("LVMH", "", "O setor da empresa é obrigatório.")
    ]
)
def test_update_company_empty_fields(
    tmp_path, name, sector, expected_error
):
    """Testa a atualização com campos obrigatórios vazios."""

    database_path = tmp_path / "test.db"
    initialize_database(database_path)

    company_id = add_company(
        "LVMH", "Luxury", database_path
    )

    with pytest.raises(ValueError, match=expected_error):
        update_company(
            company_id, name, sector, database_path
        )

# Teste 9: Testar a normalização dos valores


def test_update_company_normalizes_inputs(tmp_path):
    """Testa a normalização dos dados durante a atualização."""

    database_path = tmp_path / "test.db"
    initialize_database(database_path)

    company_id = add_company(
        "LVMH", "Luxury", database_path
    )

    update_company(
        company_id, " Kering ", " Luxury ", database_path
    )

    companies = get_all_companies(database_path)

    assert companies == [
        (company_id, "Kering", "Luxury")
    ]

# Teste 12: Eliminar uma empresa existente sem registos financeiros


def test_delete_company(tmp_path):
    """Testa a eliminação de uma empresa sem registos fianceiros"""

    database_path = tmp_path / "test.db"
    initialize_database(database_path)

    company_id = add_company(
        "LVMH", "Luxury", database_path
    )

    delete_company(company_id, database_path)

    companies = get_all_companies(database_path)

    assert companies == []

# Teste 13: Impedir a elimnação de uma empresa com registos financeiros


def test_delete_company_with_financial_records(tmp_path):
    """Testa o bloqueio da eliminação de uma empresa com registos financeiros."""

    database_path = tmp_path / "test.db"
    initialize_database(database_path)

    company_id = add_company(
        "LVMH", "Luxury", database_path
    )

    with get_connection(database_path) as connection:
        connection.execute(
            """
            INSERT INTO financial_record (
                company_id, 
                fiscal_year,
                period_end,
                currency,
                unit,
                revenue,
                total_assets,
                total_liabilities
                )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                company_id,
                2025,
                "2025-12-31",
                "EUR",
                "millions",
                1000,
                500,
                200
            )
        )

    with pytest.raises(
        ValueError,
        match="Não é possível eliminar uma empresa com registos financeiros associados."
    ):
        delete_company(company_id, database_path)
