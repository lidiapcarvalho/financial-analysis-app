import streamlit as st
import pandas as pd
import plotly.express as px

from src.database import initialize_database
from src.companies import get_all_companies
from src.financial_records import get_financial_records_by_companies
from src.financial_indicators import calculate_financial_indicators

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

selected_company_ids = [
    company_options[company]
    for company in selected_companies
]

financial_records = get_financial_records_by_companies(
    selected_company_ids
)

analysis_records = []

for record in financial_records:

    company_id = record[1]
    company_name = record[2]
    fiscal_year = record[3]
    revenue = record[7]
    operating_income = record[8]
    net_income = record[9]
    total_assets = record[10]
    equity = record[12]

    # Identifica a receita do ano anterior da mesma empresa
    previous_records = [
        previous_record
        for previous_record in financial_records
        if (
            previous_record[1] == company_id
            and previous_record[3] == fiscal_year - 1
        )
    ]

    previous_revenue = (
        previous_records[0][7]
        if previous_records
        else None
    )

    if (
        revenue is not None
        and operating_income is not None
        and net_income is not None
    ):
        indicators = calculate_financial_indicators(
            revenue,
            operating_income,
            net_income,
            previous_revenue,
            total_assets=total_assets,
            equity=equity
        )
    else:
        indicators = {
            "operating_margin": None,
            "net_profit_margin": None,
            "revenue_growth": None,
            "roa": None,
            "roe": None
        }

    analysis_records.append({
        "Company": company_name,
        "Fiscal Year": fiscal_year,
        "Currency": record[5],
        "Unit": record[6],
        "Revenue": revenue,
        "Operating Income": operating_income,
        "Net Income": net_income,
        "Total Assets": total_assets,
        "Equity": equity,
        "Operating Margin (%)": indicators["operating_margin"],
        "Net Profit Margin (%)": indicators["net_profit_margin"],
        "Revenue Growth (%)": indicators["revenue_growth"],
        "ROA (%)": indicators["roa"],
        "ROE (%)": indicators["roe"]
    })

df = pd.DataFrame(analysis_records)

st.divider()

st.subheader("Comparação dos Dados Financeiros")

if not financial_records:
    st.warning(
        "Não existem registos financeiros disponíveis "
        "para as empresas selecionadas."
    )
else:
    financial_data_columns = [
        "Company",
        "Fiscal Year",
        "Currency",
        "Unit",
        "Revenue",
        "Operating Income",
        "Net Income",
        "Total Assets",
        "Equity"
    ]

    st.dataframe(
        df[financial_data_columns],
        use_container_width=True,
        hide_index=True
    )


st.subheader("Comparação dos Indicadores")

if df.empty:
    st.warning(
        "Não existem registos financeiros disponíveis "
        "para as empresas selecionadas."
    )
else:
    indicator_columns = [
        "Operating Margin (%)",
        "Net Profit Margin (%)",
        "Revenue Growth (%)",
        "ROA (%)",
        "ROE (%)"
    ]

    for fiscal_year in sorted(df["Fiscal Year"].unique()):

        st.markdown(f"**Ano fiscal {fiscal_year}**")

        year_records = df[
            df["Fiscal Year"] == fiscal_year
        ]

        indicator_table = (
            year_records
            .set_index("Company")[indicator_columns]
            .T
        )

        indicator_table.index.name = "Indicador"

        st.dataframe(
            indicator_table,
            use_container_width=True
        )

st.subheader("Evolução do Desempenho Financeiro")

if not df.empty:

    revenue_chart = px.line(
        df,
        x="Fiscal Year",
        y="Revenue",
        color="Company",
        markers=True,
        facet_col="Currency",
        title="Evolução da Receita por Empresa",
        labels={
            "Fiscal Year": "Ano Fiscal",
            "Revenue": "Receita",
            "Company": "Empresa",
            "Currency": "Moeda"
        }
    )

    st.plotly_chart(
        revenue_chart,
        use_container_width=True
    )

st.divider()

st.subheader("Evolução do Resultado Operacional")

operating_income_chart = px.line(
    df,
    x="Fiscal Year",
    y="Operating Income",
    color="Company",
    markers=True,
    facet_col="Currency",
    title="Evolução do Resultado Operacional",
    labels={
        "Fiscal Year": "Ano Fiscal",
        "Operating Income": "Resultado Operacional",
        "Company": "Empresa",
        "Currency": "Moeda"
    }
)

st.plotly_chart(
    operating_income_chart,
    use_container_width=True
)

st.divider()

st.subheader("Evolução do Resultado Líquido")

net_income_chart = px.line(
    df,
    x="Fiscal Year",
    y="Net Income",
    color="Company",
    markers=True,
    facet_col="Currency",
    title="Evolução do Resultado Líquido por Empresa",
    labels={
        "Fiscal Year": "Ano Fiscal",
        "Net Income": "Resultado Líquido",
        "Company": "Empresa",
        "Currency": "Moeda"
    }
)

st.plotly_chart(
    net_income_chart,
    use_container_width=True
)

st.divider()

st.subheader("Comparações Guardadas")

st.info(
    "A funcionalidade de guardar, consultar e eliminar "
    "comparações será integrada posteriormente com a gestão "
    "de utilizadores."
)
