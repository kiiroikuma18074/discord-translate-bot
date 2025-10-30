import os
import discord
from discord.ext import commands
from googletrans import Translator

# 翻訳対象言語
LANGUAGES = {
    "日本語": "ja",
    "英語": "en",
    "中国語": "zh-cn",
    "韓国語": "ko",
    "スペイン語": "es",
    "ベトナム語": "vi"
}

# DiscordのIntents設定
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
translator = Translator()

@bot.event
async def on_ready():
    print(f"✅ ログインしました: {bot.user}")

@bot.event
async def on_message(message):
    # Bot自身のメッセージを無視
    if message.author.bot:
        return

    # 翻訳対象のテキスト
    text = message.content

    # 翻訳処理
    translated_texts = []
    for lang_name, lang_code in LANGUAGES.items():
        translated = translator.translate(text, dest=lang_code)
        translated_texts.append(f"**{lang_name}**: {translated.text}")

    # 結果を送信
    result = "\n".join(translated_texts)
    await message.channel.send(result)

# トークンを環境変数から取得
token = os.getenv("DISCORD_BOT_TOKEN")

if not token:
    print("❌ 環境変数 DISCORD_BOT_TOKEN が設定されていません。")
else:
    bot.run(token)
