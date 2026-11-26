import sqlite3
import shutil
from pathlib import Path

# Caminho da base de dados

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATABASE_PATH = PROJECT_DIR / "data" / "financial_analysis.db"
DEMO_DATABASE_PATH = (
    PROJECT_DIR / "docs" / "database" / "financial_analysis_demo.db"
)


def get_connection(database_path=DATABASE_PATH):
    """Estabelece uma ligação à base de dados SQLite"""

    if database_path is None:
        database_path = DATABASE_PATH

    connection = sqlite3.connect(database_path)
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def migrate_database(database_path=DATABASE_PATH):
    """Migra a estrutura da base de dados entre versões."""

    with get_connection(database_path) as connection:

        # Obtém a versão atual da base de dados
        version = connection.execute(
            "PRAGMA user_version"
        ).fetchone()[0]

        # Verifica se a tabela company existe
        company_columns = {
            column[1]
            for column in connection.execute(
                "PRAGMA table_info(company)"
            ).fetchall()
        }

        if not company_columns:
            return

        # Migração v1 -> v2
        if version == 0 and "currency" in company_columns:

            connection.execute("BEGIN")

            connection.execute("DROP TABLE financial_record")

            connection.execute("""
                CREATE TABLE company_v2 (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    sector TEXT NOT NULL
                )
            """)

            connection.execute("""
                INSERT INTO company_v2 (id, name, sector)
                SELECT id, name, sector
                FROM company
            """)

            connection.execute("DROP TABLE company")
            connection.execute(
                "ALTER TABLE company_v2 RENAME TO company"
            )

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

            connection.commit()

            connection.execute("PRAGMA user_version = 2")
            version = 2

        # Reconhece bases de dados v2 já existentes
        elif version == 0 and "currency" not in company_columns:
            version = 2
            connection.execute("PRAGMA user_version = 2")

        # Migração v2 -> v3
        if version == 2:

            comparison_columns = {
                column[1]
                for column in connection.execute(
                    "PRAGMA table_info(saved_comparison)"
                ).fetchall()
            }

            if comparison_columns and "notes" not in comparison_columns:
                connection.execute("""
                    ALTER TABLE saved_comparison
                    ADD COLUMN notes TEXT
                """)

            connection.commit()
            connection.execute("PRAGMA user_version = 3")
            version = 3

        # Migração v3 -> v4
        if version == 3:

            connection.execute("""
                CREATE TABLE IF NOT EXISTS comparison_period (
                    comparison_id INTEGER NOT NULL,
                    fiscal_year INTEGER NOT NULL CHECK(fiscal_year > 0),

                    PRIMARY KEY (comparison_id, fiscal_year),

                    FOREIGN KEY (comparison_id)
                        REFERENCES saved_comparison(id)
                        ON UPDATE NO ACTION
                        ON DELETE CASCADE
                )
            """)

            connection.commit()

            connection.execute("PRAGMA user_version = 4")
            version = 4

        # Migração v4 -> v5
        if version == 4:

            connection.execute("""
                ALTER TABLE user
                ADD COLUMN role TEXT NOT NULL DEFAULT 'user'
                CHECK(role IN ('admin', 'user'))
            """)

            connection.commit()

            connection.execute("PRAGMA user_version = 5")
            version = 5


def initialize_database(database_path=DATABASE_PATH):
    """Cria ou prepara a base de dados da aplicação."""

    database_path = Path(database_path)

    # Garante que a pasta da base de dados existe
    database_path.parent.mkdir(parents=True, exist_ok=True)

    # Cria a base de dados local a partir da demonstração,
    # caso ainda não exista
    if not database_path.exists():
        if database_path.resolve() == DATABASE_PATH.resolve():
            if DEMO_DATABASE_PATH.exists():
                shutil.copy2(DEMO_DATABASE_PATH, database_path)

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
                role TEXT NOT NULL DEFAULT 'user'
                    CHECK(role IN ('admin', 'user')),
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS saved_comparison (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                notes TEXT,

                FOREIGN KEY (user_id)
                    REFERENCES user(id)
                    ON UPDATE NO ACTION
                    ON DELETE NO ACTION
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS comparison_company (
                comparison_id INTEGER NOT NULL,
                company_id INTEGER NOT NULL,

                PRIMARY KEY (comparison_id, company_id),

                FOREIGN KEY (comparison_id)
                    REFERENCES saved_comparison(id)
                    ON UPDATE NO ACTION
                    ON DELETE NO ACTION,

                FOREIGN KEY (company_id)
                    REFERENCES company(id)
                    ON UPDATE NO ACTION
                    ON DELETE NO ACTION
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS comparison_period (
                comparison_id INTEGER NOT NULL,
                fiscal_year INTEGER NOT NULL CHECK(fiscal_year > 0),

                PRIMARY KEY (comparison_id, fiscal_year),

                FOREIGN KEY (comparison_id)
                    REFERENCES saved_comparison(id)
                    ON UPDATE NO ACTION
                    ON DELETE CASCADE
            )
        """)

        connection.execute("PRAGMA user_version = 5")


if __name__ == "__main__":
    initialize_database()
    print(f"Base de dados criada em: {DATABASE_PATH}")
