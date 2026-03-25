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

# ===== VC自動参加 =====
@client.event
async def on_voice_state_update(member, before, after):
    if member.bot:
        return

    # 誰かがVCに入った
    if after.channel is not None:
        vc = after.channel

        if vc.guild.id not in voice_clients:
            voice_client = await vc.connect()
            voice_clients[vc.guild.id] = voice_client

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
        # ===== 言語判定 =====
        lang = detect(message.content)

        if lang not in ["ja", "ko"]:
            return

        # ===== TTS作成 =====
        tts = gTTS(text=message.content, lang=lang)
        file_name = "voice.mp3"
        tts.save(file_name)

        # ===== 再生 =====
        if vc.is_playing():
            vc.stop()

        vc.play(discord.FFmpegPCMAudio(file_name))

        # 再生終わるまで待つ
        while vc.is_playing():
            await asyncio.sleep(1)

    except Exception as e:
        print(f"エラー: {e}")

# ===== 起動 =====
client.run(TOKEN)