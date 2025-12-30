from binance.client import Client

class BinanceExchange:
    def __init__(self, api_key: str, api_secret: str, testnet: bool = True):
        self.client = Client(api_key, api_secret)

        if testnet:
            self.client.API_URL = "https://testnet.binance.vision/api"

    def get_klines(self, symbol: str, interval: str, limit: int = 100):
        return self.client.get_klines(
            symbol=symbol,
            interval=interval,
            limit=limit
        )

    def place_market_order(self, symbol: str, side: str, quantity: float):
        return self.client.create_order(
            symbol=symbol,
            side=side,
            type="MARKET",
            quantity=quantity
        )
