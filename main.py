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

# 翻訳対象言語リスト
TARGET_LANGUAGES = ["ja", "en", "zh-CN", "ko", "es", "vi"]

# サーバーごとの設定を保存
server_settings = {}  # {guild_id: {"auto": True, "languages": ["en", "ja"]}}


@bot.event
async def on_ready():
    print(f"✅ ログインしました: {bot.user}")


@bot.event
async def on_message(message):
    if message.author.bot:
        return

    guild_id = message.guild.id if message.guild else None
    settings = server_settings.get(guild_id, {"auto": True, "languages": TARGET_LANGUAGES})

    # 自動翻訳OFFなら無視
    if not settings["auto"]:
        await bot.process_commands(message)
        return

    # 翻訳を実行
    for lang in settings["languages"]:
        translated = GoogleTranslator(source='auto', target=lang).translate(message.content)
        await message.channel.send(f"[{lang}] {translated}")

    await bot.process_commands(message)


# --- コマンド ---
@bot.command()
async def auto(ctx, mode: str = None):
    """自動翻訳のオンオフを切り替えます"""
    guild_id = ctx.guild.id
    settings = server_settings.get(guild_id, {"auto": True, "languages": TARGET_LANGUAGES})

    if mode is None:
        await ctx.send(f"現在の状態: {'ON' if settings['auto'] else 'OFF'}\n使い方: `!auto on` または `!auto off`")
        return

    if mode.lower() == "on":
        settings["auto"] = True
        await ctx.send("✅ 自動翻訳を **ON** にしました。")
    elif mode.lower() == "off":
        settings["auto"] = False
        await ctx.send("🛑 自動翻訳を **OFF** にしました。")
    else:
        await ctx.send("使い方: `!auto on` または `!auto off`")

    server_settings[guild_id] = settings


@bot.command()
async def lang(ctx, *langs):
    """翻訳対象の言語を変更します（例：!lang en ja）"""
    guild_id = ctx.guild.id
    if not langs:
        await ctx.send("使い方: `!lang en ja ko` のように指定してください。\n使用中の言語コード一覧: en, ja, zh-CN, ko, es, vi")
        return

    server_settings[guild_id] = server_settings.get(guild_id, {"auto": True})
    server_settings[guild_id]["languages"] = list(langs)

    await ctx.send(f"🌐 翻訳対象言語を次に設定しました: {', '.join(langs)}")


# --- 起動 ---
keep_alive()
bot.run(TOKEN)
