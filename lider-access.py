import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Dashboard Pública - Logame", layout="wide")
st.title("📈 Dashboard Pública - Afiliados Logame Analytics")

# Filtros na barra lateral
st.sidebar.header("Filtros")
start_date = st.sidebar.date_input("Data Inicial")
end_date = st.sidebar.date_input("Data Final")
campaing_name = st.sidebar.text_input("Nome da campanha", "minha-campanha")
affiliate_id = st.sidebar.text_input("Affiliate ID (opcional)", "")
mark = "liderbet"

# Botão para consultar
if st.sidebar.button("🔍 Consultar API"):
    with st.spinner("Consultando dados..."):

        # Monta os parâmetros da requisição
        params = {
            "start_date": start_date,
            "end_date": end_date,
            "campaing_name": campaing_name,
            "mark": mark
        }
        if affiliate_id:
            params["affiliate_id"] = affiliate_id

        # Faz a requisição GET
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

                # GRÁFICO
                if colunas_numericas:
                    st.subheader("📊 Gráfico de Colunas")
                    st.bar_chart(df[colunas_numericas])
            else:
                st.warning("⚠ Nenhum dado encontrado para os filtros escolhidos.")
        else:
            st.error(f"❌ Erro {response.status_code}: {response.text}")
