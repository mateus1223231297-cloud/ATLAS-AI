import streamlit as st
import pandas as pd
import os

LOG_FILE = "atlas_history.csv"

st.set_page_config(page_title="Atlas Tracker Pro", page_icon="📈", layout="centered")

st.title("📈 Atlas Tracker | Gestão de Banca")
st.markdown("Seu painel inteligente para controle de ROI e resultados.")

if not os.path.isfile(LOG_FILE):
    st.warning("⚠️ Nenhum histórico encontrado ainda. O arquivo atlas_history.csv será criado automaticamente quando você gerar sinais.")
    # Cria um arquivo vazio se não existir para evitar erros
    df_vazio = Data = pd.DataFrame(columns=["Data", "Jogo", "Mercado", "Casa", "Odd", "Probabilidade", "EV%", "Stake R$", "Status"])
    df_vazio.to_csv(LOG_FILE, index=False)
    df = df_vazio
else:
    df = pd.read_csv(LOG_FILE)

if "Status" not in df.columns:
    df["Status"] = "Pendente"
    df.to_csv(LOG_FILE, index=False)

st.subheader("📋 Suas Entradas Registradas")
st.dataframe(df, use_container_width=True)

st.markdown("---")
st.subheader("🎯 Atualizar Resultado de Entrada")

if len(df) > 0:
    index_jogo = st.selectbox("Escolha a partida para atualizar:", df.index, format_func=lambda x: f"{df.loc[x, 'Data']} - {df.loc[x, 'Jogo']} ({df.loc[x, 'Mercado']})")
    
    novo_status = st.radio("Resultado:", ["Pendente", "Green ✅", "Red ❌"], horizontal=True)
    
    if st.button("Salvar Resultado"):
        df.loc[index_jogo, "Status"] = novo_status
        df.to_csv(LOG_FILE, index=False)
        st.success("Status atualizado com sucesso!")
        st.rerun()

st.markdown("---")
st.subheader("📊 Métricas e Desempenho (ROI)")

finalizadas = df[df["Status"].isin(["Green ✅", "Red ❌"])]
total_apostas = len(finalizadas)

if total_apostas > 0:
    greens = len(df[df["Status"] == "Green ✅"])
    win_rate = (greens / total_apostas) * 100
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Finalizadas", total_apostas)
    col2.metric("Win Rate", f"{round(win_rate, 1)}%")
    col3.metric("Greens", greens)
else:
    st.info("ℹ️ Atualize ao menos uma aposta como Green ou Red para ver as estatísticas de ROI.")
    
