import os
from datetime import datetime
from alpaca_trade_api import REST
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

class TradingEngine:
    """Simple trading engine interfacing with Alpaca API"""

    def __init__(self):
        api_key = os.getenv("ALPACA_API_KEY")
        secret = os.getenv("ALPACA_SECRET_KEY")
        base_url = os.getenv("ALPACA_BASE_URL", "https://paper-api.alpaca.markets")
        if not api_key or not secret:
            raise ValueError("Alpaca keys are not set in environment variables")
        self.api = REST(api_key, secret, base_url, api_version='v2')
        self.positions = {}

    def get_price(self, symbol: str) -> float:
        barset = self.api.get_barset(symbol, 'minute', limit=1)
        return barset[symbol][0].c

    def submit_order(self, symbol: str, qty: int, side: str, type_: str = 'market', time_in_force: str = 'gtc'):
        print(f"Submitting order {side} {qty} {symbol} @ {datetime.utcnow()}")
        self.api.submit_order(symbol=symbol, qty=qty, side=side, type=type_, time_in_force=time_in_force)

    def close_position(self, symbol: str):
        try:
            self.api.close_position(symbol)
        except Exception as e:
            print(f"Error closing position {symbol}: {e}")

    def get_open_positions(self):
        return self.api.list_positions()