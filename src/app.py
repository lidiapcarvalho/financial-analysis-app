import streamlit as st

from src.database import initialize_database


st.set_page_config(
    page_title="Financial Analysis App",
    page_icon="📊",
    layout="wide"
)

initialize_database()

pages = {
    "Principal": [
        st.Page(
            "app_home.py",
            title="Início",
            icon="🏠",
            default=True
        )
    ],
    "Gestão Financeira": [
        st.Page(
            "pages/1_Empresas.py",
            title="Empresas",
            icon="🏢"
        ),
        st.Page(
            "pages/2_Registos_Financeiros.py",
            title="Registos Financeiros",
            icon="📁"
        ),
        st.Page(
            "pages/3_Analise_Financeira.py",
            title="Análise Financeira",
            icon="📊"
        ),
        st.Page(
            "pages/4_Comparacao.py",
            title="Comparação",
            icon="⚖️"
        )
    ],
    "Conta": [
        st.Page(
            "pages/5_Registo.py",
            title="Registar Utilizador",
            icon="👤"
        )
    ]
}

navigation = st.navigation(pages)
navigation.run()
