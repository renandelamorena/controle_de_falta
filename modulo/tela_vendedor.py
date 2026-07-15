"""Tela do vendedor: registrar faltas e acompanhar as proprias."""

import streamlit as st

from modulo import sheets


def render(usuario):
    st.header("🚚 Registrar falta")
    st.caption(f"Vendedor: **{usuario}**")

    cod = st.text_input("Código do produto", key="vend_cod").strip()

    produto, status = (None, None)
    if cod:
        produto, status = sheets.buscar_produto(cod)

    if status == "vazia":
        st.warning(
            "A aba `dados_rp` está vazia. Preencha-a com as colunas "
            "**cod, desc, grupo** para o vendedor conseguir buscar produtos."
        )
    elif status == "sem_coluna_cod":
        st.warning("A aba `dados_rp` não tem uma coluna de código (`cod`).")
    elif status == "nao_encontrado":
        st.error(f"Código **{cod}** não encontrado na aba `dados_rp`.")

    if produto:
        c1, c2 = st.columns(2)
        c1.text_input("Descrição", value=produto["desc"], disabled=True)
        c2.text_input("Grupo", value=produto["grupo"], disabled=True)

        with st.form("form_falta", clear_on_submit=True):
            obs = st.text_area("Observação do vendedor")
            enviar = st.form_submit_button("Registrar falta", type="primary")

        if enviar:
            sheets.registrar_falta(
                produto["cod"], produto["desc"], produto["grupo"], obs, usuario
            )
            st.success(f"Falta do produto **{produto['cod']}** registrada!")

    st.divider()
    st.subheader("📋 Minhas faltas")

    df = sheets.ler_aba(sheets.ABA_DADOS)
    if df.empty:
        st.info("Nenhuma falta registrada ainda.")
        return

    minhas = df[df["vendedor"].str.strip().str.lower() == usuario.strip().lower()]
    if minhas.empty:
        st.info("Você ainda não registrou nenhuma falta.")
    else:
        st.metric("Total de faltas registradas por você", len(minhas))
        st.dataframe(
            minhas.drop(columns=["_linha"]),
            hide_index=True,
            width="stretch",
        )
