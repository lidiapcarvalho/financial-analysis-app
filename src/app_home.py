import streamlit as st

from src.database import initialize_database
from src.users import authenticate_user

# Configuração da aplicação
st.set_page_config(
    page_title="Financial Analysis App",
    page_icon="📊",
    layout="wide"
)

# Preparar a base de dados
initialize_database()

# Página inicial
st.title("Financial Analysis App")

st.write(
    "Plataforma de análise e comparação de dados financeiros de empresas."
)

st.divider()

st.subheader("Bem-vindo!")

st.markdown(
    """
    Esta aplicação permite:

    - Gerir empresas e os respetivos registos financeiros.
    - Consultar e analisar indicadores financeiros.
    - Acompanhar a evolução do desempenho financeiro.
    - Comparar o desempenho de diferentes empresas.
    """
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
