import streamlit as st

st.set_page_config(
    page_title="Financial Analysis App",
    page_icon="📊",
    layout="wide"
)

st.title("Financial Aanalysis App")

st.write(
    "Plataforma de análise e comparação de dados financeiros"
    "de empresas do setor de luxo"
)

st.divider()

st.subheader("Bem-vindo!")

st.markdown(
    """
    Esta aplicação permitirá:
    - Consultar dados financeiros de empresas.
    - Analisar indicadores financeiros.
    - Comparar o desempenho das empresas ao longo do tempo.
    """
)

st.info(
    "Projeto em desenvolvimento. As funcionalidades serão"
    "adicionadas progressivamente."
)
