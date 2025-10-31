import os
import discord
from flask import Flask
from threading import Thread
from discord.ext import commands
from deep_translator import GoogleTranslator

# Flask アプリ（Render のポート維持用）
app = Flask('')

@app.route('/')
def home():
    return "I'm alive!"  # 動作確認用メッセージ

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# Discord Bot 設定
TOKEN = os.getenv("DISCORD_BOT_TOKEN")  # Render の環境変数からトークン取得

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# 起動時のメッセージ
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

# 翻訳対象言語
TARGET_LANGUAGES = ["ja", "en", "zh-CN", "ko", "es", "vi"]

# メッセージ受信時の処理
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    for lang in TARGET_LANGUAGES:
        translated = GoogleTranslator(source='auto', target=lang).translate(message.content)
        await message.channel.send(f"[{lang}] {translated}")

    await bot.process_commands(message)

# Flaskを起動してRenderのスリープを防止
keep_alive()

# Discord Botを起動
bot.run(TOKEN)
