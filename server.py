import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

# Çevre değişkenlerini yükle
load_dotenv()

# Discord Bot Token
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID", 0))  # Çevre değişkeninden INT olarak al

# API Anahtarını Kontrol Et
if not DISCORD_BOT_TOKEN:
    raise ValueError("ERROR: DISCORD_BOT_TOKEN bulunamadı! .env dosyanızı kontrol edin.")

# Discord Botu Başlat
intents = discord.Intents.default()
intents.message_content = True  # Mesaj içeriğini dinlemek için
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    """Bot başarıyla açıldığında çalışır."""
    print(f"✅ Bot aktif: {bot.user.name}")
    
    try:
        channel = bot.get_channel(CHANNEL_ID)
        if channel:
            await channel.send("🚀 Bot başarıyla başlatıldı!")
    except Exception as e:
        print(f"❌ Discord mesajı gönderilirken hata oluştu: {str(e)}")

@bot.command()
async def ping(ctx):
    """Ping komutu botun çalıştığını test eder."""
    try:
        await ctx.send("🏓 Pong!")
    except Exception as e:
        print(f"❌ Ping komutu çalıştırılırken hata oluştu: {str(e)}")

# Botu çalıştır
try:
    print("🚀 Discord botu başlatılıyor...")
    bot.run(DISCORD_BOT_TOKEN)
except Exception as e:
    print(f"❌ Bot başlatılırken hata oluştu: {str(e)}")
