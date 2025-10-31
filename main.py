import os
import discord
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "I'm alive!"  # 動作確認用メッセージ

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

from discord.ext import commands

TOKEN = os.getenv("DISCORD_BOT_TOKEN")  # ← Render の環境変数を取得

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

bot.run(TOKEN)

# 翻訳対象言語（日本語、英語、中国語、韓国語、スペイン語、ベトナム語）

TARGET_LANGUAGES = ["ja", "en", "zh-CN", "ko", "es", "vi"]

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"ログインしました: {bot.user}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # 翻訳して送信
    for lang in TARGET_LANGUAGES:
        translated = GoogleTranslator(source='auto', target=lang).translate(message.content)
        await message.channel.send(f"[{lang}] {translated}")

    await bot.process_commands(message)
keep_alive()
bot.run(TOKEN)

import os
import discord
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "I'm alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

from discord.ext import commands

# Renderの環境変数からトークンを取得
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

# Flaskを起動してRenderを維持
keep_alive()

# Discord botを起動
bot.run(TOKEN)
