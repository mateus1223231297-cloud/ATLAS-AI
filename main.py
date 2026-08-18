import os
import math
import requests
import json
from openai import OpenAI
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

# Inicializa o cliente OpenAI
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

API_KEY = os.getenv('ODDS_API_KEY')
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# Configura a sessão HTTP com tentativas automáticas em caso de queda de conexão
session = requests.Session()
retries = Retry(total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
session.mount('https://', HTTPAdapter(max_retries=retries))

dados_times = {
    "Flamengo": {"marcados": 1.7, "sofridos": 0.8},
    "Palmeiras": {"marcados": 1.5, "sofridos": 0.7},
    "Fluminense": {"marcados": 1.3, "sofridos": 1.0},
    "Atletico Paranaense": {"marcados": 1.4, "sofridos": 1.0},
    "Bragantino-SP": {"marcados": 1.3, "sofridos": 1.2},
    "Coritiba": {"marcados": 1.0, "sofridos": 1.4},
    "São Paulo": {"marcados": 1.4, "sofridos": 0.9},
}

def enviar_telegram(mensagem):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        session.get(url, params={'chat_id': CHAT_ID, 'text': mensagem, 'parse_mode': 'Markdown'}, timeout=10)
    except Exception as e:
        print(f"Erro ao enviar mensagem no Telegram: {e}")

def gerar_analise_atlas(partida, prob):
    try:
        prompt = f"Você é o Atlas, uma IA consultora de apostas estilo Jarvis. Analise brevemente o jogo: {partida}. A probabilidade de Over 2.5 gols calculada é de {prob}%. Seja técnico, sarcástico como o Jarvis e dê um conselho de investimento curto."
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Erro na OpenAI: {e}")
        return "Análise do protocolo Atlas indisponível no momento."

def executar_robo():
    url = 'https://api.the-odds-api.com/v4/sports/soccer_brazil_campeonato/odds'
    params = {'apiKey': API_KEY, 'regions': 'eu', 'markets': 'totals', 'oddsFormat': 'decimal'}
    
    try:
        response = session.get(url, params=params, timeout=15)
        if response.status_code != 200:
            print(f"Erro na API de Odds: Status {response.status_code}")
            return
        data = response.json()
    except Exception as e:
        print(f"Falha de conexão ao buscar odds: {e}")
        return

    lista_atlas = []

    for event in data:
        home = event.get('home_team')
        away = event.get('away_team')
        
        casa = dados_times.get(home, {"marcados": 1.3, "sofridos": 1.3})
        fora = dados_times.get(away, {"marcados": 1.3, "sofridos": 1.3})
        
        lambda_final = (((casa['marcados'] + fora['sofridos']) / 2) + ((fora['marcados'] + casa['sofridos']) / 2)) * 0.95
        prob = (1 - (math.exp(-lambda_final) * (1 + lambda_final + (lambda_final**2)/2))) * 100
        
        # Gera a análise da IA
        analise = gerar_analise_atlas(f"{home} vs {away}", f"{prob:.1f}")
        
        # Envia para o Telegram
        mensagem = f"🏟 *{home} vs {away}*\n📈 Exp. Gols: `{lambda_final:.2f}`\n⚽ Prob. Over 2.5: `{prob:.1f}%`\n\n🤖 *Atlas:* {analise}"
        enviar_telegram(mensagem)
        
        lista_atlas.append({"Partida": f"{home} vs {away}", "Exp_Gols": round(lambda_final, 2), "Prob": f"{prob:.1f}%"})

    with open('analise_jogos.json', 'w', encoding='utf-8') as f:
        json.dump(lista_atlas, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    executar_robo()
    
