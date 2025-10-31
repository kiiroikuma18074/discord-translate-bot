import os
import discord
from discord.ext import commands
from deep_translator import GoogleTranslator
from flask import Flask
from threading import Thread

# Flask サーバー (Render維持用)
app = Flask('')

@app.route('/')
def home():
    return "I'm alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()


# --- Discord Bot 設定 ---
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# 対象言語リスト
TARGET_LANGUAGES = ["ja", "en", "zh-CN", "ko", "es", "vi"]

@bot.event
async def on_ready():
    print(f"✅ ログインしました: {bot.user}")

@bot.event
async def on_message(message):
    # Bot自身のメッセージを無視
    if message.author.bot:
        return

    # 翻訳処理
    for lang in TARGET_LANGUAGES:
        translated = GoogleTranslator(source='auto', target=lang).translate(message.content)
        await message.channel.send(f"[{lang}] {translated}")

    # 他のコマンドを通すため
    await bot.process_commands(message)


# --- 起動 ---
keep_alive()
bot.run(TOKEN)
