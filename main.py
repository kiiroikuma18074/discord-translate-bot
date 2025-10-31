import os
import discord
from discord import app_commands
from discord.ext import commands
from deep_translator import GoogleTranslator
from flask import Flask
import threading

# Flaskサーバー（Renderのスリープ防止）
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    app.run(host="0.0.0.0", port=8080)

# Discord Bot 設定
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# 起動時メッセージ
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"Slash commands synced ({len(synced)} commands)")
    except Exception as e:
        print(f"Error syncing commands: {e}")

# /translate コマンド
@bot.tree.command(name="translate", description="テキストを翻訳します")
@app_commands.describe(
    text="翻訳したいテキストを入力してください",
    target_lang="翻訳先の言語コード (例: en, ja, fr)"
)
async def translate(interaction: discord.Interaction, text: str, target_lang: str):
    try:
        # 絵文字などのUnicode文字を壊さないように翻訳
        translated = GoogleTranslator(source='auto', target=target_lang).translate(text)
        await interaction.response.send_message(
            f"🌐 **翻訳結果** ({target_lang}):\n{translated}"
        )
    except Exception as e:
        await interaction.response.send_message(f"⚠️ 翻訳エラー: {e}")

# Flaskをバックグラウンドで実行
threading.Thread(target=run_flask).start()

# Bot起動
token = os.getenv("DISCORD_BOT_TOKEN")
if not token:
    print("❌ 環境変数 DISCORD_BOT_TOKEN が設定されていません。RenderのEnvironmentタブを確認してください
