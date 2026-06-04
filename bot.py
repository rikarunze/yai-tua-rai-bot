import discord
from discord.ext import commands
import os
import threading
from flask import Flask
from google import genai  # Library ใหม่ 2026

# 1. ตั้งค่า Flask
app = Flask(__name__)
@app.route('/')
def home():
    return "Bot is alive!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

# 2. ตั้งค่า Discord & Gemini
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# ใช้ client ใหม่ตามคู่มือปี 2026
client = genai.Client(api_key=os.environ['GEMINI_API_KEY'])

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
    else:
        await ctx.send("รันซ่ายังไม่ได้อยู่ในห้องเสียงเลย จะให้ออกไปไหนล่ะยะ!")

# 4. ส่วนของการคุยโต้ตอบ
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    
    # รันซ่าทักทายตอนออนไลน์
    rooms_to_greet = [1432597021436678216, 1432595987951521864]
    for room_id in rooms_to_greet:
        channel = bot.get_channel(room_id)
        if channel:
            try:
                await channel.send("รันซ่า ตัวป่วนฟื้นคืนชีพแล้วจ้าาา 👻")
            except:
                print(f"ส่งข้อความเข้าห้อง {room_id} ไม่ได้! (เช็ก Permission นะแก)")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    await bot.process_commands(message)

    if bot.user.mentioned_in(message) or message.content.startswith("รันซ่า"):
        async with message.channel.typing():
            try:
                # ใช้ gemini-3.5-flash โมเดลที่ฉลาดและเร็วที่สุดตอนนี้
                response = client.models.generate_content(
                    model="gemini-3.5-flash",
                    contents=f"""
                        แกคือ 'รันซ่า' เพื่อนซี้ของฉัน
                        - ลุค: ผมสีฟ้าสดใส ตาสีชมพูเข้มแบบตัวแม่
                        - สไตล์การพูด: วัยรุ่นไทยจ๋าๆ (ปังปุริเย่, เริ่ด, แกเอ๊ย, จึ้งมาก)
                        - กฎ: ห้ามพูดเหมือน AI, ห้ามบอกว่าตัวเองเป็นโมเดล, กวนกลับได้ถ้าฉันกวน, ซัพพอร์ตถ้าฉันเศร้า
                        คำถามคือ: {message.content}
                    """
                )
                await message.channel.send(response.text)
            except Exception as e:
                await message.channel.send(f"แกเอ๊ย... รันซ่าช็อต! Error: {str(e)[:50]}")

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    bot.run(os.environ['DISCORD_TOKEN'])
