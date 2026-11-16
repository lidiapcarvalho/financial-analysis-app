from src.saved_comparisons import save_comparison


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
