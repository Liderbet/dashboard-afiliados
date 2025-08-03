import streamlit as st
import pandas as pd
import requests
import io
import pytz
from datetime import datetime, timedelta

# ======== ESCOLHA DE LAYOUT COM URL + SESSION_STATE ========
params = st.query_params
layout_param = params.get("layout", None)

if "layout_escolhido" not in st.session_state:
    st.session_state.layout_escolhido = layout_param

if not st.session_state.layout_escolhido:
    st.title("🎯 Escolha o Layout")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("💻 Versão Desktop"):
            st.query_params["layout"] = "desktop"
            st.session_state.layout_escolhido = "desktop"
            st.rerun()
    with col2:
        if st.button("📱 Versão Mobile"):
            st.query_params["layout"] = "mobile"
            st.session_state.layout_escolhido = "mobile"
            st.rerun()

    st.stop()

layout_final = "wide" if st.session_state.layout_escolhido == "desktop" else "centered"
st.set_page_config(page_title="Dashboard Logame", layout=layout_final)

# ======== CABEÇALHO ========
st.title("📊 Dashboard Pública - Logame Analytics")

fuso_brasilia = pytz.timezone("America/Sao_Paulo")
hoje = datetime.now(fuso_brasilia).date()

# ======== FILTROS ========
st.sidebar.header("Filtros de Período")
opcao_periodo = st.sidebar.radio(
    "Escolha o intervalo:",
    ["Hoje", "Últimos 7 dias", "Últimos 15 dias", "Últimos 30 dias", "Personalizado"],
    index=0
)

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
    data_inicial = st.sidebar.date_input("Data Inicial", value=hoje - timedelta(days=7))
    data_final = st.sidebar.date_input("Data Final", value=hoje)

affiliate_id = st.sidebar.text_input("Affiliate ID", value="468543")
campaing_name = st.sidebar.text_input("Campanha (opcional)", "")
mark = "liderbet"

# Previne erro de API sem parâmetros obrigatórios
if not affiliate_id and not campaing_name:
    st.warning("⚠️ Informe pelo menos um Affiliate ID ou uma Campanha.")
    st.stop()

# ======== BOTÃO MANUAL E CACHE ========
if "filtros_anteriores" not in st.session_state:
    st.session_state.filtros_anteriores = {}

filtros_atuais = {
    "start_date": str(data_inicial),
    "end_date": str(data_final),
    "affiliate_id": affiliate_id,
    "campaing_name": campaing_name,
    "mark": mark,
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

filtros_diferentes = filtros_atuais != st.session_state["filtros_anteriores"]
if atualizar or filtros_diferentes:
    st.session_state["filtros_anteriores"] = filtros_atuais
    with st.spinner("🔄 Consultando API..."):
        df = consultar_api(filtros_atuais)
else:
    df = consultar_api(st.session_state["filtros_anteriores"])

# ======== EXIBIÇÃO DE RESULTADOS ========
st.caption(f"🗓️ Período: `{data_inicial}` a `{data_final}`")
st.caption(f"🧾 Afiliado: `{affiliate_id}` | Marca: `{mark}`")

if not df.empty:
    st.success("✅ Dados carregados com sucesso!")

    st.subheader("📌 Totais")
    colunas_numericas = df.select_dtypes(include='number').columns.tolist()
    if colunas_numericas:
        for coluna in colunas_numericas:
            valor = df[coluna].sum()
            valor_formatado = f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            st.metric(coluna, valor_formatado)

    st.subheader("📋 Tabela de Dados")
    st.dataframe(df, use_container_width=True)

    st.subheader("📥 Exportar para Excel")
    excel_buffer = io.BytesIO()
    df.to_excel(excel_buffer, index=False, engine='openpyxl')
    excel_buffer.seek(0)
    nome_arquivo = f"relatorio_logame_{datetime.now(fuso_brasilia).strftime('%Y%m%d_%H%M%S')}.xlsx"
    st.download_button(
        label="📥 Baixar Excel",
        data=excel_buffer,
        file_name=nome_arquivo,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.warning("⚠ Nenhum dado encontrado para os filtros informados.")
