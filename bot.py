import discord
from discord.ext import commands
import os
import threading
from flask import Flask
from groq import Groq

# 1. ตั้งค่า Flask
app = Flask(__name__)
@app.route('/')
def home():
    return "Bot is alive!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

# 2. ตั้งค่า Discord & Groq
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# ตั้งค่า Groq Client (ดึงคีย์มาจาก Environment Variable: GROQ_API_KEY)
client = Groq(api_key=os.environ['GROQ_API_KEY'])

# 3. คำสั่งบอท (Join & Leave)
@bot.command()
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        await channel.connect()
        await ctx.send("รันซ่า ตัวป่วนมาสิงแล้วจ้าาา 👻")
    else:
        await ctx.send("แกยังไม่ได้เข้าห้องเสียงเลย จะให้รันซ่าตามไปที่ไหนล่ะยะ!")

@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("รันซ่าไปละนะ ไว้เจอกันใหม่แก! 👻")

# 4. ส่วนของการทำงานหลัก
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    # ส่วนของ on_ready ที่ขาดไป ส้มเติมให้แล้วแก!
    rooms_to_greet = [1432597021436678216, 1432595987951521864]
    for room_id in rooms_to_greet:
        channel = bot.get_channel(room_id)
        if channel:
            await channel.send("รันซ่า ตัวป่วนฟื้นคืนชีพ (ในเวอร์ชัน Groq) แล้วจ้าาา 👻")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    await bot.process_commands(message)

    if bot.user.mentioned_in(message) or message.content.startswith("รันซ่า"):
        async with message.channel.typing():
            try:
                # เรียกใช้งาน Llama 3 ของ Groq
                completion = client.chat.completions.create(
                    model="llama3-70b-8192",
                    messages=[
                        {"role": "system", "content": "แกคือ 'รันซ่า' เพื่อนซี้ของฉัน: ผมสีฟ้า ตาสีชมพู พูดจาวัยรุ่นไทย (ปังปุริเย่, เริ่ด, แกเอ๊ย) กวนๆ แต่อบอุ่น ห้ามบอกว่าตัวเองเป็น AI โดยเด็ดขาด!"},
                        {"role": "user", "content": message.content}
                    ]
                )
                await message.channel.send(completion.choices[0].message.content)
            except Exception as e:
                await message.channel.send(f"แกเอ๊ย... รันซ่าช็อต! Groq Error: {str(e)[:50]}")

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    bot.run(os.environ['DISCORD_TOKEN'])
