import os
import math
import requests

API_KEY = os.getenv('ODDS_API_KEY')
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

dados_times = {
    "Flamengo": {"marcados": 1.7, "sofridos": 0.8, "escanteios": 6.2},
    "Palmeiras": {"marcados": 1.5, "sofridos": 0.7, "escanteios": 5.8},
    "Cruzeiro": {"marcados": 1.2, "sofridos": 1.1, "escanteios": 5.0},
    "Corinthians": {"marcados": 1.1, "sofridos": 1.2, "escanteios": 4.8},
    "Fluminense": {"marcados": 1.3, "sofridos": 1.0, "escanteios": 5.2},
    "Atletico Paranaense": {"marcados": 1.4, "sofridos": 1.0, "escanteios": 5.5},
    "Bragantino-SP": {"marcados": 1.3, "sofridos": 1.2, "escanteios": 5.6},
    "Coritiba": {"marcados": 1.0, "sofridos": 1.4, "escanteios": 4.5},
}

def enviar_telegram(mensagem):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    params = {'chat_id': CHAT_ID, 'text': mensagem}
    try:
        requests.get(url, params=params)
    except Exception as e:
        print(f"Erro ao enviar notificação: {e}")

def calcular_prob_gols(time_casa, time_fora):
    casa = dados_times.get(time_casa, {"marcados": 1.3, "sofridos": 1.3, "escanteios": 5.0})
    fora = dados_times.get(time_fora, {"marcados": 1.3, "sofridos": 1.3, "escanteios": 5.0})
    
    lambda_base = ((casa['marcados'] + fora['sofridos']) / 2) + ((fora['marcados'] + casa['sofridos']) / 2)
    lambda_final = lambda_base * 0.95
    
    p0 = math.exp(-lambda_final)
    p1 = p0 * lambda_final
    p2 = (p1 * lambda_final) / 2
    prob_over25 = 1 - (p0 + p1 + p2)
    
    prob_casa_marca = 1 - math.exp(-(((casa['marcados'] + fora['sofridos']) / 2)))
    prob_fora_marca = 1 - math.exp(-(((fora['marcados'] + casa['sofridos']) / 2)))
    prob_btts = prob_casa_marca * prob_fora_marca
    
    return prob_over25, prob_btts, lambda_final

def calcular_prob_escanteios(time_casa, time_fora):
    casa = dados_times.get(time_casa, {"escanteios": 5.0})
    fora = dados_times.get(time_fora, {"escanteios": 5.0})
    lambda_esc = casa['escanteios'] + fora['escanteios']
    
    acumulado = 0
    for k in range(10):
        acumulado += (math.exp(-lambda_esc) * (lambda_esc ** k)) / math.factorial(k)
    prob_over_95_esc = 1 - acumulado
    return prob_over_95_esc, lambda_esc

def executar_robo():
    url = 'https://api.the-odds-api.com/v4/sports/soccer_brazil_campeonato/odds'
    params = {'apiKey': API_KEY, 'regions': 'eu', 'markets': 'totals,btts', 'oddsFormat': 'decimal'}
    
    response = requests.get(url, params=params)
    if response.status_code != 200:
        print(f"Erro na API de Odds: {response.status_code}")
        return

    data = response.json()
    for event in data:
        home = event['home_team']
        away = event['away_team']
        prob_over25, prob_btts, lambda_gols = calcular_prob_gols(home, away)
        prob_esc, lambda_esc = calcular_prob_escanteios(home, away)
        
        for bookmaker in event.get('bookmakers', []):
            for market in bookmaker.get('markets', []):
                for outcome in market.get('outcomes', []):
                    if outcome['name'] == 'Over' and outcome.get('point') == 2.5:
                        odd = outcome['price']
                        ev = (prob_over25 * odd) - 1
                        if ev > 0.01:
                            msg = (
                                f"🚀 EV+ GOLS (Over 2.5)\n\n"
                                f"🏟 Partida: {home} vs {away}\n"
                                f"📈 Exp. Gols: {lambda_gols:.2f}\n"
                                f"🏢 Casa: {bookmaker['title']}\n"
                                f"💰 Odd: {odd}\n"
                                f"📊 EV: +{ev*100:.2f}%"
                            )
                            enviar_telegram(msg)
                            
                    elif outcome['name'] == 'Yes':
                        odd = outcome['price']
                        ev = (prob_btts * odd) - 1
                        if ev > 0.01:
                            msg = (
                                f"🚀 EV+ AMBOS MARCAM\n\n"
                                f"🏟 Partida: {home} vs {away}\n"
                                f"🏢 Casa: {bookmaker['title']}\n"
                                f"💰 Odd: {odd}\n"
                                f"📊 EV: +{ev*100:.2f}%"
                            )
                            enviar_telegram(msg)

                    elif outcome['name'] == 'Over' and outcome.get('point') == 9.5:
                        odd = outcome['price']
                        ev = (prob_esc * odd) - 1
                        if ev > 0.01:
                            msg = (
                                f"🚀 EV+ ESCANTEIOS (Over 9.5)\n\n"
                                f"🏟 Partida: {home} vs {away}\n"
                                f"📈 Exp. Escanteios: {lambda_esc:.1f}\n"
                                f"🏢 Casa: {bookmaker['title']}\n"
                                f"💰 Odd: {odd}\n"
                                f"📊 EV: +{ev*100:.2f}%"
                            )
                            enviar_telegram(msg)

    enviar_telegram("🤖 Robô operando: Verificação concluída (Gols, BTTS e Escanteios).")

if __name__ == "__main__":
    executar_robo()
    
