import streamlit as st

from src.database import initialize_database
from src.companies import get_all_companies


initialize_database()

st.title("Comparação Financeira")
st.write(
    "Compara os dados financeiros e os indicadores "
    "de desempenho de diferentes empresas."
)

st.divider()

st.subheader("Seleção de Empresas")

companies = get_all_companies()

if not companies:
    st.info("Ainda não existem empresas registadas.")
    st.stop()

company_options = {
    company[1]: company[0]
    for company in companies
}

selected_companies = st.multiselect(
    "Seleciona as empresas que pretendes comparar:",
    options=list(company_options.keys()),
    help="Seleciona pelo menos duas empresas para iniciar uma comparação."
)

if len(selected_companies) < 2:
    st.info(
        "Seleciona pelo menos duas empresas para "
        "consultar a comparação financeira."
    )
    st.stop()

st.divider()

st.subheader("Comparação dos Dados Financeiros")

st.info(
    "A comparação dos dados financeiros será implementada "
    "numa próxima etapa."
)

st.subheader("Comparação dos Indicadores")

st.info(
    "A comparação das margens e do crescimento da receita "
    "será implementada posteriormente."
)

st.subheader("Evolução do Desempenho Financeiro")

st.info(
    "Os gráficos comparativos serão desenvolvidos depois "
    "da conclusão dos gráficos da análise financeira individual."
)

st.divider()

st.subheader("Comparações Guardadas")

st.info(
    "A funcionalidade de guardar, consultar e eliminar "
    "comparações será integrada posteriormente com a gestão "
    "de utilizadores."
)
