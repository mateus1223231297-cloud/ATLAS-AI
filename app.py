import streamlit as st
import pandas as pd
import json

st.set_page_config(page_title="Atlas - Central de Inteligência", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    h1 { color: #00f2ff; }
    </style>
    """, unsafe_allow_html=True)

st.title("🔴 ATLAS - Central de Inteligência")
st.subheader("Protocolo de Monitoramento Brasileirão 2026")

# Esta parte vai ler um arquivo que o seu robô vai atualizar automaticamente
try:
    with open('analise_jogos.json', 'r') as f:
        dados = json.load(f)
        df = pd.DataFrame(dados)
        st.table(df)
except FileNotFoundError:
    st.warning("⚠️ Atlas em espera. Execute o robô de varredura para atualizar os dados.")

if st.button("Consultar status do Protocolo"):
    st.success("Atlas: Os sistemas estão operacionais, Senhor.")
    
