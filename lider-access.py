import streamlit as st
import pandas as pd
import requests
import io
from datetime import datetime, timedelta
import pytz
import time

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
    data_inicial = st.sidebar.date_input("Data Inicial", value=hoje - timedelta(days=7))
    data_final = st.sidebar.date_input("Data Final", value=hoje)

# Parâmetros fixos
affiliate_id = "468543"
mark = "liderbet"
campaing_name = st.sidebar.text_input("Campanha (opcional)", "")

# Exibe informações do filtro atual
st.caption(f"🗓️ Período selecionado: `{data_inicial}` até `{data_final}`")
st.caption(f"🔗 Afiliado fixo: `{affiliate_id}` | Marca: `{mark}`")

# Espaço para atualização manual
atualizar_manual = st.button("🔄 Atualizar agora")

# Timer de atualização automática
tempo_restante = st.empty()

# Atualiza se botão foi clicado OU por tempo (a cada 60s)
rodar = atualizar_manual or st.session_state.get("ultimo_update", 0) + 60 < time.time()

if rodar:
    st.session_state["ultimo_update"] = time.time()

    with st.spinner("Consultando API..."):

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

                # EXPORTAÇÃO PARA EXCEL
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
                st.warning("⚠ Nenhum dado encontrado para os filtros escolhidos.")
        else:
            st.error(f"❌ Erro {response.status_code}: {response.text}")

# Atualização automática visual (contagem regressiva)
for i in range(60, 0, -1):
    tempo_restante.markdown(f"⏳ Atualizando automaticamente em **{i} segundos**...")
    time.sleep(1)
    st.experimental_rerun()
