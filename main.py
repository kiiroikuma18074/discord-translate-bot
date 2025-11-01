import os
import discord
from discord import app_commands
from discord.ext import commands
from deep_translator import GoogleTranslator
from flask import Flask
from threading import Thread

# Flask サーバー (Renderの稼働維持用)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

def keep_alive():
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()

# Discord Bot設定
TOKEN = os.environ.get("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree  # スラッシュコマンド用

# -------------------------------
# メモリ的な簡易設定保持（Render再起動でリセット）
# -------------------------------
auto_translate_guilds = {}
user_languages = {}

# -------------------------------
# /auto コマンド
# -------------------------------
@tree.command(name="auto", description="自動翻訳をオン／オフします")
@app_commands.describe(mode="on または off")
async def auto(interaction: discord.Interaction, mode: str):
    guild_id = interaction.guild.id

    if mode.lower() == "on":
        auto_translate_
