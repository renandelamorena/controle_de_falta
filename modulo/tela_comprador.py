"""Tela do comprador: metricas com filtro de periodo, top 5 produtos com mais
faltas, assumir faltas em lote (editor + validacao) e editar as assumidas."""

import altair as alt
import streamlit as st

from modulo import sheets

VERMELHO = "#c6090e"  # cor primaria do tema


def _grafico_top5(df):
    st.subheader("🏆 Top 5 produtos com mais faltas")
    if df.empty:
        st.info("Sem faltas no período selecionado.")
        return

    contagem = (
        df.groupby(["cod", "desc"]).size().reset_index(name="faltas")
        .sort_values("faltas", ascending=False).head(5)
    )
    contagem["produto"] = (
        contagem["cod"].str.strip() + " · " + contagem["desc"].str.slice(0, 35)
    )

    grafico = (
        alt.Chart(contagem)
        .mark_bar(color=VERMELHO)
        .encode(
            x=alt.X("faltas:Q", title="Nº de faltas"),
            y=alt.Y("produto:N", sort="-x", title=None),
            tooltip=[
                alt.Tooltip("cod:N", title="Código"),
                alt.Tooltip("desc:N", title="Descrição"),
                alt.Tooltip("faltas:Q", title="Faltas"),
            ],
        )
        .properties(width="container", height=260)
    )
    st.altair_chart(grafico)


def _aba_assumir(df, usuario):
    pendentes = df[df["comprador"].str.strip() == ""]
    if pendentes.empty:
        st.success("Não há faltas pendentes. Tudo assumido! 🎉")
        return

    st.caption(
        f"Marque **Assumir** nas faltas que quiser pegar (opcionalmente escreva "
        f"uma observação) e clique em salvar. Elas entram como assumidas por "
        f"**{usuario}**. Você pode assumir várias de uma vez."
    )

    ctx = ["cod", "desc", "grupo", "data", "obs_vendedor", "vendedor"]
    base = pendentes.set_index("_linha")[ctx].copy()
    base["obs_comprador"] = ""
    base["Assumir"] = False

    editado = st.data_editor(
        base,
        hide_index=True,
        disabled=ctx,
        column_config={
            "cod": "Código",
            "desc": "Descrição",
            "grupo": "Grupo",
            "data": "Data",
            "obs_vendedor": "Obs. vendedor",
            "vendedor": "Vendedor",
            "obs_comprador": st.column_config.TextColumn(
                "Obs. comprador", help="Observação sua ao assumir a falta"
            ),
            "Assumir": st.column_config.CheckboxColumn(
                "Assumir", help=f"Marque para assumir como {usuario}", default=False
            ),
        },
        width="stretch",
        key="editor_assumir",
    )

    marcadas = editado[editado["Assumir"].fillna(False).astype(bool)]

    # ---- validacao (mostrada ANTES de salvar) ----
    st.markdown(f"**Validação:** {len(marcadas)} falta(s) marcada(s) para assumir.")
    if marcadas.empty:
        return

    previa = marcadas.reset_index()[["cod", "desc", "vendedor", "obs_comprador"]]
    previa.insert(3, "responsável", usuario)
    st.dataframe(previa, hide_index=True, width="stretch")

    if st.button("Salvar e assumir faltas", type="primary", key="btn_assumir"):
        atribuicoes = {int(linha): usuario for linha in marcadas.index}
        observacoes = {
            int(linha): row["obs_comprador"] for linha, row in marcadas.iterrows()
        }
        gravados, conflitos = sheets.assumir_faltas_lote(atribuicoes, observacoes)
        if gravados:
            st.success(f"{len(gravados)} falta(s) assumida(s) com sucesso!")
        if conflitos:
            st.warning(
                f"{len(conflitos)} falta(s) já haviam sido assumidas por outra "
                "pessoa e foram ignoradas."
            )
        st.rerun()


def _aba_minhas(df, usuario):
    minhas = df[df["comprador"].str.strip().str.lower() == usuario.strip().lower()]
    if minhas.empty:
        st.info("Você ainda não assumiu nenhuma falta.")
        return

    st.caption("Você pode editar a observação do comprador e salvar.")
    cols = ["cod", "desc", "grupo", "data", "obs_vendedor", "obs_comprador"]
    base = minhas.set_index("_linha")[cols].copy()

    editado = st.data_editor(
        base,
        hide_index=True,
        disabled=["cod", "desc", "grupo", "data", "obs_vendedor"],
        column_config={
            "cod": "Código",
            "desc": "Descrição",
            "grupo": "Grupo",
            "data": "Data",
            "obs_vendedor": "Obs. vendedor",
            "obs_comprador": st.column_config.TextColumn("Obs. comprador"),
        },
        width="stretch",
        key="editor_minhas_comp",
    )

    alteradas = editado[editado["obs_comprador"].fillna("") != base["obs_comprador"].fillna("")]
    if st.button("Salvar observações", type="primary", key="btn_obs_comp"):
        if alteradas.empty:
            st.info("Nenhuma observação foi alterada.")
        else:
            celulas = [
                (int(linha), "obs_comprador", row["obs_comprador"])
                for linha, row in alteradas.iterrows()
            ]
            sheets.atualizar_lote(sheets.ABA_DADOS, celulas)
            st.success(f"{len(celulas)} observação(ões) atualizada(s)!")
            st.rerun()


def render(usuario):
    st.header("🛒 Painel do comprador")
    st.caption(f"Comprador: **{usuario}**")

    df = sheets.ler_aba(sheets.ABA_DADOS)
    if df.empty:
        st.info("Nenhuma falta registrada pelos vendedores ainda.")
        return

    # ---- filtro de periodo (afeta metricas e grafico) ----
    periodo = st.segmented_control(
        "Período das métricas",
        ["Tudo", "Últimos 60 dias", "Últimos 30 dias"],
        default="Tudo",
        key="periodo_comprador",
    )
    df_periodo = sheets.filtrar_periodo(df, periodo)

    pendentes = df_periodo[df_periodo["comprador"].str.strip() == ""]
    minhas = df_periodo[
        df_periodo["comprador"].str.strip().str.lower() == usuario.strip().lower()
    ]
    c1, c2, c3 = st.columns(3)
    c1.metric("Total de faltas", len(df_periodo))
    c2.metric("Pendentes", len(pendentes))
    c3.metric("Assumidas por mim", len(minhas))

    _grafico_top5(df_periodo)

    st.divider()
    aba_todas, aba_assumir, aba_minhas = st.tabs(
        ["📚 Todas as faltas", "✋ Assumir faltas", "✅ Minhas faltas assumidas"]
    )
    with aba_todas:
        st.dataframe(
            df.drop(columns=["_linha"]), hide_index=True, width="stretch"
        )
    with aba_assumir:
        _aba_assumir(df, usuario)
    with aba_minhas:
        _aba_minhas(df, usuario)
