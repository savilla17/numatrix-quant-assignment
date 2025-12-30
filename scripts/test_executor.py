import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from config import load_env
from execution.binance_executor import BinanceExecutor

cfg = load_env()

executor = BinanceExecutor(
    cfg["BINANCE_API_KEY"],
    cfg["BINANCE_API_SECRET"],
    testnet=True
)

order = executor.buy_market("BTCUSDT", 0.001)
print(order)

