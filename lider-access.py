import streamlit as st
import pandas as pd
import requests
import io
import pytz
from datetime import datetime, timedelta

st.set_page_config(page_title="Dashboard Pública - Afiliados", layout="wide")

st.title("📊 Dashboard Pública - Logame Analytics")

# Timezone Brasil
fuso_brasilia = pytz.timezone("America/Sao_Paulo")
hoje = datetime.now(fuso_brasilia).date()

# Filtros
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

# Campos dinâmicos
affiliate_id = st.sidebar.text_input("Affiliate ID", value="468543")
campaing_name = st.sidebar.text_input("Campanha (opcional)", "")
mark = "liderbet"

# Estado anterior dos filtros para evitar recarga desnecessária
if "filtros_anteriores" not in st.session_state:
    st.session_state.filtros_anteriores = {}

filtros_atuais = {
    "start_date": str(data_inicial),
    "end_date": str(data_final),
    "affiliate_id": affiliate_id,
    "campaing_name": campaing_name,
    "mark": mark,
}

# Botão de atualização
atualizar = st.button("🔄 Atualizar agora")

# Função com cache
@st.cache_data(show_spinner=False)
def consultar_api(params):
    url = "https://api-logame-analytics.logame.app/api/affiliate-report"
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return pd.DataFrame(response.json())
    else:
        return pd.DataFrame()

# Verifica se deve atualizar
filtros_diferentes = filtros_atuais != st.session_state.filtros_anteriores
if atualizar or filtros_diferentes:
    st.session_state.filtros_anteriores = filtros_atuais
    with st.spinner("🔄 Consultando API..."):
        df = consultar_api(filtros_atuais)
else:
    df = consultar_api(st.session_state.filtros_anteriores)

# Exibição
st.caption(f"🗓️ Período: `{data_inicial}` a `{data_final}`")
st.caption(f"🧾 Afiliado: `{affiliate_id}` | Marca: `{mark}`")

if not df.empty:
    st.success("✅ Dados carregados com sucesso!")

    # TOTALIZADORES
    st.subheader("📌 Totais")
    colunas_numericas = df.select_dtypes(include='number').columns.tolist()
    if colunas_numericas:
        totais = df[colunas_numericas].sum()
        col1, col2, col3, col4 = st.columns(4)
        for i, coluna in enumerate(totais.index):
            valor = totais[coluna]
            valor_formatado = f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            if i % 4 == 0:
                col1.metric(coluna, valor_formatado)
            elif i % 4 == 1:
                col2.metric(coluna, valor_formatado)
            elif i % 4 == 2:
                col3.metric(coluna, valor_formatado)
            elif i % 4 == 3:
                col4.metric(coluna, valor_formatado)

    # TABELA
    st.subheader("📋 Tabela de Dados")
    st.dataframe(df)

    # EXPORTAÇÃO
    st.subheader("📥 Exportar")
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

    # GRÁFICO
    if colunas_numericas:
        st.subheader("📊 Gráfico de Colunas")
        st.bar_chart(df[colunas_numericas])
else:
    st.warning("⚠ Nenhum dado encontrado.")
