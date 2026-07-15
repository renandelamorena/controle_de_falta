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
from gspread.utils import rowcol_to_a1

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
# Leitura
# ---------------------------------------------------------------------------
def _montar_df(valores):
    """Transforma get_all_values() num DataFrame de strings.

    Adiciona a coluna auxiliar '_linha' com o numero REAL da linha na planilha
    (comeca em 2, ja que a linha 1 e o cabecalho). Isso permite atualizar a
    celula certa depois, mesmo com varios usuarios editando ao mesmo tempo.
    """
    if not valores:
        return pd.DataFrame()
    header = _dedupe([h.strip() for h in valores[0]])
    df = pd.DataFrame(valores[1:], columns=header, dtype=str)
    df["_linha"] = range(2, len(df) + 2)
    return df


@st.cache_data(ttl=30, show_spinner=False)
def ler_aba(nome):
    """Leitura com cache curto, COMPARTILHADO entre todas as sessoes do
    servidor. Com ~100 usuarios isso segura a cota da API do Google: a aba e
    lida no maximo 1x a cada 30s, nao 1x por usuario."""
    return _montar_df(_aba(nome).get_all_values())


def ler_aba_sem_cache(nome):
    """Leitura direta (ignora o cache). Usada na hora de salvar para detectar
    conflitos com o que outro usuario possa ter gravado nesse meio tempo."""
    return _montar_df(_aba(nome).get_all_values())


def limpar_cache():
    ler_aba.clear()


def _indices_colunas(nome):
    df = ler_aba(nome)
    cols = [c for c in df.columns if c != "_linha"]
    return {c: i + 1 for i, c in enumerate(cols)}


# ---------------------------------------------------------------------------
# Escrita
# ---------------------------------------------------------------------------
# RAW: o Sheets NAO interpreta o que gravamos, entao codigos como "007" ou
# codigos longos ficam como texto (nao viram numero nem notacao cientifica).
def adicionar_linha(nome, valores):
    _aba(nome).append_row(valores, value_input_option="RAW")
    limpar_cache()


def atualizar_lote(nome, celulas):
    """Grava varias celulas numa UNICA chamada de API (batch_update).

    celulas: lista de (linha, coluna_nome, valor).
    """
    if not celulas:
        return
    indices = _indices_colunas(nome)
    dados = []
    for linha, coluna, valor in celulas:
        col = indices[coluna]
        texto = "" if valor is None or pd.isna(valor) else str(valor)
        dados.append({"range": rowcol_to_a1(int(linha), col), "values": [[texto]]})
    _aba(nome).batch_update(dados, value_input_option="RAW")
    limpar_cache()


def formatar_coluna_texto(nome, coluna_letra):
    """Define o formato da coluna inteira como texto puro na planilha.

    Garante que codigos digitados direto na planilha (fora do app) tambem
    fiquem como texto, preservando zeros a esquerda.
    """
    _aba(nome).format(f"{coluna_letra}:{coluna_letra}", {"numberFormat": {"type": "TEXT"}})
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


def registros_recentes(cod, dias=7):
    """Registros de falta do MESMO codigo nos ultimos `dias` dias.

    Serve de alerta anti-duplicidade: avisa o vendedor que aquele item ja foi
    registrado recentemente. Retorna um DataFrame (vazio se nao houver)
    ordenado do mais recente para o mais antigo.
    """
    df = ler_aba(ABA_DADOS)
    if df.empty:
        return df
    mesmo = df[df["cod"].str.strip() == str(cod).strip()].copy()
    if mesmo.empty:
        return mesmo
    mesmo["_dt"] = pd.to_datetime(
        mesmo["data"], format="%d/%m/%Y %H:%M", errors="coerce"
    )
    corte = pd.Timestamp.now() - pd.Timedelta(days=dias)
    recentes = mesmo[mesmo["_dt"] >= corte]
    return recentes.sort_values("_dt", ascending=False)


def assumir_faltas_lote(atribuicoes, observacoes=None):
    """Assume varias faltas de uma vez, com checagem de conflito.

    atribuicoes: dict {linha_da_planilha: nome_do_comprador}.
    observacoes: dict opcional {linha_da_planilha: obs_comprador}.

    Antes de gravar, relê a aba SEM cache e confirma que cada linha ainda esta
    pendente (coluna comprador vazia). Se outro usuario ja tiver assumido a
    linha nesse meio tempo, ela e ignorada e volta na lista de conflitos.
    O comprador e a observacao vao na MESMA chamada em lote (1 request).

    Retorna (gravados, conflitos): dict das que foram gravadas e lista das
    linhas que ja estavam assumidas.
    """
    observacoes = observacoes or {}
    fresco = ler_aba_sem_cache(ABA_DADOS)
    if fresco.empty:
        return {}, list(atribuicoes.keys())

    pendentes = set(
        fresco.loc[fresco["comprador"].str.strip() == "", "_linha"].astype(int)
    )

    gravados, conflitos, celulas = {}, [], []
    for linha, comprador in atribuicoes.items():
        linha = int(linha)
        if linha in pendentes:
            celulas.append((linha, "comprador", comprador))
            obs = observacoes.get(linha, "")
            if obs and str(obs).strip():
                celulas.append((linha, "obs_comprador", str(obs).strip()))
            gravados[linha] = comprador
        else:
            conflitos.append(linha)

    atualizar_lote(ABA_DADOS, celulas)
    return gravados, conflitos


def listar_compradores():
    """Nomes de usuarios com cargo comprador (para o seletor de responsavel)."""
    df = ler_aba(ABA_USERS)
    if df.empty:
        return []
    mask = df["cargo"].str.strip().str.lower() == "comprador"
    return sorted(df.loc[mask, "usuario"].str.strip().unique().tolist())


def filtrar_periodo(df, periodo):
    """Filtra o DataFrame pela coluna 'data' (formato dd/mm/YYYY HH:MM).

    periodo: 'Tudo'/None (sem filtro), ou algo contendo '30' ou '60'.
    """
    if df.empty or periodo in (None, "Tudo"):
        return df
    dias = 30 if "30" in str(periodo) else 60
    dt = pd.to_datetime(df["data"], format="%d/%m/%Y %H:%M", errors="coerce")
    corte = pd.Timestamp.now() - pd.Timedelta(days=dias)
    return df[dt >= corte]
