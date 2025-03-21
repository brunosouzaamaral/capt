import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import folium_static
from datetime import datetime
import requests

# Configuração da página
st.set_page_config(page_title="Dashboard de Captações", layout="wide")

# URL base do Firebase Realtime Database
FIREBASE_URL = "https://captacao-5d200-default-rtdb.firebaseio.com"

# Título do dashboard
#st.title("Dashboard de Captações e Agendamentos")

# Função para carregar dados do Firebase via REST API

def load_data():
    # Fazer requisição GET para obter os dados
    response = requests.get(f"{FIREBASE_URL}/.json")  # Removido o nó 'captacoes'  # Ajuste o nó 'captacoes' conforme sua estrutura
    data = response.json()
    
    # Verificar se há dados e converter para lista de dicionários
    records = []
    if data:
        for key, value in data.items():
            records.append(value)
    
    # Criar DataFrame
    df = pd.DataFrame(records)
    
    # Converter formatos de data e hora
    df['data_captacao'] = pd.to_datetime(df['datacaptacao'], format='%d/%m/%Y')
    df['data_agend'] = pd.to_datetime(df['dataagend'], format='%d/%m/%Y')
    df['hora_captacao'] = df['horacaptacao'].astype(str)
    
    # Mapear coordenadas para locais (adicione mais conforme necessário)
    coordenadas = {
        'Montes Claros': {'lat': -16.7350, 'lon': -43.8617},
        # Adicione outros locais aqui
    }
    
    df['latitude'] = df['localcaptacao'].map(lambda x: coordenadas.get(x, {}).get('lat', 0))
    df['longitude'] = df['localcaptacao'].map(lambda x: coordenadas.get(x, {}).get('lon', 0))
    
    return df

# Carregar os dados
df = load_data()

# Sidebar para filtros
st.sidebar.header("Filtros")
data_inicio = st.sidebar.date_input("Data Início", datetime(2025, 3, 1))
data_fim = st.sidebar.date_input("Data Fim", datetime(2025, 3, 31))

# Botão para atualizar os dados
if st.sidebar.button("Atualizar Dados"):
    df = load_data()  # Recarregar os dados
    st.sidebar.success("Dados atualizados com sucesso!")


# Filtrar dados
df_filtrado = df[
    (df['data_captacao'].dt.date >= data_inicio) & 
    (df['data_captacao'].dt.date <= data_fim)
]

# 1. Captações por hora e dia
#st.header("Captações por Hora e Dia e Status dos Agendamentos")

# Criar colunas para exibir os gráficos lado a lado
col1, col2 = st.columns(2)

# Gráfico 1: Captações por Hora
with col1:
    st.subheader("Captações por Hora")
    df_hora_dia = df_filtrado.groupby([df_filtrado['horacaptacao']]).size().reset_index()
    df_hora_dia.columns = ['Hora', 'Quantidade']

    fig1 = px.bar(df_hora_dia, x='Hora', y='Quantidade', 
                  title='Quantidade de Captações por Hora',
                  labels={'Hora': 'Hora do Dia', 'Quantidade': 'Nº de Captações'},
                  text='Quantidade')
    fig1.update_traces(textposition='outside')  # Exibe os valores fora das barras
    st.plotly_chart(fig1, use_container_width=True)

# Gráfico 2: Confirmados vs Não Confirmados
with col2:
    st.subheader("Status dos Agendamentos")
    df_filtrado['confirmado'] = df_filtrado['confirmado'].map({'s': 'Confirmado', 'n': 'Não Confirmado'})
    status_counts = df_filtrado['confirmado'].value_counts()
    fig2 = px.pie(values=status_counts.values, 
                  names=status_counts.index, 
                  title='Confirmados vs Não Confirmados')
    st.plotly_chart(fig2, use_container_width=True)

# 3. Mapa de captações por local
st.header("Distribuição Geográfica das Captações")
locais_counts = df_filtrado.groupby(['localcaptacao', 'latitude', 'longitude']).size().reset_index()
locais_counts.columns = ['Local', 'Latitude', 'Longitude', 'Quantidade']

# Criar mapa
m = folium.Map(location=[-15.78, -47.92], zoom_start=4)  # Centro do Brasil

# Adicionar marcadores
for idx, row in locais_counts.iterrows():
    if row['Latitude'] != 0 and row['Longitude'] != 0:  # Verificar se há coordenadas válidas
        folium.CircleMarker(
            location=[row['Latitude'], row['Longitude']],
            radius=row['Quantidade']/2,  # Ajuste o divisor conforme a escala
            popup=f"{row['Local']}: {row['Quantidade']} captações",
            fill=True,
            fill_opacity=0.7
        ).add_to(m)

# Exibir mapa
folium_static(m)

# Rodapé com data de atualização
#st.write(f"Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")