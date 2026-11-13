import re
import sqlite3

from src.database import get_connection

from argon2 import PasswordHasher
from argon2.exceptions import (
    VerifyMismatchError,
    InvalidHashError
)

password_hasher = PasswordHasher()


def hash_password(password):
    """Gera o hash seguro de um palavra-passe."""

    return password_hasher.hash(password)


def verify_password(password, password_hash):
    """Verifica se uma palavra-passe corresponde ao hash armazenado."""

    try:
        return password_hasher.verify(password_hash, password)

    except (VerifyMismatchError, InvalidHashError):
        return False


def create_user(username, email, password):
    """Regista um novo utilizador na base de dados."""

    username = username.strip()
    email = email.strip().lower()

    # Validação dos campos obrigatórios
    if not username or not email or not password:
        return False, "Todos os campos são obrigatórios."

    # Validação do nome de utilizador
    if len(username) < 3 or len(username) > 30:
        return False, "O nome de utilizador deve ter entre 3 e 30 caracteres."

    if not re.fullmatch(r"[a-zA-Z0-9_]+", username):
        return False, "O nome de utilizador só pode conter letras, números e underscores."

    # Validação do endereço de e-mail
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        return False, "O endereço de e-mail não é válido."

    # Validação da palavra-passe
    if len(password) < 12:
        return False, "A palavra-passe deve ter pelo menos 12 caracteres."

    try:
        with get_connection() as connection:

            # Verifica se o nome de utilizador já existe
            username_exists = connection.execute(
                """
                SELECT 1
                FROM app_user
                WHERE username = ?
                LIMIT 1
                """,
                (username,)
            ).fetchone()

            if username_exists:
                return False, "Este nome de utilizador já está registado."

            # Verifica se o e-mail já existe
            email_exists = connection.execute(
                """
                SELECT 1
                FROM app_user
                WHERE email = ?
                LIMIT 1
                """,
                (email,)
            ).fetchone()

            if email_exists:
                return False, "Este endereço de e-mail já está registado."

            # Gera o hash da palavra-passe
            password_hash = hash_password(password)

            # Guarda o novo utilizador
            connection.execute(
                """
                INSERT INTO app_user (
                    username,
                    email,
                    password_hash
                )
                VALUES (?, ?, ?)
                """,
                (username, email, password_hash)
            )

        return True, "Utilizador registado com sucesso."

    except sqlite3.IntegrityError:
        return False, "Não foi possível registar o utilizador. Verifica os dados."
