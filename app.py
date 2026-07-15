"""Controle de Faltas - Multieletrica.

Login pela aba `user` do Google Sheets e, conforme o cargo, mostra a tela do
vendedor (registrar faltas) ou do comprador (assumir faltas).
"""

import streamlit as st

from modulo import sheets, tela_comprador, tela_vendedor

st.set_page_config(
    page_title="Controle de Faltas",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)

if "usuario" not in st.session_state:
    st.session_state.usuario = None
    st.session_state.cargo = None


def tela_login():
    st.title("📦 Controle de Faltas")
    st.caption("Multieletrica")

    with st.form("login"):
        usuario = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")
        entrar = st.form_submit_button("Entrar", type="primary")

    if entrar:
        dados = sheets.autenticar(usuario, senha)
        if dados:
            st.session_state.usuario = dados["usuario"]
            st.session_state.cargo = dados["cargo"]
            st.rerun()
        else:
            st.error("Usuário ou senha incorretos.")


def barra_lateral():
    with st.sidebar:
        st.write(f"👤 **{st.session_state.usuario}**")
        st.caption(f"Cargo: {st.session_state.cargo}")
        st.divider()
        if st.button("🔄 Atualizar dados", width="stretch"):
            sheets.limpar_cache()
            st.rerun()
        if st.button("Sair", width="stretch"):
            st.session_state.usuario = None
            st.session_state.cargo = None
            st.rerun()


def main():
    if not st.session_state.usuario:
        tela_login()
        return

    barra_lateral()

    cargo = (st.session_state.cargo or "").lower()
    if cargo == "vendedor":
        tela_vendedor.render(st.session_state.usuario)
    elif cargo == "comprador":
        tela_comprador.render(st.session_state.usuario)
    else:
        st.warning(
            f"Cargo '{cargo}' não tem tela definida. "
            "Use `vendedor` ou `comprador` na coluna **cargo** da aba `user`."
        )


main()
