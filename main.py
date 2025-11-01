import discord
from discord.ext import commands
from deep_translator import GoogleTranslator

# --- 必要な設定 ---
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

TARGET_LANGUAGES = ["ja", "en", "zh-CN", "ko", "es", "vi"]
server_settings = {}

# --- イベント: メッセージ受信 ---
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.content.startswith(("!", "/")):
        await bot.process_commands(message)
        return

    if all(not c.isalnum() for c in message.content.strip()):
        await bot.process_commands(message)
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


# --- スラッシュコマンド類 ---
@bot.slash_command(name="auto", description="自動翻訳をオン/オフします")
async def auto(ctx, mode: str):
    guild_id = ctx.guild.id
    if guild_id not in server_settings:
        server_settings[guild_id] = {"auto": True, "languages": TARGET_LANGUAGES}

    if mode.lower() == "on":
        server_settings[guild_id]["auto"] = True
        await ctx.respond("✅ 自動翻訳をオンにしました")
    elif mode.lower() == "off":
        server_settings[guild_id]["auto"] = False
        await ctx.respond("🛑 自動翻訳をオフにしました")
    else:
        await ctx.respond("on または off を指定してください。")


@bot.slash_command(name="lang", description="翻訳対象の言語を設定します")
async def lang(ctx, *langs):
    guild_id = ctx.guild.id
    server_settings[guild_id] = {"auto": True, "languages": langs}
    await ctx.respond(f"🌍 翻訳対象を {', '.join(langs)} に設定しました。")


# --- 起動 ---
bot.run("あなたのDiscordトークン")
