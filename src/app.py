import sqlite3
import streamlit as st

from src.companies import add_company, get_all_companies
from src.database import initialize_database


st.set_page_config(
    page_title="Financial Analysis App",
    page_icon="📊",
    layout="wide"
)

# Preparar a base de dados antes de iniciar a aplicação
initialize_database()

st.title("Financial Analysis App")

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

st.divider()

st.subheader("Registar empresa")

with st.form("company_form"):
    name = st.text_input("Nome da empresa")
    sector = st.text_input("Setor")
    currency = st.text_input("Moeda", placeholder="Ex.: EUR")

    submitted = st.form_submit_button("Registar empresa")

if submitted:
    try:
        add_company(name, sector, currency)
        st.success(f"A empresa {name.strip()} foi registada com sucesso!")

    except ValueError as error:
        st.error(str(error))

    except sqlite3.IntegrityError as error:
        if "UNIQUE constraint failed: company.name" in str(error):
            st.error("Já existe uma empresa registada com esse nome.")
        else:
            st.error("Ocorreu um erro ao guardar a empresa na base de dados.")

st.divider()

st.subheader("Empresas registadas")

companies = get_all_companies()

if companies:
    companies_data = [
        {
            "Nome": company[1],
            "Setor": company[2],
            "Moeda": company[3]
        }
        for company in companies
    ]

    st.dataframe(
        companies_data,
        use_container_width=True,
        hide_index=True
    )

else:
    stt.info("Ainda não existem empresas registadas.")

st.info(
    "Projeto em desenvolvimento. As funcionalidades serão "
    "adicionadas progressivamente."
)
