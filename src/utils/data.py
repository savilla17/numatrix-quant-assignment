import pandas as pd
from pathlib import Path

def load_csv(path: Path, parse_dates=None) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Data file not found: {path}")

    df = pd.read_csv(path, parse_dates=parse_dates)
    return df


def resample_ohlc(df: pd.DataFrame, timeframe: str) -> pd.DataFrame:
    return df.resample(timeframe).agg({
        "open": "first",
        "high": "max",
        "low": "min",
        "close": "last"
    }).dropna()
