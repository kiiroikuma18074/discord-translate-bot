# main.py
import os
import discord
from discord import option
from discord.ext import commands
from deep_translator import GoogleTranslator
from flask import Flask
from threading import Thread

# ===== Flask (keep alive for Render) =====
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

# ===== Discord Bot =====
TOKEN = os.environ.get("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(intents=intents)

TARGET_LANGUAGES = ["ja", "en", "zh-CN", "ko", "es", "vi"]
server_settings = {}

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"✅ Logged in as {bot.user}")

# ===== メッセージ翻訳機能 =====
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    guild_id = message.guild.id if message.guild else None
    settings = server_settings.get(guild_id, {"auto": True, "languages": TARGET_LANGUAGES})

    if not settings["auto"]:
        return

    for lang in settings["languages"]:
        try:
            translated = GoogleTranslator(source='auto', target=lang).translate(message.content)
        except Exception:
            translated = f"[{lang}] 翻訳エラー"
        await message.channel.send(f"[{lang}] {translated}")

# ===== スラッシュコマンド =====
@bot.tree.command(name="auto", description="自動翻訳をオン/オフします")
@option("mode", description="on または off", required=False)
async def auto(interaction: discord.Interaction, mode: str = None):
    guild_id = interaction.guild.id
    settings = server_settings.get(guild_id, {"auto": True, "languages": TARGET_LANGUAGES})

    if mode is None:
        status = "ON" if settings["auto"] else "OFF"
        await interaction.response.send_message(f"現在の状態: {status}\n使い方: `/auto on` または `/auto off`")
        return

    if mode.lower() == "on":
        settings["auto"] = True
        await interaction.response.send_message("✅ 自動翻訳を ON にしました。")
    elif mode.lower() == "off":
        settings["auto"] = False
        await interaction.response.send_message("🛑 自動翻訳を OFF にしました。")
    else:
        await interaction.response.send_message("使い方: `/auto on` または `/auto off`")

    server_settings[guild_id] = settings

@bot.tree.command(name="lang", description="翻訳対象言語を設定します")
@option("languages", description="例: en ja ko など（スペース区切り）", required=True)
async def lang(interaction: discord.Interaction, languages: str):
    guild_id = interaction.guild.id
    langs = languages.split()

    server_settings[guild_id] = server_settings.get(guild_id, {"auto": True})
    server_settings[guild_id]["languages"] = langs

    await interaction.response.send_message(f"翻訳対象言語を設定しました: {', '.join(langs)}")

# ===== 起動 =====
if __name__ == "__main__":
    keep_alive()
    bot.run(TOKEN)
