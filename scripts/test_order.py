import sys
from pathlib import Path

print("START SCRIPT")

# Force project root on path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
print("ROOT:", ROOT)

from config import load_env
from binance.client import Client

cfg = load_env()
print("CONFIG LOADED")

print("API KEY PREFIX:", cfg["BINANCE_API_KEY"][:6])

client = Client(
    cfg["BINANCE_API_KEY"],
    cfg["BINANCE_API_SECRET"]
)

client.API_URL = "https://testnet.binance.vision/api"
print("CLIENT INITIALIZED")

try:
    print("PLACING ORDER...")
    order = client.create_order(
        symbol="BTCUSDT",
        side="BUY",
        type="MARKET",
        quantity=0.001
    )
    print("ORDER RESPONSE:")
    print(order)
except Exception as e:
    print("ERROR OCCURRED:")
    print(type(e))
    print(e)

print("END SCRIPT")
