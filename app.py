import streamlit as st
import pandas as pd
import json

# Configuração da página como "wide" para preencher a tela toda
st.set_page_config(page_title="Atlas - Central de Inteligência", layout="wide")

# CSS personalizado para o estilo "Homem de Ferro"
st.markdown("""
    <style>
    /* Fundo escuro estilo Stark */
    .stApp { background-color: #050b16; color: #00f2ff; }
    
    /* Cabeçalho estilo Jarvis */
    h1 { color: #00f2ff; text-transform: uppercase; letter-spacing: 2px; text-shadow: 0 0 10px #00f2ff; }
    
    /* Cartões e tabelas com borda neon */
    .stDataFrame { border: 1px solid #00f2ff; border-radius: 10px; }
    
    /* Botões */
    div.stButton > button { background-color: #00f2ff; color: #000; font-weight: bold; border-radius: 5px; }
    
    /* Texto de status */
    .stMetric { background-color: #0a192f; padding: 15px; border-radius: 10px; border-left: 5px solid #00f2ff; }
    </style>
""", unsafe_allow_html=True)

st.title("🔴 ATLAS - Central de Inteligência")
st.markdown("---")

try:
    with open('analise_jogos.json', 'r') as f:
        dados = json.load(f)
        df = pd.DataFrame(dados)
        
        # Exibe a tabela com um visual melhor
        st.subheader("⚠️ Monitoramento de Partidas - Protocolo Ativo")
        st.dataframe(df, use_container_width=True)
        
except FileNotFoundError:
    st.warning("⚠️ Atlas em espera. Execute o robô de varredura para atualizar os dados do sistema.")

# Footer estilo JARVIS
st.markdown("---")
st.write("🤖 *'Senhor, todos os sistemas estão online e operacionais.'* - Atlas")
