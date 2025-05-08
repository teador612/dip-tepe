!pip install yfinance requests --quiet
import yfinance as yf
import pandas as pd
import numpy as np
from scipy.stats import linregress
import requests

# Telegram Bot Token ve Chat ID
BOT_TOKEN = '7829367094:AAGSG5ofZ6Cz6s7myex5Ad_hVLHYKVr0bHI'
CHAT_ID = '906816135'

# Telegram mesaj gönderme fonksiyonu
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={message}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print("✅ Telegram mesajı gönderildi.")
        else:
            print(f"❌ Mesaj gönderilemedi. Hata: {response.status_code}")
    except Exception as e:
        print(f"❌ Telegram mesajı gönderilemedi. Hata: {e}")

# İzlenecek BIST hisseleri
tickers = ["ADEL.IS", "AEFES.IS", "AGHOL.IS", "AGROT.IS", "AHGAZ.IS",
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

# Parametreler
length = 100       # Regresyon uzunluğu
dev = 2            # Standart sapma katsayısı
interval = '1h'    # Saatlik periyot
period = '30d'     # Son 30 gün

# BUY sinyali kontrol fonksiyonu
def check_buy_signal(ticker):
    try:
        df = yf.download(ticker, interval=interval, period=period, progress=False)
        if len(df) < length + 2:
            return None
        close = df['Close']
        y = close[-length:]
        x = np.arange(length)
        slope, intercept, _, _, _ = linregress(x, y)
        reg_line = slope * x + intercept
        deviation = np.std(y - reg_line)
        lower_band = reg_line[-1] - dev * deviation
        current_price = close.iloc[-1]
        prev_price = close.iloc[-2]

        # Fiyat alt bandını yukarı kesiyorsa (en son mumda)
        if prev_price > lower_band and current_price < lower_band:
            return ticker
    except Exception as e:
        print(f"❌ {ticker} hata: {e}")
        return None

# Tarama işlemi
buy_signals = []

for ticker in tickers:
    print(f"🔍 Taranıyor: {ticker}")
    result = check_buy_signal(ticker)
    if result:
        buy_signals.append(result)

# Sonuçları Telegram'a gönder
if buy_signals:
    message = "📈 BUY Sinyali Veren Hisseler:\n" + "\n".join(buy_signals)
    send_telegram_message(message)
else:
    send_telegram_message("🚫 BUY sinyali veren hisse bulunamadı.")
