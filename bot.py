import discord
from discord.ext import commands
import os
from flask import Flask
from threading import Thread

# --- ส่วนของ Web Server หลอกๆ เพื่อให้ Render เห็นว่า Live ---
app = Flask('')

@app.route('/')
def home():
    return "ยัยตัวร้ายออนไลน์อยู่โว้ย!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()
# --------------------------------------------------------

# ตั้งค่าบอท
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

# เรียกฟังก์ชันเปิด Web Server ก่อนรันบอท
keep_alive()

# รันบอท
if __name__ == "__main__":
    TOKEN = os.environ['TOKEN']
    bot.run(TOKEN)
