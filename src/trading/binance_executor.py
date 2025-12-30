from trading.exchange import BinanceExchange

class TradeExecutor:
    def __init__(self, exchange: BinanceExchange, symbol: str, quantity: float):
        self.exchange = exchange
        self.symbol = symbol
        self.quantity = quantity

    def execute(self, signal: str):
        if signal == "BUY":
            return self.exchange.place_market_order(
                self.symbol,
                "BUY",
                self.quantity
            )

        if signal == "SELL":
            return self.exchange.place_market_order(
                self.symbol,
                "SELL",
                self.quantity
            )

        return None
