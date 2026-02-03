import discord
import os
from discord import app_commands
import dotenv
from keep_alive import keep_alive
import time
import asyncio
from typing import Literal
import aiohttp
from google import genai
from apiclient import discovery
from httplib2 import Http
# 💡 サービスアカウント認証用のモジュールに変更
from oauth2client import service_account
from googleapiclient.errors import HttpError
import datetime
from discord.ext import tasks
import re
dotenv.load_dotenv()

TOKEN = os.getenv("token")



#botアクセス宣言
intents = discord.Intents.all()#適当に。
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client=client)
is_phalen_wakeup = False
# ボットの起動時の処理
@client.event
async def on_ready():
    await tree.sync()
    print('ログインしました')
    print(discord.__version__)
    notify_early.start()
    notify_late.start()
    reset_alarm_task.start()

# メッセージ受信時の処理
@client.event
async def on_member_join(member):
    welcome_channel_id = 1076105585428267101  
    channel = client.get_channel(welcome_channel_id)
    if channel:
        await channel.send(f'{member.mention}さん、{member.guild.name}へようこそ！\nサーバー規約を読んでからゆっくりしていってね')


async def hajime_process(guild,message):
    print("スタート")
    await asyncio.sleep(600)
    await message.channel.send(f"10分経過")
    members_in_vc = [
        m for ch in guild.voice_channels for m in ch.members if not m.bot
    ]
    for w in members_in_vc:
        try:
            await w.move_to(channel=None,reason="配信が始まるため")
        except discord.HTTPException as e:
            print(f"HTTPエラー:{e} ")
    await message.channel.send("任務完了")

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    global is_phalen_wakeup
    guild = client.get_guild(1076105584329375765)
    zatsudan = client.get_channel(1076482232342020096)
    ph = guild.get_member(1018781055215468624)    
    if message.author == ph and message.channel == zatsudan and message.content == "はじめます":
        asyncio.create_task(hajime_process(guild,message))
        is_phalen_wakeup = True
    if message.author == ph and message.content == re.fullmatch(r"(ぼく|僕|俺|オレ)\s*(?:は\s*)?(?:[1-9]|1[0-2]|[１-９]|１[０-２])(才|歳|さい)(?:です|だよ)?") :
        try:
            await message.delete()
            await message.channel.send("うそつけ")
        except discord.Forbidden:
            print("メッセージ削除権限がありません")
        except discord.HTTPException as e:
            print(f"HTTPエラー: {e}")
    return  
async def send_msg(mes,channel_id:int): # メッセージを送れる汎用関数
    try:
        channel = client.get_channel(channel_id)
        if channel :
            await channel.send(content=f"{mes}")
            print("メッセージを送信しました")
        else:
            print("channel is not found.")
    except Exception as e:
        print(f"exception error : {e}")

def can_notify():
    now = datetime.datetime.now()
    return now.weekday() in [1,2,4,5,6] and not is_phalen_wakeup

@tasks.loop(time=datetime.time(hour=21, minute=30))
async def notify_early():
    if can_notify():
        await send_msg(
            "21:30です。配信の調子はいかがでしょうか。 <@1018781055215468624>",1456890395970768951)
@tasks.loop(time=datetime.time(hour=22, minute=0))
async def notify_late():
    if can_notify():
        await send_msg(
            "22:00です。配信の時刻としては理想的でしょう。 <@1018781055215468624>",1456890395970768951)

@tasks.loop(time=datetime.time(hour=2, minute=0))
async def reset_alarm_task():
    global is_phalen_wakeup
    is_phalen_wakeup = False

@tree.command(name="ping",description="ping値を測定")
async def pingchi(inter : discord.Interaction):
    raw_ping = client.latency
    ping = round(raw_ping * 1000)
    await inter.response.send_message(f"🏓{ping}ms")

@tree.command(name="invite_url",description="ふぁれんサーバーへの招待リンクを作成する")
async def invite_ph(inter:discord.Interaction):
    url = "https://discord.gg/mdyRcy8gWt"
    try:
        await inter.response.send_message(f"{url}")
    except discord.Forbidden:
        await inter.response.send_message("権限不足")
    except discord.HTTPException :
        await inter.response.send_message("HTTP error occurred:")
@tree.command(name="introduction_phalen",description="ふぁれんが活動しているSNSを紹介します")
async def intro_ph(inter: discord.Interaction,mode: Literal["Youtube", "X", "Twitch", "全て"]):
    urls = {
        "Youtube": "https://youtube.com/channel/UC4BPiLhjSLozx2qWoR6yrhg?si=V62dclJo0PrxeOYZ",
        "Twitch": "https://www.twitch.tv/ponko2ninja",
        "X": "https://twitter.com/ponko2ninja",
    }
    if mode == "全て":
        await inter.response.send_message("\n".join(urls.values()))
    else:
        await inter.response.send_message(urls[mode])



keep_alive()
client.run(TOKEN)
