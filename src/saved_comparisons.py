import sqlite3

from src.database import get_connection


def save_comparison(user_id, name, company_ids, fiscal_years, notes=None, comparison_id=None):
    """Guarda uma comparação e associa-lhe as empresas selecionadas."""

    # Validação do ID do utilizador
    if not isinstance(user_id, int) or user_id <= 0:
        return False, "O ID do utilizador não é válido."

    # Validação do ID da comparação, quando fornecido
    if comparison_id is not None:
        if not isinstance(comparison_id, int) or comparison_id <= 0:
            return False, "O ID da comparação não é válido."

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

    # Validação dos anos fiscais
    if not isinstance(fiscal_years, (list, tuple)):
        return False, "A lista de anos fiscais não é válida."

    if not fiscal_years:
        return False, "A comparação deve incluir pelo menos um ano fiscal."

    if not all(
        type(year) is int and year > 0
        for year in fiscal_years
    ):
        return False, "Um ou mais anos fiscais não são válidos."

    if len(set(fiscal_years)) != len(fiscal_years):
        return False, "Não podes selecionar o mesmo ano fiscal mais do que uma vez."

    # Validação das notas
    if notes is not None and not isinstance(notes, str):
        return False, "As notas devem ser texto."

    if notes is not None:
        notes = notes.strip()

        if not notes:
            notes = None

    is_update = comparison_id is not None

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

            # 3. Cria ou atualiza a comparação
            if not is_update:
                cursor = connection.execute(
                    """
                    INSERT INTO saved_comparison (
                        user_id,
                        name,
                        notes
                    )
                    VALUES (?, ?, ?)
                    """,
                    (user_id, name, notes)
                )

                comparison_id = cursor.lastrowid

            else:
                comparison_exists = connection.execute(
                    """
                    SELECT 1
                    FROM saved_comparison
                    WHERE id = ? AND user_id = ?
                    LIMIT 1
                    """,
                    (comparison_id, user_id)
                ).fetchone()

                if not comparison_exists:
                    return False, "A comparação não existe ou não te pertence."

                connection.execute(
                    """
                    UPDATE saved_comparison
                    SET name = ?, notes = ?
                    WHERE id = ? AND user_id = ?
                    """,
                    (name, notes, comparison_id, user_id)
                )

            # 4. Atualiza as empresas associadas à comparação
            if is_update:
                connection.execute(
                    """
                    DELETE FROM comparison_company
                    WHERE comparison_id = ?
                    """,
                    (comparison_id,)
                )

            # 5. Atualiza os anos fiscais associados à comparação
            if is_update:
                connection.execute(
                    """
                    DELETE FROM comparison_period
                    WHERE comparison_id = ?
                    """,
                    (comparison_id,)
                )

            # 6. Associa as empresas à comparação
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

            # 7. Associa os anos fiscais à comparação
            connection.executemany(
                """
                INSERT INTO comparison_period (
                    comparison_id,
                    fiscal_year
                )
                VALUES (?, ?)
                """,
                [
                    (comparison_id, fiscal_year)
                    for fiscal_year in fiscal_years
                ]
            )

        if is_update:
            return True, "Comparação atualizada com sucesso."

        return True, "Comparação guardada com sucesso."

    except sqlite3.IntegrityError:
        return False, "Não foi possível guardar a comparação. Verifica os dados."

    except sqlite3.Error:
        return False, "Ocorreu um erro ao guardar a comparação."


def get_saved_comparisons(user_id):
    """Obtém as comparações guardadas por um utilizador."""

    try:
        with get_connection() as connection:
            comparisons = connection.execute(
                """
                SELECT
                    id,
                    name,
                    created_at,
                    notes
                FROM saved_comparison
                WHERE user_id = ?
                ORDER BY created_at DESC
                """,
                (user_id,)
            ).fetchall()

        return comparisons

    except sqlite3.Error:
        return []


def get_saved_comparison_details(user_id, comparison_id):
    """Obtém os detalhes de uma comparação guardada."""

    try:
        with get_connection() as connection:
            comparison = connection.execute(
                """
                SELECT
                    id,
                    name,
                    created_at,
                    notes
                FROM saved_comparison
                WHERE id = ? AND user_id = ?
                """,
                (comparison_id, user_id)
            ).fetchone()

            if comparison is None:
                return None

            companies = connection.execute(
                """
                SELECT
                    company.id,
                    company.name
                FROM comparison_company
                JOIN company
                    ON comparison_company.company_id = company.id
                WHERE comparison_company.comparison_id = ?
                """,
                (comparison_id,)
            ).fetchall()

            fiscal_years = connection.execute(
                """
                SELECT fiscal_year
                FROM comparison_period
                WHERE comparison_id = ?
                ORDER BY fiscal_year
                """,
                (comparison_id,)
            ).fetchall()

        return {
            "id": comparison[0],
            "name": comparison[1],
            "created_at": comparison[2],
            "notes": comparison[3],
            "companies": companies,
            "fiscal_years": [row[0] for row in fiscal_years]
        }

    except sqlite3.Error:
        return None


def update_comparison_notes(user_id, comparison_id, notes):
    """Adiciona, atualiza ou elimina as notas de uma comparação."""

    if notes is not None and not isinstance(notes, str):
        return False

    if isinstance(notes, str):
        notes = notes.strip() or None

    try:
        with get_connection() as connection:
            cursor = connection.execute(
                """
                UPDATE saved_comparison
                SET notes = ?
                WHERE id = ? AND user_id = ?
                """,
                (notes, comparison_id, user_id)
            )

            if cursor.rowcount == 0:
                return False

        return True

    except sqlite3.Error:
        return False


def delete_saved_comparison(user_id, comparison_id):
    """Elimina uma comparação guardada por um utilizador."""

    try:
        with get_connection() as connection:
            comparison = connection.execute(
                """
                SELECT id
                FROM saved_comparison
                WHERE id = ? AND user_id = ?
                """,
                (comparison_id, user_id)
            ).fetchone()

            if comparison is None:
                return False

            connection.execute(
                """
                DELETE FROM comparison_company
                WHERE comparison_id = ?
                """,
                (comparison_id,)
            )

            connection.execute(
                """
                DELETE FROM saved_comparison
                WHERE id = ? AND user_id = ?
                """,
                (comparison_id, user_id)
            )

        return True

    except sqlite3.Error:
        return False
