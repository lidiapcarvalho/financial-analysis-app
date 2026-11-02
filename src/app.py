import sqlite3
import streamlit as st

from src.companies import (
    add_company,
    get_all_companies,
    update_company,
    delete_company
)
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

st.info(
    "Projeto em desenvolvimento. As funcionalidades serão "
    "adicionadas progressivamente."
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

deleted_message = st.session_state.pop("company_deleted_message", None)

if deleted_message:
    st.success(deleted_message)

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
    st.info("Ainda não existem empresas registadas.")

st.divider()

st.subheader("Editar empresa")

if companies:
    selected_company = st.selectbox(
        "Selecionar empresa",
        companies,
        format_func=lambda company: company[1]
    )

    with st.form("edit_company_form"):
        new_name = st.text_input(
            "Novo nome da empresa",
            value=selected_company[1]
        )
        new_sector = st.text_input(
            "Novo setor",
            value=selected_company[2]
        )
        new_currency = st.text_input(
            "Nova moeda",
            value=selected_company[3]
        )

        submitted = st.form_submit_button("Guardar alterações")

    if submitted:
        try:
            update_company(
                selected_company[0],
                new_name,
                new_sector,
                new_currency
            )

            st.success(
                f"Os dados de {new_name.strip()} foram atualizados com sucesso!")
            st.rerun()

        except ValueError as error:
            st.error(str(error))

        except sqlite3.IntegrityError as error:
            if "UNIQUE constraint failed: company.name" in str(error):
                st.error("Já existe uma empresa registada com esse nome.")
            else:
                st.error(
                    "Ocorreu um erro ao guardar as alterações na base de dados.")

st.divider()

st.subheader("Eliminar empresa")

if companies:
    selected_company_to_delete = st.selectbox(
        "Selecionar empresa para eliminar",
        companies,
        format_func=lambda company: company[1],
        key="delete_company_selectbox"
    )

    with st.form("delete_company_form"):
        confirme_delete = st.checkbox(
            f"Confirmo que pretendo eliminar esta empresa."
        )

        submitted = st.form_submit_button("Eliminar empresa")

    if submitted:
        # Seleção da empresa e formulário

        if not confirme_delete:
            st.warning("É necessário confirmar a eliminação.")

        else:
            try:
                delete_company(selected_company_to_delete[0])
                st.session_state["company_deleted_message"] = (
                    f"A empresa {selected_company_to_delete[1]} "
                    "foi eliminada com sucesso!"
                )
                st.rerun()

            except ValueError as error:
                st.error(str(error))

else:
    if not deleted_message:
        st.info("Não existem empresas disponíveis para eliminar.")
