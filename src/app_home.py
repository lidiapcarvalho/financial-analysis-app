import streamlit as st

from src.database import initialize_database


# Configuração da aplicação
st.set_page_config(
    page_title="Financial Analysis App",
    page_icon="📊",
    layout="wide"
)

# Preparar a base de dados
initialize_database()

# Página inicial
st.title("Financial Analysis App")

st.write(
    "Plataforma de análise e comparação de dados financeiros de empresas."
)

st.divider()

st.subheader("Bem-vindo!")

st.markdown(
    """
    Esta aplicação permite:

    - Gerir empresas e os respetivos registos financeiros.
    - Consultar e analisar indicadores financeiros.
    - Acompanhar a evolução do desempenho financeiro.
    - Comparar o desempenho de diferentes empresas.
    """
)

st.divider()

st.info(
    "Seleciona uma das páginas no menu lateral para começar."
)
