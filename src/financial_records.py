from src.database import get_connection


def get_all_financial_records(database_path=None):
    """Devolve todos os registos financeiros, incluindo os dadaos da empresa associada."""

    with get_connection(database_path) as connection:
        financial_records = connection.execute(
            """
                SELECT
                    fr.id,
                    c.name,
                    c.currency,
                    fr.fiscal_year,
                    fr.revenue,
                    fr.operating_income,
                    fr.net_income,
                    fr.total_assets,
                    fr.total_liabilities,
                    fr.equity
                FROM financial_record AS fr
                INNER JOIN company AS c
                    ON fr.company_id = c.id
                ORDER BY c.name, fr.fiscal_year DESC
                """
        ).fetchall()

    return financial_records


def add_financial_record(company_id, fiscal_year, revenue, operating_income, net_income, total_assets, total_liabilities, equity, database_path=None):
    """Regista um novo registo financeiro associado a uma empresa."""

    with get_connection(database_path) as connection:
        cursor = connection.execute(
            """
            INSERT INTO financial_record (company_id, fiscal_year, revenue, operating_income, net_income, total_assets, total_liabilities, equity)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (company_id, fiscal_year, revenue, operating_income,
             net_income, total_assets, total_liabilities, equity)
        )

        return cursor.lastrowid


def update_financial_record(
    record_id, fiscal_year, revenue, operating_income,
    net_income, total_assets, total_liabilities, equity,
    database_path=None
):
    """Atualiza os dados deum registo financeiro existente."""

    with get_connection(database_path) as connection:
        cursor = connection.execute(
            """
            UPDATE financial_record
            SET fiscal_year = ?, 
                revenue = ?, 
                operating_income = ?, 
                net_income = ?, 
                total_assets = ?, 
                total_liabilities = ?, 
                equity = ?
            WHERE id = ?
            """,
            (
                fiscal_year, revenue, operating_income,
                net_income, total_assets, total_liabilities,
                equity, record_id)
        )
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
