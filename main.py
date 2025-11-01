import os
import discord
from discord.ext import commands
from deep_translator import GoogleTranslator
from flask import Flask
from threading import Thread

# ===== Flask: ヘルスチェック用 =====
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

bot = commands.Bot(command_prefix="!", intents=intents)

TARGET_LANGUAGES = ["ja", "en", "zh-CN", "ko", "es", "vi"]
server_settings = {}

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"✅ Slash commands synced as {bot.user}")

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
        try:
            translated = GoogleTranslator(source='auto', target=lang).translate(message.content)
        except Exception:
            translated = f"[{lang}] 翻訳エラー"
        await message.channel.send(f"[{lang}] {translated}")

    await bot.process_commands(message)

@bot.command()
async def auto(ctx, mode: str = None):
    guild_id = ctx.guild.id
    settings = server_settings.get(guild_id, {"auto": True, "languages": TARGET_LANGUAGES})
    if mode is None:
        await ctx.send(f"現在の状態: {'ON' if settings['auto'] else 'OFF'}\n使い方: `!auto on` / `!auto off`")
        return
    if mode.lower() == "on":
        settings["auto"] = True
        await ctx.send("✅ 自動翻訳を ON にしました。")
    elif mode.lower() == "off":
        settings["auto"] = False
        await ctx.send("🛑 自動翻訳を OFF にしました。")
    else:
        await ctx.send("使い方: `!auto on` または `!auto off`")
    server_settings[guild_id] = settings

@bot.command()
async def lang(ctx, *langs):
    guild_id = ctx.guild.id
    if not langs:
        await ctx.send("使い方: `!lang en ja ko` のように指定してください。")
        return
    server_settings[guild_id] = server_settings.get(guild_id, {"auto": True})
    server_settings[guild_id]["languages"] = list(langs)
    await ctx.send(f"翻訳対象言語を設定しました: {', '.join(langs)}")

# ===== 起動 =====
if __name__ == "__main__":
    keep_alive()
    bot.run(TOKEN)
