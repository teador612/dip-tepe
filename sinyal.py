import numpy as np
import yfinance as yf
import pandas as pd
from scipy.signal import argrelextrema
import requests
import os

# Ortam değişkenlerinden token ve chat ID al
BOT_TOKEN = '7829367094:AAGSG5ofZ6Cz6s7myex5Ad_hVLHYKVr0bHI'
CHAT_ID = '906816135'

# Hisse listesi
symbols = ["ADEL.IS", "AEFES.IS", "AGHOL.IS", "AGROT.IS", "AHGAZ.IS",
    "AKBNK.IS", "AKCNS.IS", "AKFGY.IS", "AKFYE.IS", "AKSA.IS",
    "AKSEN.IS", "ALARK.IS", "ALBRK.IS", "ALFAS.IS", "ALTNY.IS",
    "ANSGR.IS", "ARCLK.IS", "ARDYZ.IS", "ASELS.IS", "ASTOR.IS",
    "BERA.IS", "BFREN.IS", "BIENY.IS", "BIMAS.IS", "BINHO.IS",
    "BIOEN.IS", "BJKAS.IS", "BOBET.IS", "BRSAN.IS", "BRYAT.IS",
    "BTCIM.IS", "CANTE.IS", "CCOLA.IS", "CIMSA.IS", "CLEBI.IS",
    "CWENE.IS", "DOAS.IS", "DOHOL.IS", "ECILC.IS", "ECZYT.IS",
    "EGEEN.IS", "EKGYO.IS", "ENERY.IS", "ENJSA.IS", "ENKAI.IS",
    "EREGL.IS", "EUPWR.IS", "EUREN.IS", "FENER.IS", "FROTO.IS",
    "GARAN.IS", "GESAN.IS", "GOLTS.IS", "GUBRF.IS", "GWIND.IS",
    "HALKB.IS", "HEKTS.IS", "IPEKE.IS", "ISGYO.IS", "ISMEN.IS",
    "IZENR.IS", "KARSN.IS", "KAYSE.IS", "KCAER.IS", "KCHOL.IS",
    "KLSER.IS", "KONTR.IS", "KONYA.IS", "KOZAA.IS", "KOZAL.IS",
    "KTLEV.IS", "LMKDC.IS", "MAVI.IS", "MGROS.IS", "MIATK.IS",
    "MPARK.IS", "OBAMS.IS", "ODAS.IS", "OTKAR.IS", "OYAKC.IS",
    "PAPIL.IS", "PEKGY.IS", "PETKM.IS", "PGSUS.IS", "QUAGR.IS",
    "REEDR.IS", "RGYAS.IS", "SAHOL.IS", "SASA.IS", "SAYAS.IS",
    "SDTTR.IS", "SISE.IS", "SMRTG.IS", "SOKM.IS", "TABGD.IS",
    "TAVHL.IS", "TCELL.IS", "THYAO.IS", "TKFEN.IS", "TKNSA.IS",
    "TMSN.IS", "TOASO.IS", "TTKOM.IS", "TTRAK.IS", "TUKAS.IS",
    "TUPRS.IS", "TURSG.IS", "ULKER.IS", "VESBE.IS", "VESTL.IS",
    "YEOTK.IS", "YYLGD.IS", "ZOREN.IS"]

# Veri çekme fonksiyonu
def get_data(symbol, period='12mo', interval='1w'):
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
