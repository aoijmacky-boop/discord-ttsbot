import discord
import os
import asyncio

TOKEN = os.environ["TOKEN"]

intents = discord.Intents.default()
intents.voice_states = True

client = discord.Client(intents=intents)

voice_clients = {}

@client.event
async def on_ready():
    print(f"ログインしました: {client.user}")
    client.loop.create_task(check_voice_loop())

async def check_voice_loop():
    await client.wait_until_ready()
    while not client.is_closed():
        for guild in client.guilds:
            for vc in guild.voice_channels:
                # Bot以外の人がいるかチェック
                human_members = [m for m in vc.members if not m.bot]

                if len(human_members) > 0:
                    if guild.id not in voice_clients:
                        try:
                            voice_client = await vc.connect()
                            voice_clients[guild.id] = voice_client
                            print(f"{vc.name} に接続しました")
                        except Exception as e:
                            print(f"接続エラー: {e}")
        await asyncio.sleep(5)

client.run(TOKEN)