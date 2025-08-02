import streamlit as st
import pandas as pd
import requests

st.title("📈 Dashboard de Afiliados - Logame Analytics")

# Filtros na barra lateral
st.sidebar.header("Filtros")
start_date = st.sidebar.date_input("Data Inicial")
end_date = st.sidebar.date_input("Data Final")
campaing_name = st.sidebar.text_input("Nome da campanha", "")
affiliate_id = st.sidebar.text_input("Affiliate ID (opcional)", "")
mark = "liderbet"

# Botão para consultar
if st.sidebar.button("🔍 Consultar API"):
    with st.spinner("Consultando dados..."):

        # Parâmetros da API
        params = {
            "start_date": start_date,
            "end_date": end_date,
            "campaing_name": campaing_name,
            "mark": mark
        }
        if affiliate_id:
            params["affiliate_id"] = affiliate_id

        # URL da API
        url = "https://api-logame-analytics.logame.app/api/affiliate-report"
        response = requests.get(url, params=params)

        if response.status_code == 200:
            dados = response.json()
            df = pd.DataFrame(dados)

            if not df.empty:
                st.success("Dados carregados com sucesso!")
                st.dataframe(df)

                # Gráfico básico se houver dados numéricos
                colunas_numericas = df.select_dtypes(include='number').columns.tolist()
                if colunas_numericas:
                    st.subheader("📊 Gráfico de colunas")
                    st.bar_chart(df[colunas_numericas])
            else:
                st.warning("Nenhum dado encontrado para os filtros escolhidos.")
        else:
            st.error(f"Erro {response.status_code}: {response.text}")
