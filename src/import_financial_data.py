import math
from numbers import Real

from pathlib import Path

from openpyxl import load_workbook

from src.companies import get_all_companies
from src.database import get_connection
from datetime import date, datetime


PROJECT_DIR = Path(__file__).resolve().parent.parent
EXCEL_FILE_PATH = PROJECT_DIR / "data" / "processed" / "financial-data.xlsx"


def _read_financial_data():
    """Lê os registos financeiros do ficheiro Excel."""

    if not EXCEL_FILE_PATH.exists():
        raise FileNotFoundError(
            f"Ficheiro Excel não encontrado: {EXCEL_FILE_PATH}"
        )

    workbook = load_workbook(
        EXCEL_FILE_PATH,
        read_only=True,
        data_only=True
    )

    try:
        worksheet = workbook.active

        headers = next(
            worksheet.iter_rows(
                min_row=1,
                max_row=1,
                values_only=True
            )
        )

        expected_headers = (
            "company",
            "fiscal_year",
            "period_end",
            "currency",
            "unit",
            "revenue",
            "operating_income",
            "net_income",
            "total_assets",
            "total_liabilities",
            "equity",
            "equity_attributable_to_owners"
        )

        if headers != expected_headers:
            raise ValueError(
                "Os cabeçalhos do ficheiro Excel não são os esperados.")

        records = [
            row
            for row in worksheet.iter_rows(
                min_row=2,
                max_col=12,
                values_only=True
            )
            if row[0] is not None
        ]

        return records

    finally:
        workbook.close()


def _get_company_ids(database_path=None):
    """Devolve um dicionário com os nomes e IDs das empresas."""

    companies = get_all_companies(database_path)

    return {
        name.strip().casefold(): company_id
        for company_id, name, _ in companies
    }


def _validate_companies(records, company_ids):
    """Verifica se todas as empresas dos registos existem na base de dados."""

    unknown_companies = {
        row[0].strip()
        for row in records
        if row[0].strip().casefold() not in company_ids
    }

    if unknown_companies:
        names = ", ".join(sorted(unknown_companies))
        raise ValueError(
            f"As seguintes não estarão registadas na base de dados: {names}"
        )


def import_financial_data(database_path=None):
    """Importa os registos financeiros do Excel para a base de dados."""

    records = _read_financial_data()

    _validate_financial_data(records)

    company_ids = _get_company_ids(database_path)

    _validate_companies(records, company_ids)

    financial_records = []

    for row in records:
        (
            company_name,
            fiscal_year,
            period_end,
            currency,
            unit,
            revenue,
            operating_income,
            net_income,
            total_assets,
            total_liabilities,
            equity,
            equity_attributable_to_owners
        ) = row

        financial_records.append((
            company_ids[company_name.strip().casefold()],
            fiscal_year,
            (
                period_end.date().isoformat()
                if isinstance(period_end, datetime)
                else period_end.isoformat()
            ),
            currency,
            unit,
            revenue,
            operating_income,
            net_income,
            total_assets,
            total_liabilities,
            equity,
            equity_attributable_to_owners
        ))

    with get_connection(database_path) as connection:
        connection.executemany(
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
                total_liabilities,
                equity,
                equity_attributable_to_owners
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            financial_records
        )

    return len(financial_records)


def _validate_financial_data(records):
    """Valida os dados financeiros lidos do ficheiro Excel."""

    numeric_fields = (
        "revenue",
        "operating_income",
        "net_income",
        "total_assets",
        "total_liabilities",
        "equity",
        "equity_attributable_to_owners"
    )

    for row_number, row in enumerate(records, start=2):

        if len(row) != 12:
            raise ValueError(
                f"A linha {row_number} não contém os 12 campos esperados."
            )

        company, fiscal_year, period_end, currency, unit = row[:5]

        # Validar o nome da empresa

        if not isinstance(company, str) or not company.strip():
            raise ValueError(
                f"Nome da empresa inválido na linha {row_number}."
            )

        # Validar o exercício fiscal
        if not isinstance(fiscal_year, int) or isinstance(fiscal_year, bool):
            raise ValueError(
                f"Exercício fiscal inválido na linha {row_number}."
            )

        # Validar a data de fim do período
        if not isinstance(period_end, date):
            raise ValueError(
                f"Data de fim do período inválida na linha {row_number}."
            )

        # Validar a moeda
        if not isinstance(currency, str) or not currency.strip():
            raise ValueError(
                f"Moeda inválida na linha {row_number}."
            )

        # Validar a unidade
        if not isinstance(unit, str) or not unit.strip():
            raise ValueError(
                f"Unidade inválida na linha {row_number}."
            )

        # Validar os valores financeiros
        for field_index, field_name in enumerate(
            numeric_fields, start=5
        ):
            value = row[field_index]

            if value is None:
                continue

            if (
                isinstance(value, bool)
                or not isinstance(value, Real)
                or not math.isfinite(value)
            ):
                raise ValueError(
                    f"Valor inválido para {field_name} "
                    f"na linha {row_number}."
                )
