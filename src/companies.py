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
