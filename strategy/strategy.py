from datetime import time

class SessionBiasStrategy:
    def __init__(self):
        self.in_position = False
        self.side = None
        self.entry_price = None

        self.stop_pct = 0.005
        self.target_pct = 0.01

    # ---------- SESSION HELPERS ----------
    def _in_session(self, ts, start, end):
        t = ts.time()
        return start <= t <= end

    def _asia(self, ts):
        return self._in_session(ts, time(0, 0), time(6, 0))

    def _london(self, ts):
        return self._in_session(ts, time(7, 0), time(13, 0))

    def _ny(self, ts):
        return self._in_session(ts, time(13, 30), time(20, 0))

    # ---------- CORE LOGIC ----------
    def on_bar(self, ts, row, df_day):
        """
        Returns:
        - "BUY"
        - "SELL"
        - "EXIT"
        - None
        """

        # Trade only during New York session
        if not self._ny(ts):
            return None

        asia = df_day[df_day["session"] == "ASIA"]
        london = df_day[df_day["session"] == "LONDON"]

        if asia.empty or london.empty:
            return None

        asia_bias = 1 if asia.iloc[-1]["close"] > asia.iloc[0]["open"] else -1
        london_bias = 1 if london.iloc[-1]["close"] > london.iloc[0]["open"] else -1

        if asia_bias != london_bias:
            return None

        bias = "LONG" if asia_bias == 1 else "SHORT"

        price = row["close"]
        ema = row["ema20"]
        prev_price = row["prev_close"]

        # ---------- ENTRY ----------
        if not self.in_position:
            if bias == "LONG" and prev_price < ema and price > ema:
                self.in_position = True
                self.side = "BUY"
                self.entry_price = price
                return "BUY"

            if bias == "SHORT" and prev_price > ema and price < ema:
                self.in_position = True
                self.side = "SELL"
                self.entry_price = price
                return "SELL"

        # ---------- EXIT ----------
        else:
            if self.side == "BUY":
                if price <= self.entry_price * (1 - self.stop_pct) or \
                   price >= self.entry_price * (1 + self.target_pct):
                    self.in_position = False
                    return "EXIT"

            if self.side == "SELL":
                if price >= self.entry_price * (1 + self.stop_pct) or \
                   price <= self.entry_price * (1 - self.target_pct):
                    self.in_position = False
                    return "EXIT"

        return None
