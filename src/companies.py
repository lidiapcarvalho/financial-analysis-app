from src.database import get_connection


def get_all_companies(database_path=None):
    """Devolve todas as empresas registradas na base de dados."""

    with get_connection(database_path) as connection:
        companies = connection.execute(
            """
            SELECT id, name, sector, currency
            FROM company
            ORDER BY name
            """
        ).fetchall()

    return companies


def add_company(name, sector, currency, database_path=None):
    """Regista uma nova empresa na base de dados"""

    name = name.strip()
    sector = sector.strip()
    currency = currency.strip().upper()

    if not name:
        raise ValueError("O nome da empresa é obrigatório.")

    if not sector:
        raise ValueError("O sector da empresa é obrigatório.")

    if not currency:
        raise ValueError("A moeda da empresa é obrigatória.")

    with get_connection(database_path) as connection:
        cursor = connection.execute(
            """
            INSERT INTO company (name, sector, currency)
            VALUES (?, ?, ?)
            """,
            (name, sector, currency)
        )

        return cursor.lastrowid


def update_company(company_id, name, sector, currency, database_path=None):
    """Atualiza os dados de uma empresa registada na base de dados"""

    name = name.strip()
    sector = sector.strip()
    currency = currency.strip().upper()

    if not name:
        raise ValueError("O nome da empresa é obrigatório.")

    if not sector:
        raise ValueError("O setor da empresa é obrigatório.")

    if not currency:
        raise ValueError("A moeda da empresa é obrigatória.")

    with get_connection(database_path) as connection:
        company = connection.execute(
            """
            SELECT id
            FROM company
            WHERE id = ?
            """,
            (company_id,)
        ).fetchone()

        if company is None:
            raise ValueError("A empresa não existe.")

        financial_records = connection.execute(
            """
            SELECT id
            FROM financial_record
            WHERE company_id = ?
            """,
            (company_id,)
        ).fetchone()

        if financial_records is not None:
            current_currency = connection.execute(
                """
                SELECT currency
                FROM company
                WHERE id = ?
                """,
                (company_id,)
            ).fetchone()[0]
            if current_currency != currency:
                raise ValueError(
                    "Não é possível atualizar a moeda de uma empresa "
                    "com registos financeiros associados."
                )

        connection.execute(
            """
            UPDATE company
            SET name = ?, sector = ?, currency = ?
            WHERE id = ?
            """,
            (name, sector, currency, company_id)
        )
