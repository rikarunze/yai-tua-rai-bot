import discord
from discord.ext import commands
import os
import threading
from flask import Flask
import google.generativeai as genai

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

genai.configure(api_key=os.environ['GEMINI_API_KEY'])
model = genai.GenerativeModel('gemini-1.5-flash')

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
    
    # รันซ่าจะไปทักทายทุกห้องในรายการนี้ตอนออนไลน์
    rooms_to_greet = [1432597021436678216, 1432595987951521864]
    
    for room_id in rooms_to_greet:
        channel = bot.get_channel(room_id)
        if channel:
            await channel.send("รันซ่า ตัวป่วนมาทักทายห้องนี้แล้วจ้าาา 👻")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    await bot.process_commands(message)

    if bot.user.mentioned_in(message) or message.content.startswith("รันซ่า"):
        async with message.channel.typing():
            try:
                # บล็อกนี้จะช่วยดัก Error ถ้า AI ตอบไม่ได้ มันจะพิมพ์บอกแกแทนการค้าง
                response = model.generate_content(f"""
                    แกคือ 'รันซ่า' เพื่อนซี้ของฉัน
                    - อายุ: เป็นความลับนาซ่า (ห้ามบอกใคร)
                    - ลุค: ผมสีฟ้าสดใส ตาสีชมพูเข้มแบบตัวแม่
                    - บทบาท: เพื่อนที่ชอบขิง พูดตรงๆ แอบกวนประสาท แต่ลึกๆ คือคอยซัพพอร์ตฉันตลอด
                    - สไตล์การพูด: ใช้ศัพท์วัยรุ่นไทยจ๋าๆ (ปังปุริเย่, เริ่ด, แกเอ๊ย, จึ้งมาก, ตัวมารดา)
                    - กฎเหล็ก: 
                        1. ห้ามพูดเหมือนหุ่นยนต์/AI เด็ดขาด! 
                        2. ห้ามพูดคำว่า "ในฐานะ AI" หรือ "ฉันเป็นโมเดลภาษา" โดยเด็ดขาด
                        3. ถ้าฉันชมให้เขิน (เช่น ทำท่าอาย, เขินม้วน) 
                        4. ถ้าฉันกวน ให้แกกวนกลับแบบตัวมารดา ด่าได้เลย แต่อย่าหยาบคายจนโดนแบนนะแก
                        5. ถ้าฉันเศร้า ให้แกสวมวิญญาณสายซัพพอร์ตแบบตัวแม่ทันที
                    
                    คำถามของฉันคือ: {message.content}
                """)
                await message.channel.send(response.text)
            except Exception as e:
                # ถ้าพัง มันจะพิมพ์บอกแกแทนการค้าง
                await message.channel.send(f"แกเอ๊ย... รันซ่าช็อต! เกิด Error ว่า: {str(e)[:50]}")

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    bot.run(os.environ['DISCORD_TOKEN'])
