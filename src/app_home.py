import streamlit as st

from src.database import initialize_database
from src.users import authenticate_user
from src.companies import get_all_companies
from src.financial_records import get_all_financial_records

# Configuração da aplicação
st.set_page_config(
    page_title="Financial Analysis App",
    page_icon="📊",
    layout="wide"
)

# Preparar a base de dados
initialize_database()

# Consultar dados para o painel de controlo
companies = get_all_companies()
financial_records = get_all_financial_records()

# Página inicial
st.title("Financial Analysis App")

st.write(
    "Plataforma de análise e comparação de dados financeiros de empresas."
)

st.divider()

st.subheader("Visão Geral")

# Estatísticas gerais
total_companies = len(companies)
total_financial_records = len(financial_records)

companies_with_records = {
    record[1]
    for record in financial_records
}

total_companies_with_records = len(companies_with_records)

if financial_records:
    latest_fiscal_year = max(
        record[2]
        for record in financial_records
    )
else:
    latest_fiscal_year = None

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Empresas", total_companies)

with col2:
    st.metric("Registos Financeiros", total_financial_records)

with col3:
    st.metric("Empresas com Dados", total_companies_with_records)

with col4:
    st.metric(
        "Ano Fiscal Mais Recente",
        latest_fiscal_year if latest_fiscal_year is not None else "N/A"
    )

if not companies:
    st.info(
        "Ainda não existem empresas registadas na aplicação."
    )

if not financial_records:
    st.info(
        "Ainda não existem registos financeiros disponíveis."
    )

st.divider()

st.subheader("Acessos Rápidos")

if st.session_state.get("authenticated", False):

    col1, col2, col3 = st.columns(3)

    with col1:
        st.page_link(
            "pages/1_Empresas.py",
            label="Empresas",
            icon="🏢"
        )

        st.page_link(
            "pages/2_Registos_Financeiros.py",
            label="Registos Financeiros",
            icon="📁"
        )

    with col2:
        st.page_link(
            "pages/3_Analise_Financeira.py",
            label="Análise Financeira",
            icon="📊"
        )

        st.page_link(
            "pages/4_Comparacao.py",
            label="Comparação",
            icon="⚖️"
        )

    with col3:
        st.page_link(
            "pages/6_Comparacoes_Guardadas.py",
            label="Comparações Guardadas",
            icon="🔖"
        )

else:

    st.page_link(
        "pages/5_Registo.py",
        label="Registar Utilizador",
        icon="👤"
    )

    st.info(
        "Inicia sessão através do formulário abaixo "
        "para aceder às funcionalidades de gestão financeira."
    )

st.divider()

# Autenticação do utilizador

if st.session_state.get("authenticated", False):

    st.success(
        f" Sessão iniciada como {st.session_state['user']['username']}."
    )

    if st.button("Terminar sessão"):
        st.session_state.pop("authenticated", None)
        st.session_state.pop("user", None)
        st.rerun()

else:

    st.subheader("Iniciar sessão")

    with st.form("login_form"):

        username = st.text_input("Nome de utilizador")
        password = st.text_input(
            "Palavra-passe",
            type="password"
        )

        submitted = st.form_submit_button(
            "Entrar",
            use_container_width=True
        )

    if submitted:

        success, user = authenticate_user(username, password)

        if success:
            st.session_state["authenticated"] = True
            st.session_state["user"] = user
            st.success("Autenticação efetuada com sucesso.")
            st.rerun()

        else:
            st.error("Nome de utilizador ou palavra-passe incorretos.")

    st.info("Ainda não tens conta? Utiliza a página de registo para criar uma.")
