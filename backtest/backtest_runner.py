import pandas as pd
import sys
from pathlib import Path

print("BACKTEST STARTED")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

print("ROOT PATH:", ROOT)

from strategy.strategy import SessionBiasStrategy
print("STRATEGY IMPORTED")

# ---------- LOAD DATA ----------
DATA_PATH = ROOT / "data" / "BTCUSDT_15m.csv"
print("DATA PATH:", DATA_PATH)

df = pd.read_csv(DATA_PATH, parse_dates=["timestamp"])
print("DATA LOADED:", len(df))

df.set_index("timestamp", inplace=True)
df.sort_index(inplace=True)

# ---------- FEATURES ----------
df["ema20"] = df["close"].ewm(span=20, adjust=False).mean()
df["prev_close"] = df["close"].shift(1)

print("FEATURES CALCULATED")

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
print("SESSIONS TAGGED")

# ---------- BACKTEST ----------
strategy = SessionBiasStrategy()
trades = []
current_trade = {}

print("STARTING LOOP")

for ts, row in df.iterrows():
    day_df = df[df.index.date == ts.date()]
    signal = strategy.on_bar(ts, row, day_df)

    if signal in ["BUY", "SELL"]:
        current_trade = {
            "entry_time": ts,
            "side": signal,
            "entry_price": row["close"]
        }
        print("ENTRY:", current_trade)

    if signal == "EXIT" and current_trade:
        current_trade["exit_time"] = ts
        current_trade["exit_price"] = row["close"]
        trades.append(current_trade)
        print("EXIT:", current_trade)
        current_trade = {}

print("LOOP FINISHED")

# ---------- SAVE ----------
out = ROOT / "backtest_trades.csv"
pd.DataFrame(trades).to_csv(out, index=False)

print(f"BACKTEST COMPLETE. TRADES: {len(trades)}")
print("SAVED TO:", out)
