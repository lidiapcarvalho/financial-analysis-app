import pytest

from src.database import get_connection, initialize_database
from src.saved_comparisons import (
    save_comparison,
    get_saved_comparisons,
    get_saved_comparison_details,
    update_comparison_notes,
    delete_saved_comparison
)


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

        fiscal_years = [2024, 2025]

    return database_path, user_id, company_ids, fiscal_years


def test_save_comparison_invalid_user_id():
    success, message = save_comparison(0, "Comparação 1", [1, 2], [2024, 2025])

    assert success is False
    assert message == "O ID do utilizador não é válido."


def test_save_comparison_empty_name():
    success, message = save_comparison(1, "   ", [1, 2], [2024, 2025])

    assert success is False
    assert message == "O nome da comparação é obrigatório."


def test_save_comparison_name_too_long():
    success, message = save_comparison(1, "A" * 101, [1, 2], [2024, 2025])

    assert success is False
    assert message == "O nome da comparação não pode ultrapassar 100 caracteres."


def test_save_comparison_less_than_two_companies():
    success, message = save_comparison(1, "Comparação 1", [1], [2024, 2025])

    assert success is False
    assert message == "A comparação deve incluir pelo menos duas empresas."


def test_save_comparison_duplicate_companies():
    success, message = save_comparison(1, "Comparação 1", [1, 1], [2024, 2025])

    assert success is False
    assert message == "Não podes selecionar a mesma empresa mais do que uma vez."


def test_save_comparison_invalid_company_ids():
    success, message = save_comparison(
        1, "Comparação 1", [1, -2], [2024, 2025])

    assert success is False
    assert message == "Um ou mais IDs de empresas não são válidos."


def test_save_comparison_empty_fiscal_years():
    success, message = save_comparison(
        1, "Comparação 1", [1, 2], []
    )

    assert success is False
    assert message == "A comparação deve incluir pelo menos um ano fiscal."


def test_save_comparison_invalid_fiscal_years_type():
    success, message = save_comparison(
        1, "Comparação 1", [1, 2], "2024"
    )

    assert success is False
    assert message == "A lista de anos fiscais não é válida."


def test_save_comparison_invalid_fiscal_years():
    success, message = save_comparison(
        1, "Comparação 1", [1, 2], [2024, 0]
    )

    assert success is False
    assert message == "Um ou mais anos fiscais não são válidos."


def test_save_comparison_duplicate_fiscal_years():
    success, message = save_comparison(
        1, "Comparação 1", [1, 2], [2024, 2024]
    )

    assert success is False
    assert message == "Não podes selecionar o mesmo ano fiscal mais do que uma vez."


def test_save_comparison_name_with_100_characters(test_database):

    database_path, user_id, company_ids, fiscal_years = test_database

    name = "A" * 100

    success, message = save_comparison(
        user_id,
        name,
        company_ids,
        fiscal_years
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


def test_get_saved_comparisons(test_database):
    database_path, user_id, company_ids, fiscal_years = test_database

    save_comparison(user_id, "Comparação A", company_ids, fiscal_years)

    comparisons = get_saved_comparisons(user_id)

    assert len(comparisons) == 1
    assert comparisons[0][1] == "Comparação A"
    assert comparisons[0][3] is None


def test_get_saved_comparisons_only_returns_user_comparisons(test_database):
    database_path, user_id, company_ids, fiscal_years = test_database

    # Cria um segundo utilizador
    with get_connection(database_path) as connection:
        cursor = connection.execute(
            """
            INSERT INTO user (username, email, password_hash)
            VALUES (?, ?, ?)
            """,
            ("other_user", "other@example.com", "other_hash")
        )
        other_user_id = cursor.lastrowid

    # Guarda uma comparação para cada utilizador
    save_comparison(user_id, "Comparação A", company_ids, fiscal_years)
    save_comparison(other_user_id, "Comparação B", company_ids, fiscal_years)

    comparisons = get_saved_comparisons(user_id)

    assert len(comparisons) == 1
    assert comparisons[0][1] == "Comparação A"


def test_get_saved_comparisons_returns_empty_list(test_database):
    database_path, user_id, company_ids, fiscal_years = test_database

    comparisons = get_saved_comparisons(user_id)

    assert comparisons == []


def test_get_saved_comparison_details(test_database):
    database_path, user_id, company_ids, fiscal_years = test_database

    save_comparison(user_id, "Comparação A", company_ids, fiscal_years)

    comparisons = get_saved_comparisons(user_id)
    comparison_id = comparisons[0][0]

    comparison = get_saved_comparison_details(user_id, comparison_id)

    assert comparison is not None
    assert comparison["id"] == comparison_id
    assert comparison["name"] == "Comparação A"
    assert comparison["notes"] is None
    assert len(comparison["companies"]) == 2
    assert comparison["companies"][0][0] in company_ids
    assert comparison["companies"][1][0] in company_ids


def test_get_saved_comparison_details_returns_fiscal_years(test_database):
    database_path, user_id, company_ids, fiscal_years = test_database

    save_comparison(
        user_id,
        "Comparação A",
        company_ids,
        fiscal_years
    )

    comparison_id = get_saved_comparisons(user_id)[0][0]

    comparison = get_saved_comparison_details(
        user_id,
        comparison_id
    )

    assert comparison is not None
    assert comparison["fiscal_years"] == [2024, 2025]


def test_get_saved_comparison_details_not_found(test_database):
    database_path, user_id, company_ids, fiscal_years = test_database

    comparison = get_saved_comparison_details(user_id, 999)

    assert comparison is None


def test_get_saved_comparison_details_other_user(test_database):
    database_path, user_id, company_ids, fiscal_years = test_database

    # Cria um segundo utilizador
    with get_connection(database_path) as connection:
        cursor = connection.execute(
            """
            INSERT INTO user (username, email, password_hash)
            VALUES (?, ?, ?)
            """,
            ("other_user", "other@example.com", "other_hash")
        )
        other_user_id = cursor.lastrowid

    # Guarda uma comparação para o segundo utilizador
    save_comparison(other_user_id, "Comparação B", company_ids, fiscal_years)

    other_comparisons = get_saved_comparisons(other_user_id)
    comparison_id = other_comparisons[0][0]

    # O primeiro utilizador tenta consultar a comparação
    comparison = get_saved_comparison_details(user_id, comparison_id)

    assert comparison is None


def test_update_comparison_notes(test_database):
    database_path, user_id, company_ids, fiscal_years = test_database

    save_comparison(user_id, "Comparação A", company_ids, fiscal_years)

    comparisons = get_saved_comparisons(user_id)
    comparison_id = comparisons[0][0]

    success = update_comparison_notes(
        user_id,
        comparison_id,
        "Análise das empresas selecionadas."
    )

    assert success is True

    comparison = get_saved_comparison_details(user_id, comparison_id)

    assert comparison["notes"] == "Análise das empresas selecionadas."


def test_update_existing_comparison_notes(test_database):
    database_path, user_id, company_ids, fiscal_years = test_database

    save_comparison(user_id, "Comparação A", company_ids, fiscal_years)

    comparison_id = get_saved_comparisons(user_id)[0][0]

    update_comparison_notes(user_id, comparison_id, "Notas iniciais.")

    success = update_comparison_notes(
        user_id,
        comparison_id,
        "Notas atualizadas."
    )

    assert success is True

    comparison = get_saved_comparison_details(user_id, comparison_id)

    assert comparison["notes"] == "Notas atualizadas."


def test_delete_comparison_notes(test_database):
    database_path, user_id, company_ids, fiscal_years = test_database

    save_comparison(user_id, "Comparação A", company_ids, fiscal_years)

    comparison_id = get_saved_comparisons(user_id)[0][0]

    update_comparison_notes(user_id, comparison_id, "Notas iniciais.")

    success = update_comparison_notes(user_id, comparison_id, None)

    assert success is True

    comparison = get_saved_comparison_details(user_id, comparison_id)

    assert comparison["notes"] is None


def test_update_comparison_notes_with_empty_string(test_database):
    database_path, user_id, company_ids, fiscal_years = test_database

    save_comparison(user_id, "Comparação A", company_ids, fiscal_years)

    comparison_id = get_saved_comparisons(user_id)[0][0]

    update_comparison_notes(user_id, comparison_id, "Notas iniciais.")

    success = update_comparison_notes(user_id, comparison_id, "")

    assert success is True

    comparison = get_saved_comparison_details(user_id, comparison_id)

    assert comparison["notes"] is None


def test_update_comparison_notes_other_user(test_database):
    database_path, user_id, company_ids, fiscal_years = test_database

    with get_connection(database_path) as connection:
        cursor = connection.execute(
            """
            INSERT INTO user (username, email, password_hash)
            VALUES (?, ?, ?)
            """,
            ("other_user", "other@example.com", "other_hash")
        )
        other_user_id = cursor.lastrowid

    save_comparison(other_user_id, "Comparação B", company_ids, fiscal_years)

    comparison_id = get_saved_comparisons(other_user_id)[0][0]

    success = update_comparison_notes(
        user_id,
        comparison_id,
        "Tentativa de alteração."
    )

    assert success is False

    comparison = get_saved_comparison_details(
        other_user_id,
        comparison_id
    )

    assert comparison["notes"] is None


def test_update_comparison_notes_invalid_type(test_database):
    database_path, user_id, company_ids, fiscal_years = test_database

    save_comparison(user_id, "Comparação A", company_ids, fiscal_years)

    comparison_id = get_saved_comparisons(user_id)[0][0]

    success = update_comparison_notes(
        user_id,
        comparison_id,
        123
    )

    assert success is False


def test_delete_saved_comparison(test_database):
    database_path, user_id, company_ids, fiscal_years = test_database

    save_comparison(user_id, "Comparação A", company_ids, fiscal_years)

    comparison_id = get_saved_comparisons(user_id)[0][0]

    success = delete_saved_comparison(user_id, comparison_id)

    assert success is True
    assert get_saved_comparisons(user_id) == []


def test_delete_saved_comparison_removes_company_associations(test_database):
    database_path, user_id, company_ids, fiscal_years = test_database

    save_comparison(user_id, "Comparação A", company_ids, fiscal_years)

    comparison_id = get_saved_comparisons(user_id)[0][0]

    success = delete_saved_comparison(user_id, comparison_id)

    assert success is True

    with get_connection(database_path) as connection:
        associations = connection.execute(
            """
            SELECT *
            FROM comparison_company
            WHERE comparison_id = ?
            """,
            (comparison_id,)
        ).fetchall()

    assert associations == []


def test_delete_saved_comparison_other_user(test_database):
    database_path, user_id, company_ids, fiscal_years = test_database

    save_comparison(user_id, "Comparação A", company_ids, fiscal_years)

    comparison_id = get_saved_comparisons(user_id)[0][0]

    with get_connection(database_path) as connection:
        cursor = connection.execute(
            """
            INSERT INTO user (username, email, password_hash)
            VALUES (?, ?, ?)
            """,
            ("outro_utilizador", "outro@example.com", "hash")
        )

        other_user_id = cursor.lastrowid

    success = delete_saved_comparison(other_user_id, comparison_id)

    assert success is False
    assert len(get_saved_comparisons(user_id)) == 1


def test_delete_saved_comparison_removes_fiscal_years(test_database):
    database_path, user_id, company_ids, fiscal_years = test_database

    save_comparison(
        user_id,
        "Comparação A",
        company_ids,
        fiscal_years
    )

    comparison_id = get_saved_comparisons(user_id)[0][0]

    success = delete_saved_comparison(user_id, comparison_id)

    assert success is True

    with get_connection(database_path) as connection:
        periods = connection.execute(
            """
            SELECT *
            FROM comparison_period
            WHERE comparison_id = ?
            """,
            (comparison_id,)
        ).fetchall()

    assert periods == []


def test_save_comparison_update_other_user(test_database):
    database_path, user_id, company_ids, fiscal_years = test_database

    # Cria um segundo utilizador
    with get_connection(database_path) as connection:
        cursor = connection.execute(
            """
            INSERT INTO user (username, email, password_hash)
            VALUES (?, ?, ?)
            """,
            ("other_user", "other@example.com", "other_hash")
        )
        other_user_id = cursor.lastrowid

    # Guarda uma comparação pertencente ao segundo utilizador
    save_comparison(
        other_user_id,
        "Comparação original",
        company_ids,
        fiscal_years
    )

    comparison_id = get_saved_comparisons(other_user_id)[0][0]

    # O primeiro utilizador tenta atualizar essa comparação
    success, message = save_comparison(
        user_id,
        "Tentativa de alteração",
        company_ids,
        [2023],
        notes="Tentativa de acesso indevido.",
        comparison_id=comparison_id
    )

    assert success is False
    assert message == "A comparação não existe ou não te pertence."

    # Confirma que a comparação original não foi alterada
    comparison = get_saved_comparison_details(
        other_user_id,
        comparison_id
    )

    assert comparison["name"] == "Comparação original"
    assert comparison["notes"] is None
    assert comparison["fiscal_years"] == fiscal_years
