import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Configuração da Página em Modo Wide com Tema Futurista
st.set_page_config(page_title="ATLAS QUANT PRO", page_icon="⚡", layout="wide")

# Estilização CSS Personalizada (Estilo Terminal Quantitativo / Dark Neon)
st.markdown("""
    <style>
    .stApp {
        background-color: #0b0f19;
        color: #f3f4f6;
    }
    h1, h2, h3 {
        color: #00ffcc !important;
        font-family: 'Inter', sans-serif;
        letter-spacing: -0.5px;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #111827;
        border-radius: 8px;
        color: #9ca3af;
        padding: 10px 20px;
        font-weight: 600;
        border: 1px solid #1f2937;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #00ffcc 0%, #00bfff 100%) !important;
        color: #0b0f19 !important;
        border: none;
    }
    </style>
""", unsafe_allow_html=True)

st.title("⚡ ATLAS QUANT | Institutional Betting Terminal")
st.markdown("### Painel de Alta Performance, Gestão de Banca & Valor Matemático (+EV)")

LOG_FILE = "atlas_history.csv"

# Inicializa o banco de dados local se não existir
if not os.path.isfile(LOG_FILE):
    df = pd.DataFrame(columns=["Data", "Jogo", "Mercado", "Casa", "Odd", "Probabilidade", "EV%", "Stake R$", "Status"])
    df.to_csv(LOG_FILE, index=False)
else:
    df = pd.read_csv(LOG_FILE)

if "Status" not in df.columns:
    df["Status"] = "Pendente"
    df.to_csv(LOG_FILE, index=False)

# Sistema de Abas Profissional
tab1, tab2, tab3 = st.tabs(["📊 Dashboard & ROI", "📋 Gestão de Entradas", "🎯 Inserir Oportunidade"])

with tab1:
    st.subheader("📈 Métricas de Desempenho Global")
    
    finalizadas = df[df["Status"].isin(["Green ✅", "Red ❌"])]
    total_fin = len(finalizadas)
    
    greens = len(df[df["Status"] == "Green ✅"])
    reds = len(df[df["Status"] == "Red ❌"])
    win_rate = (greens / total_fin * 100) if total_fin > 0 else 0
    
    # Cálculo dinâmico de Lucro e ROI
    lucro_total = 0.0
    investido_total = 0.0
    
    for _, row in finalizadas.iterrows():
        try:
            stake = float(str(row["Stake R$"]).replace("R$", "").replace(" ", "").replace(",", "."))
            odd = float(str(row["Odd"]).replace("@", "").replace(" ", "").replace(",", "."))
            investido_total += stake
            if "Green" in row["Status"]:
                lucro_total += stake * (odd - 1)
            elif "Red" in row["Status"]:
                lucro_total -= stake
        except:
            pass
            
    roi = (lucro_total / investido_total * 100) if investido_total > 0 else 0.0

    # Cartões de Métricas Estilizados
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Lucro Líquido", f"R$ {round(lucro_total, 2)}", delta=f"{round(roi, 2)}% ROI")
    col2.metric("Win Rate", f"{round(win_rate, 1)}%", delta=f"{greens}G / {reds}R")
    col3.metric("Total no Sistema", len(df))
    col4.metric("Entradas Resolvidas", total_fin)

    st.markdown("---")
    st.subheader("📉 Curva de Crescimento da Banca (Lucro Acumulado)")
    
    if total_fin > 0:
        cum_profit = []
        current_p = 0
        for _, row in finalizadas.iterrows():
            try:
                stake = float(str(row["Stake R$"]).replace("R$", "").replace(" ", "").replace(",", "."))
                odd = float(str(row["Odd"]).replace("@", "").replace(" ", "").replace(",", "."))
                if "Green" in row["Status"]:
                    current_p += stake * (odd - 1)
                else:
                    current_p -= stake
            except:
                pass
            cum_profit.append(current_p)
            
        chart_data = pd.DataFrame({"Lucro Acumulado (R$)": cum_profit})
        st.line_chart(chart_data)
    else:
        st.info("ℹ️ Atualize ao menos uma aposta como Green ou Red para gerar o gráfico interativo de evolução.")

with tab2:
    st.subheader("📋 Histórico Completo de Entradas")
    st.dataframe(df, use_container_width=True)

    if len(df) > 0:
        st.markdown("---")
        st.subheader("⚙️ Central de Atualização de Resultados")
        
        index_jogo = st.selectbox("Selecione a partida para atualizar:", df.index, format_func=lambda x: f"{df.loc[x, 'Data']} | {df.loc[x, 'Jogo']} -> {df.loc[x, 'Mercado']}")
        novo_status = st.radio("Definir Status:", ["Pendente", "Green ✅", "Red ❌"], horizontal=True)
        
        if st.button("Salvar Alteração no Sistema"):
            df.loc[index_jogo, "Status"] = novo_status
            df.to_csv(LOG_FILE, index=False)
            st.success("Status atualizado com sucesso! O dashboard foi recalculado em tempo real.")
            st.rerun()

with tab3:
    st.subheader("🎯 Espaço para Nova Oportunidade de Entrada")
    st.markdown("Cadastre manualmente uma nova entrada gerada pelo seu fluxo ou robô:")
    
    with st.form("nova_entrada_form"):
        f_data = st.text_input("Data e Hora", value=datetime.now().strftime("%Y-%m-%d %H:%M"))
        f_jogo = st.text_input("Partida (Ex: Vitória x Bahia)")
        f_mercado = st.text_input("Mercado (Ex: Vitória Simples / BTTS)")
        f_casa = st.selectbox("Casa de Apostas", ["Superbet", "Betano"])
        f_odd = st.text_input("Odd Oferecida (Ex: 1.95)")
        f_prob = st.text_input("Probabilidade Real (Ex: 52%)")
        f_ev = st.text_input("Valor Matemático EV% (Ex: +4.2%)")
        f_stake = st.text_input("Stake Recomendada (Ex: R$ 25.00)")
        
        submitted = st.form_submit_button("Lançar Oportunidade no PWA")
        if submitted:
            nova_linha = pd.DataFrame([{
                "Data": f_data, "Jogo": f_jogo, "Mercado": f_mercado, 
                "Casa": f_casa, "Odd": f_odd, "Probabilidade": f_prob, 
                "EV%": f_ev, "Stake R$": f_stake, "Status": "Pendente"
            }])
            df = pd.concat([df, nova_linha], ignore_index=True)
            df.to_csv(LOG_FILE, index=False)
            st.success("Oportunidade lançada com sucesso! Ela já aparece na aba de histórico e no seu app do celular.")
            st.rerun()
            
