from streamlit.testing.v1 import AppTest


def test_company_selection_persists(monkeypatch):

    # Evita inicializar a base de dados real
    monkeypatch.setattr(
        "src.database.initialize_database",
        lambda: None
    )

    # Simula as empresas disponíveis
    monkeypatch.setattr(
        "src.companies.get_all_companies",
        lambda: [
            (1, "LVMH"),
            (2, "Kering"),
            (3, "Richemont")
        ]
    )

    # Simula registos financeiros
    monkeypatch.setattr(
        "src.financial_records.get_all_financial_records",
        lambda: [
            (1, "LVMH", 2024, "2024-12-31", "EUR", "millions",
             1000, 200, 150, 5000, 2000, 3000, 3000),
            (2, "LVMH", 2025, "2025-12-31", "EUR", "millions",
             1200, 250, 180, 5500, 2200, 3300, 3300),
            (3, "Richemont", 2024, "2024-03-31", "EUR", "millions",
             800, 150, 100, 4000, 1800, 2200, 2200),
            (4, "Richemont", 2025, "2025-03-31", "EUR", "millions",
             900, 180, 120, 4200, 1900, 2300, 2300)
        ]
    )

    app = AppTest.from_file(
        "../src/pages/3_Analise_Financeira.py"
    ).run(timeout=10)

    # Seleciona Richemont
    app.selectbox[0].set_value("Richemont").run()

    assert app.session_state["selected_company"] == "Richemont"

    # Simula uma nova execução da página
    app.run()

    assert app.session_state["selected_company"] == "Richemont"
    assert app.selectbox[0].value == "Richemont"
    assert not app.exception
