import pytest

from src.database import get_connection, initialize_database
from src.saved_comparisons import save_comparison


@pytest.fixture
def test_database(tmp_path, monkeypatch):
    """Cria uma base de dados isolada para os testes."""

    database_path = tmp_path / "test.db"

    initialize_database(database_path)

    monkeypatch.setattr(
        "src.saved_comparisons.get_connection",
        lambda: get_connection(database_path)
    )

    # Cria um utilizador e duas empresas para os testes
    with get_connection(database_path) as connection:

        cursor = connection.execute(
            """
            INSERT INTO user (username, email, password_hash)
            VALUES (?, ?, ?)
            """,
            ("test_user", "test@example.com", "test_hash")
        )

        user_id = cursor.lastrowid

        company_ids = []

        for name in ["Empresa A", "Empresa B"]:
            cursor = connection.execute(
                """
                INSERT INTO company (name, sector)
                VALUES (?, ?)
                """,
                (name, "Luxury")
            )

            company_ids.append(cursor.lastrowid)

    return database_path, user_id, company_ids


def test_save_comparison_invalid_user_id():
    success, message = save_comparison(0, "Comparação 1", [1, 2])

    assert success is False
    assert message == "O ID do utilizador não é válido."


def test_save_comparison_empty_name():
    success, message = save_comparison(1, "   ", [1, 2])

    assert success is False
    assert message == "O nome da comparação é obrigatório."


def test_save_comparison_name_too_long():
    success, message = save_comparison(1, "A" * 101, [1, 2])

    assert success is False
    assert message == "O nome da comparação não pode ultrapassar 100 caracteres."


def test_save_comparison_less_than_two_companies():
    success, message = save_comparison(1, "Comparação 1", [1])

    assert success is False
    assert message == "A comparação deve incluir pelo menos duas empresas."


def test_save_comparison_duplicate_companies():
    success, message = save_comparison(1, "Comparação 1", [1, 1])

    assert success is False
    assert message == "Não podes selecionar a mesma empresa mais do que uma vez."


def test_save_comparison_invalid_company_ids():
    success, message = save_comparison(1, "Comparação 1", [1, -2])

    assert success is False
    assert message == "Um ou mais IDs de empresas não são válidos."


def test_save_comparison_name_with_100_characters(test_database):

    database_path, user_id, company_ids = test_database

    name = "A" * 100

    success, message = save_comparison(
        user_id,
        name,
        company_ids
    )

    assert success is True, message
    assert message == "Comparação guardada com sucesso."

    with get_connection(database_path) as connection:

        comparison = connection.execute(
            """
            SELECT name, user_id
            FROM saved_comparison
            """
        ).fetchone()

    assert comparison is not None
    assert comparison[0] == name
    assert comparison[1] == user_id
