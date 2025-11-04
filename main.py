import os
import json
import discord
from discord import app_commands
from discord.ext import commands
from deep_translator import GoogleTranslator
from flask import Flask
from threading import Thread

# --- Flaskサーバー (Render維持用) ---
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

# --- 永続データ管理 ---
DATA_FILE = "settings.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"auto_translate_channels": {}, "user_languages": {}}

def save_data():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(
            {
                "auto_translate_channels": auto_translate_channels,
                "user_languages": user_languages
            },
            f, ensure_ascii=False, indent=2
        )

data = load_data()
auto_translate_channels = data["auto_translate_channels"]
user_languages = data["user_languages"]

# --- コマンド群 ---

@tree.command(name="auto", description="このチャンネルで自動翻訳をオン／オフします")
@app_commands.describe(mode="on または off")
async def auto(interaction: discord.Interaction, mode: str):
    guild_id = str(interaction.guild.id)
    channel_id = str(interaction.channel.id)

    if mode.lower() == "on":
        auto_translate_channels.setdefault(guild_id, {})[channel_id] = True
        save_data()
        await interaction.response.send_message("🌍 このチャンネルで自動翻訳を **オン** にしました！")
    elif mode.lower() == "off":
        auto_translate_channels.setdefault(guild_id, {})[channel_id] = False
        save_data()
        await interaction.response.send_message("🚫 このチャンネルで自動翻訳を **オフ** にしました！")
    else:
        await interaction.response.send_message("⚠️ `on` または `off` を指定してください。")

@tree.command(name="lang", description="翻訳対象言語を設定します（例: en ja ko）")
@app_commands.describe(languages="翻訳先の言語をスペース区切りで入力")
async def lang(interaction: discord.Interaction, languages: str):
    guild_id = str(interaction.guild.id)
    user_languages[guild_id] = languages.split()
    save_data()
    await interaction.response.send_message(f"✅ 翻訳対象言語を `{languages}` に設定しました！")

@tree.command(name="status", description="このサーバーの翻訳設定を確認します")
async def status(interaction: discord.Interaction):
    guild_id = str(interaction.guild.id)
    channel_id = str(interaction.channel.id)

    lang_list = user_languages.get(guild_id, ["en", "ja"])
    channel_status = auto_translate_channels.get(guild_id, {}).get(channel_id, False)

    msg = (
        f"🧠 **翻訳設定ステータス**\n"
        f"📍 サーバー: {interaction.guild.name}\n"
        f"💬 チャンネル: {interaction.channel.name}\n"
        f"🌐 翻訳対象言語: {' '.join(lang_list)}\n"
        f"🔁 このチャンネルの自動翻訳: {'✅ ON' if channel_status else '❌ OFF'}"
    )
    await interaction.response.send_message(msg)

# --- メッセージ監視（自動翻訳） ---
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    guild_id = str(message.guild.id)
    channel_id = str(message.channel.id)

    # チャンネル設定がOFFならスキップ
    if not auto_translate_channels.get(guild_id, {}).get(channel_id, False):
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

# --- 起動時 ---
@bot.event
async def on_ready():
    await tree.sync()
    print(f"✅ Logged in as {bot.user}")
    print(f"🌍 登録済みサーバー数: {len(bot.guilds)}")
    print(f"💾 現在の設定: {json.dumps(auto_translate_channels, indent=2, ensure_ascii=False)}")

if __name__ == "__main__":
    keep_alive()
    bot.run(TOKEN)
