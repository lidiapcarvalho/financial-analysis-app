import streamlit as st

from src.users import create_user

st.title("Registo de Utilizador")

st.write(
    "Cria uma conta para utilizar a aplicação."
)

with st.form("registration_form"):

    username = st.text_input("Nome de utilizador")

    email = st.text_input("Endereço de e-mail")

    password = st.text_input(
        "Palavra-passe",
        type="password"
    )

    password_confirmation = st.text_input(
        "Confirmar palavra-passe",
        type="password"
    )

    submitted = st.form_submit_button(
        "Registar",
        use_container_width=True
    )

if submitted:

    if password != password_confirmation:
        st.error("As palavras-passe não coincidem.")

    else:
        success, message = create_user(
            username,
            email,
            password
        )

        if success:
            st.success(message)
        else:
            st.error(message)
