import math
import sqlite3

from src.database import get_connection


def get_all_financial_records(database_path=None):
    """Devolve todos os registos financeiros, incluindo os dadaos da empresa associada."""

    with get_connection(database_path) as connection:
        financial_records = connection.execute(
            """
                SELECT
                    fr.id,
                    c.name,
                    fr.fiscal_year,
                    fr.period_end,
                    fr.currency,
                    fr.unit,
                    fr.revenue,
                    fr.operating_income,
                    fr.net_income,
                    fr.total_assets,
                    fr.total_liabilities,
                    fr.equity,
                    fr.equity_attributable_to_owners
                FROM financial_record AS fr
                INNER JOIN company AS c
                    ON fr.company_id = c.id
                ORDER BY c.name, fr.fiscal_year DESC
                """
        ).fetchall()

    return financial_records


def _validate_fiscal_year(fiscal_year):
    """Valida o ano fiscal."""
    if isinstance(fiscal_year, bool) or not isinstance(fiscal_year, int):
        raise ValueError("O ano fiscal tem de ser um número inteiro.")

    if not 1900 <= fiscal_year <= 2100:
        raise ValueError("O ano fiscal tem de estar entre 1900 e 2100.")


def _validate_non_negative_value(value, field_name):
    """Valida um valor financeiro obrigatório e não negativo."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field_name} tem de ser um número.")

    if not math.isfinite(value):
        raise ValueError(f"{field_name} tem de ser um número finito.")

    if value < 0:
        raise ValueError(f"{field_name} não pode ser negativo.")


def _validate_numeric_value(value, field_name):
    """Valida um valor financeiro obrigatório que pode ser negativo."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field_name} tem de ser um número.")

    if not math.isfinite(value):
        raise ValueError(f"{field_name} tem de ser um número finito.")


def add_financial_record(
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
        equity_attributable_to_owners,
        database_path=None):
    """Regista um novo registo financeiro associado a uma empresa."""
    _validate_fiscal_year(fiscal_year)

    _validate_non_negative_value(revenue, "revenue")
    _validate_numeric_value(operating_income, "operating_income")
    _validate_numeric_value(net_income, "net_income")
    _validate_non_negative_value(total_assets, "total_assets")
    _validate_non_negative_value(total_liabilities, "total_liabilities")
    _validate_numeric_value(equity, "equity")
    _validate_numeric_value(equity_attributable_to_owners,
                            "equity_attributable_to_owners")

    with get_connection(database_path) as connection:
        try:
            cursor = connection.execute(
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
                (
                    company_id, fiscal_year, period_end, currency, unit, revenue, operating_income,
                    net_income, total_assets, total_liabilities, equity, equity_attributable_to_owners
                )
            )
        except sqlite3.IntegrityError as error:
            if error.sqlite_errorname == "SQLITE_CONSTRAINT_FOREIGNKEY":
                raise ValueError(
                    f"A empresa associada ao registo financeiro não existe.") from error

            elif error.sqlite_errorname == "SQLITE_CONSTRAINT_UNIQUE":
                raise ValueError(
                    f"Já existe um registo financeiro para esta empresa e ano fiscal.") from error
            raise

        return cursor.lastrowid


def update_financial_record(
    record_id, fiscal_year, period_end, currency, unit, revenue, operating_income,
    net_income, total_assets, total_liabilities, equity, equity_attributable_to_owners,
    database_path=None
):
    """Atualiza os dados deum registo financeiro existente."""
    _validate_fiscal_year(fiscal_year)

    _validate_non_negative_value(revenue, "revenue")
    _validate_numeric_value(operating_income, "operating_income")
    _validate_numeric_value(net_income, "net_income")
    _validate_non_negative_value(total_assets, "total_assets")
    _validate_non_negative_value(total_liabilities, "total_liabilities")
    _validate_numeric_value(equity, "equity")
    _validate_numeric_value(equity_attributable_to_owners,
                            "equity_attributable_to_owners")

    with get_connection(database_path) as connection:
        try:
            cursor = connection.execute(
                """
                UPDATE financial_record
                SET fiscal_year = ?,
                    period_end = ?,
                    currency = ?,
                    unit = ?,
                    revenue = ?, 
                    operating_income = ?, 
                    net_income = ?, 
                    total_assets = ?, 
                    total_liabilities = ?, 
                    equity = ?,
                    equity_attributable_to_owners = ?
                WHERE id = ?
                """,
                (
                    fiscal_year, period_end, currency, unit, revenue, operating_income,
                    net_income, total_assets, total_liabilities, equity, equity_attributable_to_owners, record_id
                )
            )
        except sqlite3.IntegrityError as error:
            if error.sqlite_errorname == "SQLITE_CONSTRAINT_UNIQUE":
                raise ValueError(
                    f"Já existe um registo financeiro para esta empresa e ano fiscal.") from error
            raise

        return cursor.rowcount


def delete_financial_record(record_id, database_path=None):
    """Elimina um registo financeiro existente."""

    with get_connection(database_path) as connection:
        cursor = connection.execute(
            """
            DELETE FROM financial_record
            WHERE id = ?
            """,
            (record_id,)
        )
        return cursor.rowcount
