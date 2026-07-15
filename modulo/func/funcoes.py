import streamlit as st
from streamlit_gsheets import GSheetsConnection
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from time import sleep
from datetime import datetime
import pytz
import base64

import pandas as pd

try:
    from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
    from streamlit_cookies_controller import CookieController
except ImportError:
    BadSignature = SignatureExpired = URLSafeTimedSerializer = CookieController = None

AUTH_COOKIE_NAME = "ecommerce_multi_login"
AUTH_COOKIE_MAX_AGE = 60 * 60 * 24 * 30

def iniciar_coneccao(nome_planilha):
    # Ler as credenciais do secrets.toml
    google_service_account = st.secrets["google_service_account"]

    # Configuração do escopo e autenticação
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(google_service_account, scope)
    client = gspread.authorize(creds)

    # Abrir a planilha
    spreadsheet = client.open(nome_planilha)

    # Objeto de conexão com o Google Sheets
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    return spreadsheet, conn, client

def update_registro_confg(spreadsheet, worksheet_name, row_index, col_name, new_value, df):
    try:
        worksheet = spreadsheet.worksheet(worksheet_name)
        
        # Localizar o índice da coluna (gspread usa 1-index)
        col_index = df.columns.get_loc(col_name) + 1
        
        # Atualizar a célula específica
        worksheet.update_cell(row_index + 2, col_index, new_value)
        st.warning(":green[Registro alterado!]")
        
    except gspread.exceptions.APIError as e:
        st.error(f"Erro ao alterar o registro: {e}")
    except Exception as e:
        st.error(f"Ocorreu um erro inesperado: {e}")
        
def conect_users(conn):
    
    return conn.read(worksheet='user', ttl=60)

# def conect_data(client):
    
#     sheet = client.open("DADOS_CALCULO").worksheet("data")
#     valores = sheet.get_all_values()  # <- Aqui preserva os zeros à esquerda
#     valores = sheet.get_all_values()
#     colunas = valores[0]

#     # Adiciona sufixos para duplicatas
#     seen = {}
#     for i, col in enumerate(colunas):
#         if col in seen:
#             seen[col] += 1
#             colunas[i] = f"{col}_{seen[col]}"
#         else:
#             seen[col] = 0

#     dados = pd.DataFrame(valores[1:], columns=colunas)
        
#     return dados

@st.cache_data(ttl=30)
def conect_data(_client):
    sheet = _client.open("DADOS_CALCULO").worksheet("data")
    valores = sheet.get_all_values()

    colunas = valores[0]

    # Resolver duplicatas
    seen = {}
    for i, col in enumerate(colunas):
        if col in seen:
            seen[col] += 1
            colunas[i] = f"{col}_{seen[col]}"
        else:
            seen[col] = 0

    dados = pd.DataFrame(valores[1:], columns=colunas)
    return dados

def autenticar_usuario(df , user, senha):
    
    if user in df['usuario'].values:
        user_row = df.loc[df['usuario'] == user]
        senha_armazenada = user_row['senha'].values[0]
        if senha_armazenada == senha:
            return True
    return False

def retorna_cargo(df, user):
    
    user_row = df.loc[df['usuario'] == user]
    
    return user_row['cargo'].values[0]

def _auth_cookie_secret():
    if "auth_cookie_key" in st.secrets:
        return st.secrets["auth_cookie_key"]

    google_service_account = st.secrets.get("google_service_account", {})
    return google_service_account.get("private_key") or google_service_account.get("client_email")

def _auth_cookie_controller():
    if CookieController is None:
        return None

    return CookieController()

def _auth_cookie_serializer():
    if URLSafeTimedSerializer is None:
        return None

    secret = _auth_cookie_secret()
    if not secret:
        return None

    return URLSafeTimedSerializer(secret)

def salvar_login_cookie(user):
    controller = _auth_cookie_controller()
    serializer = _auth_cookie_serializer()

    if controller is None or serializer is None:
        return False

    token = serializer.dumps({"user": user})
    controller.set(AUTH_COOKIE_NAME, token, max_age=AUTH_COOKIE_MAX_AGE)
    return True

def remover_login_cookie():
    controller = _auth_cookie_controller()

    if controller is not None:
        controller.remove(AUTH_COOKIE_NAME)

def restaurar_login_cookie():
    if st.session_state.get("user") and st.session_state.get("role"):
        return False

    controller = _auth_cookie_controller()
    serializer = _auth_cookie_serializer()

    if controller is None or serializer is None:
        return False

    token = controller.get(AUTH_COOKIE_NAME)
    if not token:
        return False

    try:
        dados_cookie = serializer.loads(token, max_age=AUTH_COOKIE_MAX_AGE)
    except (BadSignature, SignatureExpired):
        remover_login_cookie()
        return False

    user = dados_cookie.get("user")
    if not user:
        remover_login_cookie()
        return False

    try:
        _, conn, _ = iniciar_coneccao('DADOS_CALCULO')
        df = conect_users(conn).astype(str)

        if user not in df['usuario'].values:
            remover_login_cookie()
            return False

        st.session_state.user = user
        st.session_state.role = str(retorna_cargo(df, user)).strip()
        return True
    except Exception:
        return False

def login(conn):
    
    st.header('Entrar')
    
    with st.form('formulario_login'):
    
        user = st.text_input('Usuário', value=None, key='usuario_login')
        senha = st.text_input('Senha', type='password', value=None, key='sennha_login')
        
        if st.form_submit_button('Entrar'):
        
            if senha != None:

                df = conect_users(conn)
                df = df.astype(str)
                                
                autenticacao = autenticar_usuario(df, user, senha)
                
                if autenticacao == True:
                    cargo = str(retorna_cargo(df, user)).strip()
                                        
                    st.session_state.user = user
                    st.session_state.role = cargo
                    salvar_login_cookie(user)
                                        
                    st.success(':green-background[Logado com sucesso!]')
                                        
                    st.rerun()
                else:
                    st.error('Usuario e/ou senha incorreto(s)')    
                
            else:
                st.warning('Senha não informada')

# @st.cache_resource()
def tela_login_ou_registro():

    spreadsheet, conn, client = iniciar_coneccao('DADOS_CALCULO')

    st.title('Ecommerce Multieletrica')
    
    login(conn)

def somar_estoque(client, valor):

    # Abre a planilha pelo nome e seleciona a aba "estoque"
    planilha = client.open('DADOS_CALCULO').worksheet("estoque")

    # Obtém o valor da coluna "estoque" na linha 2
    valor_estoque = planilha.cell(2, planilha.find('estoque').col).value  # Procura a coluna "estoque"

    # Converte o valor para float (ou int, dependendo do que for necessário)
    valor_estoque = float(valor_estoque) if valor_estoque else 0

    # Soma o valor (exemplo: adicionando 10)
    valor_estoque += valor

    # Atualiza o valor na planilha
    planilha.update_cell(2, planilha.find('estoque').col, valor_estoque)
    
def adicionar_linha(client, nova_linha, aba):

    planilha = client.open('DADOS_CALCULO').worksheet(aba)

    # Adiciona a nova linha
    planilha.append_row(nova_linha)

def editar_linha(client, linha, novos_valores, aba):
    
    planilha = client.open('DADOS_CALCULO').worksheet(aba)

    # Ex.: se a planilha vai de A até, digamos, coluna AK
    range_name = f"A{linha}:AK{linha}"

    # worksheet.update espera uma lista de listas (2D)
    planilha.update(range_name, [novos_valores])

def salvar_linha(client, nova_linha, aba, acao="adicionar", linha_editar=None):
    """
    acao: "adicionar" (padrão) ou "editar"
    linha: número da linha quando acao = "editar"
    """
    planilha = client.open('DADOS_CALCULO').worksheet(aba)

    if acao == "adicionar":
        # Adiciona nova linha no final
        planilha.append_row(nova_linha)

    elif acao == "editar":
        if linha_editar is None:
            raise ValueError("Para editar, informe o parâmetro 'linha'.")

        # Ajuste o fim do range (AK) de acordo com a quantidade de colunas
        range_name = f"A{linha_editar}:AK{linha_editar}"
        planilha.update(range_name, [nova_linha])

    else:
        raise ValueError("acao deve ser 'adicionar' ou 'editar'.")

def formulario_cancelar_linha(df, spreadsheet, key, worksheet_name):
    with st.form(key, clear_on_submit=True):
                
        id_atv = st.number_input('Selecione o "ID" do registro :red[*]', min_value=1, step=1, value=None, placeholder=None)
        
        # Interface de edição
        selected_row = id_atv
        selected_column = 'Situação'
        new_value = 'Cancelado'

        # Botão para confirmar a edição
        if st.form_submit_button('Confirmar'):
                        
            if id_atv:
                if any(df['id'] == id_atv):
                    try:
                        update_google_sheet_gspread(df, spreadsheet, worksheet_name, (selected_row - 1), selected_column, new_value)
                        st.rerun()
                        
                    except gspread.exceptions.APIError as e:
                        st.error(f"Erro ao cancelar registro: {e}")
                else:
                    st.error('Registro não encontrado')
            else:
                st.error("Por favor, preencha todos os campos obrigatórios :red[*]")
                
def update_google_sheet_gspread(df, spreadsheet, worksheet_name, row_index, col_name, new_value):
    try:
        worksheet = spreadsheet.worksheet(worksheet_name)
        
        # Localizar o índice da coluna (gspread usa 1-index)
        col_index = df.columns.get_loc(col_name) + 1
        
        # Ler o valor atual da célula para verificar se já está cancelado
        current_value = worksheet.cell(row_index + 2, col_index).value
        if current_value == 'TRUE':  # Assume que o valor cancelado é 'TRUE'
            st.warning(f"O registro de ID: {row_index + 1} já está cancelado.")
            return
        
        # Atualizar a célula específica
        worksheet.update_cell(row_index + 2, col_index, new_value)
        st.session_state['toast_message'] = ':green-background[Registro cancelado!]'
        
    except gspread.exceptions.APIError as e:
        st.error(f"Erro ao cancelar o registro: {e}")
    except Exception as e:
        st.error(f"Ocorreu um erro inesperado: {e}")
        
@st.cache_data(ttl=60)
def carregar_dados(_spreadsheet, worksheet_name):
    worksheet = _spreadsheet.worksheet(worksheet_name)
    data = worksheet.get_all_records(numericise_ignore=['all'])
    return data

def carregar_planilhas_em_ordem(_spreadsheet, worksheet_names):
    """
    Recebe o objeto da planilha (_spreadsheet) e uma lista de nomes de subplanilhas (worksheet_names).
    Retorna um dicionário com os DataFrames na ordem passada.
    """
    dataframes = {}
    for name in worksheet_names:
        dataframes[name] = carregar_dados(_spreadsheet, name)
    return dataframes
