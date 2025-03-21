import streamlit as st
import requests
import re
from datetime import datetime, timedelta

# Configuração da página
st.set_page_config(page_title="Cadastro de Clientes", page_icon="📋")
st.title("Agendamento")

# Função para validar a quantidade de dígitos do telefone
def validar_telefone(telefone):
    return len(telefone) == 14

# Formulário
with st.form(key='cadastro_form'):
    # Campo Nome
    nome = st.text_input("Nome", max_chars=100)
    
    # Campo Telefone restrito a números
    telefone = st.text_input(
        "Telefone",
        placeholder="Digite apenas números",
        help="Digite apenas os números do telefone"
    )
    
    # Remover caracteres não numéricos
    telefone = re.sub(r'\D', '', telefone)
    
    telefone = "+55" + telefone
    
    # Campo Data/Hora de agendamento
    data_hora = st.date_input("Data do Agendamento").strftime("%d/%m/%Y")
    horario = st.time_input("Horário do Agendamento")
    
    # Botão de submit
    submit_button = st.form_submit_button(label="Cadastrar")

# Processamento do formulário quando submetido
if submit_button:
    # Validação dos campos
    if not nome:
        st.error("O campo Nome é obrigatório!")
    elif not telefone:
        st.error("O campo Telefone é obrigatório!")
    elif not validar_telefone(telefone):
        st.error("O telefone deve ser um número de celular válido")
    else:
        # Capturar data e hora atuais
        agora = datetime.utcnow() - timedelta(hours=3)
        datacaptacao = agora.strftime("%d/%m/%Y")
        horariocaptacao = agora.strftime("%H:%M:%S")
        horacaptacao = agora.strftime("%H")
        
        # Dados a serem enviados
        dados = {
            "nome": nome,
            "telefone": telefone,
            "dataagend": str(data_hora),
            "horarioagend": str(horario)[:5],
            "origem": "appcaptacao",
            "datacaptacao": datacaptacao,
            "horariocaptacao": horariocaptacao,
            "horacaptacao": horacaptacao,
            "localcaptacao": "Montes Claros",
            "confirmado": "n"
        }
        # Envio para a API
        try:
            response = requests.post(
                "https://n8n.financeironet.com.br/webhook-test/1f55d4fe-9479-4af7-8d90-7da8b3e193ac",
                json=dados
            )
            
            if response.status_code == 200:
                st.success("Cliente cadastrado com sucesso!")
                # Limpar o formulário
                st.session_state.clear()
            else:
                st.error(f"Erro ao cadastrar: Status {response.status_code}")
        except requests.exceptions.RequestException as e:
            st.error(f"Erro na conexão com a API: {str(e)}")

# Estilização adicional com CSS
st.markdown("""
    <style>
    .stTextInput > div > div > input {
        width: 100%;
    }
    </style>
""", unsafe_allow_html=True)