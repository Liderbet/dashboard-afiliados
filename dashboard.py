import streamlit as st
import pandas as pd
import requests

# Título
st.title("📈 Dashboard de Afiliados - Logame Analytics")

# Parâmetros de filtro
st.sidebar.header("Filtros")
start_date = st.sidebar.date_input("Data Inicial")
end_date = st.sidebar.date_input("Data Final")
campaing_name = st.sidebar.text_input("Nome da campanha", "minha-campanha")
affiliate_id = st.sidebar.text_input("Affiliate ID (opcional)", "")
mark = "liderbet"

# Botão de consulta
if st.sidebar.button("🔍 Consultar API"):
    with st.spinner("Consultando dados..."):

        # Montar parâmetros
        params = {
            "start_date": start_date,
            "end_date": end_date,
            "campaing_name": campaing_name,
            "mark": mark
        }
        if affiliate_id:
            params["affiliate_id"] = affiliate_id

        # Consultar API
        url = "https://api-logame-analytics.logame.app/api/affiliate-report"
        response = requests.get(url, params=params)

        if response.status_code == 200:
            dados = response.json()
            df = pd.DataFrame(dados)

            if not df.empty:
                st.success("Dados carregados com sucesso!")
                st.dataframe(df)

                # Visualização simples (se houver colunas como 'clicks', 'leads', 'revenue' etc)
                colunas_numericas = df.select_dtypes(include='number').columns.tolist()
                if colunas_numericas:
                    st.subheader("📊 Resumo numérico")
                    st.bar_chart(df[colunas_numericas])
            else:
                st.warning("Nenhum dado encontrado para os filtros selecionados.")
        else:
            st.error(f"Erro {response.status_code}: {response.text}")
