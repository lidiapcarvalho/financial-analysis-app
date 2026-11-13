import pytest
import sqlite3

from openpyxl import Workbook

from src.import_financial_data import (
    _read_financial_data,
    _get_company_ids,
    _validate_companies,
    _validate_financial_data,
    import_financial_data
)

from src.companies import add_company
from src.financial_records import get_all_financial_records
from src.database import initialize_database
from datetime import datetime


def test_read_financial_data_returns_expected_records():
    records = _read_financial_data()

    assert len(records) == 19
    assert records[0][0] == "LVMH"
    assert records[0][1] == 2020
    assert records[-1][0] == "RICHEMONT"
    assert records[-1][1] == 2026


def test_get_company_ids_returns_expected_companies():

    company_ids = _get_company_ids()

    assert company_ids["lvmh"] == 1
    assert company_ids["kering"] == 2
    assert company_ids["richemont"] == 3
    assert company_ids["prada"] == 4


def test_validate_companies_raises_error_for_unknown_company():
    records = [
        ("LVMH", 2020),
        ("Unknown Company", 2021)
    ]

    company_ids = {
        "lvmh": 1,
        "kering": 2,
        "richemont": 3,
        "prada": 4
    }

    with pytest.raises(ValueError, match="Unknown Company"):
        _validate_companies(records, company_ids)


def test_import_financial_data_imports_all_records(tmp_path):
    database_path = tmp_path / "test.db"
    initialize_database(database_path)

    add_company("LVMH", "Luxury", database_path)
    add_company("Kering", "Luxury", database_path)
    add_company("Richemont", "Luxury", database_path)

    imported_count = import_financial_data(database_path)

    records = get_all_financial_records(database_path)

    assert imported_count == 19
    assert len(records) == 19


def test_read_financial_data_raises_error_if_file_not_found(monkeypatch, tmp_path):
    missing_file = tmp_path / "missing.xlsx"

    monkeypatch.setattr(
        "src.import_financial_data.EXCEL_FILE_PATH",
        missing_file
    )

    with pytest.raises(FileNotFoundError, match="Ficheiro Excel não encontrado"):
        _read_financial_data()


def test_read_financial_data_raises_error_if_headers_are_invalid(
    monkeypatch, tmp_path
):
    invalid_file = tmp_path / "invalid.xlsx"

    workbook = Workbook()
    worksheet = workbook.active
    worksheet.append(["company", "fiscal_year"])
    workbook.save(invalid_file)
    workbook.close()

    monkeypatch.setattr(
        "src.import_financial_data.EXCEL_FILE_PATH",
        invalid_file
    )

    with pytest.raises(ValueError, match="cabeçalhos"):
        _read_financial_data()


def test_import_financial_data_fails_if_company_is_unknown(tmp_path):
    database_path = tmp_path / "test.db"
    initialize_database(database_path)

    add_company("LVMH", "Luxury", database_path)
    add_company("Kering", "Luxury", database_path)

    with pytest.raises(ValueError, match="RICHEMONT"):
        import_financial_data(database_path)

    records = get_all_financial_records(database_path)

    assert records == []


def test_import_financial_data_prevents_duplicate_imports(tmp_path):
    database_path = tmp_path / "test.db"
    initialize_database(database_path)

    add_company("LVMH", "Luxury", database_path)
    add_company("Kering", "Luxury", database_path)
    add_company("Richemont", "Luxury", database_path)

    first_import_count = import_financial_data(database_path)

    assert first_import_count == 19

    with pytest.raises(sqlite3.IntegrityError):
        import_financial_data(database_path)

    records = get_all_financial_records(database_path)

    assert len(records) == 19


def test_validate_financial_data_accepts_valid_records():
    records = [
        (
            "LVMH",
            2025,
            datetime(2025, 12, 31),
            "EUR",
            "millions",
            80.807,
            18.7,
            12.5,
            150.0,
            70.0,
            80.0,
            75.0
        )
    ]

    _validate_financial_data(records)


def test_validate_financial_data_rejects_empty_company_name():
    records = [
        (
            "",
            2025,
            datetime(2025, 12, 31),
            "EUR",
            "millions",
            80.807,
            18.7,
            12.5,
            150.0,
            70.0,
            80.0,
            75.0
        )
    ]

    with pytest.raises(ValueError, match="Nome da empresa inválido"):
        _validate_financial_data(records)


def test_validate_financial_data_rejects_invalid_fiscal_year():
    records = [
        (
            "LVMH",
            "2025",
            datetime(2025, 12, 31),
            "EUR",
            "millions",
            80.807,
            18.7,
            12.5,
            150.0,
            70.0,
            80.0,
            75.0
        )
    ]

    with pytest.raises(ValueError, match="Exercício fiscal inválido"):
        _validate_financial_data(records)


def test_validate_financial_data_rejects_invalid_date():
    records = [
        (
            "LVMH",
            2025,
            "2025-12-31",
            "EUR",
            "millions",
            80.807,
            18.7,
            12.5,
            150.0,
            70.0,
            80.0,
            75.0
        )
    ]

    with pytest.raises(ValueError, match="Data de fim do período inválida"):
        _validate_financial_data(records)


def test_validate_financial_data_rejects_empty_currency():
    records = [
        (
            "LVMH",
            2025,
            datetime(2025, 12, 31),
            "",
            "millions",
            80.807,
            18.7,
            12.5,
            150.0,
            70.0,
            80.0,
            75.0
        )
    ]

    with pytest.raises(ValueError, match="Moeda inválida"):
        _validate_financial_data(records)


def test_validate_financial_data_rejects_empty_unit():
    records = [
        (
            "LVMH",
            2025,
            datetime(2025, 12, 31),
            "EUR",
            "",
            80.807,
            18.7,
            12.5,
            150.0,
            70.0,
            80.0,
            75.0
        )
    ]

    with pytest.raises(ValueError, match="Unidade inválida"):
        _validate_financial_data(records)


def test_validate_financial_data_rejects_non_numeric_financial_value():
    records = [
        (
            "LVMH",
            2025,
            datetime(2025, 12, 31),
            "EUR",
            "millions",
            "invalid",
            18.7,
            12.5,
            150.0,
            70.0,
            80.0,
            75.0
        )
    ]

    with pytest.raises(ValueError, match="revenue"):
        _validate_financial_data(records)


def test_validate_financial_data_rejects_nan_values():
    records = [
        (
            "LVMH",
            2025,
            datetime(2025, 12, 31),
            "EUR",
            "millions",
            float("nan"),
            18.7,
            12.5,
            150.0,
            70.0,
            80.0,
            75.0
        )
    ]

    with pytest.raises(ValueError, match="revenue"):
        _validate_financial_data(records)


def test_validate_financial_data_rejects_infinite_values():
    records = [
        (
            "LVMH",
            2025,
            datetime(2025, 12, 31),
            "EUR",
            "millions",
            float("inf"),
            18.7,
            12.5,
            150.0,
            70.0,
            80.0,
            75.0
        )
    ]

    with pytest.raises(ValueError, match="revenue"):
        _validate_financial_data(records)
