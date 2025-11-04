import os
import discord
from discord import app_commands
from discord.ext import commands
from deep_translator import GoogleTranslator
from flask import Flask
from threading import Thread

# ==============================
# Flask（Render維持用）
# ==============================
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


# ==============================
# Discord Bot設定
# ==============================
TOKEN = os.environ.get("DISCORD_BOT_TOKEN")
if not TOKEN:
    print("❌ 環境変数 DISCORD_BOT_TOKEN が見つかりません！")
else:
    print("✅ DISCORD_BOT_TOKEN 読み込み完了")

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree


# ==============================
# 各種データ
# ==============================
auto_translate_guilds = {}
user_languages = {}
channel_whitelist = {}

# 翻訳メッセージの紐づけ用
translated_message_map = {}  # {元メッセージID: [翻訳メッセージID1, 翻訳メッセージID2, ...]}

# 国旗マッピング
flags = {
    "en": "🇺🇸", "ja": "🇯🇵", "ko": "🇰🇷", "zh": "🇨🇳",
    "fr": "🇫🇷", "de": "🇩🇪", "es": "🇪🇸", "it": "🇮🇹",
    "ru": "🇷🇺", "pt": "🇧🇷", "id": "🇮🇩", "vi": "🇻🇳", "th": "🇹🇭"
}


# ==============================
# /auto 自動翻訳ON/OFF
# ==============================
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


# ==============================
# /lang 翻訳対象言語設定
# ==============================
@tree.command(name="lang", description="翻訳対象言語を設定します（例: en ja ko）")
@app_commands.describe(languages="翻訳先の言語をスペース区切りで入力")
async def lang(interaction: discord.Interaction, languages: str):
    guild_id = interaction.guild.id
    user_languages[guild_id] = languages.split()

    flags_display = " ".join(flags.get(lang, f"[{lang}]") for lang in user_languages[guild_id])
    await interaction.response.send_message(f"✅ 翻訳対象言語を {flags_display} に設定しました！")


# ==============================
# /channel 翻訳を有効にするチャンネル選択
# ==============================
@tree.command(name="channel", description="翻訳を有効にするチャンネルを設定します")
@app_commands.describe(channel="翻訳を有効にしたいチャンネル")
async def channel(interaction: discord.Interaction, channel: discord.TextChannel):
    guild_id = interaction.guild.id
    if guild_id not in channel_whitelist:
        channel_whitelist[guild_id] = set()
    if channel.id in channel_whitelist[guild_id]:
        channel_whitelist[guild_id].remove(channel.id)
        await interaction.response.send_message(f"🚫 {channel.mention} の翻訳をオフにしました。")
    else:
        channel_whitelist[guild_id].add(channel.id)
        await interaction.response.send_message(f"✅ {channel.mention} で翻訳をオンにしました。")


# ==============================
# /status 現在設定確認
# ==============================
@tree.command(name="status", description="現在の翻訳設定を確認します")
async def status(interaction: discord.Interaction):
    guild_id = interaction.guild.id
    auto_status = "オン ✅" if auto_translate_guilds.get(guild_id, False) else "オフ ❌"
    langs = user_languages.get(guild_id, ["en", "ja"])
    flags_display = " ".join(flags.get(lang, f"[{lang}]") for lang in langs)
    channels = channel_whitelist.get(guild_id, set())
    ch_list = ", ".join(f"<#{ch_id}>" for ch_id in channels) if channels else "（未設定）"

    embed = discord.Embed(title="🌐 翻訳Bot ステータス", color=0x3498db)
    embed.add_field(name="自動翻訳", value=auto_status, inline=False)
    embed.add_field(name="翻訳対象言語", value=flags_display, inline=False)
    embed.add_field(name="対象チャンネル", value=ch_list, inline=False)
    await interaction.response.send_message(embed=embed)


# ==============================
# メッセージ監視・翻訳
# ==============================
@bot.event
async def on_message(message):
    if message.author.bot:
        return
    guild_id = message.guild.id

    # 自動翻訳ONチェック
    if not auto_translate_guilds.get(guild_id, False):
        return

    # チャンネル制限
    allowed_channels = channel_whitelist.get(guild_id, set())
    if allowed_channels and message.channel.id not in allowed_channels:
        return

    target_langs = user_languages.get(guild_id, ["en", "ja"])
    text = message.content.strip()
    if not text:
        return

    translated_message_map[message.id] = []  # 元メッセージに紐づく翻訳を記録

    try:
        for lang in target_langs:
            translated = GoogleTranslator(source='auto', target=lang).translate(text)
            if translated and translated != text:
                flag = flags.get(lang, f"[{lang}]")
                sent_msg = await message.channel.send(f"{flag} {translated}")
                translated_message_map[message.id].append(sent_msg.id)
    except Exception as e:
        await message.channel.send(f"⚠️ 翻訳エラー: {e}")


# ==============================
# メッセージ削除 → 翻訳も削除
# ==============================
@bot.event
async def on_message_delete(message):
    if message.id in translated_message_map:
        translated_ids = translated_message_map.pop(message.id)
        for msg_id in translated_ids:
            try:
                msg = await message.channel.fetch_message(msg_id)
                await msg.delete()
            except:
                pass  # 既に削除済みでもOK


# ==============================
# 起動イベント
# ==============================
@bot.event
async def on_ready():
    await tree.sync()
    print(f"✅ Logged in as {bot.user}")


# ==============================
# メイン実行
# ==============================
if __name__ == "__main__":
    keep_alive()
    bot.run(TOKEN)
