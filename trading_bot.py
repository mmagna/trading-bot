# trading_bot.py
import os
from dotenv import load_dotenv
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
import time

load_dotenv()

class TradingBot:
    def __init__(self):
        self.api = TradingClient(
            os.getenv('ALPACA_API_KEY'),
            os.getenv('ALPACA_SECRET_KEY'),
            paper=True
        )
        
    def check_position(self, symbol):
        try:
            position = self.api.get_position(symbol)
            return float(position.qty)
        except:
            return 0
            
    def place_order(self, symbol, qty, side):
        order_data = MarketOrderRequest(
            symbol=symbol,
            qty=qty,
            side=side,
            time_in_force=TimeInForce.DAY
        )
        return self.api.submit_order(order_data)
        
    def run(self, symbol="AAPL", interval=60):
        while True:
            try:
                position = self.check_position(symbol)
                print(f"Posición actual en {symbol}: {position}")
                
                # Aquí irá tu estrategia
                
                time.sleep(interval)
                
            except Exception as e:
                print(f"Error: {e}")
                time.sleep(interval)

if __name__ == "__main__":
    bot = TradingBot()
    bot.run()