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
