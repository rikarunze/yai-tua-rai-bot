import discord
from discord.ext import commands

# ⚠️ เอา Token ที่ก๊อปเก็บไว้ตอนแรกมาใส่ตรงนี้ 
# (ให้มันอยู่ในเครื่องหมาย ' ' เหมือนเดิมนะเว้ย)
TOKEN = 'MTUxMTkxMDM4MTk3MzU0MDkzNQ.GM2ILx.7t4CjcNedoFSikOvJPbHvaxCiwTrazuI6S4mdU'

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'✅ ยัยตัวร้ายรายงานตัว! บอทออนไลน์แล้วเว้ยยย!')

@bot.command()
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        await channel.connect()
        await ctx.send("เข้ามาสิงแล้วจ้าาา 👻")
    else:
        await ctx.send("แกต้องเข้าห้องเสียงก่อนดิโว้ย ถึงจะเรียกชั้นเข้าไปได้!")

bot.run(TOKEN)
