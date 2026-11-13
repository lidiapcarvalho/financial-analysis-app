import pytest

from src.database import get_connection, initialize_database
from src.users import create_user, verify_password, hash_password


@pytest.fixture
def test_database(tmp_path, monkeypatch):
    """Cria uma base de dados isolada para os testes."""

    database_path = tmp_path / "test.db"

    initialize_database(database_path)

    monkeypatch.setattr(
        "src.users.get_connection",
        lambda: get_connection(database_path)
    )

    return database_path


def test_create_user_successfully(test_database):

    success, message = create_user(
        "test_user",
        "test@example.com",
        "Password12345!"
    )

    assert success is True
    assert message == "Utilizador registado com sucesso."

    with get_connection(test_database) as connection:

        user = connection.execute(
            """
            SELECT username, email, password_hash
            FROM user
            WHERE username = ?
            """,
            ("test_user",)
        ).fetchone()

    assert user is not None
    assert user[0] == "test_user"
    assert user[1] == "test@example.com"

    # Confirma que a palavra-passe não está em texto simples
    assert user[2] != "Password12345!"

    # Confirma que o hash corresponde à palavra-passe original
    assert verify_password("Password12345!", user[2]) is True


# Validação dos campos obrigatórios vazios
@pytest.mark.parametrize(
    "username, email, password",
    [
        ("", "test@example.com", "Password12345!"),
        ("test_user", "", "Password12345!"),
        ("test_user", "test@example.com", ""),
    ]
)
def test_create_user_with_empty_fields(
    test_database, username, email, password
):

    success, message = create_user(username, email, password)

    assert success is False
    assert message == "Todos os campos são obrigatórios."

# Nome de utilizador inválido


@pytest.mark.parametrize(
    "username",
    [
        "ab",
        "user-name",
    ]
)
def test_create_user_with_invalid_username(test_database, username):

    success, message = create_user(
        username,
        "test@example.com",
        "Password12345!"
    )

    assert success is False
    assert message in [
        "O nome de utilizador deve ter entre 3 e 30 caracteres.",
        "O nome de utilizador só pode conter letras, números e underscores."
    ]

# Email inválido


@pytest.mark.parametrize(
    "email",
    [
        "testexample.com",
        "test@example",
    ]
)
def test_create_user_with_invalid_email(test_database, email):

    success, message = create_user(
        "test_user",
        email,
        "Password12345!"
    )

    assert success is False
    assert message == "O endereço de e-mail não é válido."

# Password inválida


def test_create_user_with_short_password(test_database):

    success, message = create_user(
        "test_user",
        "test@example.com",
        "Short123!"
    )

    assert success is False
    assert message == "A palavra-passe deve ter pelo menos 12 caracteres."

# Nome de utilizador duplicado


def test_create_user_with_existing_username(test_database):

    create_user(
        "test_user",
        "test@example.com",
        "Password12345!"
    )

    success, message = create_user(
        "test_user",
        "another@example.com",
        "AnotherPassword123!"
    )

    assert success is False
    assert message == "Este nome de utilizador já está registado."

# Email duplicado


def test_create_user_with_existing_email(test_database):

    create_user(
        "test_user",
        "test@example.com",
        "Password12345!"
    )

    success, message = create_user(
        "another_user",
        "test@example.com",
        "AnotherPassword123!"
    )

    assert success is False
    assert message == "Este endereço de e-mail já está registado."

# Palavra-passe incorreta


def test_verify_password_with_wrong_password():

    password_hash = hash_password("Password12345!")

    result = verify_password(
        "WrongPassword123!",
        password_hash
    )

    assert result is False

# Nome de utilizador com maiúsculas


def test_create_user_with_username_different_case(test_database):

    create_user(
        "test_user",
        "test@example.com",
        "Password12345!"
    )

    success, message = create_user(
        "TEST_USER",
        "another@example.com",
        "AnotherPassword123!"
    )

    assert success is False
    assert message == "Este nome de utilizador já está registado."

# Email com maiúsculas


def test_create_user_with_email_different_case(test_database):

    create_user(
        "test_user",
        "test@example.com",
        "Password12345!"
    )

    success, message = create_user(
        "another_user",
        "TEST@EXAMPLE.COM",
        "AnotherPassword123!"
    )

    assert success is False
    assert message == "Este endereço de e-mail já está registado."
