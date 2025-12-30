from trading.exchange import BinanceExchange
from utils.logger import get_logger

class TradeExecutor:
    def __init__(self, exchange: BinanceExchange):
        self.exchange = exchange
        self.logger = get_logger("EXECUTOR")

    def execute(self, symbol: str, signal: str, quantity: float):
        if signal not in ("BUY", "SELL"):
            return None

        self.logger.info(f"Placing {signal} order for {symbol}, qty={quantity}")

        order = self.exchange.place_market_order(
            symbol=symbol,
            side=signal,
            quantity=quantity
        )

        self.logger.info(f"Order executed: {order}")
        return order
