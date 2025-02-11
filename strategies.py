# strategies.py
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
import pandas as pd
from datetime import datetime, timedelta

class MovingAverageStrategy:
    def __init__(self, api_key, secret_key):
        self.data_client = StockHistoricalDataClient(api_key, secret_key)
        self.short_window = 20  # Media móvil corta (20 períodos)
        self.long_window = 50   # Media móvil larga (50 períodos)

    def get_historical_data(self, symbol):
        """Obtiene datos históricos para el cálculo de medias móviles"""
        end = datetime.now()
        start = end - timedelta(days=100)  # Obtener 100 días de datos

        request_params = StockBarsRequest(
            symbol_or_symbols=symbol,
            timeframe=TimeFrame.Day,
            start=start,
            end=end
        )

        try:
            bars = self.data_client.get_stock_bars(request_params)
            df = pd.DataFrame([{
                'timestamp': bar.timestamp,
                'close': bar.close,
                'open': bar.open,
                'high': bar.high,
                'low': bar.low,
                'volume': bar.volume
            } for bar in bars.data[symbol]])
            
            # Asegurarnos que tenemos la columna 'close'
            if 'close' not in df.columns:
                raise ValueError("No se encontró la columna 'close' en los datos")
                
            return df
            
        except Exception as e:
            logging.error(f"Error obteniendo datos históricos: {e}")
            return pd.DataFrame()

    def calculate_signals(self, df):
        """Calcula las señales basadas en el cruce de medias móviles"""
        if df.empty:
            return df
            
        try:
            df['SMA_short'] = df['close'].rolling(window=self.short_window).mean()
            df['SMA_long'] = df['close'].rolling(window=self.long_window).mean()
            
            # Genera señales
            df['signal'] = 0
            df.loc[df['SMA_short'] > df['SMA_long'], 'signal'] = 1  # Señal de compra
            df.loc[df['SMA_short'] < df['SMA_long'], 'signal'] = -1 # Señal de venta
            
            return df
        except Exception as e:
            logging.error(f"Error calculando señales: {e}")
            return pd.DataFrame()

    def get_signal(self, symbol):
        """Retorna la señal actual: 'BUY', 'SELL' o 'HOLD' con explicación"""
        try:
            df = self.get_historical_data(symbol)
            df = self.calculate_signals(df)
            
            if len(df) < self.long_window:
                return 'HOLD', f'No hay suficientes datos (necesita {self.long_window} días)'
            
            current_signal = df['signal'].iloc[-1]
            previous_signal = df['signal'].iloc[-2]
            
            # Obtener valores actuales para explicación
            current_short_ma = df['SMA_short'].iloc[-1]
            current_long_ma = df['SMA_long'].iloc[-1]
            current_price = df['close'].iloc[-1]
            
            explanation = f'Precio: ${current_price:.2f}, SMA20: ${current_short_ma:.2f}, SMA50: ${current_long_ma:.2f}'
            
            # Solo genera señal cuando hay un cambio
            if current_signal == 1 and previous_signal <= 0:
                return 'BUY', explanation
            elif current_signal == -1 and previous_signal >= 0:
                return 'SELL', explanation
            
            # Explicar por qué HOLD
            if current_signal == 1:
                return 'HOLD', f'{explanation} - Tendencia alcista, mantener posición larga'
            elif current_signal == -1:
                return 'HOLD', f'{explanation} - Tendencia bajista, mantener posición corta'
            else:
                return 'HOLD', f'{explanation} - Sin tendencia clara'
            
        except Exception as e:
            return 'HOLD', f'Error al obtener señal: {e}'