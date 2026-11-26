from streamlit.testing.v1 import AppTest


def test_login_and_logout(monkeypatch):

    # Evita inicializar a base de dados real
    monkeypatch.setattr(
        "src.database.initialize_database",
        lambda: None
    )

    # Simula as empresas disponíveis
    monkeypatch.setattr(
        "src.companies.get_all_companies",
        lambda: [
            (1, "LVMH", "Luxury"),
            (2, "Kering", "Luxury")
        ]
    )

    # Simula os registos financeiros
    monkeypatch.setattr(
        "src.financial_records.get_all_financial_records",
        lambda: [
            (1, "LVMH", 2025, "2025-12-31", "EUR", "millions",
             1000, 200, 150, 5000, 2000, 3000, 3000),
            (2, "Kering", 2025, "2025-12-31", "EUR", "millions",
             800, 150, 100, 4000, 1800, 2200, 2200)
        ]
    )

    # Simula uma autenticação bem-sucedida
    monkeypatch.setattr(
        "src.users.authenticate_user",
        lambda username, password: (
            True,
            {
                "id": 1,
                "username": "test_user",
                "email": "test@example.com",
                "role": "user"
            }
        )
    )

    app = AppTest.from_file("../src/app_home.py").run(timeout=10)

    # Preenche as credenciais
    app.text_input[0].set_value("test_user")
    app.text_input[1].set_value("Password12345!")

    # Inicia sessão
    app.button[0].click().run()

    assert app.session_state["authenticated"] is True
    assert app.session_state["user"]["username"] == "test_user"

    # Termina sessão
    app.button[0].click().run()

    assert app.session_state.get("authenticated", False) is False
    assert "user" not in app.session_state
    assert not app.exception


def test_dashboard_without_authentication(monkeypatch):

    # Evita inicializar a base de dados real
    monkeypatch.setattr(
        "src.database.initialize_database",
        lambda: None
    )

    # Simula as empresas disponíveis
    monkeypatch.setattr(
        "src.companies.get_all_companies",
        lambda: [
            (1, "LVMH", "Luxury"),
            (2, "Kering", "Luxury")
        ]
    )

    # Simula os registos financeiros
    monkeypatch.setattr(
        "src.financial_records.get_all_financial_records",
        lambda: [
            (1, "LVMH", 2025, "2025-12-31", "EUR", "millions",
             1000, 200, 150, 5000, 2000, 3000, 3000),
            (2, "Kering", 2025, "2025-12-31", "EUR", "millions",
             800, 150, 100, 4000, 1800, 2200, 2200)
        ]
    )

    app = AppTest.from_file("../src/app_home.py").run()

    # Confirma os indicadores gerais
    assert app.metric[0].value == "2"
    assert app.metric[1].value == "2"
    assert app.metric[2].value == "2"
    assert app.metric[3].value == "2025"

    # Confirma que a página carrega sem erros
    assert not app.exception


def test_dashboard_without_data(monkeypatch):

    # Evita inicializar a base de dados real
    monkeypatch.setattr(
        "src.database.initialize_database",
        lambda: None
    )

    # Simula uma base de dados sem empresas
    monkeypatch.setattr(
        "src.companies.get_all_companies",
        lambda: []
    )

    # Simula uma base de dados sem registos financeiros
    monkeypatch.setattr(
        "src.financial_records.get_all_financial_records",
        lambda: []
    )

    app = AppTest.from_file("../src/app_home.py").run()

    # Confirma que os indicadores apresentam valores vazios
    assert app.metric[0].value == "0"
    assert app.metric[1].value == "0"
    assert app.metric[2].value == "0"
    assert app.metric[3].value == "N/A"

    # Confirma as mensagens informativas
    assert any(
        "Ainda não existem empresas registadas" in message.value
        for message in app.info
    )

    assert any(
        "Ainda não existem registos financeiros disponíveis" in message.value
        for message in app.info
    )

    assert not app.exception
