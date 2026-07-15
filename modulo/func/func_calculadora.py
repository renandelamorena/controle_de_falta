import streamlit as st
import pandas as pd
import plotly.express as px
import requests

from modulo.func import funcoes
from paginas.pages_user.promos import resumo_promos
from paginas.pages_user.promos import dados_promos

import base64

def caculadora(
        vrp_mp=None,
        vrp_cod=None,
        vrp_custo_nota=None,
        vrp_custo_tab=None,
        vrp_ipi=None,
        vrp_st=0,
        vrp_icms=None,
        vrp_taxa_rs=None,
        vrp_taxa_percent=None,
        vrp_taxa_adm_=0,
        vrp_taxa_adm=4,
        vrp_tray=0.15,
        vrp_margem=0.01,
        vrp_link=None,
        acao="adicionar",
        linha_editar=None,
        stts_mktplace=False,
        stts_cod=False,
        stts_link=False,
        vrp_off = None,
        vrp_atacado = None
        ):

    total_promos, a_expirar, expiradas = dados_promos()
    resumo_promos(len(total_promos), len(a_expirar), len(expiradas))

    # Define a imagem de fundo usando CSS
    def add_bg_from_local(image_file):
        with open(image_file, "rb") as f:
            img_data = f.read()
        b64 = base64.b64encode(img_data).decode()
        css = f"""
        <style>
        .stApp {{
            background-image: url(data:image/png;base64,{b64});
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        
        /* Tornar o cabeçalho e o rodapé transparentes */
        header {{
            background: rgba(0,0,0,0) !important;
        }}
        
        .css-18e3th9 {{
            padding-top: 0;
        }}
        
        footer {{
            visibility: hidden;
        }}
        </style>
        """
        st.markdown(css, unsafe_allow_html=True)

    add_bg_from_local('imagens/bg_dark.png')
    
    estados = (
        "AC", 
        "AL", 
        "AP", 
        "AM", 
        "BA", 
        "CE", 
        "DF",
        "ES",
        "GO", 
        "MA", 
        "MT",
        "MS",
        "MG",
        "PA", 
        "PB", 
        "PR", 
        "PE", 
        "PI", 
        "RJ",
        "RN",
        "RS",
        "RO", 
        "RR", 
        "SC",
        "SP",
        "SE", 
        "TO",
        'GERAL',
        'MEDIA 5',
    )

    dados_guia_icms = pd.read_excel('data/calculos/aliquota_guia_icms_proprio_compra.xlsx')

    from modulo.func import func_comparacao_dados
    from modulo.func import funcoes

    spreadsheet, conn, client = funcoes.iniciar_coneccao('DADOS_CALCULO')

    dados_equipe_ativo = func_comparacao_dados.dados_equipe_ativo()
    dados_equipe_ativo_rp = func_comparacao_dados.dados_equipe_ativo_rp()

    def carregar_produtos_manuais():
        try:
            produtos_manuais = pd.DataFrame(funcoes.carregar_dados(spreadsheet, 'produtos_manuais'))
        except Exception:
            return pd.DataFrame(columns=['Base', 'Codigo', 'Descricao', 'Ativo'])

        mapa_colunas = {str(col).strip().lower(): col for col in produtos_manuais.columns}
        renomear = {}

        for destino in ['Base', 'Codigo', 'Descricao', 'Ativo']:
            origem = mapa_colunas.get(destino.lower())
            if origem is not None:
                renomear[origem] = destino

        produtos_manuais = produtos_manuais.rename(columns=renomear)

        for coluna in ['Base', 'Codigo', 'Descricao', 'Ativo']:
            if coluna not in produtos_manuais.columns:
                produtos_manuais[coluna] = '' if coluna != 'Ativo' else True

        return produtos_manuais[['Base', 'Codigo', 'Descricao', 'Ativo']]

    def valor_ativo(valor):
        if isinstance(valor, bool):
            return valor

        if pd.isna(valor):
            return True

        return str(valor).strip().upper() in ['TRUE', 'VERDADEIRO', 'SIM', 'YES', '1', 'X', '']

    produtos_manuais = carregar_produtos_manuais()

    def retorna_base_equipe(marketplace):
        if not marketplace:
            return None, None

        base = marketplace[-2:]
        bases_equipe = {
            'MG': dados_equipe_ativo,
            'RP': dados_equipe_ativo_rp,
        }

        return base, bases_equipe.get(base)

    def retorna_descricao(cod, marketplace):
        base, dados_equipe = retorna_base_equipe(marketplace)

        if dados_equipe is None:
            return None

        codigo = str(cod).strip()
        codigos_base = dados_equipe['Codigo'].astype(str).str.strip()
        descricoes = dados_equipe.loc[codigos_base == codigo, 'Descricao']

        if not descricoes.empty:
            return descricoes.iloc[0]

        produtos_manuais_base = produtos_manuais.copy()
        produtos_manuais_base['Base'] = produtos_manuais_base['Base'].astype(str).str.strip().str.upper()
        produtos_manuais_base['Codigo'] = (
            produtos_manuais_base['Codigo']
            .astype(str)
            .str.strip()
            .str.replace(r'\.0$', '', regex=True)
        )

        selecao_manual = (
            (produtos_manuais_base['Base'] == base)
            & (produtos_manuais_base['Codigo'] == codigo)
            & (produtos_manuais_base['Ativo'].apply(valor_ativo))
        )

        descricoes_manuais = produtos_manuais_base.loc[selecao_manual, 'Descricao']

        if descricoes_manuais.empty:
            st.warning(f'Codigo {codigo} nao encontrado na base {base}.')
            return None

        return descricoes_manuais.iloc[-1]

    def se_vazio_recebe(valor, recebe=' - - - '):
        if valor == None:
            valor = recebe
        else:
            valor = round(valor, 2)
        return valor

    col1, col2, col3, col4, col5 = st.columns([15, 15, 50, 10, 10], vertical_alignment="bottom")

    with col1:
        marketplaces_contas = [
    'MLMG',
    'MLRP',
    'SHMG',
    'SHRP',
    'TKMG',
    'TKRP',
    'AMMG',
    'AMRP',
    ]

        if vrp_mp == None:
            idx_marketplace = None
        else:
            idx_marketplace = marketplaces_contas.index(vrp_mp)
            
        select_mktplace = st.selectbox('Marketplace:',marketplaces_contas , index = idx_marketplace, placeholder='', disabled=stts_mktplace)

    with col2:
        cod_produto = st.text_input('Código:', value=vrp_cod, placeholder=None, disabled=stts_cod)

    with col3:
        st.write('')
        with st.container(border=True):
            if cod_produto and select_mktplace:
                desc = retorna_descricao(cod_produto, select_mktplace)
                st.write(f'{desc}')
            else:
                desc = None
                st.write('')
                st.write('')
                st.write('')

    with col4:
        variacao = st.toggle('Variação', disabled=True)

    with col5:
        st.link_button('CADASTRO', 'https://docs.google.com/spreadsheets/d/10R6ZvCpuM8GViLBewd7SGr4riNmnkw0bdKigILtVlD0/edit?usp=sharing', width='stretch')

    col1, col2, col3, col4, col5 = st.columns([19, 19, 19, 17, 27])

    with col1:
        with st.container(border=True):
            st.write('###### Formação Custo')
            # col_custo1, col_custo2 = st.columns(2)
            # with col_custo1:
            custo_s_imp_nota = st.number_input('Custo S\Imp (NOTA):', value=vrp_custo_nota, placeholder=None, icon=':material/attach_money:')
            custo_s_imp_tab =st.number_input('Custo S\Imp (TABELA):', value=vrp_custo_tab, placeholder=None, icon=':material/attach_money:')
            ipi = st.number_input('IPI:', value=vrp_ipi, placeholder=None, icon=':material/percent:')

            i_st = vrp_st
            stts_comp_st = False
            i_icms_c = vrp_icms
            stts_comp_icms_c = False 

            if select_mktplace:

                estado_plataforma = select_mktplace[-2:]

                if estado_plataforma == 'MG':
                    i_st = 0
                    stts_comp_st = False
                if estado_plataforma == 'RP':
                    i_icms_c = 0
                    stts_comp_icms_c = False 

            st_ = st.number_input('ST:', value=float(i_st), placeholder=None, icon=':material/percent:', disabled=stts_comp_st, step=0.01)
            # icms_c = st.number_input('ICMS Compra:', value=i_icms_c, placeholder=None, icon=':material/percent:', help='18% Dentro do estado, 12% Fora do estado', disabled=stts_comp_icms_c)

    with col2:
        with st.container(border=True):
            st.write('###### Marketplaces')

            comissao = st.number_input('Comissão:', value=vrp_taxa_percent, placeholder=None, icon=':material/percent:')
            frete = st.number_input('FRETE ou TAXA de Envio:', value=vrp_taxa_rs, placeholder=None, icon=':material/attach_money:', help='00 a 29 = **06,25**  |  29 a 50 = **06,50**  |  50 a 79 = **06,75**')

            # margem_base = st.selectbox('Base da margem:', ['NOTA', 'TABELA'], index=0, disabled=True, placeholder=None)

            st.write('')

            with st.popover('Padrão', width='stretch'):

                taxa_adm = st.number_input('Taxa ADM:', value=vrp_taxa_adm, placeholder=None, icon=':material/percent:')
                # publi = st.number_input('PUBLI:', value=vrp_publi, placeholder=None, icon=':material/percent:')
                # perca = st.number_input('PERCA:', value=vrp_perca, placeholder=None, icon=':material/percent:')
                tray = st.number_input('TRAY:', value=vrp_tray)

            margem = st.number_input('Margem:', value=vrp_margem, placeholder=None, icon=':material/percent:')

    variaveis = {
        'select_mktplace': select_mktplace,
        'cod_produto': cod_produto,
        'desc': desc,
        'custo_s_imp_nota': custo_s_imp_nota,
        'custo_s_imp_tab': custo_s_imp_tab,
        'ipi': ipi,
        'st_': st_,
        # 'icms_c': icms_c,
        'comissao': comissao,
        'frete': frete,
        'taxa_adm': taxa_adm,
        # 'publi': publi,
        # 'perca': perca,
        'margem': margem,
        'tray': tray,
        # 'icms_c' : icms_c,
    }

    # Lista das variáveis obrigatórias (nomes das chaves)
    obrigatorias = [
        "select_mktplace",
        "cod_produto",
        "desc",
        "custo_s_imp_nota",
        "custo_s_imp_tab",
        "ipi",
        "st_",
        "icms_c",
        "comissao",
        "frete",
        "taxa_adm",
        # "publi",
        # "perca",
        "margem",
        "tray",
        "icms_c",
    ]

    # Lista das variáveis opcionais (nomes das chaves)
    opcionais = []

    def validar_variaveis(variaveis, obrigatorias, opcionais):
        # Quem está vazio
        faltando = [nome for nome, valor in variaveis.items() if valor is None]

        # Regras de validação
        obrigatorias_ok = all(variaveis.get(v) is not None for v in obrigatorias)
        opcionais_ok = any(variaveis.get(v) is not None for v in opcionais)

        if obrigatorias_ok and opcionais_ok:
            return True, []
        else:
            return False, faltando

    ok, faltando = validar_variaveis(variaveis, obrigatorias, opcionais)

    if faltando:
        st.info(f'Faltando alguns campos para calcular: {faltando}', icon='ℹ️')
    else:

        vr_ipi_nota = (ipi / 100) * custo_s_imp_nota
        vr_ipi_tab = (ipi / 100) * custo_s_imp_tab
        
        vr_st_nota = (st_ / 100) * custo_s_imp_nota
        vr_st_tab = (st_ / 100) * custo_s_imp_tab
        
        custo_c_imp_nota = custo_s_imp_nota + vr_ipi_nota + vr_st_nota
        custo_c_imp_tab = custo_s_imp_tab + vr_ipi_tab + vr_st_tab

        # preco de venda selec
        
        fator_total_acrescimo = (1 + comissao/100) * (1 + taxa_adm/100) * (1 + tray/100)
        vr_venda_sem_margem = (custo_c_imp_nota + frete) * fator_total_acrescimo
        vr_venda = (custo_c_imp_nota + frete) * fator_total_acrescimo * (1 + margem/100)

        descont_custo_produto = -custo_c_imp_nota
        descont_custo_produto_tab = -custo_c_imp_tab

        pis_cof = 9.25

        def calculo_desconto_guia(estado_venda):

            estado_plataforma = select_mktplace[-2:]

            if estado_plataforma == 'RP':
                coluna_desconto = 'ALIQUOTA'
            if estado_plataforma == 'MG':
                coluna_desconto = 'DESCONTAR'

            # Agora, pega o valor da linha referente ao estado_venda
            linha = dados_guia_icms.loc[dados_guia_icms['SIGLA'].str.lower() == estado_venda.lower()]
            valor = linha[coluna_desconto].iloc[0]

            if estado_plataforma == 'RP':
                if estado_venda == 'SP':
                    if st_ == 0:
                        valor = 18/100

            return valor

        ########################################################################################################################

        with col3:

            with st.container(border=True):
                st.write('###### Consulta')

                # selec_pesquisa = st.selectbox('Pesquisar no valor:', ('NOTA', 'TABELA'), index=None, placeholder='Selecione')
                # selec_pesquisa = st.selectbox('Pesquisar no valor:', ('NOTA'), index=None, placeholder='Selecione')
                selec_pesquisa = 'NOTA'

                if selec_pesquisa:
                    # if selec_pesquisa == 'NOTA':
                    #     valor_utilizar = custo_c_imp_nota_frete_comissao_publi_perca_tray
                    #     valor_utilizar_final = soma_todos_descontos_nota *-1
                    # if selec_pesquisa == 'TABELA':
                    #     valor_utilizar = custo_c_imp_tab_frete_comissao_publi_perca_tray

                    valor_utilizar = vr_venda_sem_margem

                    valor_pela_margem = st.number_input('Valor:', value=None, placeholder=None, icon=':material/attach_money:', help='Infomeme um valor final de anúncio para ser retornado margem respectiva')
                    if valor_pela_margem:
                        margem_pelo_valor = round(((valor_pela_margem / valor_utilizar) - 1) *100, 3)

                        st.code(margem_pelo_valor, language=None)

        with col4:

            with st.container(border=True):
                st.write('###### "DESCONTO"')

                off = st.number_input('OFF:', value=vrp_off, placeholder=None, icon=':material/percent:')
                if off != None:
                    vr_c_off = vr_venda - (off / 100) * vr_venda
                else:
                    vr_c_off = None
                    
                atacado = st.number_input('ATACADO:', value=vrp_atacado, placeholder=None, icon=':material/percent:')
                if atacado != None:
                    vr_c_atacado = vr_venda - (atacado / 100) * vr_venda
                else:
                    vr_c_atacado = None

            with col5:
                with st.container(border=True):
                    st.write('#### Valores')

                    with st.container(border=True):
                        st.metric('Valor Base', f'R$ {se_vazio_recebe(vr_venda)}')

                    col_vr_off, col_vr_atacado = st.columns(2)

                    with col_vr_off:
                        with st.container(border=True):
                            st.metric('Valor Com OFF', f'R$ {se_vazio_recebe(vr_c_off)}')
                    with col_vr_atacado:
                        with st.container(border=True):
                            st.metric('Atacado', f'R$ {se_vazio_recebe(vr_c_atacado)}')

        ########################################################################################################################

        # 1. GeoJSON dos estados brasileiros
        @st.cache_data
        def carregar_geojson():
            url = "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson"
            return requests.get(url).json()

        geojson = carregar_geojson()

        base_custo_sobra = ['Nota', 'Tabela']
        custo_base = st.pills('Base para o custo:', base_custo_sobra, default='Nota')

        # opcoes_sobra_valor_f = ['Valor Base', 'Valor Com OFF', 'Atacado']
        opcoes_sobra_valor_f = []

        if vr_venda:
            opcoes_sobra_valor_f.append('Valor Base')
        if vr_c_off:
            opcoes_sobra_valor_f.append('Valor Com OFF')
        if vr_c_atacado:
            opcoes_sobra_valor_f.append('Atacado')

        base_valor_sobra = st.pills('Base de valor para sobra:', opcoes_sobra_valor_f, default='Valor Base')

        # BASE VENDA F
        # Valor Base
        if base_valor_sobra == 'Valor Base':
            valor_venda_f_utilizar = vr_venda
        # Valor Com OFF
        if base_valor_sobra == 'Valor Com OFF':
            valor_venda_f_utilizar = vr_c_off
        # ATACADO
        if base_valor_sobra == 'Atacado':
            valor_venda_f_utilizar = vr_c_atacado

        valor_descontar = valor_venda_f_utilizar
        
        descont_frete = -frete
        descont_comissao = -(comissao / 100) * valor_descontar
        descont_taxa_adm = -(taxa_adm / 100) * valor_descontar
        # descont_perca = -(perca / 100) * valor_descontar
        # descont_publi = -(publi / 100) * valor_descontar
        descont_tray = -(tray / 100) * valor_descontar

        # vr_icms_c = ((icms_c/100)/1)+1

        # custo_fab = custo_s_imp_nota / vr_icms_c
        # pis_cof_mais = (pis_cof / 100) * custo_fab
        # pis_cof_menos = -(pis_cof / 100) * valor_venda_f_utilizar

        # descont_ips_cof = pis_cof_mais + pis_cof_menos

        # custo_fab_tab = custo_s_imp_tab / vr_icms_c
        # pis_cof_mais_tab = (pis_cof / 100) * custo_fab_tab
        # pis_cof_menos_tab = -(pis_cof / 100) * valor_venda_f_utilizar

        # descont_ips_cof_tab = pis_cof_mais_tab + pis_cof_menos_tab

        imp_federal = 6
        descont_imp_federal = -(imp_federal / 100) * valor_venda_f_utilizar
        
        imp_federal_filial = 6
        descont_imp_federal_filial = -(imp_federal_filial / 100) * valor_venda_f_utilizar

        descontos_sem_guia = descont_frete + descont_comissao + descont_taxa_adm + descont_tray + descont_custo_produto
        descontos_sem_guia_tab = descont_frete + descont_comissao + descont_taxa_adm + descont_tray + descont_custo_produto_tab

        if custo_base == 'Tabela':
            descontos_sem_guia = descontos_sem_guia_tab
        # if custo_base == 'Tabela':
        #     descont_ips_cof = descont_ips_cof_tab

        # CUSTO F
        # NOTA
        if custo_base == 'Nota':
            valor_custo_f_utilizar_s_guia = descontos_sem_guia
        # TAB
        if custo_base == 'Tabela':
            valor_custo_f_utilizar_s_guia = descontos_sem_guia_tab

        descont_guia_AC = - calculo_desconto_guia(estados[0]) * valor_venda_f_utilizar
        descont_guia_AL = - calculo_desconto_guia(estados[1]) * valor_venda_f_utilizar
        descont_guia_AP = - calculo_desconto_guia(estados[2]) * valor_venda_f_utilizar
        descont_guia_AM = - calculo_desconto_guia(estados[3]) * valor_venda_f_utilizar
        descont_guia_BA = - calculo_desconto_guia(estados[4]) * valor_venda_f_utilizar
        descont_guia_CE = - calculo_desconto_guia(estados[5]) * valor_venda_f_utilizar
        descont_guia_DF = - calculo_desconto_guia(estados[6]) * valor_venda_f_utilizar
        descont_guia_ES = - calculo_desconto_guia(estados[7]) * valor_venda_f_utilizar
        descont_guia_GO = - calculo_desconto_guia(estados[8]) * valor_venda_f_utilizar
        descont_guia_MA = - calculo_desconto_guia(estados[9]) * valor_venda_f_utilizar
        descont_guia_MT = - calculo_desconto_guia(estados[10]) * valor_venda_f_utilizar
        descont_guia_MS = - calculo_desconto_guia(estados[11]) * valor_venda_f_utilizar
        descont_guia_MG = - calculo_desconto_guia(estados[12]) * valor_venda_f_utilizar
        descont_guia_PA = - calculo_desconto_guia(estados[13]) * valor_venda_f_utilizar
        descont_guia_PB = - calculo_desconto_guia(estados[14]) * valor_venda_f_utilizar
        descont_guia_PR = - calculo_desconto_guia(estados[15]) * valor_venda_f_utilizar
        descont_guia_PE = - calculo_desconto_guia(estados[16]) * valor_venda_f_utilizar
        descont_guia_PI = - calculo_desconto_guia(estados[17]) * valor_venda_f_utilizar
        descont_guia_RJ = - calculo_desconto_guia(estados[18]) * valor_venda_f_utilizar
        descont_guia_RN = - calculo_desconto_guia(estados[19]) * valor_venda_f_utilizar
        descont_guia_RS = - calculo_desconto_guia(estados[20]) * valor_venda_f_utilizar
        descont_guia_RO = - calculo_desconto_guia(estados[21]) * valor_venda_f_utilizar
        descont_guia_RR = - calculo_desconto_guia(estados[22]) * valor_venda_f_utilizar
        descont_guia_SC = - calculo_desconto_guia(estados[23]) * valor_venda_f_utilizar
        descont_guia_SP = - calculo_desconto_guia(estados[24]) * valor_venda_f_utilizar
        descont_guia_SE = - calculo_desconto_guia(estados[25]) * valor_venda_f_utilizar
        descont_guia_TO = - calculo_desconto_guia(estados[26]) * valor_venda_f_utilizar
        descont_guia_GERAL = - calculo_desconto_guia(estados[27]) * valor_venda_f_utilizar
        descont_guia_5_ESTADOS = - calculo_desconto_guia(estados[28]) * valor_venda_f_utilizar

        # 2. Criar DataFrame base com valores iniciais
        dados = pd.DataFrame([
            ["AC", "Acre", (valor_venda_f_utilizar + (descontos_sem_guia + descont_guia_AC)) / (valor_custo_f_utilizar_s_guia + descont_guia_AC) * 100 * -1],
            ["AL", "Alagoas", (valor_venda_f_utilizar + (descontos_sem_guia + descont_guia_AL)) / (valor_custo_f_utilizar_s_guia + descont_guia_AL) * 100 * -1],
            ["AP", "Amapá", (valor_venda_f_utilizar + (descontos_sem_guia + descont_guia_AP)) / (valor_custo_f_utilizar_s_guia + descont_guia_AP) * 100 * -1],
            ["AM", "Amazonas", (valor_venda_f_utilizar + (descontos_sem_guia + descont_guia_AM)) / (valor_custo_f_utilizar_s_guia + descont_guia_AM) * 100 * -1],
            ["BA", "Bahia", (valor_venda_f_utilizar + (descontos_sem_guia + descont_guia_BA)) / (valor_custo_f_utilizar_s_guia + descont_guia_BA) * 100 * -1],
            ["CE", "Ceará", (valor_venda_f_utilizar + (descontos_sem_guia + descont_guia_CE)) / (valor_custo_f_utilizar_s_guia + descont_guia_CE) * 100 * -1],
            ["DF", "Distrito Federal", (valor_venda_f_utilizar + (descontos_sem_guia + descont_guia_DF)) / (valor_custo_f_utilizar_s_guia + descont_guia_DF) * 100 * -1],
            ["ES", "Espírito Santo", (valor_venda_f_utilizar + (descontos_sem_guia + descont_guia_ES)) / (valor_custo_f_utilizar_s_guia + descont_guia_ES) * 100 * -1],
            ["GO", "Goiás", (valor_venda_f_utilizar + (descontos_sem_guia + descont_guia_GO)) / (valor_custo_f_utilizar_s_guia + descont_guia_GO) * 100 * -1],
            ["MA", "Maranhão", (valor_venda_f_utilizar + (descontos_sem_guia + descont_guia_MA)) / (valor_custo_f_utilizar_s_guia + descont_guia_MA) * 100 * -1],
            ["MT", "Mato Grosso", (valor_venda_f_utilizar + (descontos_sem_guia + descont_guia_MT)) / (valor_custo_f_utilizar_s_guia + descont_guia_MT) * 100 * -1],
            ["MS", "Mato Grosso do Sul", (valor_venda_f_utilizar + (descontos_sem_guia + descont_guia_MS)) / (valor_custo_f_utilizar_s_guia + descont_guia_MS) * 100 * -1],
            ["MG", "Minas Gerais", (valor_venda_f_utilizar + (descontos_sem_guia + descont_guia_MG)) / (valor_custo_f_utilizar_s_guia + descont_guia_MG) * 100 * -1],
            ["PA", "Pará", (valor_venda_f_utilizar + (descontos_sem_guia + descont_guia_PA)) / (valor_custo_f_utilizar_s_guia + descont_guia_PA) * 100 * -1],
            ["PB", "Paraíba", (valor_venda_f_utilizar + (descontos_sem_guia + descont_guia_PB)) / (valor_custo_f_utilizar_s_guia + descont_guia_PB) * 100 * -1],
            ["PR", "Paraná", (valor_venda_f_utilizar + (descontos_sem_guia + descont_guia_PR)) / (valor_custo_f_utilizar_s_guia + descont_guia_PR) * 100 * -1],
            ["PE", "Pernambuco", (valor_venda_f_utilizar + (descontos_sem_guia + descont_guia_PE)) / (valor_custo_f_utilizar_s_guia + descont_guia_PE) * 100 * -1],
            ["PI", "Piauí", (valor_venda_f_utilizar + (descontos_sem_guia + descont_guia_PI)) / (valor_custo_f_utilizar_s_guia + descont_guia_PI) * 100 * -1],
            ["RJ", "Rio de Janeiro", (valor_venda_f_utilizar + (descontos_sem_guia + descont_guia_RJ)) / (valor_custo_f_utilizar_s_guia + descont_guia_RJ) * 100 * -1],
            ["RN", "Rio Grande do Norte", (valor_venda_f_utilizar + (descontos_sem_guia + descont_guia_RN)) / (valor_custo_f_utilizar_s_guia + descont_guia_RN) * 100 * -1],
            ["RS", "Rio Grande do Sul", (valor_venda_f_utilizar + (descontos_sem_guia + descont_guia_RS)) / (valor_custo_f_utilizar_s_guia + descont_guia_RS) * 100 * -1],
            ["RO", "Rondônia", (valor_venda_f_utilizar + (descontos_sem_guia + descont_guia_RO)) / (valor_custo_f_utilizar_s_guia + descont_guia_RO) * 100 * -1],
            ["RR", "Roraima", (valor_venda_f_utilizar + (descontos_sem_guia + descont_guia_RR)) / (valor_custo_f_utilizar_s_guia + descont_guia_RR) * 100 * -1],
            ["SC", "Santa Catarina", (valor_venda_f_utilizar + (descontos_sem_guia + descont_guia_SC)) / (valor_custo_f_utilizar_s_guia + descont_guia_SC) * 100 * -1],
            ["SP", "São Paulo", (valor_venda_f_utilizar + (descontos_sem_guia + descont_guia_SP)) / (valor_custo_f_utilizar_s_guia + descont_guia_SP) * 100 * -1],
            ["SE", "Sergipe", (valor_venda_f_utilizar + (descontos_sem_guia + descont_guia_SE)) / (valor_custo_f_utilizar_s_guia + descont_guia_SE) * 100 * -1],
            ["TO", "Tocantins", (valor_venda_f_utilizar + (descontos_sem_guia + descont_guia_TO)) / (valor_custo_f_utilizar_s_guia + descont_guia_TO) * 100 * -1],
        ], columns=["estado", "nome", "percentual"])

        # 3. Usar DataFrame fixo (sem edição no app)
        # Valores já definidos no DataFrame base
        dados_editado = dados.copy()

        # 4. Definir cores fixas conforme a faixa de percentual
        def definir_cor(valor):
            if valor <= 0:
                return "Menor que 0%"
            elif valor <= 10:
                return "Entre 0% e 10%"
            elif valor <= 15:
                return "Entre 10% e 15%"
            else:
                return "Maior que 15%"

        dados_editado["cor"] = dados_editado["percentual"].apply(definir_cor)

        # 5. Criar mapa com cores fixas e tooltip personalizado
        fig = px.choropleth(
            dados_editado,
            geojson=geojson,
            locations="estado",
            featureidkey="properties.sigla",
            color="cor",
            color_discrete_map={
                "Menor que 0%": "red",
                "Entre 0% e 10%": "orange",
                "Entre 10% e 15%": "yellow",
                "Maior que 15%": "green",
            },
            title="Sobra de Vendas Por Estado (%)",
            hover_data={
                "estado": True,
                "percentual": ':.1f'  # Formata com 1 casa decimal
            }
        )

        fig.update_geos(fitbounds="locations", visible=False, bgcolor="rgba(0,0,0,0)")
        fig.update_layout(
            margin={"r": 0, "t": 40, "l": 0, "b": 0},
            coloraxis_showscale=False,
            showlegend=False,
            dragmode=False,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
        )

        # Formatar o rótulo do tooltip
        fig.update_traces(
            hovertemplate="<b>%{customdata[0]}</b><br>Valor: %{customdata[1]:.1f}%<extra></extra>",
            marker_line_width=0.5,
            marker_line_color="white"
        )

        # 6. Layout com 2 colunas: mapa + legenda lateral
        col1, col2 = st.columns([3, 1])

        with col1:
            st.write('### Margens Sobre Custo Final')
            st.plotly_chart(fig, width='stretch')

        with col2:

            def get_emoji(percentual: float) -> str:

                if percentual <= 0:
                    return "🟥"
                elif percentual <= 10:
                    return "🟧"
                elif percentual <= 15:
                    return "🟨"
                else:
                    return "🟩"

            with st.container(border=True):
                if estado_plataforma == 'MG':
                    # TODO fazer condicionalmente baseado no cusoto nota e tabela
                    sobra_descont_guia_GERAL = (valor_venda_f_utilizar + (descontos_sem_guia + descont_imp_federal_filial)) / (valor_custo_f_utilizar_s_guia + descont_imp_federal_filial) * 100 * -1
                    st.metric(f'{get_emoji(sobra_descont_guia_GERAL)} Sobre Filial', f'{se_vazio_recebe(sobra_descont_guia_GERAL)} %')

                if estado_plataforma == 'RP':
                    sobra_descont_guia_GERAL = (valor_venda_f_utilizar + (descontos_sem_guia + descont_imp_federal)) / (valor_custo_f_utilizar_s_guia + descont_imp_federal) * 100 * -1
                    st.metric(f'{get_emoji(sobra_descont_guia_GERAL)} Sobra Loja', f'{se_vazio_recebe(sobra_descont_guia_GERAL)} %', help='Sobra pelo imposto da loja')

                # st.write(valor_venda_f_utilizar)
                # st.write(descontos_sem_guia)
                # st.write(descont_imp_federal_filial)
                # st.write(valor_custo_f_utilizar_s_guia)
                # st.write('')
                # st.write(descont_imp_federal_filial)
                # st.write('')
                # st.write(((valor_venda_f_utilizar + (descontos_sem_guia + descont_imp_federal_filial)) / valor_venda_f_utilizar) * 100)

            with st.container(border=True):
                sobra_descont_guia_5_ESTADOS = (valor_venda_f_utilizar + (descontos_sem_guia + descont_guia_5_ESTADOS)) / (valor_custo_f_utilizar_s_guia + descont_guia_5_ESTADOS) * 100 * -1
                st.metric(f'{get_emoji(sobra_descont_guia_5_ESTADOS)} Média 5 Est.', f'{se_vazio_recebe(sobra_descont_guia_5_ESTADOS)} %', help='Média dos 5 estados com mais venda (MG -> BA, PR, RJ, RS, SP) | (SP -> BA, MG, PR, RJ, RS)')

            # Legenda de cores fixa
            st.markdown("#### 📋 Legenda")
            st.markdown("- 🟩 **Maior que 15%**")
            st.markdown("- 🟨 **Entre 10% e 15%**")
            st.markdown("- 🟧 **Entre 0% e 10%**")
            st.markdown("- 🟥 **Menor ou igual a 0%**")

            # Popover com resumo
            with st.popover("📋 Resumo por Estado", width='stretch'):
                st.markdown("### Percentuais por Estado")
                dados_ordenado = dados_editado.sort_values("percentual", ascending=False)

                for _, row in dados_ordenado.iterrows():
                    if row["percentual"] <= 0:
                        emoji = "🟥"
                    elif row["percentual"] <= 10:
                        emoji = "🟧"
                    elif row["percentual"] <= 15:
                        emoji = "🟨"
                    else:
                        emoji = "🟩"

                    st.markdown(f"{emoji} **{row['estado']} - {row['nome']}**: {se_vazio_recebe(row['percentual'])}%")

    st.divider()

    if not faltando:

        with st.popover('RESUMO DO CALCULO', width='stretch'):

            st.write(f'**Conta:** {(select_mktplace)}')
            st.write(f'**Código:** {(cod_produto)}')
            st.write(f'**Descrição:** {(desc)}')

            col_preco_resumo, col_ml_resumo, col_desc_resumo = st.columns(3)

            with col_preco_resumo:
                st.write('##### Formação Preço Custo')

                st.write(':blue-background[NOTA] | :red-background[TABELA]')
                st.write(f'**Custo S/Imp:** -> R$: :blue-background[{se_vazio_recebe(custo_s_imp_nota)}] | :red-background[{se_vazio_recebe(custo_s_imp_tab)}]')
                st.write(f'**IPI:** {(ipi)} % -> R$: :blue-background[{se_vazio_recebe(vr_ipi_nota)}] | :red-background[{se_vazio_recebe(vr_ipi_tab)}]')
                st.write(f'**ST:** {(st_)} % -> R$: :blue-background[{se_vazio_recebe(vr_st_nota)}] | :red-background[{se_vazio_recebe(vr_st_tab)}]')
                
                # st.write(f'**ICMS Compra:** {(icms_c)} %')
                
                st.divider()
                st.write('')

                st.write(f'**Custo C/Imp:** -> R$: :blue-background[{se_vazio_recebe(custo_c_imp_nota)}] | :red-background[{se_vazio_recebe(custo_c_imp_tab)}]')

            with col_ml_resumo:

                st.write('##### Custos Marketplaces')
                st.write(f'**Comissão:** {se_vazio_recebe(comissao)} %')
                st.write(f'**Frete/Taxa:** R$: {se_vazio_recebe(frete)}')
                st.write(f'**Taxa ADM:** {se_vazio_recebe(taxa_adm)} %')
                # st.write(f'**Perca:** {se_vazio_recebe(perca)} %')
                # st.write(f'**Publicidade:** {se_vazio_recebe(publi)} %')
                st.write(f'**TRAY:** {se_vazio_recebe(tray)} %')
                st.write(f'**Margem:** {se_vazio_recebe(margem)} %')

                st.divider()
                st.write('')

                st.write(f'**Preço venda:** R$: {se_vazio_recebe(valor_venda_f_utilizar)} -> {base_valor_sobra}')

            with col_desc_resumo:
                st.write('##### Descontos')

                st.write(f'**Desconto da Comissão:** R$ {se_vazio_recebe(descont_comissao)}')
                st.write(f'**Desconto da Frete/Taxa:** R$ {se_vazio_recebe(descont_frete)}')
                st.write(f'**Taxa ADM:** R$ {se_vazio_recebe(descont_taxa_adm)}')
                # st.write(f'**Desconto da Perca:** R$ {se_vazio_recebe(descont_perca)}')
                # st.write(f'**Desconto da Publicidade:** R$ {se_vazio_recebe(descont_publi)}')
                st.write(f'**Desconto da Tray:** R$ {se_vazio_recebe(descont_tray)}')
                
                st.write(f'**Desconto do Custo do produto:** R$ :blue-background[{se_vazio_recebe(descont_custo_produto)}] | :red-background[{se_vazio_recebe(descont_custo_produto_tab)}]')
                if estado_plataforma == 'MG':
                    st.write(f'**Desconto Federal Filial:** R$ {se_vazio_recebe(descont_imp_federal_filial)}')
                    # st.write(f'**Desconto do Pis/Cofins:** R$ :blue-background[{se_vazio_recebe(descont_ips_cof)}] | :red-background[{se_vazio_recebe(descont_ips_cof_tab)}]')
                if estado_plataforma == 'RP':
                    st.write(f'**Desconto Federal:** R$ {se_vazio_recebe(descont_imp_federal)}')
                    # st.write(f'**Desconto do Pis/Cofins:** R$ :blue-background[{se_vazio_recebe(descont_ips_cof)}] | :red-background[{se_vazio_recebe(descont_ips_cof_tab)}]')

                # with st.container(border=True):
                #     st.write(f'**Desconto do ICMS + Guia:** R$ {se_vazio_recebe(descont_guia_SP)} -> SP')
                # st.write(f'**Desconto do ICMS + Guia:** R$ {se_vazio_recebe(descont_guia_MG)} -> MG')
                
                st.divider()
                st.write('')
                
                if estado_plataforma == 'MG':
                    st.write(f'**Total descontos:** R$: :blue-background[{se_vazio_recebe(descontos_sem_guia + descont_imp_federal_filial)}] | :red-background[{se_vazio_recebe(descontos_sem_guia_tab + descont_imp_federal_filial)}] -> Média Geral')

                if estado_plataforma == 'RP':
                    st.write(f'**Total descontos:** R$: :blue-background[{se_vazio_recebe(descontos_sem_guia + descont_imp_federal)}] | :red-background[{se_vazio_recebe(descontos_sem_guia_tab + descont_imp_federal)}] -> Imposto Federal')

            with col5:
                link_anuncio = st.text_input('Link Anúncio:', placeholder='Cole o link aqui!', value=vrp_link, disabled=stts_link)

                if link_anuncio:
                    bloquear_salvamento = False
                else:
                    bloquear_salvamento = True

                if st.button('SALVAR CALCULO', width='stretch', disabled=bloquear_salvamento):

                    linha = [False, select_mktplace, cod_produto, desc, custo_s_imp_nota, custo_s_imp_tab, ipi, st_, None, frete, comissao, None, taxa_adm, tray, margem, link_anuncio, vr_venda, vr_c_off, vr_c_atacado, None, None, None, None, None, None, None, None, None, None, None]

                    funcoes.salvar_linha(client, linha, 'data', acao=acao, linha_editar=linha_editar)
                    st.success('Salvo com sucesso!')
                    st.toast(':green-background[Salvo com sucesso!]', icon='✅')
