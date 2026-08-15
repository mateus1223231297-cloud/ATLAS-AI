import streamlit as st
import pandas as pd
import math

# Estilo "Homem de Ferro"
st.set_page_config(page_title="Atlas - Central de Inteligência", layout="wide")

st.title("🔴 ATLAS - Central de Análise Brasileirão")
st.markdown("---")

# Simulando dados (em breve vamos conectar direto ao seu script)
data = {
    "Partida": ["Fluminense x Palmeiras", "Athletico-PR x Bragantino", "São Paulo x Coritiba"],
    "Exp_Gols": [2.14, 2.33, 2.38],
    "Prob_Over_25": [36.0, 41.1, 42.4]
}
df = pd.DataFrame(data)

# Layout das Colunas (Cards de Inteligência)
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="Análises Ativas", value="3")
with col2:
    st.metric(label="Status do Protocolo", value="Online", delta="Estável")
with col3:
    st.metric(label="Confiança Média", value="39.8%")

# Tabela de Jogos
st.subheader("⚠️ Monitoramento de Partidas")
st.table(df)

# Área de Notícias (Simulando a integração futura com IA)
st.sidebar.header("🛡 Protocolos")
if st.sidebar.button("Forçar Varredura"):
    st.sidebar.write("Atlas varrendo mercados...")
  
