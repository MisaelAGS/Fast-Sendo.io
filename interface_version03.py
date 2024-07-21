import pandas as pd
import streamlit as st
from pandas import read_csv
from urllib.parse import quote
import webbrowser
from time import sleep
import pyautogui
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

# Função para enviar a lista de contatos
def enviar_lista_contatos(df, coluna_contato, mensagem_template):
    for index, row in df.iterrows():
        telefone = row[coluna_contato]
        mensagem = mensagem_template.format(**row)
        link_mensagem = f'https://web.whatsapp.com/send?phone={int(telefone)}&text={quote(mensagem)}'
        webbrowser.open(link_mensagem)
        sleep(10)
        pyautogui.hotkey('enter')
        sleep(5)
        pyautogui.hotkey('ctrl', 'w')
        sleep(5)

# Função para inicializar o DataFrame no estado da sessão
def iniciar_sessao():
    if 'df' not in st.session_state:
        data = {'ID': [], 'Telefone': []}
        st.session_state.df = pd.DataFrame(data)

# Configurações de Layout
st.set_page_config(page_title="Fast Send.io", page_icon="⚡", layout="wide")

# Estilos CSS personalizados
st.markdown("""
    <style>
        body {
            background-color: #fff8e1;
        }
        .stButton>button {
            background-color: #fdd835;
            color: black;
            border: none;
            border-radius: 5px;
            padding: 10px 20px;
            cursor: pointer;
            transition: background-color 0.3s;
        }
        .stButton>button:hover {
            background-color: #fbc02d;
        }
        .stTextInput>div>div>input {
            border-radius: 5px;
        }
        .stTextArea>div>div>textarea {
            border-radius: 5px;
        }
        .stRadio>div>div>label {
            color: #fdd835;
        }
        .sidebar .sidebar-content {
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
        }
        .sidebar .sidebar-content img {
            width: 80px;
            margin-bottom: 10px;
        }
        .sidebar .sidebar-content h2 {
            color: #fdd835;
            font-size: 24px;
        }
        .sidebar .sidebar-content h3 {
            color: #fdd835;
            font-size: 20px;
        }
    </style>
""", unsafe_allow_html=True)

# Iniciar sessão para DataFrame
iniciar_sessao()

# Barra lateral
with st.sidebar:
    st.markdown("<h2>⚡ Fast Send.io ⚡</h2>", unsafe_allow_html=True)
    st.markdown("<h3>Escolha uma opção de envio:</h3>", unsafe_allow_html=True)

    escolha = st.selectbox('', ['Lista', 'Escrita'])

# Título principal
st.markdown("<h1 style='text-align: center; color: #fdd835;'>⚡ Fast Send.io ⚡</h1>", unsafe_allow_html=True)

# Opção de envio por lista
if escolha == 'Lista':
    st.markdown("<h2 style='color: #fdd835;'>Envio por Lista de Contatos</h2>", unsafe_allow_html=True)

    arquivo = st.file_uploader('Suba sua lista de contatos aqui:', type=['csv'])

    if arquivo:
        df = read_csv(arquivo)
        st.dataframe(df)

        coluna_telefone = st.radio('Qual das colunas corresponde aos números de telefone?', df.columns.tolist())

        mensagem = st.text_area('Escreva a sua mensagem aqui:')

        if st.button('Enviar Lista'):
            enviar_lista_contatos(df, coluna_telefone, mensagem)
            st.success('Mensagens enviadas com sucesso!')

# Opção de envio por escrita
else:
    st.markdown("<h2 style='color: #fdd835;'>Envio por Escrita de Contatos</h2>", unsafe_allow_html=True)

    st.subheader('Adicionar Nova Coluna')
    nome_nova_coluna = st.text_input('Nome da nova coluna')

    if st.button('Adicionar Coluna'):
        if nome_nova_coluna and nome_nova_coluna not in st.session_state.df.columns:
            st.session_state.df[nome_nova_coluna] = ''
            st.success('Coluna adicionada com sucesso!')
        else:
            st.warning('Por favor, insira um nome válido e único para a nova coluna.')

    st.subheader('Remover Coluna Existente')
    colunas_remover = [col for col in st.session_state.df.columns if col not in ['ID', 'Telefone']]
    coluna_remover = st.selectbox('Selecione a coluna a ser removida', colunas_remover)

    if st.button('Remover Coluna'):
        if coluna_remover in st.session_state.df.columns:
            st.session_state.df.drop(columns=[coluna_remover], inplace=True)
            st.success('Coluna removida com sucesso!')
        else:
            st.warning('Coluna não encontrada na tabela.')

    st.subheader('Adicionar Nova Linha')
    dados_nova_linha = {}

    for column in st.session_state.df.columns:
        if column != 'ID':
            dados_nova_linha[column] = st.text_input(f'Novo valor para {column}', key=f'new_row_{column}')

    if st.button('Adicionar Linha'):
        if all(dados_nova_linha.values()):
            novo_id = st.session_state.df['ID'].max() + 1 if not st.session_state.df['ID'].empty else 1
            dados_nova_linha['ID'] = novo_id
            new_row = pd.DataFrame([dados_nova_linha])
            st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)
            st.success('Linha adicionada com sucesso!')
        else:
            st.warning('Por favor, preencha todos os campos para a nova linha.')

    st.subheader('Eliminar Linha')
    id_eliminar = st.number_input('ID da linha a eliminar', min_value=1, step=1)

    if st.button('Eliminar Linha'):
        if id_eliminar in st.session_state.df['ID'].values:
            st.session_state.df = st.session_state.df[st.session_state.df['ID'] != id_eliminar]
            st.success('Linha eliminada com sucesso!')
        else:
            st.warning('ID não encontrado na tabela.')

    st.subheader('Alterar Linha')
    id_alterar = st.number_input('ID da linha a alterar', min_value=1, step=1)

    if id_alterar in st.session_state.df['ID'].values:
        dados_alterar = {}
        for column in st.session_state.df.columns:
            if column != 'ID':
                dados_alterar[column] = st.text_input(f'Novo valor para {column} (ID {id_alterar})',
                                                      key=f'edit_row_{column}')

        if st.button('Alterar Linha'):
            if all(dados_alterar.values()):
                for column, value in dados_alterar.items():
                    st.session_state.df.loc[st.session_state.df['ID'] == id_alterar, column] = value
                st.success('Linha alterada com sucesso!')
            else:
                st.warning('Por favor, preencha todos os campos para alterar a linha.')

    gb = GridOptionsBuilder.from_dataframe(st.session_state.df)
    gb.configure_default_column(editable=True)
    grid_options = gb.build()

    grid_response = AgGrid(
        st.session_state.df,
        gridOptions=grid_options,
        update_mode=GridUpdateMode.MODEL_CHANGED,
        height=300,
        fit_columns_on_grid_load=True
    )

    # Atualiza o DataFrame com os dados da grid
    updated_df = pd.DataFrame(grid_response['data'])
    if not updated_df.equals(st.session_state.df):
        st.session_state.df = updated_df

    st.write('Tabela atualizada:')
    st.dataframe(st.session_state.df)

    coluna_telefone = st.radio('Qual das colunas corresponde aos números de telefone?',
                               st.session_state.df.columns.tolist())

    mensagem = st.text_area('Escreva a sua mensagem aqui:')

    if st.button('Enviar'):
        enviar_lista_contatos(st.session_state.df, coluna_telefone, mensagem)
        st.success('Mensagens enviadas com sucesso!')
