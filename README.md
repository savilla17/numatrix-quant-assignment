\# Numatrix Quant Developer Assignment



\## Strategy Overview

This project implements a rule-based intraday trading strategy on BTCUSDT.

The strategy uses Asian and London session price behavior to define a

directional bias and executes trades only during the New York session.



The system is fully deterministic and designed to ensure parity between

backtesting and live execution.



---



\## Strategy Logic

1\. Asian session (00:00–06:00 UTC) bias is determined by open vs close.

2\. London session (07:00–13:00 UTC) bias is determined by open vs close.

3\. If Asian and London biases agree, trades are allowed in that direction.

4\. If they disagree, no trades are taken.

5\. Trades are executed only during the New York session (13:30–20:00 UTC).

6\. Entry is triggered using a 15-minute EMA pullback confirmation.

7\. Stop-loss and take-profit are static percentage-based exits.



---



\## Project Structure



