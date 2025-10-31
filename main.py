import os
import re
import discord
from discord.ext import commands
from discord import app_commands
from deep_translator import GoogleTranslator
from flask import Flask
from threading import Thread

# --- Flask サーバー（Render維持用） ---
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
server_settings = {}  # 各サーバー設定を保存
TARGET_LANGUAGES = ["ja", "en", "zh-CN", "ko", "es", "vi"]


# --- Bot起動時イベント ---
@bot.event
async def on_ready():
    print(f"✅ ログインしました: {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"🟢 スラッシュコマンド同期済み: {len(synced)}個")
    except Exception as e:
        print(f"❌ コマンド同期エラー: {e}")


# --- メッセージ受信イベント ---
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    guild_id = message.guild.id if message.guild else None
    settings = server_settings.get(guild_id, {"auto": True, "languages": TARGET_LANGUAGES})

    # 自動翻訳がOFFの場合は無視
    if not settings["auto"]:
        await bot.process_commands(message)
        return

    # 絵文字とURLを保持しつつ翻訳
    text = message.content
    emoji_pattern = r"(<:[a-zA-Z0-9_]+:[0-9]+>|[\U0001F300-\U0001F6FF\u2600-\u26FF\u2700-\u27BF])"
    emojis = re.findall(emoji_pattern, text)
    clean_text = re.sub(emoji_pattern, "", text)

    if clean_text.strip():
        for lang in settings["languages"]:
            try:
                translated = GoogleTranslator(source='auto', target=lang).translate(clean_text)
                result = f"[{lang}] {translated} {' '.join(emojis)}"
                awa
