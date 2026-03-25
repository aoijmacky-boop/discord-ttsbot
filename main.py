import discord
import asyncio
import os
from gtts import gTTS
import imageio_ffmpeg

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

client = discord.Client(intents=intents)

TARGET_CHANNEL_NAME = "🔊tts"

ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
print("FFmpeg path:", ffmpeg_path)

@client.event
async def on_ready():
    print(f"ログインしました: {client.user}")

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
        await asyncio.sleep(5)

        vc = discord.utils.get(client.voice_clients, guild=member.guild)
        if vc is None:
            return

        channel = vc.channel

        if len([m for m in channel.members if not m.bot]) == 0:
            await vc.disconnect()
            print("VCから退出しました")

@client.event
async def on_message(message):
    print("メッセージ検知:", message.content)

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

    print("読み上げ開始:", text)

    # 言語判定（日本語 or 韓国語）
    lang = "ja"
    if any('\uac00' <= c <= '\ud7a3' for c in text):
        lang = "ko"

    try:
        tts = gTTS(text=text, lang=lang)
        tts.save("voice.wav")

        print("ファイル存在:", os.path.exists("voice.wav"))

        # 再生中なら待機
        while vc.is_playing():
            await asyncio.sleep(0.5)

        audio = discord.FFmpegPCMAudio(
            "voice.wav",
            executable=ffmpeg_path,
            options="-loglevel quiet"
        )

        def after_playing(error):
            if error:
                print("再生エラー:", error)
            else:
                print("再生完了")

        vc.play(audio, after=after_playing)
        print("再生開始")

    except Exception as e:
        print("読み上げエラー:", e)

client.run(TOKEN)
