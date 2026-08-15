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
}

def enviar_telegram(mensagem):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    params = {'chat_id': CHAT_ID, 'text': mensagem}
    try:
        requests.get(url, params=params)
    except Exception as e:
        print(f"Erro ao enviar notificação: {e}")

def calcular_prob_over(time_casa, time_fora):
    casa = dados_times.get(time_casa, {"marcados": 1.3, "sofridos": 1.3})
    fora = dados_times.get(time_fora, {"marcados": 1.3, "sofridos": 1.3})
    
    lambda_base = ((casa['marcados'] + fora['sofridos']) / 2) + ((fora['marcados'] + casa['sofridos']) / 2)
    fator_ia_contexto = 0.95 
    lambda_final = lambda_base * fator_ia_contexto
    
    p0 = (math.exp(-lambda_final) * (lambda_final ** 0)) / math.factorial(0)
    p1 = (math.exp(-lambda_final) * (lambda_final ** 1)) / math.factorial(1)
    p2 = (math.exp(-lambda_final) * (lambda_final ** 2)) / math.factorial(2)
    prob_over = 1 - (p0 + p1 + p2)
    
    return prob_over, lambda_final

def executar_robo():
    url = 'https://api.the-odds-api.com/v4/sports/soccer_brazil_campeonato/odds'
    params = {'apiKey': API_KEY, 'regions': 'eu', 'markets': 'totals', 'oddsFormat': 'decimal'}
    
    response = requests.get(url, params=params)
    if response.status_code != 200:
        print(f"Erro na API de Odds: {response.status_code}")
        return

    data = response.json()
    for event in data:
        home = event['home_team']
        away = event['away_team']
        prob_real, lambda_val = calcular_prob_over(home, away)
        
        for bookmaker in event.get('bookmakers', []):
            for market in bookmaker.get('markets', []):
                for outcome in market.get('outcomes', []):
                    if outcome['name'] == 'Over' and outcome.get('point') == 2.5:
                        odd = outcome['price']
                        ev = (prob_real * odd) - 1
                        
                        if ev > 0.05: 
                            msg = (
                                f"🚀 OPORTUNIDADE EV+ (Série A)\n\n"
                                f"🏟 Partida: {home} vs {away}\n"
                                f"📈 Expectativa: {lambda_val:.2f} gols\n"
                                f"🏢 Casa: {bookmaker['title']}\n"
                                f"💰 Odd: {odd}\n"
                                f"📊 EV: +{ev*100:.2f}%"
                            )
                            enviar_telegram(msg)

if __name__ == "__main__":
    executar_robo()
      
