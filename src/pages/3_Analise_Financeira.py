
import streamlit as st
import pandas as pd
import plotly.express as px

from src.database import initialize_database
from src.companies import get_all_companies
from src.financial_records import get_all_financial_records
from src.financial_indicators import calculate_financial_indicators


initialize_database()

st.title("Análise Financeira")
st.write(
    "Consulta os dados financeiros e acompanha a evolução "
    "dos indicadores de uma empresa."
)

st.divider()

# Seleção da empresa
companies = get_all_companies()

if not companies:
    st.info("Ainda não existem empresas registadas.")
    st.stop()

company_options = {
    company[1]: company[0]
    for company in companies
}

selected_company = st.selectbox(
    "Seleciona uma empresa:",
    options=list(company_options.keys())
)

selected_company_id = company_options[selected_company]

# Consulta dos registos financeiros
all_records = get_all_financial_records()

company_records = [
    record
    for record in all_records
    if record[1] == selected_company
]

if not company_records:
    st.info(
        "Ainda não existem registos financeiros associados "
        "a esta empresa."
    )
    st.stop()

# Ordenação cronológica
company_records.sort(key=lambda record: record[2])

# Cálculo dos indicadores
analysis_records = []

for record in company_records:

    fiscal_year = record[2]
    revenue = record[6]
    operating_income = record[7]
    net_income = record[8]

    # Identifica a receita do ano fiscal imediatamente anterior
    previous_revenue = None

    previous_records = [
        previous_record
        for previous_record in company_records
        if previous_record[2] == fiscal_year - 1
    ]

    if previous_records:
        previous_revenue = previous_records[0][6]

    if (
        revenue is not None
        and operating_income is not None
        and net_income is not None
    ):
        indicators = calculate_financial_indicators(
            revenue,
            operating_income,
            net_income,
            previous_revenue
        )
    else:
        indicators = {
            "operating_margin": None,
            "net_profit_margin": None,
            "revenue_growth": None
        }

    analysis_records.append({
        "Fiscal Year": fiscal_year,
        "Period End": record[3],
        "Currency": record[4],
        "Unit": record[5],
        "Revenue": revenue,
        "Operating Income": operating_income,
        "Net Income": net_income,
        "Operating Margin (%)": indicators["operating_margin"],
        "Net Profit Margin (%)": indicators["net_profit_margin"],
        "Revenue Growth (%)": indicators["revenue_growth"]
    })

df = pd.DataFrame(analysis_records)

# Dados do último ano fiscal
latest_record = df.iloc[-1]

st.subheader("Indicadores Financeiros")

st.caption(
    f"Último ano fiscal disponível: {int(latest_record['Fiscal Year'])}"
)

col1, col2, col3 = st.columns(3)

operating_margin = latest_record["Operating Margin (%)"]
net_profit_margin = latest_record["Net Profit Margin (%)"]
revenue_growth = latest_record["Revenue Growth (%)"]

col1.metric(
    "Margem Operacional",
    f"{operating_margin:.2f}%" if pd.notna(operating_margin) else "N/D"
)

col2.metric(
    "Margem de Lucro Líquida",
    f"{net_profit_margin:.2f}%" if pd.notna(net_profit_margin) else "N/D"
)

col3.metric(
    "Crescimento da Receita",
    f"{revenue_growth:.2f}%" if pd.notna(revenue_growth) else "N/D"
)

st.divider()

# Tabela de dados financeiros e indicadores
st.subheader("Dados Financeiros e Indicadores")

st.dataframe(
    df,
    use_container_width=True,
    hide_index=True
)

st.divider()

# Gráfico da evolução da receita
st.subheader("Evolução da Receita")

revenue_chart = px.line(
    df,
    x="Fiscal Year",
    y="Revenue",
    markers=True,
    title="Evolução da Receita por Ano Fiscal",
    labels={
        "Fiscal Year": "Ano Fiscal",
        "Revenue": f"Receita ({latest_record['Currency']} {latest_record['Unit']})"
    },
    custom_data=["Revenue"]
)

revenue_chart.update_traces(
    line=dict(width=3),
    marker=dict(size=9),
    hovertemplate=(
        "<b>Ano Fiscal:</b> %{x}<br>"
        "<b>Receita:</b> %{y:,.2f}<br>"
        "<extra></extra>"
    )
)

revenue_chart.update_layout(
    template="plotly_dark",
    height=450,
    font=dict(
        family="Arial",
        size=12
    ),
    title=dict(
        x=0.5,
        xanchor="center",
        font=dict(size=18)
    ),
    xaxis=dict(
        title="Ano Fiscal",
        tickmode="linear",
        dtick=1,
        showgrid=False,
        zeroline=False
    ),
    yaxis=dict(
        title=f"Receita ({latest_record['Currency']} {latest_record['Unit']})",
        tickformat=",.0f",
        showgrid=True,
        zeroline=False
    ),
    margin=dict(
        l=60,
        r=30,
        t=70,
        b=50
    )
)


st.plotly_chart(
    revenue_chart,
    use_container_width=True
)

# Gráfico da evolução das margens
st.subheader("Evolução das Margens")

margin_df = df.melt(
    id_vars=["Fiscal Year"],
    value_vars=["Operating Margin (%)", "Net Profit Margin (%)"],
    var_name="Indicator",
    value_name="Percentage"
)

margin_df["Indicator"] = margin_df["Indicator"].replace({
    "Operating Margin (%)": "Margem Operacional",
    "Net Profit Margin (%)": "Margem de Lucro Líquida"
})

margin_chart = px.line(
    margin_df,
    x="Fiscal Year",
    y="Percentage",
    color="Indicator",
    markers=True,
    title="Evolução das Margens por Ano Fiscal",
    labels={
        "Fiscal Year": "Ano Fiscal",
        "Percentage": "Margem (%)",
        "Indicator": "Indicador"
    },
    color_discrete_map={
        "Margem Operacional": "#60A5FA",
        "Margem de Lucro Líquida": "#F59E0B"
    }
)

margin_chart.update_traces(
    line=dict(width=3),
    marker=dict(size=9),
    hovertemplate=(
        "<b>Ano Fiscal:</b> %{x}<br>"
        "<b>Margem:</b> %{y:.2f}%"
        "<extra>%{fullData.name}</extra>"
    )
)

margin_chart.update_layout(
    template="plotly_dark",
    height=450,
    font=dict(family="Arial", size=12),
    title=dict(
        x=0.5,
        xanchor="center",
        font=dict(size=18)
    ),
    xaxis=dict(
        title="Ano Fiscal",
        tickmode="linear",
        dtick=1,
        showgrid=False,
        zeroline=False
    ),
    yaxis=dict(
        title="Margem (%)",
        ticksuffix="%",
        showgrid=True,
        zeroline=False
    ),
    legend=dict(
        title="Indicador",
        orientation="h",
        y=-0.2,
        x=0.5,
        xanchor="center"
    ),
    margin=dict(l=60, r=30, t=70, b=70)
)

st.plotly_chart(margin_chart, use_container_width=True)
