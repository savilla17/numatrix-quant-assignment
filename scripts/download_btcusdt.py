from binance.client import Client
import pandas as pd
from pathlib import Path

print("IMPORTS OK")

# ---------- CONFIG ----------
SYMBOL = "BTCUSDT"
INTERVAL = Client.KLINE_INTERVAL_15MINUTE

# ISO 8601 dates (SAFE, FUTURE-PROOF)
START_DATE = "2025-01-01"
END_DATE   = "2025-12-01"

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

OUTPUT_FILE = DATA_DIR / "BTCUSDT_15m.csv"

print("CONFIG OK")

# ---------- CLIENT ----------
client = Client()  # No API key required
print("CLIENT CREATED")

# ---------- FETCH ----------
print("DOWNLOADING DATA...")
klines = client.get_historical_klines(
    SYMBOL,
    INTERVAL,
    START_DATE,
    END_DATE
)

print("KLINES FETCHED:", len(klines))

if not klines:
    raise RuntimeError("No data returned from Binance")

# ---------- FORMAT ----------
df = pd.DataFrame(klines, columns=[
    "timestamp", "open", "high", "low", "close", "volume",
    "close_time", "quote_asset_volume", "number_of_trades",
    "taker_buy_base", "taker_buy_quote", "ignore"
])

df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")

df = df[["timestamp", "open", "high", "low", "close"]]
df = df.astype({
    "open": float,
    "high": float,
    "low": float,
    "close": float
})

# ---------- SAVE ----------
df.to_csv(OUTPUT_FILE, index=False)
print(f"SAVED {len(df)} ROWS TO {OUTPUT_FILE}")
