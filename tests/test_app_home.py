from streamlit.testing.v1 import AppTest


def test_login_and_logout(monkeypatch):

    # Evita inicializar a base de dados real
    monkeypatch.setattr(
        "src.database.initialize_database",
        lambda: None
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

    app = AppTest.from_file("../src/app_home.py").run()

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
