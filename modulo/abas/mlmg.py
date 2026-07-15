import streamlit as st
import pandas as pd
import os

from modulo.func import func_comparacao_dados

def caminho_pasta(caminho_pasta, nome_arquivo):
    caminho_arquivo = os.path.join(caminho_pasta, nome_arquivo)
    return caminho_arquivo

dados_anucios = pd.read_excel(caminho_pasta('tratamento_dados/dados_tratados/mlmg', 'df_final.xlsx'))

def aba_geral():

    st.write('#### Relatorio Ajustes GERAIS')
    with st.container(border=True):

        col_geral_1, col_geral_2 = st.columns(2)

        with col_geral_1:
            with st.container(border=True):
                'a'

        with col_geral_2:
            with st.container(border=True):
                'a'

def aba_equipe():

    st.write('#### Relatorio Ajustes EQUIPE')

    with st.container(border=True):
        
        col_equipe_1, col_equipe_2, col_equipe_3 = st.columns(3) 
        col_equipe_4, col_equipe_5, col_equipe_6 = st.columns(3)
        col_equipe_7, col_equipe_8, col_equipe_9 = st.columns(3)
        col_equipe_10, col_equipe_11, col_equipe_12 = st.columns(3)

        with col_equipe_1:
            with st.container(border=True):
                itens_n_cadastrados_tray = func_comparacao_dados.cadastro_equipe_x_sem_cadastro_tray()

                st.metric('Cadastrar na **Tray**', len(itens_n_cadastrados_tray), help='Cadastrado Equipe; Sem Cadastro Tray')

                with st.popover('Itens', use_container_width=True):

                    st.dataframe(itens_n_cadastrados_tray, hide_index=True)

        with col_equipe_2:
            with st.container(border=True):
                itens_n_cadastrados_meli = func_comparacao_dados.cadastro_equipe_x_sem_cadastro_meli()
                st.metric('Cadastrar no **MELI**', len(itens_n_cadastrados_meli), help='Cadastrado Equipe; Sem Cadastro MELI')
                with st.popover('Itens', use_container_width=True):
                    st.dataframe(itens_n_cadastrados_meli, hide_index=True)

        with col_equipe_3:
            with st.container(border=True):
                # itens_n_cadastrados_calculo = func_comparacao_dados.cadastro_equipe_x_sem_cadastro_calculo()
                st.metric('Fazer **calculo**', len([]), help='Cadastrado Equipe; Sem Cálculo')
                with st.popover('Itens', use_container_width=True):
                    ''
                    # st.dataframe(itens_n_cadastrados_calculo, hide_index=True)    

        with col_equipe_4:
            with st.container(border=True):
                queima_zerado_ativo_cadastrados_tray = func_comparacao_dados.queima_zerado_ativo_x_cadastrado_tray()
                st.metric('Inataivar no **Equipe** e excluir na **Tray**', len(queima_zerado_ativo_cadastrados_tray), help='Queima, Zerado e ***ativo***; Cadastrado na Tray')
                with st.popover('Itens', use_container_width=True):
                    st.dataframe(queima_zerado_ativo_cadastrados_tray, hide_index=True)

        with col_equipe_5:
            with st.container(border=True):
                itens_n_cadastrados_meli = func_comparacao_dados.queima_zerado_ativo_x_cadastrado_meli()
                st.metric('Inataivar no **Equipe** e excluir no **MELI**', len(itens_n_cadastrados_meli), help='Queima, Zerado e ***ativo***; Cadastrado na MELI')
                with st.popover('Itens', use_container_width=True):
                    st.dataframe(itens_n_cadastrados_meli, hide_index=True) 

        with col_equipe_6:
            with st.container(border=True):
                st.metric('Inataivar no **Equipe** e excluir no **calculo**', len([]), help='Inataivar no Equipe e excluir na Tray')
                with st.popover('Itens', use_container_width=True):
                    ''
                    # st.dataframe(x, hide_index=True)    

        with col_equipe_7:
            with st.container(border=True):
                queima_zerado_tivo_n_cadastrados_tray = func_comparacao_dados.queima_zerado_ativo_x_n_cadastrado_tray()
                st.metric('Inativar no **Equipe**', len(queima_zerado_tivo_n_cadastrados_tray), help='Queima, Zerado e ***Ativo***; Não Cadastrado na Tray')
                with st.popover('Itens', use_container_width=True):
                    st.dataframe(queima_zerado_tivo_n_cadastrados_tray, hide_index=True)

        with col_equipe_8:
            with st.container(border=True):
                queima_zerado_ativo_n_cadastrados_meli = func_comparacao_dados.queima_zerado_ativo_x_n_cadastrado_meli()
                st.metric('Inativar no **Equipe**', len(queima_zerado_ativo_n_cadastrados_meli), help='Queima, Zerado e ***ativo***; Não Cadastrado no MELI')
                with st.popover('Itens', use_container_width=True):
                    st.dataframe(queima_zerado_ativo_n_cadastrados_meli, hide_index=True)

        with col_equipe_9:
            with st.container(border=True):
                st.metric('Inativar no **Equipe**', len([]), help='Queima, zerado e ***ativo***; Não Calculado')
                with st.popover('Itens', use_container_width=True):
                    ''
                    # st.dataframe(x, hide_index=True)  

        with col_equipe_10:
            with st.container(border=True):
                queima_zerado_inativo_cadastrados_tray = func_comparacao_dados.queima_zerado_inativo_x_cadastrado_tray()
                st.metric('Excluir na **Tray**', len(queima_zerado_inativo_cadastrados_tray), help='Queima, zerado e ***inativo***; Cadastrado na Tray')
                with st.popover('Itens', use_container_width=True):
                    st.dataframe(queima_zerado_inativo_cadastrados_tray, hide_index=True)

        with col_equipe_11:
            with st.container(border=True):
                queima_zerado_inativo_x_cadastrado_meli = func_comparacao_dados.queima_zerado_inativo_x_cadastrado_meli()
                st.metric('Excluir no **MELI**', len(queima_zerado_inativo_x_cadastrado_meli), help='Queima, zerado e ***inativo***; Cadastrado no MELI')
                with st.popover('Itens', use_container_width=True):
                    st.dataframe(queima_zerado_inativo_x_cadastrado_meli, hide_index=True)   

        with col_equipe_12:
            with st.container(border=True):
                st.metric('Excluir no **Calculo**', len([]), help='Queima, zerado e ***inativo***; Calculado')
                with st.popover('Itens', use_container_width=True):
                    ''
                    # st.dataframe(x, hide_index=True)

    st.divider()
    st.write('')

    with st.popover('DADOS EQUIPE', use_container_width=True):

        dados_ativos = func_comparacao_dados.dados_equipe_ativo()
        dados_inativos = func_comparacao_dados.dados_equipe_inativo()

        st.write(f'Número de registros ativos: {len(dados_ativos)}')
        st.write(f'Número de registros inativos: {len(dados_inativos)}')

        # if st.button('BAIXAR', key='10'):
        #     st.write('teste')

        with st.expander('Registros Ativos'):
            st.dataframe(dados_ativos, hide_index=True)
        with st.expander('Registros inativos'):
            st.dataframe(dados_ativos, hide_index=True)

def aba_tray():

    st.write('#### Relatorio Ajustes TRAY')

    with st.container(border=True):

        col_tray_1, col_tray_2, col_tray_3 = st.columns(3)    
        col_tray_4, col_tray_5 = st.columns(2)    

        with col_tray_1:
            with st.container(border=True):
                itens_n_cadastrados_tray = func_comparacao_dados.cadastro_tray_x_n_cadastro_equipe()
                st.metric('Cadastrar no **Equipe**', len(itens_n_cadastrados_tray), help='Cadastrado; Sem cadastro no Equipe')
                with st.popover('Itens', use_container_width=True):
                    st.dataframe(itens_n_cadastrados_tray, hide_index=True)

        with col_tray_2:
            with st.container(border=True):
                itens_n_cadastrados_meli = func_comparacao_dados.cadastro_tray_x_n_cadastro_meli()
                st.metric('Cadastrar no **MELI**', len(itens_n_cadastrados_meli), help='Cadastrado; Sem cadastro no Meli')
                with st.popover('Itens', use_container_width=True):
                    st.dataframe(itens_n_cadastrados_meli, hide_index=True)

        with col_tray_3:
            with st.container(border=True):
                st.metric('Calcular', len([]), help='Cadastrado; Sem Calculo')
                with st.popover('Itens', use_container_width=True):
                    ''
                    # st.dataframe(x, hide_index=True)

        with col_tray_4:
            with st.container(border=True):
                equipe_queima_zerado_ativo_cadastrados_tray = func_comparacao_dados.queima_zerado_ativo_x_cadastrado_tray()
                st.metric('Excluir na **Tray** e inativar no **Equipe**', len(equipe_queima_zerado_ativo_cadastrados_tray), help='Cadastrado; Produto Queima, zerado e ***ATIVO*** no equipe')
                with st.popover('Itens', use_container_width=True):
                    st.dataframe(equipe_queima_zerado_ativo_cadastrados_tray[['Codigo', 'Descricao']], hide_index=True)  

        with col_tray_5:
            with st.container(border=True):
                equipe_queima_zerado_inativo_cadastrados_tray = func_comparacao_dados.queima_zerado_inativo_x_cadastrado_tray()
                st.metric('Excluiur na **Tray**', len(equipe_queima_zerado_inativo_cadastrados_tray), help='Cadastrado; Produto Queima, zerado e ***INATIVO*** no equipe')
                with st.popover('Itens', use_container_width=True):
                    st.dataframe(equipe_queima_zerado_inativo_cadastrados_tray, hide_index=True)

        with st.container(border=True):
            equipe_queima_zerado_ativo_n_cadastrados_tray = func_comparacao_dados.queima_zerado_ativo_x_n_cadastrado_tray()
            st.metric('Inativar no **Equipe**', len(equipe_queima_zerado_ativo_n_cadastrados_tray), help='Não Cadastrado; Produto Queima, zerado e ***ATIVO*** no equipe')
            with st.popover('Itens', use_container_width=True):
                st.dataframe(equipe_queima_zerado_ativo_n_cadastrados_tray, hide_index=True)  

    st.divider()
    st.write('')

    with st.popover('DADOS TRAY', use_container_width=True):
        dados_ativos = func_comparacao_dados.dados_tray_pai()
        dados_inativos = func_comparacao_dados.dados_tray_filho()

        st.write(f'Número de registros ativos: {len(dados_ativos)}')
        st.write(f'Número de registros inativos: {len(dados_inativos)}')

        with st.expander('Registros Pai'):
            st.dataframe(dados_ativos, hide_index=True)
        with st.expander('Registros Filhos'):
            st.dataframe(dados_ativos, hide_index=True)

def aba_ml():

    st.write('#### Relatorio Ajustes MERCADO LIVRE')
    with st.container(border=True):

        col_ml_1, col_ml_2, col_ml_3 = st.columns(3)
        col_ml_4, col_ml_5 = st.columns(2)

        with col_ml_1:
            with st.container(border=True):
                st.metric('Cadastrar no **Equipe**', len([]), help='Cadastrado; Sem cadastro no Equipe')
                with st.popover('Itens', use_container_width=True):
                    ''
                    # st.dataframe(x, hide_index=True)

        with col_ml_2:
            with st.container(border=True):
                st.metric('Cadastrar na **Tray**', len([]), help='Cadastrado; Sem cadastro na Tray')
                with st.popover('Itens', use_container_width=True):
                    ''
                    # st.dataframe(x, hide_index=True)  

        with col_ml_3:
            with st.container(border=True):
                st.metric('Calcular', len([]), help='Cadastrado; Sem Calculo')
                with st.popover('Itens', use_container_width=True):
                    ''
                    # st.dataframe(x, hide_index=True)  

        with col_ml_4:
            with st.container(border=True):
                st.metric('Excluir no **MELI** e inativar no **Equipe**', len([]), help='Cadastrado; Produto Queima, zerado e ***ATIVO*** no equipe')
                with st.popover('Itens', use_container_width=True):
                    ''
                    # st.dataframe(x, hide_index=True)

        with col_ml_5:
            with st.container(border=True):
                st.metric('Excluir no **MELI**', len([]), help='Cadastrado; Produto Queima, zerado e ***INATIVO*** no equipe')
                with st.popover('Itens', use_container_width=True):
                    ''
                    # st.dataframe(x, hide_index=True)  

        with st.container(border=True):
            st.metric('Inativar no **Equipe**', len([]), help='Não Cadastrado; Produto Queima, zerado e ***ATIVO*** no equipe')
            with st.popover('Itens', use_container_width=True):
                ''
                # st.dataframe(x, hide_index=True)  

    st.divider()
    st.write('')

    with st.popover('DADOS MELI', use_container_width=True):

        st.write(f'Número de registros: {len(dados_anucios)}')
        with st.expander('Registros'):
            st.dataframe(dados_anucios, hide_index=True)

def aba_calculo():
    st.write('#### Relatorio Ajustes CALCULOS')
    # with st.container(border=True):

    #     col_ml_1, col_ml_2, col_ml_3 = st.columns(3)
    #     col_ml_4, col_ml_5 = st.columns(2)

    #     with col_ml_1:
    #         with st.container(border=True):
    #             st.metric('Cadastrado; Sem cadastro no Equipe', 'X')
    #             with st.popover('Itens', use_container_width=True):
    #                 ''
    #                 # st.dataframe(x, hide_index=True)

    #     with col_ml_2:
    #         with st.container(border=True):
    #             st.metric('Cadastrado; Sem cadastro no Tray', 'X')
    #             with st.popover('Itens', use_container_width=True):
    #                 ''
    #                 # st.dataframe(x, hide_index=True)  

    #     with col_ml_3:
    #         with st.container(border=True):
    #             st.metric('Cadastrado; Sem cadastro no MELI', 'X')
    #             with st.popover('Itens', use_container_width=True):
    #                 ''
    #                 # st.dataframe(x, hide_index=True)  

    #     with col_ml_4:
    #         with st.container(border=True):
    #             st.metric('Cadastrado; Produto Queima, zerado e ***ATIVO*** no equipe', 'X')
    #             with st.popover('Itens', use_container_width=True):
    #                 ''
    #                 # st.dataframe(x, hide_index=True)

    #     with col_ml_5:
    #         with st.container(border=True):
    #             st.metric('Cadastrado; Produto Queima, zerado e ***INATIVO*** no equipe', 'X')
    #             with st.popover('Itens', use_container_width=True):
    #                 ''
    #                 # st.dataframe(x, hide_index=True)  

    #     with st.container(border=True):
    #         st.metric('Não Cadastrado; Produto Queima, zerado e ***ATIVO*** no equipe', 'X')
    #         with st.popover('Itens', use_container_width=True):
    #             ''
    #             # st.dataframe(x, hide_index=True) 

    st.divider()
    st.write('')

    with st.popover('DADOS CALCULOS', use_container_width=True):

        st.write(f'Número de registros: {len([])}')
        with st.expander('Registros'):
            ''
            # st.dataframe(dados_anucios, hide_index=True)
