import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


from ta.trend import SMAIndicator, MACD
from ta.momentum import RSIIndicator


SYMBOL = "BTC-USD"     

START_DATE = "2022-01-01"

print(f"Downloading {SYMBOL} data...")

df = yf.download(
    SYMBOL,
    start=START_DATE,
    auto_adjust=True
)

if len(df) == 0:
    raise Exception("No data found.")

if isinstance(df.columns, pd.MultiIndex):
  
    new_columns = []
    for col in df.columns:
        if isinstance(col, tuple):
            
            if len(col) == 2 and col[0] in ['Price', 'Volume', 'Adj Close', 'Close', 'High', 'Low', 'Open'] and col[1] == SYMBOL: 
                new_columns.append(col[0])
            elif len(col) == 2 and col[0] in ['Price', 'Volume'] and col[1] in ['Close', 'High', 'Low', 'Open', 'Adj Close'] : 
                new_columns.append(col[1])
            else:
                new_columns.append('_'.join(map(str, col)).strip('_')) 
        else:
            new_columns.append(str(col))
    df.columns = new_columns





close = df["Close"]

df["SMA20"] = SMAIndicator(
    close=close,
    window=20
).sma_indicator()


df["SMA50"] = SMAIndicator(
    close=close,
    window=50
).sma_indicator()


df["RSI"] = RSIIndicator(
    close=close,
    window=14
).rsi()


macd = MACD(close=close)

df["MACD"] = macd.macd()
df["MACD_SIGNAL"] = macd.macd_signal()




signals = []

for i in range(len(df)):

    if pd.isna(df["RSI"].iloc[i]):
        signals.append("HOLD")
        continue

    rsi = df["RSI"].iloc[i]

    sma20 = df["SMA20"].iloc[i]
    sma50 = df["SMA50"].iloc[i]

    if pd.isna(sma20) or pd.isna(sma50):
        signals.append("HOLD")
        continue

  
    if rsi < 30 and sma20 > sma50:
        signals.append("BUY")

    
    elif rsi > 70 and sma20 < sma50:
        signals.append("SELL")

    else:
        signals.append("HOLD")

df["Signal"] = signals


latest = df.iloc[-1]

print("\n===== LATEST ANALYSIS =====")
print(f"Symbol: {SYMBOL}")

print(f"Close: {float(latest['Close']):.2f}")
print(f"RSI: {float(latest['RSI']):.2f}")
print(f"SMA20: {float(latest['SMA20']):.2f}")
print(f"SMA50: {float(latest['SMA50']):.2f}")
print(f"Signal: {latest['Signal']}")

plt.figure(figsize=(14, 8))

plt.subplot(3, 1, 1)

plt.plot(
    df.index,
    df["Close"], 
    label="Close Price"
)

plt.plot(
    df.index,
    df["SMA20"],
    label="SMA20"
)

plt.plot(
    df.index,
    df["SMA50"],
    label="SMA50"
)

plt.title(f"{SYMBOL} Price")
plt.legend()


plt.subplot(3, 1, 2)

plt.plot(
    df.index,
    df["RSI"],
    label="RSI"
)

plt.axhline(
    70,
    linestyle="--"
)

plt.axhline(
    30,
    linestyle="--"
)

plt.title("RSI")
plt.legend()


plt.subplot(3, 1, 3)

plt.plot(
    df.index,
    df["MACD"],
    label="MACD"
)

plt.plot(
    df.index,
    df["MACD_SIGNAL"],
    label="Signal"
)

plt.title("MACD")
plt.legend()

plt.tight_layout()
plt.show()


print("\n===== LAST 10 SIGNALS =====")

print(
    df[
        ["Close", "RSI", "Signal"]
    ].tail(10)
)
