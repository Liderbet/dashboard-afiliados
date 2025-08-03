import streamlit as st
import pandas as pd
import requests
import io
import pytz
from datetime import datetime, timedelta

st.set_page_config(page_title="Dashboard Mobile - LiderBet", layout="centered")

# Para layout mais espaçado em desktop:
# st.set_page_config(page_title="Dashboard Desktop", layout="wide")


st.title("📊 Dashboard Mobile")

# Timezone Brasil
fuso_brasilia = pytz.timezone("America/Sao_Paulo")
hoje = datetime.now(fuso_brasilia).date()

# Filtros laterais simplificados
with st.sidebar:
    st.header("📅 Filtros")
    opcao_periodo = st.radio(
        "Período:",
        ["Hoje", "7 dias", "15 dias", "30 dias", "Personalizado"],
        index=0
    )

    if opcao_periodo == "Hoje":
        data_inicial = data_final = hoje
    elif opcao_periodo == "7 dias":
        data_inicial = hoje - timedelta(days=6)
        data_final = hoje
    elif opcao_periodo == "15 dias":
        data_inicial = hoje - timedelta(days=14)
        data_final = hoje
    elif opcao_periodo == "30 dias":
        data_inicial = hoje - timedelta(days=29)
        data_final = hoje
    else:
        data_inicial = st.date_input("Data Inicial", value=hoje - timedelta(days=7))
        data_final = st.date_input("Data Final", value=hoje)

    affiliate_id = st.text_input("Affiliate ID", value="468543")
    campaing_name = st.text_input("Campanha (opcional)", "")

# Atualização manual
if "filtros_mobile" not in st.session_state:
    st.session_state["filtros_mobile"] = {}

filtros_atuais = {
    "start_date": str(data_inicial),
    "end_date": str(data_final),
    "affiliate_id": affiliate_id,
    "campaing_name": campaing_name,
    "mark": "liderbet"
}

atualizar = st.button("🔄 Atualizar agora")

@st.cache_data(show_spinner=False)
def consultar_api(params):
    url = "https://api-logame-analytics.logame.app/api/affiliate-report"
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return pd.DataFrame(response.json())
    else:
        return pd.DataFrame()

filtros_diferentes = filtros_atuais != st.session_state["filtros_mobile"]
if atualizar or filtros_diferentes:
    st.session_state["filtros_mobile"] = filtros_atuais
    with st.spinner("🔄 Carregando dados..."):
        df = consultar_api(filtros_atuais)
else:
    df = consultar_api(st.session_state["filtros_mobile"])

st.markdown(f"🗓️ `{data_inicial}` a `{data_final}` | 🔗 Afiliado: `{affiliate_id}`")

if not df.empty:
    st.success("✅ Dados carregados")

    # Totais (empilhado)
    st.subheader("📌 Totais")
    colunas_numericas = df.select_dtypes(include='number').columns.tolist()
    if colunas_numericas:
        for coluna in colunas_numericas:
            valor = df[coluna].sum()
            valor_formatado = f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            st.metric(coluna, valor_formatado)

    # Tabela
    st.subheader("📋 Dados")
    st.dataframe(df, use_container_width=True)

    # Exportar Excel
    st.subheader("📥 Exportar")
    excel_buffer = io.BytesIO()
    df.to_excel(excel_buffer, index=False, engine='openpyxl')
    excel_buffer.seek(0)
    nome_arquivo = f"relatorio_mobile_{datetime.now(fuso_brasilia).strftime('%Y%m%d_%H%M%S')}.xlsx"
    st.download_button(
        label="📥 Baixar Excel",
        data=excel_buffer,
        file_name=nome_arquivo,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.warning("⚠ Nenhum dado encontrado.")
