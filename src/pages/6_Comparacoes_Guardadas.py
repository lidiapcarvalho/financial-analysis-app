import streamlit as st

from src.saved_comparisons import (
    get_saved_comparisons,
    get_saved_comparison_details,
    update_comparison_notes,
    delete_saved_comparison
)

user_id = st.session_state["user"]["id"]


@st.dialog("Confirmar eliminação")
def confirm_delete_dialog(comparison_id):
    st.warning("Tens a certeza de que pretendes eliminar esta comparação?")

    if st.button("Confirmar eliminação", type="primary"):
        success = delete_saved_comparison(
            user_id,
            comparison_id
        )

        if success:
            st.success("Comparação eliminada com sucesso!")
            st.rerun()
        else:
            st.error("Não foi possível eliminar a comparação.")


st.title("Comparações Guardadas")

st.write("Consulte e gira as suas comparações financeiras guardadas.")

comparisons = get_saved_comparisons(user_id)

if comparisons:
    st.subheader("As minhas comparações")

    for comparison in comparisons:
        comparison_id, name, created_at, notes = comparison

        with st.expander(name):
            st.caption(f"Criada em: {created_at}")

            details = get_saved_comparison_details(
                user_id,
                comparison_id
            )

            if details:
                if st.button(
                    "Abrir comparação",
                    key=f"open_{comparison_id}"
                ):
                    st.session_state["saved_comparison"] = details

                    st.switch_page("pages/4_Comparacao.py")

            if details and details["companies"]:
                st.write("**Empresas:**")

                for company_id, company_name in details["companies"]:
                    st.write(f"- {company_name}")

            if details and details["fiscal_years"]:
                st.write("**Anos fiscais:**")
                st.write(", ".join(map(str, details["fiscal_years"])))

            if details:
                if details and details["notes"]:
                    st.write("**Notas:**")
                    st.write(details["notes"])

                st.divider()
                st.write("**Editar notas**")

                updated_notes = st.text_area(
                    "Notas da comparação",
                    value=details["notes"] or "",
                    key=f"notes_{comparison_id}"
                )

                if st.button(
                    "Guardar notas",
                    key=f"save_notes_{comparison_id}"
                ):
                    success = update_comparison_notes(
                        user_id,
                        comparison_id,
                        updated_notes
                    )

                    if success:
                        st.success("Notas atualizadas com sucesso!")
                    else:
                        st.error("Não foi possível atualizar as notas.")

            st.divider()

            if st.button(
                "Eliminar comparação",
                key=f"delete_{comparison_id}",
                type="secondary"
            ):
                confirm_delete_dialog(comparison_id)

else:
    st.info("Ainda não existem comparações guardadas.")
