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
    period_end = record[4]
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
        "Period End": period_end,
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

companies_with_data = df["Company"].unique()

companies_without_data = [
    company
    for company in selected_companies
    if company not in companies_with_data
]

if companies_without_data:
    st.warning(
        "Não existem registos financeiros para: "
        + ", ".join(companies_without_data)
    )

if not df.empty:
    all_companies = pd.DataFrame({
        "Company": selected_companies
    })

    available_year = sorted(df["Fiscal Year"].unique())

    complete_combinations = (
        all_companies.assign(key=1)
        .merge(
            pd.DataFrame({
                "Fiscal Year": available_year,
                "key": 1
            }),
            on="key"
        )
        .drop(columns="key")
    )

    df = complete_combinations.merge(
        df,
        on=["Company", "Fiscal Year"],
        how="left"
    )

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
        "Period End",
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

        year_records = year_records.copy()

        period_end_labels = (
            pd.to_datetime(year_records["Period End"])
            .dt.strftime("%d/%m/%Y")
        )

        year_records["Company"] = (
            year_records["Company"]
            + period_end_labels.map(
                lambda date: f" ({date})" if pd.notna(date) else ""
            )
        )

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

    currencies = df["Currency"].dropna().unique()

    columns = st.columns(len(currencies))

    for column, currency in zip(columns, currencies):

        currency_data = df[df["Currency"] == currency]

        revenue_chart = px.line(
            currency_data,
            x="Fiscal Year",
            y="Revenue",
            color="Company",
            markers=True,
            title=f"Evolução da Receita ({currency})",
            labels={
                "Fiscal Year": "Ano Fiscal",
                "Revenue": "Receita",
                "Company": "Empresa",
            }
        )

        with column:

            st.plotly_chart(
                revenue_chart,
                use_container_width=True
            )

st.divider()

st.subheader("Evolução do Resultado Operacional")

if not df.empty:

    currencies = df["Currency"].dropna().unique()

    columns = st.columns(len(currencies))

    for column, currency in zip(columns, currencies):

        currency_data = df[df["Currency"] == currency]

        operating_income_chart = px.line(
            currency_data,
            x="Fiscal Year",
            y="Operating Income",
            color="Company",
            markers=True,
            title=f"Evolução do Resultado Operacional ({currency})",
            labels={
                "Fiscal Year": "Ano Fiscal",
                "Operating Income": "Resultado Operacional",
                "Company": "Empresa"
            }
        )

        with column:
            st.plotly_chart(
                operating_income_chart,
                use_container_width=True
            )

st.divider()

st.subheader("Evolução do Resultado Líquido")

if not df.empty:

    currencies = df["Currency"].dropna().unique()

    columns = st.columns(len(currencies))

    for column, currency in zip(columns, currencies):

        currency_data = df[df["Currency"] == currency]

        net_income_chart = px.line(
            currency_data,
            x="Fiscal Year",
            y="Net Income",
            color="Company",
            markers=True,
            title=f"Evolução do Resultado Líquido ({currency})",
            labels={
                "Fiscal Year": "Ano Fiscal",
                "Net Income": "Resultado Líquido",
                "Company": "Empresa"
            }
        )

        with column:
            st.plotly_chart(
                net_income_chart,
                use_container_width=True
            )

st.divider()

st.subheader("Evolução da Margem Operacional")

indicator_table = df.dropna(subset=["Operating Margin (%)"])

operating_margin_chart = px.line(
    indicator_table,
    x="Fiscal Year",
    y="Operating Margin (%)",
    color="Company",
    markers=True,
    title="Evolução da Margem Operacional por Empresa",
    labels={
        "Fiscal Year": "Ano Fiscal",
        "Operating Margin (%)": "Margem Operacional (%)",
        "Company": "Empresa"
    }
)

st.plotly_chart(
    operating_margin_chart,
    use_container_width=True
)

st.divider()

st.subheader("Evolução da Margem do Lucro Líquida")

indicator_table = df.dropna(subset=["Net Profit Margin (%)"])

net_profit_margin_chart = px.line(
    indicator_table,
    x="Fiscal Year",
    y="Net Profit Margin (%)",
    color="Company",
    markers=True,
    title="Evolução da Margem do Lucro Líquida por Empresa",
    labels={
        "Fiscal Year": "Ano Fiscal",
        "Net Profti Margin (%)": "Margem de Lucro Líquida (%)",
        "Company": "Empresa"
    }
)

st.plotly_chart(
    net_profit_margin_chart,
    use_container_width=True
)

st.divider()

st.subheader("Evolução da Taxa de Crescimento da Receita")

indicator_table = df.dropna(subset=["Revenue Growth (%)"])

revenue_growth_chart = px.line(
    indicator_table,
    x="Fiscal Year",
    y="Revenue Growth (%)",
    color="Company",
    markers=True,
    title="Evolução da Taxa de Crescimento da Receita por Empresa",
    labels={
        "Fiscal Year": "Ano Fiscal",
        "Revenue Growth (%)": "Taxa de Crescimento da Receita (%)",
        "Company": "Empresa"
    }
)

st.plotly_chart(
    revenue_growth_chart,
    use_container_width=True
)

st.divider()

st.subheader("Evolução do ROA")

indicator_table = df.dropna(subset=["ROA (%)"])

roa_chart = px.line(
    indicator_table,
    x="Fiscal Year",
    y="ROA (%)",
    color="Company",
    markers=True,
    title="Evolução do ROA (%)",
    labels={
        "Fiscal Year": "Ano Fiscal",
        "ROA (%)": "Rendibilidade do Ativo (%)",
        "Company": "Empresa"
    }
)

st.plotly_chart(
    roa_chart,
    use_container_width=True
)

st.divider()

st.subheader("Evolução do ROE")

indicator_table = df.dropna(subset=["ROE (%)"])

roe_chart = px.line(
    indicator_table,
    x="Fiscal Year",
    y="ROE (%)",
    color="Company",
    markers=True,
    title="Evolução do ROE (%)",
    labels={
        "Fiscal Year": "Ano Fiscal",
        "ROE (%)": "Rendibilidade dos Capitais Próprios (%)",
        "Company": "Empresa"
    }
)

st.plotly_chart(
    roe_chart,
    use_container_width=True
)

st.divider()

st.subheader("Comparações Guardadas")

st.info(
    "A funcionalidade de guardar, consultar e eliminar "
    "comparações será integrada posteriormente com a gestão "
    "de utilizadores."
)
