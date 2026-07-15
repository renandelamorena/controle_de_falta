import pandas as pd
import os
import streamlit as st

def caminho_pasta(caminho_pasta, nome_arquivo):
    caminho_arquivo = os.path.join(caminho_pasta, nome_arquivo)
    return caminho_arquivo

# DADOS MELI
dados_anucios = pd.read_excel(caminho_pasta('tratamento_dados/dados_tratados/mlmg', 'df_final.xlsx'))
col_anuncios_meli = dados_anucios['SKU_x']

# DADOS EQUIPE
dados_equipe_ativos = pd.read_excel(
    caminho_pasta('tratamento_dados/dados_tratados/equipe', 'dados_tratados_equipe_mg.xlsx'),
    dtype={'Codigo': str}  # força a coluna Codigo a ser string
)
dados_equipe_ativos = dados_equipe_ativos[dados_equipe_ativos['Nome Grupo'] != 'USO CONSUMO']
col_ativos_equipe = dados_equipe_ativos['Codigo']

# DADOS EQUIPE
dados_equipe_ativos_rp = pd.read_excel(
    caminho_pasta('tratamento_dados/dados_tratados/equipe', 'dados_tratados_equipe_rp.xlsx'),
    dtype={'Codigo': str}  # força a coluna Codigo a ser string
)
dados_equipe_ativos_rp = dados_equipe_ativos_rp[dados_equipe_ativos_rp['Nome Grupo'] != 'USO CONSUMO']
col_ativos_equipe = dados_equipe_ativos_rp['Codigo']

dados_equipe_inativos = pd.read_excel(caminho_pasta('tratamento_dados/dados_tratados/equipe', 'dados_brutos_produtos_inativos_mg.xlsx'))

# DADOS TRAY
dados_tray_produtos = pd.read_excel(caminho_pasta('tratamento_dados/dados_tratados/tray', 'produtos_tratados.xlsx'))
dados_tray_variacoes = pd.read_excel(caminho_pasta('tratamento_dados/dados_tratados/tray', 'variacoes_tratadas.xlsx'))

df_produtos_tray = dados_tray_produtos[(dados_tray_produtos['referência']).astype(str).str.contains('MLMG')]
df_variacoes_tray = dados_tray_variacoes[(dados_tray_variacoes['referência']).astype(str).str.contains('MLMG')]

df_produtos_variacoes_tray = pd.concat([df_produtos_tray, df_variacoes_tray], ignore_index=True)
df_produtos_variacoes_tray['referência'] = (
    df_produtos_variacoes_tray['referência']
    .astype(str)
    .str.replace('MLMG', '', regex=False)
    .str.strip()
)

col_produtos_variacoes_tray = pd.concat([df_produtos_tray['referência'], df_variacoes_tray['referência']], ignore_index=True)
col_produtos_variacoes_tray = col_produtos_variacoes_tray.str.replace(" MLMG", "", regex=False)

# --- EQUIPE --- #

def dados_equipe_ativo():
    return dados_equipe_ativos
def dados_equipe_ativo_rp():
    return dados_equipe_ativos_rp

def dados_equipe_inativo():
    return dados_equipe_inativos

def dados_tray_pai():
    return df_produtos_tray

def dados_tray_filho():
    return df_variacoes_tray

# 1 Cadastrado Equipe; Sem Cadastro Tray
def cadastro_equipe_x_sem_cadastro_tray():

    selec_n_cadastrado = ~col_ativos_equipe.isin(col_produtos_variacoes_tray)
    df_n_cadastrado = dados_equipe_ativos[selec_n_cadastrado]

    # st.dataframe(col_n_cadastrado, hide_index=True)

    return df_n_cadastrado[['Codigo', 'Descricao', 'Qtde']]

# 2 Cadastrado Equipe; Sem Cadastro MELI
def cadastro_equipe_x_sem_cadastro_meli():

    col_ativos_equipe = dados_equipe_ativos['Codigo']

    selec_n_cadastrado = ~col_ativos_equipe.isin(col_anuncios_meli)
    df_n_cadastrado = dados_equipe_ativos[selec_n_cadastrado]

    # st.dataframe(df_n_cadastrado, hide_index=True)

    return df_n_cadastrado[['Codigo', 'Descricao', 'Qtde']]

# 3 Cadastrado Equipe; Sem Cadastro Calculo
def cadastro_equipe_x_sem_cadastro_calculo():

    col_ativos_equipe = dados_equipe_ativos['Codigo']
    col_anuncios_meli = dados_anucios['SKU_x']

    selec_n_cadastrado = ~col_ativos_equipe.isin(col_anuncios_meli)
    df_n_cadastrado = dados_equipe_ativos[selec_n_cadastrado]

    # st.dataframe(df_n_cadastrado, hide_index=True)

    return df_n_cadastrado[['Codigo', 'Descricao', 'Qtde']]

# 4 Queima, Zerado e ***ativo***; Cadastrado na Tray
def queima_zerado_ativo_x_cadastrado_tray():

    # seleção dos grupo de queima
    selec_dados_equipe_ativos_queima_zerado = (
        (dados_equipe_ativos['Nome Grupo'] == 'QUEIMA DIVERSOS') &
        (dados_equipe_ativos['Qtde'] == 0)
    )

    dados_equipe_ativos_queima_zerado = dados_equipe_ativos[selec_dados_equipe_ativos_queima_zerado]

    col_ativos_equipe = dados_equipe_ativos_queima_zerado['Codigo']

    selec_n_cadastrado = ~col_ativos_equipe.isin(col_produtos_variacoes_tray)
    df_cadastrado = dados_equipe_ativos_queima_zerado[selec_n_cadastrado]

    # st.dataframe(dados_equipe_ativos_queima_zerado, hide_index=True)

    return df_cadastrado[['Codigo', 'Descricao', 'Qtde']]

# 5 Queima, Zerado e ***ativo***; Cadastrado na MELI
def queima_zerado_ativo_x_cadastrado_meli():

    # seleção dos grupo de queima
    selec_dados_equipe_ativos_queima_zerado = (
        (dados_equipe_ativos['Nome Grupo'] == 'QUEIMA DIVERSOS') &
        (dados_equipe_ativos['Qtde'] == 0)
    )

    dados_equipe_ativos_queima_zerado = dados_equipe_ativos[selec_dados_equipe_ativos_queima_zerado]

    col_ativos_equipe = dados_equipe_ativos_queima_zerado['Codigo']

    selec_n_cadastrado = ~col_ativos_equipe.isin(col_anuncios_meli)
    df_cadastrado = dados_equipe_ativos_queima_zerado[selec_n_cadastrado]

    # st.dataframe(dados_equipe_ativos_queima_zerado, hide_index=True)

    return df_cadastrado[['Codigo', 'Descricao', 'Qtde']]

# 6

# 7 Queima, Zerado e ***ativo***; Não Cadastrado na Tray
def queima_zerado_ativo_x_n_cadastrado_tray():

    # seleção dos grupo de queima
    selec_dados_equipe_ativos_queima_zerado = (
        (dados_equipe_ativos['Nome Grupo'] == 'QUEIMA DIVERSOS') &
        (dados_equipe_ativos['Qtde'] == 0)
    )

    dados_equipe_ativos_queima_zerado = dados_equipe_ativos[selec_dados_equipe_ativos_queima_zerado]

    col_ativos_equipe = dados_equipe_ativos_queima_zerado['Codigo']

    selec_n_cadastrado = col_ativos_equipe.isin(col_produtos_variacoes_tray)
    df_cadastrado = dados_equipe_ativos_queima_zerado[selec_n_cadastrado]

    # st.dataframe(dados_equipe_ativos_queima_zerado, hide_index=True)

    return df_cadastrado[['Codigo', 'Descricao', 'Qtde']]

# 8 Queima, Zerado e ***ativo***; Não Cadastrado na Tray
def queima_zerado_ativo_x_n_cadastrado_meli():

    col_anuncios_meli = dados_anucios['SKU_x']

    # seleção dos grupo de queima
    selec_dados_equipe_ativos_queima_zerado = (
        (dados_equipe_ativos['Nome Grupo'] == 'QUEIMA DIVERSOS') &
        (dados_equipe_ativos['Qtde'] == 0)
    )

    dados_equipe_ativos_queima_zerado = dados_equipe_ativos[selec_dados_equipe_ativos_queima_zerado]

    col_ativos_equipe = dados_equipe_ativos_queima_zerado['Codigo']

    selec_n_cadastrado = col_ativos_equipe.isin(col_anuncios_meli)
    df_cadastrado = dados_equipe_ativos_queima_zerado[selec_n_cadastrado]

    # st.dataframe(dados_equipe_ativos_queima_zerado, hide_index=True)

    return df_cadastrado[['Codigo', 'Descricao', 'Qtde']]

# 9 

# 10 Queima, zerado e ***inativo***; Cadastrado na Tray
def queima_zerado_inativo_x_cadastrado_tray():

    dados_equipe_inativos_queima_zerado = dados_equipe_inativos

    col_ativos_equipe = dados_equipe_inativos_queima_zerado['Código']

    selec_n_cadastrado = col_ativos_equipe.isin(col_produtos_variacoes_tray)
    df_cadastrado = dados_equipe_inativos_queima_zerado[selec_n_cadastrado]

    # st.dataframe(dados_equipe_ativos_queima_zerado, hide_index=True)

    return df_cadastrado[['Código', 'Descrição']]

# 11
def queima_zerado_inativo_x_cadastrado_meli():

    col_anuncios_meli = dados_anucios['SKU_x']

    dados_equipe_inativos_queima_zerado = dados_equipe_inativos

    col_ativos_equipe = dados_equipe_inativos_queima_zerado['Código']

    selec_n_cadastrado = col_ativos_equipe.isin(col_anuncios_meli)
    df_cadastrado = dados_equipe_inativos_queima_zerado[selec_n_cadastrado]

    # st.dataframe(dados_equipe_ativos_queima_zerado, hide_index=True)

    return df_cadastrado[['Código', 'Descrição']]

# 12

# --- TRAY --- #

# 1 Cadastrado; Sem cadastro no Equipe
def cadastro_tray_x_n_cadastro_equipe():

    selec_n_cadastrado = ~col_produtos_variacoes_tray.isin(col_ativos_equipe)
    col_n_cadastrado = col_produtos_variacoes_tray[selec_n_cadastrado]

    selec_df_tray_n_cadastrado = df_produtos_variacoes_tray['referência'].isin(col_n_cadastrado)
    df_tray_n_cadastrado = df_produtos_variacoes_tray[selec_df_tray_n_cadastrado]

    # st.dataframe(df_tray_n_cadastrado, hide_index=True)

    return df_tray_n_cadastrado[['referência', 'nome_produto', 'estoque_atual']]

# 2 Cadastrado; Sem cadastro no Meli
def cadastro_tray_x_n_cadastro_meli():

    selec_n_cadastrado = ~col_produtos_variacoes_tray.isin(col_anuncios_meli)
    col_n_cadastrado = col_produtos_variacoes_tray[selec_n_cadastrado]

    selec_df_tray_n_cadastrado = df_produtos_variacoes_tray['referência'].isin(col_n_cadastrado)
    df_tray_n_cadastrado = df_produtos_variacoes_tray[selec_df_tray_n_cadastrado]

    # st.dataframe(df_tray_n_cadastrado, hide_index=True)

    return df_tray_n_cadastrado[['referência', 'nome_produto', 'estoque_atual']]

# 3 Cadastrado; Sem Calculo

# --- MELI --- #

# 

# --- CALCULO --- #

# 
