# trading_bot.py
import os
import time
import signal
import logging
from datetime import datetime
from dotenv import load_dotenv
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from strategies import MovingAverageStrategy

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trading_bot.log'),
        logging.StreamHandler()
    ]
)

class TradingBot:
    def __init__(self):
        load_dotenv()
        self.api = TradingClient(
            os.getenv('ALPACA_API_KEY'),
            os.getenv('ALPACA_SECRET_KEY'),
            paper=True
        )
        self.strategy = MovingAverageStrategy(
            os.getenv('ALPACA_API_KEY'),
            os.getenv('ALPACA_SECRET_KEY')
        )
        self.running = True
        
        # Configurar manejo de señales
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, signum, frame):
        """Maneja la señal de interrupción (Ctrl+C)"""
        logging.info("🛑 Deteniendo el bot de forma segura...")
        self.running = False
        # Forzar la salida después de 3 segundos
        time.sleep(3)
        os._exit(0)

    def check_position(self, symbol):
        """Verifica la posición actual en un símbolo"""
        try:
            positions = self.api.get_all_positions()
            for position in positions:
                if position.symbol == symbol:
                    return float(position.qty)
            return 0
        except Exception as e:
            logging.error(f"Error al verificar posición: {e}")
            return 0

    def place_order(self, symbol, qty, side):
        """Coloca una orden de mercado"""
        try:
            order_data = MarketOrderRequest(
                symbol=symbol,
                qty=qty,
                side=side,
                time_in_force=TimeInForce.DAY
            )
            order = self.api.submit_order(order_data)
            logging.info(f"Orden enviada: {side} {qty} {symbol}")
            return order
        except Exception as e:
            logging.error(f"Error al colocar orden: {e}")
            return None

    def run(self, symbol="AAPL", interval=60):
        """Ejecuta el bot de trading"""
        logging.info(f"Iniciando bot de trading para {symbol}")
        
        try:
            while self.running:
                try:
                    # Para pruebas, omitimos la verificación del mercado
                    # clock = self.api.get_clock()
                    # if not clock.is_open:
                    #     logging.info("Mercado cerrado. Esperando...")
                    #     time.sleep(300)  # Esperar 5 minutos
                    #     continue

                    # Obtener posición actual
                    position = self.check_position(symbol)
                    logging.info(f"Posición actual en {symbol}: {position}")

                    # Obtener señal de la estrategia
                    signal, explanation = self.strategy.get_signal(symbol)
                    logging.info(f"Señal para {symbol}: {signal} - {explanation}")

                    # Ejecutar operaciones según la señal
                    if signal == 'BUY' and position <= 0:
                        self.place_order(symbol, 1, OrderSide.BUY)
                    elif signal == 'SELL' and position >= 0:
                        self.place_order(symbol, abs(position) if position > 0 else 1, OrderSide.SELL)

                    time.sleep(interval)

                except Exception as e:
                    logging.error(f"Error en el ciclo principal: {e}")
                    time.sleep(60)  # Esperar un minuto antes de reintentar
        
        except KeyboardInterrupt:
            logging.info("Interrupción de teclado detectada")
            self.exit_gracefully(None, None)
        finally:
            logging.info("Bot detenido")

if __name__ == "__main__":
    bot = TradingBot()
    bot.run()