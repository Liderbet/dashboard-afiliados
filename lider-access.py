import streamlit as st
import pandas as pd
import requests
import io
from datetime import datetime, timedelta
import pytz

# Configurações gerais
st.set_page_config(page_title="Dashboard Afiliado", layout="wide")
st.title("📈 Dashboard Afiliado - Logame Analytics")

# Timezone Brasil
fuso_brasilia = pytz.timezone("America/Sao_Paulo")
hoje = datetime.now(fuso_brasilia).date()

# Sidebar com filtro de intervalo
st.sidebar.header("Período do Relatório")

opcao_periodo = st.sidebar.radio(
    "Escolha o intervalo:",
    ["Hoje", "Últimos 7 dias", "Últimos 15 dias", "Últimos 30 dias"],
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

# Parâmetros fixos
affiliate_id = "468543"
mark = "liderbet"
campaing_name = st.sidebar.text_input("Campanha (opcional)", "")

# Exibe as datas usadas
st.caption(f"🗓️ Período selecionado: `{data_inicial}` até `{data_final}`")
st.caption(f"🔗 Afiliado: `{affiliate_id}` | Marca: `{mark}`")

# Consulta automática ao carregar
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

            # TOTALIZADOR
            st.subheader("📌 Totais")
            colunas_numericas = df.select_dtypes(include='number').columns.tolist()
            if colunas_numericas:
                totais = df[colunas_numericas].sum()
                col1, col2, col3, col4 = st.columns(4)
                colunas = totais.index.tolist()
                for i, coluna in enumerate(colunas):
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
