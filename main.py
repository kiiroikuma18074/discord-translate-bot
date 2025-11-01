@bot.event
async def on_message(message):
    # ボット自身のメッセージは無視
    if message.author.bot:
        return

    # コマンドメッセージ（!や/で始まる）・絵文字だけのメッセージは翻訳しない
    if message.content.startswith(("!", "/")):
        await bot.process_commands(message)
        return

    # メッセージが絵文字だけなら翻訳しない
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
