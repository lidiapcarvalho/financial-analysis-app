
import sqlite3
import streamlit as st

from src.companies import (
    add_company,
    get_all_companies,
    update_company,
    delete_company
)
from src.database import initialize_database


# Preparar a base de dados antes de iniciar a aplicação
initialize_database()

st.title("Gestão de Empresas")

st.write(
    "Registo, consulta, edição e eliminação de empresas."
)

st.divider()

# Registar empresa
st.subheader("Registar empresa")

with st.form("company_form"):
    name = st.text_input("Nome da empresa")
    sector = st.text_input("Setor")

    submitted = st.form_submit_button("Registar empresa")

if submitted:
    try:
        add_company(name, sector)
        st.success(
            f"A empresa {name.strip()} foi registada com sucesso!"
        )
        st.rerun()

    except ValueError as error:
        st.error(str(error))

    except sqlite3.IntegrityError as error:
        if "UNIQUE constraint failed: company.name" in str(error):
            st.error("Já existe uma empresa registada com esse nome.")
        else:
            st.error(
                "Ocorreu um erro ao guardar a empresa na base de dados."
            )

st.divider()

# Consultar empresas
st.subheader("Empresas registadas")

companies = get_all_companies()

deleted_message = st.session_state.pop(
    "company_deleted_message", None
)

if deleted_message:
    st.success(deleted_message)

if companies:
    companies_data = [
        {
            "Nome": company[1],
            "Setor": company[2]
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

# Editar empresa
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

        submitted = st.form_submit_button("Guardar alterações")

    if submitted:
        try:
            update_company(
                selected_company[0],
                new_name,
                new_sector
            )

            st.success(
                f"Os dados de {new_name.strip()} "
                "foram atualizados com sucesso!"
            )
            st.rerun()

        except ValueError as error:
            st.error(str(error))

        except sqlite3.IntegrityError as error:
            if "UNIQUE constraint failed: company.name" in str(error):
                st.error("Já existe uma empresa registada com esse nome.")
            else:
                st.error(
                    "Ocorreu um erro ao guardar as alterações na base de dados."
                )

st.divider()

# Eliminar empresa
st.subheader("Eliminar empresa")

if companies:
    selected_company_to_delete = st.selectbox(
        "Selecionar empresa para eliminar",
        companies,
        format_func=lambda company: company[1],
        key="delete_company_selectbox"
    )

    with st.form("delete_company_form"):
        confirm_delete = st.checkbox(
            "Confirmo que pretendo eliminar esta empresa."
        )

        submitted = st.form_submit_button("Eliminar empresa")

    if submitted:
        if not confirm_delete:
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
