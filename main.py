import os
import math
import requests

API_KEY = os.getenv('ODDS_API_KEY')
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

dados_times = {
    "Flamengo": {"marcados": 1.7, "sofridos": 0.8},
    "Palmeiras": {"marcados": 1.5, "sofridos": 0.7},
    "Cruzeiro": {"marcados": 1.2, "sofridos": 1.1},
    "Corinthians": {"marcados": 1.1, "sofridos": 1.2},
    "Fluminense": {"marcados": 1.3, "sofridos": 1.0},
    "Atletico Paranaense": {"marcados": 1.4, "sofridos": 1.0},
    "Bragantino-SP": {"marcados": 1.3, "sofridos": 1.2},
    "Coritiba": {"marcados": 1.0, "sofridos": 1.4},
    "São Paulo": {"marcados": 1.4, "sofridos": 0.9},
}

def enviar_telegram(mensagem):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    params = {'chat_id': CHAT_ID, 'text': mensagem, 'parse_mode': 'Markdown'}
    try:
        requests.get(url, params=params)
    except Exception as e:
        print(f"Erro ao enviar: {e}")

def executar_robo():
    url = 'https://api.the-odds-api.com/v4/sports/soccer_brazil_campeonato/odds'
    params = {'apiKey': API_KEY, 'regions': 'eu', 'markets': 'totals,btts', 'oddsFormat': 'decimal'}
    
    response = requests.get(url, params=params)
    if response.status_code != 200:
        enviar_telegram(f"❌ Erro na API de Odds: {response.status_code}")
        return

    data = response.json()
    if not data:
        enviar_telegram("⚠️ Nenhum jogo encontrado na grade da API neste momento.")
        return

    enviar_telegram("📊 *RELATÓRIO DE ANÁLISE - RODADA DE HOJE* ⚽")

    for event in data:
        home = event.get('home_team')
        away = event.get('away_team')
        
        # Pega as estatísticas dos times ou usa uma média padrão se não encontrar
        casa = dados_times.get(home, {"marcados": 1.3, "sofridos": 1.3})
        fora = dados_times.get(away, {"marcados": 1.3, "sofridos": 1.3})
        
        # Cálculo de Expectativa de Gols (Poisson simplificado)
        lambda_base = ((casa['marcados'] + fora['sofridos']) / 2) + ((fora['marcados'] + casa['sofridos']) / 2)
        lambda_final = lambda_base * 0.95
        
        # Probabilidade de Over 2.5
        p0 = math.exp(-lambda_final)
        p1 = p0 * lambda_final
        p2 = (p1 * lambda_final) / 2
        prob_over25 = (1 - (p0 + p1 + p2)) * 100
        
        # Probabilidade de Ambos Marcam (BTTS)
        prob_casa_marca = (1 - math.exp(-((casa['marcados'] + fora['sofridos']) / 2))) * 100
        prob_fora_marca = (1 - math.exp(-((fora['marcados'] + casa['sofridos']) / 2))) * 100
        prob_btts = (prob_casa_marca / 100) * (prob_fora_marca / 100) * 100

        # Monta a mensagem de análise detalhada do jogo
        msg = (
            f"🏟 *{home} vs {away}*\n"
            f"📈 Exp. de Gols: `{lambda_final:.2f}`\n"
            f"⚽ Prob. Over 2.5: `{prob_over25:.1f}%`\n"
            f"🤝 Prob. Ambos Marcam: `{prob_btts:.1f}%`\n"
            f"-----------------------------------"
        )
        enviar_telegram(msg)

if __name__ == "__main__":
    executar_robo()
    
