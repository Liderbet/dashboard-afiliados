import streamlit as st
import pandas as pd
import requests
import io
from datetime import datetime, timedelta
import pytz

# Configuração da página
st.set_page_config(page_title="Dashboard Afiliado", layout="wide")
st.title("📈 Dashboard Afiliado - Logame Analytics")

# Fuso horário Brasil (Brasília)
fuso_brasilia = pytz.timezone("America/Sao_Paulo")
hoje = datetime.now(fuso_brasilia).date()

# Sidebar: seleção de período
st.sidebar.header("Período do Relatório")

opcao_periodo = st.sidebar.radio(
    "Escolha o intervalo:",
    ["Hoje", "Últimos 7 dias", "Últimos 15 dias", "Últimos 30 dias", "Personalizado"],
    index=0
)

# Calcula intervalo com base na opção
if opcao_periodo == "Hoje":
    data_inicial = data_final = hoje
elif opcao_periodo == "Últimos 7 dias":
    data_inicial = hoje - timedelta(days=6)
    data_final = hoje
elif opcao_periodo == "Últimos 15 dias":
    data_inicial = hoje - timedelta(days=14)
    data_final = hoje
elif opcao_periodo == "Últimos 30 dias":
    data_inicial = hoje - timedelta(days=29)
    data_final = hoje
else:
    data_inicial = st.sidebar.date_input("Data Inicial", hoje - timedelta(
