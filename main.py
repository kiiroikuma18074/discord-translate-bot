import os
import discord
from discord.ext import commands 
from discord import app_commands
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
tree = app_commands.CommandTree(bot)

# 翻訳対象言語リスト
TARGET_LANGUAGES = ["ja", "en", "zh-CN", "ko", "es", "vi"]
server_settings = {}  # {guild_id: {"auto": True, "languages": ["en", "ja"]}}

@bot.event
async def on_ready():
    print(f"✅ ログインしました: {bot.user}")
    try:
        synced = await tree.sync()
        print(f"🟢 スラッシュコマンド {len(synced)} 件を同期しました。")
    except Exception as e:
        print(f"❌ コマンド同期エラー: {e}")

# --- メッセージ自動翻訳 ---
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    guild_id = message.guild.id if message.guild else None
    settings = server_settings.get(guild_id, {"auto": True, "languages": TARGET_LANGUAGES})

    if not settings["auto"]:
        await bot.process_commands(message)
        return

    for lang in settings["languages"]:
        translated = GoogleTranslator(source='auto', target=lang).translate(message.content)
        await message.channel.send(f"[{lang}] {translated}")

    await bot.process_commands(message)

# --- /auto コマンド ---
@tree.command(name="auto", description="自動翻訳のオンオフを切り替えます")
async def auto(interaction: discord.Interaction, mode: str = None):
    guild_id = interaction.guild.id
    settings = server_settings.get(guild_id, {"auto": True, "languages": TARGET_LANGUAGES})

    if mode is None:
        await interaction.response.send_message(
            f"現在の状態: {'ON' if settings['auto'] else 'OFF'}\n使い方: `/auto on` または `/auto off`"
        )
        return

    if mode.lower() == "on":
        settings["auto"] = True
        await interaction.response.send_message("✅ 自動翻訳を **ON** にしました。")
    elif mode.lower() == "off":
        settings["auto"] = False
        await interaction.response.send_message("🛑 自動翻訳を **OFF** にしました。")
    else:
        await interaction.response.send_message("使い方: `/auto on` または `/auto off`")

    server_settings[guild_id] = settings

# --- /lang コマンド ---
@tree.command(name="lang", description="翻訳対象の言語を変更します（例：/lang en ja）")
async def lang(interaction: discord.Interaction, *langs: str):
    guild_id = interaction.guild.id
    if not langs:
        await interaction.response.send_message(
            "使い方: `/lang en ja ko` のように指定してください。\n使用中の言語コード一覧: en, ja, zh-CN, ko, es, vi"
        )
        return

    server_settings[guild_id] = server_settings.get(guild_id, {"auto": True})
    server_settings[guild_id]["languages"] = list(langs)

    await interaction.response.send_message(f"🌐 翻訳対象言語を次に設定しました: {', '.join(langs)}")

# --- 起動 ---
keep_alive()
bot.run(TOKEN)
