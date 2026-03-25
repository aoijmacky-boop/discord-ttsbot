import discord
import os
from gtts import gTTS
from langdetect import detect
import asyncio

TOKEN = os.environ["TOKEN"]

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

client = discord.Client(intents=intents)

TARGET_CHANNEL_NAME = "🔊tts"

voice_clients = {}

@client.event
async def on_ready():
    print(f"ログインしました: {client.user}")
    client.loop.create_task(check_voice_loop())

# ===== VC自動参加（安定版）=====
async def check_voice_loop():
    await client.wait_until_ready()
    while not client.is_closed():
        for guild in client.guilds:
            for vc in guild.voice_channels:
                if len(vc.members) > 0:
                    if guild.id not in voice_clients:
                        try:
                            voice_client = await vc.connect()
                            voice_clients[guild.id] = voice_client
                            print(f"{vc.name} に接続しました")
                        except Exception as e:
                            print(f"接続エラー: {e}")
        await asyncio.sleep(5)

# ===== メッセージ読み上げ =====
@client.event
async def on_message(message):
    if message.channel.name != TARGET_CHANNEL_NAME:
        return

    if not message.content:
        return

    if message.guild.id not in voice_clients:
        return

    vc = voice_clients[message.guild.id]

    try:
        lang = detect(message.content)

        if lang not in ["ja", "ko"]:
            return

        tts = gTTS(text=message.content, lang=lang)
        file_name = "voice.mp3"
        tts.save(file_name)

        if vc.is_playing():
            vc.stop()

        vc.play(discord.FFmpegPCMAudio(file_name))

        while vc.is_playing():
            await asyncio.sleep(1)

    except Exception as e:
        print(f"エラー: {e}")

client.run(TOKEN)