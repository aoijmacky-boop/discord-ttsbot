import discord
import asyncio
import os
from gtts import gTTS

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

client = discord.Client(intents=intents)

TARGET_CHANNEL_NAME = "🔊tts"

@client.event
async def on_ready():
    print(f"ログインしました: {client.user}")

@client.event
async def on_voice_state_update(member, before, after):
    # 誰かがVCに入ったらbotも入る
    if after.channel is not None and before.channel is None:
        vc = discord.utils.get(client.voice_clients, guild=member.guild)

        if vc is None:
            try:
                await after.channel.connect()
                print("VCに接続しました")
            except Exception as e:
                print(f"接続エラー: {e}")

@client.event
async def on_message(message):
    if message.channel.name != TARGET_CHANNEL_NAME:
        return

    if message.guild is None:
        return

    vc = discord.utils.get(client.voice_clients, guild=message.guild)

    if vc is None:
        return

    text = message.content
    if text == "":
        return

    # 🌏 言語判定（ざっくり）
    lang = "ja"
    if any('\uac00' <= c <= '\ud7a3' for c in text):
        lang = "ko"

    try:
        tts = gTTS(text=text, lang=lang)
        tts.save("voice.mp3")

        # 再生中なら待つ
        while vc.is_playing():
            await asyncio.sleep(0.5)

        vc.play(discord.FFmpegPCMAudio("voice.mp3"))

    except Exception as e:
        print(f"読み上げエラー: {e}")

@client.event
async def on_voice_state_update(member, before, after):
    vc = discord.utils.get(client.voice_clients, guild=member.guild)

    # 誰か入ったら接続
    if after.channel is not None and before.channel is None:
        if vc is None:
            try:
                await after.channel.connect()
                print("VCに接続しました")
            except Exception as e:
                print(f"接続エラー: {e}")

    # 全員抜けたら退出
    if before.channel is not None:
        channel = before.channel
        if len(channel.members) == 1:  # botだけになる
            if vc is not None:
                await vc.disconnect()
                print("VCから退出しました")

client.run(TOKEN)
