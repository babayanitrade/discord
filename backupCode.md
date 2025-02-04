from flask import Flask, request, jsonify, render_template
import discord
from discord.ext import commands
import asyncio
import ast
from binance.client import Client
import os
from dotenv import load_dotenv
from threading import Thread
import logging

# Çevre değişkenlerini yükle
load_dotenv()

# API Anahtarlarını Al
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
TOKEN_BINANCEFIRST = os.getenv("TOKEN_BINANCEFIRST")
TOKEN_BINANCESECOND = os.getenv("TOKEN_BINANCESECOND")
CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID", 0))  # Çevre değişkeninden INT olarak al

# API Anahtarlarını Kontrol Et
if not DISCORD_BOT_TOKEN:
    raise ValueError("ERROR: DISCORD_BOT_TOKEN bulunamadı! .env dosyanızı kontrol edin.")
if not TOKEN_BINANCEFIRST or not TOKEN_BINANCESECOND:
    raise ValueError("ERROR: Binance API anahtarları eksik! .env dosyanızı kontrol edin.")

# Flask Uygulamasını Başlat
app = Flask(__name__)

# Binance API Bağlantısı
client = Client(TOKEN_BINANCEFIRST, TOKEN_BINANCESECOND, testnet=True)

# Discord Botu Başlat
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# Gelen istekleri saklamak için bir liste
requests_log = []

@app.route('/')
def home():
    """Ana sayfa: Gelen istekleri liste olarak göster."""
    print("Gelen İstekler:", requests_log)
    return render_template("index.html", logs=requests_log)

# ---------------------- DISCORD BOT OLAYLARI ---------------------- #

@bot.event
async def on_ready():
    """Bot başarıyla açıldığında çalışır."""
    print(f"✅ Bot aktif: {bot.user.name}")
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        await channel.send("🚀 Bot başarıyla başlatıldı!")

async def send_discord_message(message):
    """Discord kanalına mesaj göndermek için yardımcı fonksiyon."""
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        await channel.send(message)

# ---------------------- FLASK WEBHOOK ---------------------- #

@app.route('/webhook', methods=['POST'])
def webhook():
    """Webhook POST isteğini işler."""
    try:
        print("=== Yeni Webhook ===")
        print("Headers:", request.headers)
        print("Body (raw):", request.data)

        raw_data = request.data.decode('utf-8')

        # JSON verisini güvenli bir şekilde ayrıştır
        try:
            data = ast.literal_eval(raw_data)
        except (ValueError, SyntaxError) as e:
            print(f"❌ JSON Ayrıştırma Hatası: {e}")
            return jsonify({"success": False, "message": "Geçersiz JSON formatı"}), 400

        print("İşlenen Veri:", data)

        if data:
            action = data.get("action")
            symbol = data.get("symbol")
            amount = data.get("amount")

            # Web arayüzünde gösterilecek veriyi sakla
            requests_log.insert(0, {
                "action": action,
                "symbol": symbol,
                "amount": amount,
                "headers": dict(request.headers),
                "body": data
            })

            if action == "BUY":
                order = client.order_market_buy(symbol=symbol, quantity=amount)
                balance = client.get_asset_balance(asset="XRP")  # Sembolü çıkart
                message = f"📈 **ALIM EMRİ**\nBakiye: {balance}\nSembol: {symbol}\nMiktar: {amount}"
                asyncio.run_coroutine_threadsafe(send_discord_message(message), bot.loop)

            elif action == "SELL":
                order = client.order_market_sell(symbol=symbol, quantity=amount)
                balance = client.get_asset_balance(asset="XRP")  # Sembolü çıkart
                message = f"📉 **SATIM EMRİ**\nBakiye: {balance}\nSembol: {symbol}\nMiktar: {amount}"
                asyncio.run_coroutine_threadsafe(send_discord_message(message), bot.loop)

        return jsonify({"success": True, "message": "Webhook başarıyla işlendi."})

    except Exception as e:
        print(f"❌ Hata: {str(e)}")
        return jsonify({"success": False, "message": str(e)}), 400

# ---------------------- ÇOKLU THREAD ÇALIŞTIRICI ---------------------- #

def run_bot():
    """Discord botunu çalıştırmak için bir iş parçacığı (thread) aç."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(bot.start(DISCORD_BOT_TOKEN))
    except asyncio.CancelledError:
        pass  # Program kapanırken hataları önlemek için
    finally:
        loop.run_until_complete(bot.close())

def run_flask():
    """Flask uygulamasını başlatır."""
    app.run(host="0.0.0.0", port=8080, use_reloader=False)  # Yeniden yükleme kapalı

# ---------------------- ANA GİRİŞ NOKTASI ---------------------- #

if __name__ == "__main__":
    # Flask ve Discord botunu farklı iş parçacıklarında çalıştır
    bot_thread = Thread(target=run_bot, daemon=True)
    flask_thread = Thread(target=run_flask, daemon=True)

    # İş parçacıklarını başlat
    bot_thread.start()
    flask_thread.start()

    try:
        # Program çalışırken bekleyelim
        while True:
            pass
    except KeyboardInterrupt:
        print("\nÇıkış yapılıyor...")
        os._exit(0)  # Tüm işlemleri anında kapat
