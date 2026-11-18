import sqlite3

from src.database import get_connection


def save_comparison(user_id, name, company_ids):
    """Guarda uma comparação e associa-lhe as empresas selecionadas."""

    # Validação do ID do utilizador
    if not isinstance(user_id, int) or user_id <= 0:
        return False, "O ID do utilizador não é válido."

    # Validação do nome da comparação
    if not isinstance(name, str) or not name.strip():
        return False, "O nome da comparação é obrigatório."

    name = name.strip()

    if len(name) > 100:
        return False, "O nome da comparação não pode ultrapassar 100 caracteres."

    # Validação das empresas selecionadas

    if not isinstance(company_ids, (list, tuple)):
        return False, "A lista de empresas não é válido."

    if len(company_ids) < 2:
        return False, "A comparação deve incluir pelo menos duas empresas."

    if len(set(company_ids)) != len(company_ids):
        return False, "Não podes selecionar a mesma empresa mais do que uma vez."

    # Validação do IDs das empresas
    if not all(
        isinstance(company_id, int) and company_id > 0
        for company_id in company_ids
    ):
        return False, "Um ou mais IDs de empresas não são válidos."

    try:
        with get_connection() as connection:

            # 1. Verifica se o utilizador existe
            user_exists = connection.execute(
                """
                SELECT 1
                FROM user
                WHERE id = ?
                LIMIT 1
                """,
                (user_id,)
            ).fetchone()

            if not user_exists:
                return False, "O utilizador não existe."

            # 2. Verifica se todas as empresas existem
            placeholders = ", ".join("?" for _ in company_ids)

            companies = connection.execute(
                f"""
                SELECT id
                FROM company
                WHERE id IN ({placeholders})
                """,
                tuple(company_ids)
            ).fetchall()

            if len(companies) != len(company_ids):
                return False, "Uma ou mais empresas não existem."

            # 3. Guarda a comparação
            cursor = connection.execute(
                """
                INSERT INTO saved_comparison (
                    user_id,
                    name
                )
                VALUES (?, ?)        
                """,
                (user_id, name)
            )

            # 4. Obtém o ID da comparação criada
            comparison_id = cursor.lastrowid

            # 5. Associa as empresas à comparação
            connection.executemany(
                """
                INSERT INTO comparison_company (
                    comparison_id,
                    company_id
                )
                VALUES (?, ?)
                """,
                [
                    (comparison_id, company_id)
                    for company_id in company_ids
                ]
            )

        return True, "Comparação guardada com sucesso."

    except sqlite3.IntegrityError:
        return False, "Não foi possível guardar a comparação. Verifica os dados."

    except sqlite3.Error:
        return False, "Ocorreu um erro ao guardar a comparação."
