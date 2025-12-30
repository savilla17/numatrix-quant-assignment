import pandas as pd
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from strategy.strategy import SessionBiasStrategy

# ---------- LOAD DATA ----------
df = pd.read_csv(
    "data/BTCUSDT_15m.csv",
    parse_dates=["timestamp"]
)

df.set_index("timestamp", inplace=True)
df.sort_index(inplace=True)

# ---------- FEATURES ----------
df["ema20"] = df["close"].ewm(span=20, adjust=False).mean()
df["prev_close"] = df["close"].shift(1)

# ---------- SESSION TAG ----------
def tag_session(ts):
    t = ts.time()
    if t >= pd.Timestamp("00:00").time() and t <= pd.Timestamp("06:00").time():
        return "ASIA"
    if t >= pd.Timestamp("07:00").time() and t <= pd.Timestamp("13:00").time():
        return "LONDON"
    if t >= pd.Timestamp("13:30").time() and t <= pd.Timestamp("20:00").time():
        return "NY"
    return None

df["session"] = df.index.map(tag_session)

# ---------- BACKTEST ----------
strategy = SessionBiasStrategy()
trades = []
current_trade = {}

for ts, row in df.iterrows():
    day_df = df[df.index.date == ts.date()]
    signal = strategy.on_bar(ts, row, day_df)

    if signal in ["BUY", "SELL"]:
        current_trade = {
            "entry_time": ts,
            "side": signal,
            "entry_price": row["close"]
        }

    if signal == "EXIT" and current_trade:
        current_trade["exit_time"] = ts
        current_trade["exit_price"] = row["close"]
        trades.append(current_trade)
        current_trade = {}

# ---------- SAVE ----------
pd.DataFrame(trades).to_csv("backtest_trades.csv", index=False)
print("Backtest complete. Trades:", len(trades))
