import os
import discord
from discord import app_commands
from discord.ext import commands
from deep_translator import GoogleTranslator
from flask import Flask
from threading import Thread

# --- Flask サーバー（Render維持用） ---
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

# --- Discord Bot 設定 ---
TOKEN = os.environ.get("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

auto_translate_guilds = {}
user_languages = {}

@tree.command(name="auto", description="自動翻訳をオン／オフします")
@app_commands.describe(mode="on または off")
async def auto(interaction: discord.Interaction, mode: str):
    guild_id = interaction.guild.id
    if mode.lower() == "on":
        auto_translate_guilds[guild_id] = True
        await interaction.response.send_message("🌍 自動翻訳を **オン** にしました！")
    elif mode.lower() == "off":
        auto_translate_guilds[guild_id] = False
        await interaction.response.send_message("🚫 自動翻訳を **オフ** にしました！")
    else:
        await interaction.response.send_message("⚠️ `on` または `off` を指定してください。")

@tree.command(name="lang", description="翻訳対象言語を設定します（例: en ja ko）")
@app_commands.describe(languages="翻訳先の言語をスペース区切りで入力")
async def lang(interaction: discord.Interaction, languages: str):
    guild_id = interaction.guild.id
    user_languages[guild_id] = languages.split()
    await interaction.response.send_message(f"✅ 翻訳対象言語を `{languages}` に設定しました！")

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    guild_id = message.guild.id
    if not auto_translate_guilds.get(guild_id, False):
        return
    target_langs = user_languages.get(guild_id, ["en", "ja"])
    text = message.content
    try:
        for lang in target_langs:
            translated = GoogleTranslator(source='auto', target=lang).translate(text)
            if translated and translated != text:
                await message.channel.send(f"💬 **{lang}**: {translated}")
    except Exception as e:
        await message.channel.send(f"⚠️ 翻訳エラー: {e}")

@bot.event
async def on_ready():
    await tree.sync()
    print(f"✅ Logged in as {bot.user}")

if __name__ == "__main__":
    keep_alive()
    bot.run(TOKEN)
