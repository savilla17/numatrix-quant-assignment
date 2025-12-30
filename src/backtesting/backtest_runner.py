import pandas as pd
import numpy as np
import sys
from pathlib import Path

print("BACKTEST STARTED")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from strategy.strategy import SessionBiasStrategy

# ================= CONFIG =================
INITIAL_CAPITAL = 100_000.0   # INR
RISK_PCT = 0.01               # 1% per trade
POINT_VALUE = 1.0             # BTCUSDT linear assumption

# ================= LOAD DATA =================
DATA_PATH = ROOT / "data" / "BTCUSDT_15m.csv"
df = pd.read_csv(DATA_PATH, parse_dates=["timestamp"])
df.set_index("timestamp", inplace=True)
df.sort_index(inplace=True)

# ================= FEATURES =================
df["ema20"] = df["close"].ewm(span=20, adjust=False).mean()
df["prev_close"] = df["close"].shift(1)

# ================= SESSION TAG =================
def tag_session(ts):
    t = ts.time()
    if t <= pd.Timestamp("06:00").time():
        return "ASIA"
    if pd.Timestamp("07:00").time() <= t <= pd.Timestamp("13:00").time():
        return "LONDON"
    if pd.Timestamp("13:30").time() <= t <= pd.Timestamp("20:00").time():
        return "NY"
    return None

df["session"] = df.index.map(tag_session)

# ================= BACKTEST =================
strategy = SessionBiasStrategy()

capital = INITIAL_CAPITAL
equity_curve = []
trades = []

current_trade = None

for ts, row in df.iterrows():
    day_df = df[df.index.date == ts.date()]
    signal = strategy.on_bar(ts, row, day_df)

    price = row["close"]

    # -------- ENTRY --------
    if signal in ["BUY", "SELL"] and current_trade is None:
        risk_amount = capital * RISK_PCT

        stop_price = (
            price * (1 - strategy.stop_pct)
            if signal == "BUY"
            else price * (1 + strategy.stop_pct)
        )

        risk_per_unit = abs(price - stop_price)
        position_size = risk_amount / risk_per_unit

        current_trade = {
            "entry_time": ts,
            "side": signal,
            "entry_price": price,
            "position_size": position_size,
            "capital_before": capital
        }

    # -------- EXIT --------
    if signal == "EXIT" and current_trade:
        pnl = (
            (price - current_trade["entry_price"]) * current_trade["position_size"]
            if current_trade["side"] == "BUY"
            else (current_trade["entry_price"] - price) * current_trade["position_size"]
        )

        capital += pnl

        trade = {
            **current_trade,
            "exit_time": ts,
            "exit_price": price,
            "pnl": pnl,
            "capital_after": capital,
            "return_pct": pnl / current_trade["capital_before"]
        }

        trades.append(trade)
        current_trade = None

    equity_curve.append({"timestamp": ts, "equity": capital})

# ================= RESULTS =================
trades_df = pd.DataFrame(trades)
equity_df = pd.DataFrame(equity_curve).set_index("timestamp")

# ---------- METRICS ----------
returns = trades_df["return_pct"]

metrics = {
    "initial_capital": INITIAL_CAPITAL,
    "final_capital": capital,
    "total_trades": len(trades_df),
    "wins": int((trades_df["pnl"] > 0).sum()),
    "losses": int((trades_df["pnl"] <= 0).sum()),
    "win_rate": (trades_df["pnl"] > 0).mean() if len(trades_df) else 0,
    "net_pnl": trades_df["pnl"].sum(),
    "avg_return": returns.mean() if len(returns) else 0,
    "z_score": (returns.mean() / returns.std()) if returns.std() != 0 else 0,
    "sharpe": (returns.mean() / returns.std()) * np.sqrt(252) if returns.std() != 0 else 0,
    "max_drawdown": ((equity_df["equity"].cummax() - equity_df["equity"]) /
                     equity_df["equity"].cummax()).max()
}

# ================= SAVE =================
OUTPUT_DIR = ROOT / "results"
OUTPUT_DIR.mkdir(exist_ok=True)

trades_df.to_csv(OUTPUT_DIR / "backtest_trades.csv", index=False)
equity_df.to_csv(OUTPUT_DIR / "equity_curve.csv")
pd.Series(metrics).to_csv(OUTPUT_DIR / "metrics.csv")

print("BACKTEST COMPLETE")
print(metrics)
