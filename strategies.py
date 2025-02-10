from config import ALPACA_CONFIG, TRADING_CONFIG
from strategies import MovingAverageStrategy
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
import time

class TradingBot:
    def __init__(self):
        self.api = TradingClient(
            ALPACA_CONFIG['API_KEY'],
            ALPACA_CONFIG['SECRET_KEY'],
            paper=True
        )
        self.strategy = MovingAverageStrategy(
            ALPACA_CONFIG['API_KEY'],
            ALPACA_CONFIG['SECRET_KEY']
        )
        
    def run(self, symbol="AAPL"):
        while True:
            try:
                # Obtener señal
                signal = self.strategy.get_signal(symbol)
                print(f"Señal para {symbol}: {signal}")
                
                # Ejecutar operación según señal
                if signal == 'BUY':
                    self.place_order(symbol, 1, OrderSide.BUY)
                elif signal == 'SELL':
                    self.place_order(symbol, 1, OrderSide.SELL)
                    
                time.sleep(TRADING_CONFIG['INTERVAL'])
                
            except Exception as e:
                print(f"Error: {e}")
                time.sleep(60)

    def place_order(self, symbol, qty, side):
        order = MarketOrderRequest(
            symbol=symbol,
            qty=qty,
            side=side,
            time_in_force=TimeInForce.DAY
        )
        return self.api.submit_order(order)

if __name__ == "__main__":
    bot = TradingBot()
    bot.run()