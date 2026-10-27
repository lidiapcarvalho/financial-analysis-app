import sqlite3
from pathlib import Path

# Caminho da base de dados

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATABASE_PATH = PROJECT_DIR / "data" / "financial_analysis.db"


def get_connection():
    """Estabelece uma ligação à base de dados SQLite"""
    connection = sqlite3.connect(DATABASE_PATH)
    connection.execute("PRAGMA forign_keys = ON")
    return connection


def initialize_database():
    """Cria as tabelas de aplicação, caso ainda não existam."""

    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS company (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                sector TEXT NOT NULL UNIQUE,
                currency TEXT NOT NULL    
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS financial_record (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                fiscal_year INTEGER NOT NULL,
                revenue REAL,
                operating_income REAL,
                net_income REAL,
                total_assets REAL,
                total_liabilities REAL,
                equity REAL,

                FOREIGN KEY (company_id)
                    REFERENCES company(id)
                    ON DELETE RESTRICT,

                UNIQUE (company_id, fiscal_year)
            )
        """)


if __name__ == "__main__":
    initialize_database()
    print(f"Base de dados criada em: {DATABASE_PATH}")
