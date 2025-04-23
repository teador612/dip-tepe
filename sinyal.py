import numpy as np
import yfinance as yf
import pandas as pd
from scipy.signal import argrelextrema
import requests
import os

# Ortam değişkenlerinden token ve chat ID al
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Hisse listesi
symbols = ["ADEL.IS", "AEFES.IS", "AGHOL.IS", "AGROT.IS", "AHGAZ.IS", "AKBNK.IS", "AKCNS.IS"]

# Veri çekme fonksiyonu
def get_data(symbol, period='6mo', interval='1d'):
    df = yf.download(symbol, period=period, interval=interval, auto_adjust=True, progress=False)
    df.dropna(inplace=True)
    return df

# Dip ve tepe tespiti (son mum için)
def detect_last_extrema(df, symbol):
    close = df['Close']
    last_index = len(df) - 1

    price_lows = argrelextrema(close.values, np.less_equal, order=3)[0]
    price_highs = argrelextrema(close.values, np.greater_equal, order=3)[0]

    result = None
    if last_index in price_lows:
        result = ("Alış", df.index[last_index].date(), close.iloc[last_index].item())
    elif last_index in price_highs:
        result = ("Satış", df.index[last_index].date(), close.iloc[last_index].item())

    return result

# Telegram'a mesaj gönderme
def send_telegram_message(message):
    if not BOT_TOKEN or not CHAT_ID:
        print("❌ Telegram bilgileri eksik.")
        return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    requests.post(url, data=payload)

# Sinyal tablosunu oluştur
signal_data = []

for symbol in symbols:
    df = get_data(symbol)
    if not df.empty:
        signal = detect_last_extrema(df, symbol)
        if signal:
            sinyal_tipi, tarih, fiyat = signal
            signal_data.append((symbol, sinyal_tipi, tarih, fiyat))

# Telegram mesajı oluştur ve gönder
if signal_data:
    message = "<b>📊 Güncel Sinyaller:</b>\n\n"
    for symbol, tip, tarih, fiyat in signal_data:
        message += f"• <b>{symbol}</b> - <i>{tip}</i> - {tarih} - {fiyat:.2f} ₺\n"
else:
    message = "⚠️ Bugün için dip/tepe sinyali yok."

send_telegram_message(message)
