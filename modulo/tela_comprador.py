"""Tela do comprador: ve todas as faltas, assume uma e acompanha as suas."""

import streamlit as st

from modulo import sheets


def render(usuario):
    st.header("🛒 Painel do comprador")
    st.caption(f"Comprador: **{usuario}**")

    df = sheets.ler_aba(sheets.ABA_DADOS)
    if df.empty:
        st.info("Nenhuma falta registrada pelos vendedores ainda.")
        return

    pendentes = df[df["comprador"].str.strip() == ""]
    minhas = df[df["comprador"].str.strip().str.lower() == usuario.strip().lower()]

    col1, col2, col3 = st.columns(3)
    col1.metric("Total de faltas", len(df))
    col2.metric("Pendentes", len(pendentes))
    col3.metric("Assumidas por mim", len(minhas))

    aba_todas, aba_assumir, aba_minhas = st.tabs(
        ["📚 Todas as faltas", "✋ Assumir falta", "✅ Minhas faltas assumidas"]
    )

    with aba_todas:
        st.dataframe(
            df.drop(columns=["_linha"]), hide_index=True, width="stretch"
        )

    with aba_assumir:
        if pendentes.empty:
            st.success("Não há faltas pendentes. Tudo assumido! 🎉")
        else:
            opcoes = {
                f'{r["cod"]} · {r["desc"]} · vendedor: {r["vendedor"]}  (linha {r["_linha"]})':
                int(r["_linha"])
                for _, r in pendentes.iterrows()
            }
            escolha = st.selectbox("Falta pendente", list(opcoes.keys()))
            obs = st.text_area("Observação do comprador (opcional)")
            if st.button("Assumir esta falta", type="primary"):
                sheets.assumir_falta(opcoes[escolha], usuario, obs)
                st.success("Falta assumida com sucesso!")
                st.rerun()

    with aba_minhas:
        if minhas.empty:
            st.info("Você ainda não assumiu nenhuma falta.")
        else:
            st.dataframe(
                minhas.drop(columns=["_linha"]),
                hide_index=True,
                width="stretch",
            )
