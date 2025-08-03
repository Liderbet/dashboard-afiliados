import streamlit as st
import pandas as pd
import requests
import io
import pytz
import time
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

# Campo editável com valor padrão
affiliate_id = st.sidebar.text_input("Affiliate ID", value="468543")
campaing_name = st.sidebar.text_input("Campanha (opcional)", "")
mark = "liderbet"

st.caption(f"🗓️ Período: `{data_inicial}` a `{data_final}`")
st.caption(f"🧾 Afiliado: `{affiliate_id}` | Marca: `{mark}`")

# Botão e controle de tempo
atualizar_manual = st.button("🔄 Atualizar agora")

if "ultimo_update" not in st.session_state:
    st.session_state["ultimo_update"] = 0

rodar = atualizar_manual or (time.time() - st.session_state["ultimo_update"] > 60)

if rodar:
    st.session_state["ultimo_update"] = time.time()

    with st.spinner("🔄 Consultando API..."):
        params = {
            "start_date": str(data_inicial),
            "end_date": str(data_final),
            "affiliate_id": affiliate_id,
            "mark": mark
        }
        if campaing_name:
            params["campaing_name"] = campaing_name

        url = "https://api-logame-analytics.logame.app/api/affiliate-report"
        response = requests.get(url, params=params)

        if response.status_code == 200:
            dados = response.json()
            df = pd.DataFrame(dados)

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
        else:
            st.error(f"❌ Erro {response.status_code}: {response.text}")

# Informação de atualização
segundos = int(time.time() - st.session_state["ultimo_update"])
st.caption(f"⏳ Atualização automática a cada 60s. Última: {segundos} segundos atrás.")
