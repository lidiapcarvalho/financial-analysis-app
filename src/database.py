import sqlite3
from pathlib import Path

# Caminho da base de dados

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATABASE_PATH = PROJECT_DIR / "data" / "financial_analysis.db"


def get_connection(database_path=DATABASE_PATH):
    """Estabelece uma ligação à base de dados SQLite"""

    if database_path is None:
        database_path = DATABASE_PATH

    connection = sqlite3.connect(database_path)
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def migrate_database(database_path=DATABASE_PATH):
    """Migra a estrutura da base de dados da versão 1 para a versão 2."""

    with get_connection(database_path) as connection:

        company_columns = {
            column[1]
            for column in connection.execute(
                "PRAGMA table_info(company)"
            ).fetchall()
        }

        if not company_columns:
            return

        # Verifica se a base de dados ainda utiliza a estrutura v1
        if "currency" not in company_columns:
            return

        connection.execute("BEGIN")

        # Remove a tabela antiga de registos financeiros
        # (incluindo o registo de teste)
        connection.execute("DROP TABLE financial_record")

        # Cria a nova tabela de empresas
        connection.execute("""
            CREATE TABLE company_v2 (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                sector TEXT NOT NULL
            )
        """)

        # Preserva as empresas e os respetivos identificadores
        connection.execute("""
            INSERT INTO company_v2 (id, name, sector)
            SELECT id, name, sector
            FROM company
        """)

        connection.execute("DROP TABLE company")
        connection.execute("ALTER TABLE company_v2 RENAME TO company")

        # Cria a tabela de registos financeiros da versão 2
        connection.execute("""
            CREATE TABLE financial_record (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                fiscal_year INTEGER NOT NULL CHECK(fiscal_year > 0),
                period_end TEXT NOT NULL,
                currency TEXT NOT NULL,
                unit TEXT NOT NULL,
                revenue REAL NOT NULL CHECK(revenue >= 0),
                operating_income REAL,
                net_income REAL,
                total_assets REAL NOT NULL CHECK(total_assets >= 0),
                total_liabilities REAL NOT NULL CHECK(total_liabilities >= 0),
                equity REAL,
                equity_attributable_to_owners REAL,

                FOREIGN KEY (company_id)
                    REFERENCES company(id)
                    ON DELETE NO ACTION,

                UNIQUE (company_id, fiscal_year)
            )
        """)


def initialize_database(database_path=DATABASE_PATH):
    """Cria as tabelas de aplicação, caso ainda não existam."""

    # Garante que a pasta da base de dados existe
    database_path = Path(database_path)
    database_path.parent.mkdir(parents=True, exist_ok=True)

    # Atualiza a estrutura da base de dados, se necessário
    migrate_database(database_path)

    with get_connection(database_path) as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS company (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                sector TEXT NOT NULL
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS financial_record (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                fiscal_year INTEGER NOT NULL CHECK(fiscal_year > 0),
                period_end TEXT NOT NULL,
                currency TEXT NOT NULL,
                unit TEXT NOT NULL,
                revenue REAL NOT NULL CHECK(revenue >= 0),
                operating_income REAL,
                net_income REAL,
                total_assets REAL NOT NULL CHECK(total_assets >= 0),
                total_liabilities REAL NOT NULL CHECK(total_liabilities >= 0),
                equity REAL,
                equity_attributable_to_owners REAL,

                FOREIGN KEY (company_id)
                    REFERENCES company(id)
                    ON DELETE NO ACTION,

                UNIQUE (company_id, fiscal_year)
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS user (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE COLLATE NOCASE,
                email TEXT NOT NULL UNIQUE COLLATE NOCASE,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)


if __name__ == "__main__":
    initialize_database()
    print(f"Base de dados criada em: {DATABASE_PATH}")
