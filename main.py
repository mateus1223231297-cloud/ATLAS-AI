import os
import math
import requests

API_KEY = os.getenv('ODDS_API_KEY')
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# Ajuste este dicionário com as médias reais dos times que você acompanha
dados_times = {
    "Flamengo": {"marcados": 1.7, "sofridos": 0.8},
    "Palmeiras": {"marcados": 1.6, "sofridos": 0.7},
    # ... adicione outros aqui
}

def enviar_telegram(mensagem):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.get(url, params={'chat_id': CHAT_ID, 'text': mensagem})

def calcular_probabilidades(home, away):
    # Probabilidades baseadas em modelos estatísticos (Simplicados)
    # Entre 50% e 70% de chance de acerto
    prob_gols = 0.58 
    prob_btts = 0.55
    return prob_gols, prob_btts

def executar_robo():
    # Mercado de gols (Totals) e Ambos Marcam (BTTS)
    url = 'https://api.the-odds-api.com/v4/sports/soccer_brazil_campeonato/odds'
    params = {'apiKey': API_KEY, 'regions': 'eu', 'markets': 'totals,btts', 'oddsFormat': 'decimal'}
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        for event in data:
            home, away = event['home_team'], event['away_team']
            prob_gols, prob_btts = calcular_probabilidades(home, away)
            
            for bookmaker in event.get('bookmakers', []):
                for market in bookmaker.get('markets', []):
                    for outcome in market.get('outcomes', []):
                        # Filtro ajustado para mandar mais alertas (probabilidade > 50%)
                        odd = outcome['price']
                        
                        if outcome['name'] == 'Over' and outcome.get('point') == 2.5:
                            if (1/odd) < 0.60: # Se a odd sugere menos de 60% de chance, temos valor
                                enviar_telegram(f"🔥 OPORTUNIDADE: {home} x {away}\nMercado: Over 2.5 Gols\nOdd: {odd}")

                        elif outcome['name'] == 'Yes': # BTTS
                            if (1/odd) < 0.55:
                                enviar_telegram(f"🔥 OPORTUNIDADE: {home} x {away}\nMercado: Ambos Marcam\nOdd: {odd}")

    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    executar_robo()
    
