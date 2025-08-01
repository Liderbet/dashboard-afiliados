import streamlit as st
import pandas as pd
import requests

# Configurações de login
USUARIO_CORRETO = "eric"
SENHA_CORRETA = "Lider@2025"

# Sessão de autenticação
def autenticar():
    st.title("🔐 Login necessário")
    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        if usuario == USUARIO_CORRETO and senha == SENHA_CORRETA:
            st.success("Login realizado com sucesso!")
            st.session_state["autenticado"] = True
        else:
            st.error("Usuário ou senha incorretos.")

# Verifica se o usuário está autenticado
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    autenticar()
    st.stop()

# Conteúdo principal da dashboard
st.title("📈 Dashboard de Afiliados - Logame Analytics")

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

        params = {
            "start_date": start_date,
            "end_date": end_date,
            "campaing_name": campaing_name,
            "mark": mark
        }
        if affiliate_id:
            params["affiliate_id"] = affiliate_id

        url = "https://api-logame-analytics.logame.app/api/affiliate-report"
        response = requests.get(url, params=params)

        if response.status_code == 200:
            dados = response.json()
            df = pd.DataFrame(dados)

            if not df.empty:
                st.success("Dados carregados com sucesso!")
                st.dataframe(df)

                colunas_numericas = df.select_dtypes(include='number').columns.tolist()
                if colunas_numericas:
                    st.subheader("📊 Gráfico de colunas")
                    st.bar_chart(df[colunas_numericas])
            else:
                st.warning("Nenhum dado encontrado para os filtros escolhidos.")
        else:
            st.error(f"Erro {response.status_code}: {response.text}")
