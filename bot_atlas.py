import os
import math
import requests
import telebot
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

# Carrega os tokens das variáveis de ambiente
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
ODDS_API_KEY = os.getenv('ODDS_API_KEY')

bot = telebot.TeleBot(BOT_TOKEN)

# Sessão HTTP robusta
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

def buscar_dados_jogos():
    url = 'https://api.the-odds-api.com/v4/sports/soccer_brazil_campeonato/odds'
    params = {'apiKey': ODDS_API_KEY, 'regions': 'eu', 'markets': 'totals', 'oddsFormat': 'decimal'}
    try:
        response = session.get(url, params=params, timeout=15)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Erro ao buscar odds: {e}")
    return []

# Comando inicial /start
@bot.message_handler(commands=['start', 'ajuda'])
def enviar_welcome(message):
    texto = (
        "🤖 *Atlas online e operacional, Senhor.*\n\n"
        "Estou pronto para processar os dados do Brasileirão. Você pode me dizer:\n"
        "• *'Quais jogos de hoje?'*\n"
        "• *'Me passe as entradas seguras para hoje'* ou mandar o comando /entradas\n"
        "• /jogos para ver a grade completa."
    )
    bot.reply_to(message, texto, parse_mode='Markdown')

# Comando ou gatilho para listar jogos
@bot.message_handler(commands=['jogos'])
@bot.message_handler(func=lambda msg: "jogos" in msg.text.lower())
def listar_jogos(message):
    bot.reply_to(message, "🔍 Acessando os servidores de dados e cruzando as odds do Brasileirão...")
    data = buscar_dados_jogos()
    
    if not data:
        bot.reply_to(message, "⚠️ Senhor, os servidores da API de odds não responderam no momento.")
        return

    for event in data[:5]:
        home = event.get('home_team')
        away = event.get('away_team')
        
        casa = dados_times.get(home, {"marcados": 1.3, "sofridos": 1.3})
        fora = dados_times.get(away, {"marcados": 1.3, "sofridos": 1.3})
        
        lambda_final = (((casa['marcados'] + fora['sofridos']) / 2) + ((fora['marcados'] + casa['sofridos']) / 2)) * 0.95
        prob = (1 - (math.exp(-lambda_final) * (1 + lambda_final + (lambda_final**2)/2))) * 100
        
        resposta = (
            f"🏟 *{home} vs {away}*\n"
            f"📈 Expectativa de Gols: `{lambda_final:.2f}`\n"
            f"⚽ Probabilidade Over 2.5: `{prob:.1f}%`"
        )
        bot.send_message(message.chat.id, resposta, parse_mode='Markdown')

# Gatilho para entradas seguras / análises profundas
@bot.message_handler(commands=['entradas'])
@bot.message_handler(func=lambda msg: any(palavra in msg.text.lower() for palavra in ["entradas", "seguras", "analise", "análise"]))
def entradas_seguras(message):
    bot.reply_to(message, "📊 Processando matriz de risco e filtrando o mercado de maior valor...")
    data = buscar_dados_jogos()
    
    if not data:
        bot.reply_to(message, "⚠️ Erro ao recuperar os dados de entradas.")
        return

    for event in data:
        home = event.get('home_team')
        away = event.get('away_team')
        
        casa = dados_times.get(home, {"marcados": 1.3, "sofridos": 1.3})
        fora = dados_times.get(away, {"marcados": 1.3, "sofridos": 1.3})
        
        lambda_final = (((casa['marcados'] + fora['sofridos']) / 2) + ((fora['marcados'] + casa['sofridos']) / 2)) * 0.95
        prob = (1 - (math.exp(-lambda_final) * (1 + lambda_final + (lambda_final**2)/2))) * 100
        
        if prob >= 40:
            conselho = "Análise sólida. Indicado para o mercado de Gols com margem de segurança." if prob >= 44 else "Cenário de cautela. As estatísticas pedem entradas fracionadas."
            
            resposta = (
                f"🎯 **FUNDAMENTOS - ATLAS**\n"
                f"🏟 Partida: *{home} vs {away}*\n"
                f"📈 Exp. Gols: `{lambda_final:.2f}`\n"
                f"📊 Prob. Calculada: `{prob:.1f}%`\n"
                f"🤖 *Parecer:* {conselho}"
            )
            bot.send_message(message.chat.id, resposta, parse_mode='Markdown')

# Resposta padrão para qualquer outra conversa estilo Jarvis
@bot.message_handler(func=lambda message: True)
def falar_com_jarvis(message):
    texto = message.text.lower()
    if "tudo bem" in texto or "olá" in texto or "ola" in texto:
        bot.reply_to(message, "Tudo em ordem nos sistemas, Senhor. O que deseja analisar no Brasileirão hoje?")
    else:
        bot.reply_to(message, "Comando não catalogado nos meus protocolos, Senhor. Tente digitar 'quais os jogos' ou pedir 'entradas seguras'.")

if __name__ == "__main__":
    print("🤖 Atlas Interativo iniciado com sucesso...")
    bot.infinity_polling()
      
