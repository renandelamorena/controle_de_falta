"""Tela do vendedor: registrar faltas e acompanhar as proprias."""

import streamlit as st

from modulo import sheets

DIAS_ALERTA = 7


def _aviso_registros_recentes(cod, usuario):
    """Alerta se o mesmo codigo ja teve falta registrada nos ultimos dias."""
    recentes = sheets.registros_recentes(cod, dias=DIAS_ALERTA)
    if recentes.empty:
        return

    st.warning(
        f"⚠️ Este item (**{cod}**) já tem **{len(recentes)}** registro(s) de "
        f"falta nos últimos {DIAS_ALERTA} dias."
    )

    meus = recentes[
        recentes["vendedor"].str.strip().str.lower() == usuario.strip().lower()
    ]
    if not meus.empty:
        ultima = meus.iloc[0]["data"]
        st.info(f"Você mesmo já registrou este item em **{ultima}**.")

    with st.expander("Ver registros recentes deste item"):
        st.dataframe(
            recentes[["data", "vendedor", "obs_vendedor", "comprador"]],
            hide_index=True,
            width="stretch",
        )


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

    if cod:
        _aviso_registros_recentes(cod, usuario)

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
        return

    periodo = st.segmented_control(
        "Período",
        ["Tudo", "Últimos 60 dias", "Últimos 30 dias"],
        default="Tudo",
        key="periodo_vendedor",
    )
    minhas = sheets.filtrar_periodo(minhas, periodo)
    st.metric("Faltas no período", len(minhas))

    if minhas.empty:
        st.info("Nenhuma falta no período selecionado.")
        return

    st.caption("Você pode editar a **observação do vendedor** e salvar.")
    cols = ["cod", "desc", "grupo", "data", "obs_vendedor", "obs_comprador", "comprador"]
    base = minhas.set_index("_linha")[cols].copy()

    editado = st.data_editor(
        base,
        hide_index=True,
        disabled=["cod", "desc", "grupo", "data", "obs_comprador", "comprador"],
        column_config={
            "cod": "Código",
            "desc": "Descrição",
            "grupo": "Grupo",
            "data": "Data",
            "obs_vendedor": st.column_config.TextColumn("Obs. vendedor"),
            "obs_comprador": "Obs. comprador",
            "comprador": "Assumida por",
        },
        width="stretch",
        key="editor_vendedor",
    )

    alteradas = editado[
        editado["obs_vendedor"].fillna("") != base["obs_vendedor"].fillna("")
    ]
    if st.button("Salvar observações", type="primary", key="btn_obs_vend"):
        if alteradas.empty:
            st.info("Nenhuma observação foi alterada.")
        else:
            celulas = [
                (int(linha), "obs_vendedor", row["obs_vendedor"])
                for linha, row in alteradas.iterrows()
            ]
            sheets.atualizar_lote(sheets.ABA_DADOS, celulas)
            st.success(f"{len(celulas)} observação(ões) atualizada(s)!")
            st.rerun()
