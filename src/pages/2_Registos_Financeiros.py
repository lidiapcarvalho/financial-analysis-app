import streamlit as st
from datetime import date

from src.companies import get_all_companies
from src.financial_records import (
    add_financial_record,
    get_all_financial_records,
    update_financial_record,
    delete_financial_record
)
from src.database import initialize_database

# Preparar a base de dados
initialize_database()

st.title("Gestão de Registos Financeiros")

st.write(
    "Adicionar, consultar, editar e eliminar "
    "registos financeiros das empresas."
)

st.divider()

# Obter empresas registadas
companies = get_all_companies()

# Adicionar registo financeiro

st.subheader("Adicionar registo financeiro")

if companies:

    selected_company = st.selectbox(
        "Empresa",
        companies,
        format_func=lambda company: company[1],
        key="add_record_company"
    )

    with st.form("financial_record_form"):

        fiscal_year = st.number_input(
            "Ano fiscal",
            min_value=1900,
            max_value=2100,
            value=date.today().year,
            step=1
        )

        period_end = st.date_input(
            "Data de encerramento do período",
            value=date.today()
        )

        currency = st.text_input(
            "Moeda",
            value="EUR"
        )

        unit = st.text_input(
            "Unidade",
            value="millions"
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

        equity_attributable_to_owners = st.number_input(
            "Capital próprio atribuível aos detentores de capital",
            value=0.0,
            step=0.01
        )

        submitted = st.form_submit_button("Adicionar registo")

    if submitted:
        try:
            add_financial_record(
                selected_company[0],
                fiscal_year,
                period_end.isoformat(),
                currency,
                unit,
                revenue,
                operating_income,
                net_income,
                total_assets,
                total_liabilities,
                equity,
                equity_attributable_to_owners
            )

            st.success("Registo financeiro adicionado com sucesso!")
            st.rerun()

        except ValueError as error:
            st.error(str(error))

else:
    st.info(
        "É necessário registar uma empresa antes de adicionar "
        "registos financeiros."
    )


st.divider()

# Consultar registos financeiros

st.subheader("Registos financeiros")

financial_records = get_all_financial_records()

if financial_records:

    financial_records_data = [
        {
            "Empresa": record[1],
            "Ano fiscal": record[2],
            "Período": record[3],
            "Moeda": record[4],
            "Unidade": record[5],
            "Receita": record[6],
            "Resultado operacional": record[7],
            "Resultado líquido": record[8],
            "Ativo total": record[9],
            "Passivo total": record[10],
            "Capital próprio": record[11],
            "Capital próprio atribuível aos detentores de capital": record[12]
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


st.divider()


# Editar registo financeiro

st.subheader("Editar registo financeiro")

if financial_records:

    selected_record = st.selectbox(
        "Selecionar registo",
        financial_records,
        format_func=lambda record: (
            f"{record[1]} - Ano fiscal {record[2]}"
        ),
        key="edit_financial_record"
    )

    with st.form("edit_financial_record_form"):

        new_fiscal_year = st.number_input(
            "Ano fiscal",
            min_value=1900,
            max_value=2100,
            value=selected_record[2],
            step=1
        )

        new_period_end = st.date_input(
            "Data de encerramento do período",
            value=date.fromisoformat(selected_record[3])
        )

        new_currency = st.text_input(
            "Moeda",
            value=selected_record[4]
        )

        new_unit = st.text_input(
            "Unidade",
            value=selected_record[5]
        )

        new_revenue = st.number_input(
            "Receita",
            min_value=0.0,
            value=float(selected_record[6]),
            step=0.01
        )

        new_operating_income = st.number_input(
            "Resultado operacional",
            value=float(selected_record[7]),
            step=0.01
        )

        new_net_income = st.number_input(
            "Resultado líquido",
            value=float(selected_record[8]),
            step=0.01
        )

        new_total_assets = st.number_input(
            "Ativo total",
            min_value=0.0,
            value=float(selected_record[9]),
            step=0.01
        )

        new_total_liabilities = st.number_input(
            "Passivo total",
            min_value=0.0,
            value=float(selected_record[10]),
            step=0.01
        )

        new_equity = st.number_input(
            "Capital próprio",
            value=float(selected_record[11]),
            step=0.01
        )

        new_equity_attributable_to_owners = st.number_input(
            "Capital próprio atribuível aos detentores de capital",
            value=float(selected_record[12]),
            step=0.01
        )

        submitted = st.form_submit_button("Guardar alterações")

    if submitted:
        try:
            update_financial_record(
                selected_record[0],
                new_fiscal_year,
                new_period_end.isoformat(),
                new_currency,
                new_unit,
                new_revenue,
                new_operating_income,
                new_net_income,
                new_total_assets,
                new_total_liabilities,
                new_equity,
                new_equity_attributable_to_owners
            )

            st.success("Registo financeiro atualizado com sucesso!")
            st.rerun()

        except ValueError as error:
            st.error(str(error))

else:
    st.info("Não existem registos financeiros disponíveis para editar.")


st.divider()

# Eliminar registo financeiro

st.subheader("Eliminar registo financeiro")

if financial_records:

    selected_record_to_delete = st.selectbox(
        "Selecionar registo para eliminar",
        financial_records,
        format_func=lambda record: (
            f"{record[1]} - Ano fiscal {record[2]}"
        ),
        key="delete_financial_record"
    )

    with st.form("delete_financial_record_form"):

        confirm_delete = st.checkbox(
            "Confirmo que pretendo eliminar este registo."
        )

        submitted = st.form_submit_button("Eliminar registo")

    if submitted:

        if not confirm_delete:
            st.warning("É necessário confirmar a eliminação.")

        else:
            try:
                delete_financial_record(selected_record_to_delete[0])

                st.success("Registo financeiro eliminado com sucesso!")
                st.rerun()

            except ValueError as error:
                st.error(str(error))

else:
    st.info("Não existem registos financeiros disponíveis para eliminar.")
