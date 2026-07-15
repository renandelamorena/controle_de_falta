"""Acesso ao Google Sheets (planilha controle_de_faltas).

Toda a leitura/escrita da aplicacao passa por aqui. A conexao usa a conta de
servico definida em .streamlit/secrets.toml e abre a planilha pela URL
configurada em [connections.gsheets], entao nada fica "chumbado" no codigo.
"""

from datetime import datetime

import gspread
import pandas as pd
import pytz
import streamlit as st
from google.oauth2.service_account import Credentials

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

# Nomes reais das abas na planilha
ABA_DADOS = "data"        # registros de falta
ABA_USERS = "user"        # login
ABA_RP = "dados_rp"       # cadastro de produtos (cod -> desc, grupo)

# Ordem das colunas da aba "data"
COLUNAS_DADOS = [
    "cod", "desc", "grupo", "data",
    "obs_vendedor", "obs_comprador", "vendedor", "comprador",
]

FUSO = pytz.timezone("America/Sao_Paulo")


# ---------------------------------------------------------------------------
# Conexao
# ---------------------------------------------------------------------------
@st.cache_resource(show_spinner="Conectando ao Google Sheets...")
def _planilha():
    conta = dict(st.secrets["google_service_account"])
    creds = Credentials.from_service_account_info(conta, scopes=SCOPE)
    cliente = gspread.authorize(creds)
    url = st.secrets["connections"]["gsheets"]["spreadsheet"]
    return cliente.open_by_url(url)


def _aba(nome):
    return _planilha().worksheet(nome)


def _dedupe(colunas):
    """Evita erro do pandas quando ha cabecalhos repetidos na planilha."""
    vistos, saida = {}, []
    for c in colunas:
        c = c or "col"
        if c in vistos:
            vistos[c] += 1
            saida.append(f"{c}_{vistos[c]}")
        else:
            vistos[c] = 0
            saida.append(c)
    return saida


# ---------------------------------------------------------------------------
# Leitura (com cache curto)
# ---------------------------------------------------------------------------
@st.cache_data(ttl=30, show_spinner=False)
def ler_aba(nome):
    """Le a aba inteira como DataFrame de strings.

    Adiciona a coluna auxiliar '_linha' com o numero REAL da linha na planilha
    (comeca em 2, ja que a linha 1 e o cabecalho). Isso permite atualizar a
    celula certa depois.
    """
    valores = _aba(nome).get_all_values()
    if not valores:
        return pd.DataFrame()
    header = _dedupe([h.strip() for h in valores[0]])
    df = pd.DataFrame(valores[1:], columns=header, dtype=str)
    df["_linha"] = range(2, len(df) + 2)
    return df


def limpar_cache():
    ler_aba.clear()


# ---------------------------------------------------------------------------
# Escrita
# ---------------------------------------------------------------------------
def adicionar_linha(nome, valores):
    _aba(nome).append_row(valores, value_input_option="USER_ENTERED")
    limpar_cache()


def atualizar_celula(nome, linha, coluna_1index, valor):
    _aba(nome).update_cell(linha, coluna_1index, valor)
    limpar_cache()


# ---------------------------------------------------------------------------
# Autenticacao (aba user)
# ---------------------------------------------------------------------------
def autenticar(usuario, senha):
    """Retorna {'usuario', 'cargo'} se login valido, senao None."""
    if not usuario or senha is None:
        return None
    df = ler_aba(ABA_USERS)
    if df.empty:
        return None
    alvo = df[df["usuario"].str.strip().str.lower() == usuario.strip().lower()]
    if alvo.empty:
        return None
    linha = alvo.iloc[0]
    if linha["senha"].strip() != str(senha).strip():
        return None
    return {
        "usuario": linha["usuario"].strip(),
        "cargo": linha["cargo"].strip().lower(),
    }


# ---------------------------------------------------------------------------
# Produtos (aba dados_rp)
# ---------------------------------------------------------------------------
def _achar_coluna(df, candidatos):
    mapa = {c.lower(): c for c in df.columns}
    for cand in candidatos:
        if cand in mapa:
            return mapa[cand]
    return None


def buscar_produto(cod):
    """Procura o codigo em dados_rp.

    Retorna (produto, status) onde status pode ser:
    'ok', 'vazia', 'sem_coluna_cod', 'nao_encontrado'.
    """
    df = ler_aba(ABA_RP)
    if df.empty or [c for c in df.columns if c != "_linha"] == []:
        return None, "vazia"

    col_cod = _achar_coluna(df, ["cod", "codigo", "codigo", "código"])
    col_desc = _achar_coluna(df, ["desc", "descricao", "descrição"])
    col_grupo = _achar_coluna(df, ["grupo"])

    if not col_cod:
        return None, "sem_coluna_cod"

    alvo = df[df[col_cod].str.strip() == str(cod).strip()]
    if alvo.empty:
        return None, "nao_encontrado"

    linha = alvo.iloc[0]
    produto = {
        "cod": str(cod).strip(),
        "desc": linha[col_desc].strip() if col_desc else "",
        "grupo": linha[col_grupo].strip() if col_grupo else "",
    }
    return produto, "ok"


# ---------------------------------------------------------------------------
# Faltas (aba data)
# ---------------------------------------------------------------------------
def registrar_falta(cod, desc, grupo, obs_vendedor, vendedor):
    agora = datetime.now(FUSO).strftime("%d/%m/%Y %H:%M")
    linha = [cod, desc, grupo, agora, obs_vendedor or "", "", vendedor, ""]
    adicionar_linha(ABA_DADOS, linha)


def assumir_falta(linha, comprador, obs_comprador=""):
    """Grava o comprador (e a obs opcional) na linha indicada da aba data."""
    atualizar_celula(ABA_DADOS, linha, COLUNAS_DADOS.index("comprador") + 1, comprador)
    if obs_comprador and obs_comprador.strip():
        atualizar_celula(
            ABA_DADOS, linha, COLUNAS_DADOS.index("obs_comprador") + 1, obs_comprador.strip()
        )
