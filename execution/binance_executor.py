from binance.client import Client

class BinanceExecutor:
    def __init__(self, api_key: str, api_secret: str, testnet: bool = True):
        self.client = Client(api_key, api_secret)

        if testnet:
            self.client.API_URL = "https://testnet.binance.vision/api"

    def buy_market(self, symbol: str, quantity: float):
        return self.client.create_order(
            symbol=symbol,
            side="BUY",
            type="MARKET",
            quantity=quantity
        )

    def sell_market(self, symbol: str, quantity: float):
        return self.client.create_order(
            symbol=symbol,
            side="SELL",
            type="MARKET",
            quantity=quantity
        )
