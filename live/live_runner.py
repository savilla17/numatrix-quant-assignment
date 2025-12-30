print("LIVE FILE EXECUTED")

import time
import sys
from pathlib import Path
import pandas as pd
from datetime import datetime, timezone

# ---------- PATH SETUP ----------
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# ---------- IMPORTS ----------
from strategy.strategy import SessionBiasStrategy
from execution.binance_executor import BinanceExecutor
from config import load_env
from binance.client import Client

# ---------- CONFIG ----------
SYMBOL = "BTCUSDT"
INTERVAL = Client.KLINE_INTERVAL_15MINUTE
QTY = 0.001

LOG_FILE = ROOT / "live_trades.csv"

# ---------- INIT ----------
cfg = load_env()

strategy = SessionBiasStrategy()
executor = BinanceExecutor(
    cfg["BINANCE_API_KEY"],
    cfg["BINANCE_API_SECRET"],
    testnet=True
)

client = executor.client  # reuse same client

print("LIVE RUNNER STARTED")

# ---------- HELPERS ----------
def fetch_recent_klines(limit=100):
    klines = client.get_klines(
        symbol=SYMBOL,
        interval=INTERVAL,
        limit=limit
    )

    df = pd.DataFrame(klines, columns=[
        "timestamp", "open", "high", "low", "close", "volume",
        "close_time", "quote_asset_volume", "trades",
        "taker_buy_base", "taker_buy_quote", "ignore"
    ])

    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
    df.set_index("timestamp", inplace=True)

    df = df.astype({
        "open": float,
        "high": float,
        "low": float,
        "close": float
    })

    return df[["open", "high", "low", "close"]]


def wait_for_candle_close():
    now = datetime.now(timezone.utc)
    sleep_seconds = 900 - (now.minute % 15) * 60 - now.second
    time.sleep(max(sleep_seconds, 1))


# ---------- MAIN LOOP ----------
while True:
    try:
        print("Waiting for candle close...")
        wait_for_candle_close()

        df = fetch_recent_klines()
        df["ema20"] = df["close"].ewm(span=20, adjust=False).mean()
        df["prev_close"] = df["close"].shift(1)

        # Tag sessions
        def tag_session(ts):
            t = ts.time()
            if t <= datetime.strptime("06:00", "%H:%M").time():
                return "ASIA"
            if datetime.strptime("07:00", "%H:%M").time() <= t <= datetime.strptime("13:00", "%H:%M").time():
                return "LONDON"
            if datetime.strptime("13:30", "%H:%M").time() <= t <= datetime.strptime("20:00", "%H:%M").time():
                return "NY"
            return None

        df["session"] = df.index.map(tag_session)

        ts = df.index[-1]
        row = df.iloc[-1]
        day_df = df[df.index.date == ts.date()]

        signal = strategy.on_bar(ts, row, day_df)

        print(f"{ts} | SIGNAL: {signal}")

        if signal == "BUY":
            order = executor.buy_market(SYMBOL, QTY)
        elif signal == "SELL":
            order = executor.sell_market(SYMBOL, QTY)
        else:
            continue

        trade = {
            "timestamp": ts,
            "symbol": SYMBOL,
            "side": signal,
            "price": row["close"],
            "order_id": order["orderId"]
        }

        pd.DataFrame([trade]).to_csv(
            LOG_FILE,
            mode="a",
            header=not LOG_FILE.exists(),
            index=False
        )

        print("TRADE EXECUTED:", trade)

    except Exception as e:
        print("ERROR:", e)
        time.sleep(30)
