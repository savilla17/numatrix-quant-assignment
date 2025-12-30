import sys
from pathlib import Path

# Force project root on path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from binance.client import Client
from config import load_env

cfg = load_env()

client = Client(
    cfg["BINANCE_API_KEY"],
    cfg["BINANCE_API_SECRET"]
)

# IMPORTANT: Binance Spot Testnet endpoint
client.API_URL = "https://testnet.binance.vision/api"

print("PING:", client.ping())
print("ACCOUNT:")
print(client.get_account())
