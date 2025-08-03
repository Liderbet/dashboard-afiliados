import streamlit as st
import pandas as pd
import requests
import io
from datetime import datetime

# Configurações de login
USUARIO_CORRETO = "eric"
SENHA_CORRETA = "Lider@2025"

# Página com layout largo
st.set_page_config(page_title="Dashboard Protegida", layout="wide")

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

# Conteúdo principal
st.title("📈 Dashboard Protegida - Afiliados Logame Analytics")

# Filtros
st.sidebar.header("Filtros")
start_date = st.sidebar.date_input("Data Inicial")
end_date = st.sidebar.date_input("Data Final")
campaing_name = st.sidebar.text_input("Nome da campanha", "minha-campanha")
affiliate_id = st.sidebar.text_input("Affiliate ID (opcional)", "")
mark = "liderbet"

# Botão de consulta
if st.sidebar.button("🔍 Consultar API"):
    with st.spinner("Consultando dados..."):

        # Parâmetros
        params = {
            "start_date": start_date,
            "end_date": end_date,
            "campaing_name": campaing_name,
            "mark": mark
        }
        if affiliate_id:
            params["affiliate_id"] = affiliate_id

        # Requisição
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

                nome_arquivo = f"relatorio_logame_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
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
