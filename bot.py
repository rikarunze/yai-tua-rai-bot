import discord
from discord.ext import commands
import os

# ตั้งค่าสิ่งที่บอททำได้ (Intents)
intents = discord.Intents.default()
intents.message_content = True

# สร้างตัวบอท
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'✅ ยัยตัวร้ายรายงานตัว! บอทออนไลน์แล้วเว้ยยย!')

@bot.command()
async def join(ctx):
    # ตรวจสอบว่าคนเรียกอยู่ในห้องเสียงหรือไม่
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        await channel.connect()
        await ctx.send("เข้ามาสิงแล้วจ้าาา 👻")
    else:
        await ctx.send("แกต้องเข้าห้องเสียงก่อนดิโว้ย ถึงจะเรียกชั้นเข้าไปได้!")

# ดึง Token จาก Environment Variables ที่เราตั้งไว้ใน Render
# วิธีนี้ปลอดภัยและยาม GitHub จะไม่ระเบิด Token แกทิ้งแล้ว!
if __name__ == "__main__":
    try:
        TOKEN = os.environ['TOKEN']
        bot.run(TOKEN)
    except KeyError:
        print("❌ Error: ยังไม่ได้ตั้งค่า TOKEN ใน Environment ของ Render นะแก!")
