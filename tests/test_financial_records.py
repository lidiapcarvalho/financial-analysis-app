import pytest
import sqlite3

from src.financial_records import (
    get_all_financial_records,
    add_financial_record,
    update_financial_record,
    delete_financial_record,
    _validate_fiscal_year,
    _validate_non_negative_value,
    _validate_numeric_value
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

# Teste 6: Validação do ano fiscal


@pytest.mark.parametrize("fiscal_year", [1900, 2025, 2100])
def test_validate_fiscal_year_valid(fiscal_year):
    """Testa anos fiscais válidos."""
    _validate_fiscal_year(fiscal_year)


@pytest.mark.parametrize("fiscal_year", [1899, 2101])
def test_validate_fiscal_year_out_of_range(fiscal_year):
    """Testa anos fiscais fora do intervalo permitido."""
    with pytest.raises(ValueError):
        _validate_fiscal_year(fiscal_year)


@pytest.mark.parametrize("fiscal_year", [2025.5, "2025", True, False])
def test_validate_fiscal_year_invalid_type(fiscal_year):
    """Testa anos fiscais com tipos inválidos."""
    with pytest.raises(ValueError):
        _validate_fiscal_year(fiscal_year)

# Teste 7: Validação de valores financeiros obrigatórios e não negativos


@pytest.mark.parametrize(
    "value",
    [0, 1000, 250.50]
)
def test_validate_non_negative_value_valid(value):
    """Testa valores financeiros válidos."""
    _validate_non_negative_value(value, "revenue")


@pytest.mark.parametrize(
    "value",
    [-1, -1000]
)
def test_validate_non_negative_value_negative(value):
    """Testa valores financeiros negativos."""
    with pytest.raises(ValueError):
        _validate_non_negative_value(value, "revenue")


@pytest.mark.parametrize(
    "value",
    [None, "1000", True, False]
)
def test_validate_non_negative_value_invalid_type(value):
    """Testa tipos de dados inválidos."""
    with pytest.raises(ValueError):
        _validate_non_negative_value(value, "revenue")


@pytest.mark.parametrize(
    "value",
    [float("nan"), float("inf"), float("-inf")]
)
def test_validate_non_negative_value_not_finite(value):
    """Testa valores não finitos."""
    with pytest.raises(ValueError):
        _validate_non_negative_value(value, "revenue")

# Teste 8: Validação de valores financeiros obrigatórios que podem ser negativos


@pytest.mark.parametrize(
    "value",
    [-1000, -250.50, 0, 1000, 250.50]
)
def test_validate_numeric_value_valid(value):
    """Testa valores numéricos válidos, incluindo negativos."""
    _validate_numeric_value(value, "net_income")


@pytest.mark.parametrize(
    "value",
    [None, "1000", True, False]
)
def test_validate_numeric_value_invalid_type(value):
    """Testa tipos de dados inválidos."""
    with pytest.raises(ValueError):
        _validate_numeric_value(value, "net_income")


@pytest.mark.parametrize(
    "value",
    [float("nan"), float("inf"), float("-inf")]
)
def test_validate_numeric_value_not_finite(value):
    """Testa valores não finitos."""
    with pytest.raises(ValueError):
        _validate_numeric_value(value, "net_income")

# Teste 9: Rejeitção de anos fiscais inválidos ao criar registos


@pytest.mark.parametrize(
    "fiscal_year",
    [1899, 2101, 2025.5, "2025", True]
)
def test_add_financial_record_invalid_fiscal_year(tmp_path, fiscal_year):
    """Testa a rejeição de anos fiscais inválidos ao criar registos."""

    database_path = tmp_path / "test_financial_record.db"
    initialize_database(database_path)

    company_id = add_company("LVMH", "Luxury", "EUR", database_path)

    with pytest.raises(ValueError):
        add_financial_record(
            company_id, fiscal_year, 1000.0, 250.0, 150.0,
            2000.0, 1200.0, 800.0, database_path
        )

    assert get_all_financial_records(database_path) == []


# Teste 10: Rejeição de valores financeiros inválidos

@pytest.mark.parametrize(
    "field_values",
    [
        {"revenue": -100},
        {"operating_income": float("nan")},
        {"net_income": None},
        {"total_assets": -100},
        {"total_liabilities": float("inf")},
        {"equity": "800"},
    ]
)
def test_add_financial_record_invalid_financial_values(tmp_path, field_values):
    """Testa a rejeição de valores financeiros inválidos."""

    database_path = tmp_path / "test_financial_record.db"
    initialize_database(database_path)

    company_id = add_company("LVMH", "Luxury", "EUR", database_path)

    financial_values = {
        "revenue": 1000.0,
        "operating_income": 250.0,
        "net_income": 150.0,
        "total_assets": 2000.0,
        "total_liabilities": 1200.0,
        "equity": 800.0,
    }

    financial_values.update(field_values)

    with pytest.raises(ValueError):
        add_financial_record(
            company_id,
            2025,
            financial_values["revenue"],
            financial_values["operating_income"],
            financial_values["net_income"],
            financial_values["total_assets"],
            financial_values["total_liabilities"],
            financial_values["equity"],
            database_path,
        )

    assert get_all_financial_records(database_path) == []

# Teste 11: Testa a criação de registos com resultados financeiros negativos


def test_add_financial_record_accepts_negative_values(tmp_path):
    """Testa a criação de registos com resultados financeiros negativos."""

    database_path = tmp_path / "test_financial_record.db"
    initialize_database(database_path)

    company_id = add_company("LVMH", "Luxury", "EUR", database_path)

    record_id = add_financial_record(
        company_id, 2025, 1000.0, -250.0, -150.0,
        2000.0, 1200.0, -800.0, database_path
    )

    assert record_id is not None

    records = get_all_financial_records(database_path)
    assert len(records) == 1
    assert records[0][5] == -250.0
    assert records[0][6] == -150.0
    assert records[0][9] == -800.0

# Teste 12: Testa a rejeição de anos fiscais inválidos ao atualizar registos


@pytest.mark.parametrize(
    "fiscal_year",
    [1899, 2101, 2025.5, "2025", True]
)
def test_update_financial_record_invalid_fiscal_year(tmp_path, fiscal_year):
    """Testa a rejeição de anos fiscais inválidos ao atualizar registos."""

    database_path = tmp_path / "test_financial_record.db"
    initialize_database(database_path)

    company_id = add_company("LVMH", "Luxury", "EUR", database_path)

    record_id = add_financial_record(
        company_id, 2025, 1000.0, 250.0, 150.0,
        2000.0, 1200.0, 800.0, database_path
    )

    with pytest.raises(ValueError):
        update_financial_record(
            record_id, fiscal_year, 1000.0, 250.0, 150.0,
            2000.0, 1200.0, 800.0, database_path
        )

    records = get_all_financial_records(database_path)
    assert len(records) == 1
    assert records[0][3] == 2025

# Teste 13: Testa a rejeição de valores financeiros inválidos ao atualizar registos


@pytest.mark.parametrize(
    "field_values",
    [
        {"revenue": -100},
        {"operating_income": float("nan")},
        {"net_income": None},
        {"total_assets": -100},
        {"total_liabilities": float("inf")},
        {"equity": "800"},
    ]
)
def test_update_financial_record_invalid_financial_values(tmp_path, field_values):
    """Testa a rejeição de valores financeiros inválidos ao atualizar registos."""

    database_path = tmp_path / "test_financial_record.db"
    initialize_database(database_path)

    company_id = add_company("LVMH", "Luxury", "EUR", database_path)

    record_id = add_financial_record(
        company_id, 2025, 1000.0, 250.0, 150.0,
        2000.0, 1200.0, 800.0, database_path
    )

    financial_values = {
        "revenue": 1000.0,
        "operating_income": 250.0,
        "net_income": 150.0,
        "total_assets": 2000.0,
        "total_liabilities": 1200.0,
        "equity": 800.0,
    }

    financial_values.update(field_values)

    with pytest.raises(ValueError):
        update_financial_record(
            record_id,
            2025,
            financial_values["revenue"],
            financial_values["operating_income"],
            financial_values["net_income"],
            financial_values["total_assets"],
            financial_values["total_liabilities"],
            financial_values["equity"],
            database_path,
        )

    records = get_all_financial_records(database_path)
    assert len(records) == 1
    assert records[0][5] == 250.0
    assert records[0][6] == 150.0
    assert records[0][9] == 800.0


# Teste 14: Testar a duplicação de registos financeiros

def test_add_financial_record_rejects_duplicate_company_and_year(tmp_path):
    database_path = tmp_path / "test.db"
    initialize_database(database_path)

    company_id = add_company(
        "LVMH", "Luxury Goods", "EUR", database_path
    )

    add_financial_record(
        company_id, 2025, 80000, 15000, 10000,
        120000, 50000, 70000, database_path
    )

    with pytest.raises(
        ValueError,
        match="Já existe um registo financeiro para esta empresa e ano fiscal."
    ):
        add_financial_record(
            company_id, 2025, 90000, 16000, 11000,
            130000, 55000, 75000, database_path
        )

    records = get_all_financial_records(database_path)
    assert len(records) == 1

# Teste 15: Impedir que a atualização cria um registo duplicado


def test_update_financial_record_rejects_duplicate_company_and_year(tmp_path):
    database_path = tmp_path / "test.db"
    initialize_database(database_path)

    company_id = add_company(
        "LVMH", "Luxury Goods", "EUR", database_path
    )

    first_record_id = add_financial_record(
        company_id, 2024, 80000, 15000, 10000,
        120000, 50000, 70000, database_path
    )

    add_financial_record(
        company_id, 2025, 90000, 16000, 11000,
        130000, 55000, 75000, database_path
    )

    with pytest.raises(
        ValueError,
        match="Já existe um registo financeiro para esta empresa e ano fiscal."
    ):
        update_financial_record(
            first_record_id, 2025, 85000, 15500, 10500,
            125000, 52000, 73000, database_path
        )

    records = get_all_financial_records(database_path)

    assert len(records) == 2
    assert records[0][3] == 2025
    assert records[1][3] == 2024
