import sqlite3
import streamlit as st

from src.companies import (
    add_company,
    get_all_companies,
    update_company,
    delete_company
)
from src.financial_records import (
    add_financial_record,
    get_all_financial_records,
    update_financial_record,
    delete_financial_record
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

st.divider()

st.subheader("Adicionar registo financeiro")

if companies:
    selected_company_for_record = st.selectbox(
        "Empresa",
        companies,
        format_func=lambda company: company[1],
        key="financial_record_company"
    )

    with st.form("financial_record_form"):
        fiscal_year = st.number_input(
            "Ano fiscal",
            min_value=1900,
            max_value=2100,
            step=1
        )
        revenue = st.number_input(
            "Receita",
            min_value=0.0,
            value=0.0,
            step=0.01
        )
        operating_income = st.number_input(
            "Resultado operacional",
            value=0.0,
            step=0.01
        )
        net_income = st.number_input(
            "Resultado líquido",
            value=0.0,
            step=0.01
        )
        total_assets = st.number_input(
            "Ativo total",
            min_value=0.0,
            value=0.0,
            step=0.01
        )
        total_liabilities = st.number_input(
            "Passivo total",
            min_value=0.0,
            value=0.0,
            step=0.01
        )
        equity = st.number_input(
            "Capital próprio",
            value=0.0,
            step=0.01
        )

        submitted = st.form_submit_button("Adicionar registo")

    if submitted:
        try:
            add_financial_record(
                selected_company_for_record[0],
                fiscal_year,
                revenue,
                operating_income,
                net_income,
                total_assets,
                total_liabilities,
                equity
            )

            st.success("Registo financeiro adicionado com sucesso!")

        except ValueError as error:
            st.error(str(error))

else:
    st.info("É necessário registar uma empresa antes de adicionar dados financeiros.")

st.divider()

st.subheader("Editar registo financeiro")

financial_records = get_all_financial_records()

update_message = st.session_state.pop(
    "financial_record_updated_message",
    None
)

if update_message:
    st.success(update_message)

if financial_records:
    selected_record = st.selectbox(
        "Selecionar registo",
        financial_records,
        format_func=lambda record: (
            f"{record[1]} - Ano fiscal {record[3]}"
        ),
        key="edit_financial_record"
    )

    with st.form("edit_financial_record_form"):
        new_fiscal_year = st.number_input(
            "Ano fiscal",
            min_value=1900,
            max_value=2100,
            step=1,
            value=selected_record[3]
        )
        new_revenue = st.number_input(
            "Receita",
            min_value=0.0,
            value=selected_record[4],
            step=0.01
        )
        new_operating_income = st.number_input(
            "Resultado operacional",
            value=selected_record[5],
            step=0.01
        )
        new_net_income = st.number_input(
            "Resultado líquido",
            value=selected_record[6],
            step=0.01
        )
        new_total_assets = st.number_input(
            "Ativo total",
            min_value=0.0,
            value=selected_record[7],
            step=0.01
        )
        new_total_liabilities = st.number_input(
            "Passivo total",
            min_value=0.0,
            value=selected_record[8],
            step=0.01
        )
        new_equity = st.number_input(
            "Capital próprio",
            value=selected_record[9],
            step=0.01
        )

        submitted = st.form_submit_button("Guardar alterações")

    if submitted:
        try:
            update_financial_record(
                selected_record[0],
                new_fiscal_year,
                new_revenue,
                new_operating_income,
                new_net_income,
                new_total_assets,
                new_total_liabilities,
                new_equity
            )

            st.session_state["financial_record_updated_message"] = (
                f"O registo financeiro foi atualizado com sucesso!"
            )

        except ValueError as error:
            st.error(str(error))

else:
    st.info("Não existem registos financeiros disponíveis para editar.")

st.divider()

st.subheader("Eliminar registo financeiro")

financial_records = get_all_financial_records()

deleted_message = st.session_state.pop(
    "financial_record_deleted_message",
    None
)

if deleted_message:
    st.success(deleted_message)

if financial_records:
    selected_record_to_delete = st.selectbox(
        "Selecionar registo para eliminar",
        financial_records,
        format_func=lambda record: (
            f"{record[1]} - Ano fiscal {record[3]}"
        ),
        key="delete_financial_record"
    )

    with st.form("delete_financial_record_form"):
        confirme_delete = st.checkbox(
            f"Confirmo que pretendo eliminar este registo"
        )

        submitted = st.form_submit_button("Eliminar registo")

    if submitted:
        if not confirme_delete:
            st.warning("É necessário confirmar a eliminação.")

        else:
            try:
                delete_financial_record(selected_record_to_delete[0])

                st.session_state["financial_record_deleted_message"] = (
                    f"O registo financeiro foi eliminado com sucesso!"
                )

                st.rerun()

            except ValueError as error:
                st.error(str(error))

else:
    st.info("Não existem registos financeiros disponíveis para eliminar.")

st.divider()

st.subheader("Registos financeiros")

financial_records = get_all_financial_records()

if financial_records:
    financial_records_data = [
        {
            "Empresa": record[1],
            "Moeda": record[2],
            "Ano fiscal": record[3],
            "Receita": record[4],
            "Resultado operacional": record[5],
            "Resultado líquido": record[6],
            "Ativo total": record[7],
            "Passivo total": record[8],
            "Capital próprio": record[9]
        }
        for record in financial_records
    ]

    st.dataframe(
        financial_records_data,
        use_container_width=True,
        hide_index=True
    )

else:
    st.info("Ainda não existem registos financeiros disponíveis.")
