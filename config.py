# config.py
import os
from dotenv import load_dotenv

load_dotenv()

ALPACA_CONFIG = {
    'API_KEY': os.getenv('ALPACA_API_KEY'),
    'SECRET_KEY': os.getenv('ALPACA_SECRET_KEY'),
    'BASE_URL': os.getenv('ALPACA_BASE_URL')
}

TRADING_CONFIG = {
    'SYMBOLS': ['AAPL', 'GOOGL'],  # Símbolos a operar
    'INTERVAL': 60,                 # Intervalo en segundos
    'MAX_POSITION': 5000,           # Máximo valor por posición ($)
    'STOP_LOSS_PCT': 0.02          # Stop loss 2%
}