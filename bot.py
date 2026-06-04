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

# 3. คำสั่งบอท (เอาส่วนที่แกใช้จริงมาแปะตรงนี้)
@bot.command()
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        await channel.connect()
        await ctx.send("รันซ่ามาสิงแล้วจ้าาา 👻")
    else:
        await ctx.send("แกยังไม่ได้เข้าห้องเสียงเลย จะให้รันซ่าตามไปที่ไหนล่ะยะ!")

# 4. ส่วนของการคุยโต้ตอบ
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # ให้ระบบประมวลผลคำสั่ง ! ก่อนเสมอ
    await bot.process_commands(message)

    # เช็กว่าเรียก 'รันซ่า' ไหม
    if bot.user.mentioned_in(message) or message.content.startswith("รันซ่า"):
        async with message.channel.typing():
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

# 5. รันพร้อมกัน
if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    bot.run(os.environ['DISCORD_TOKEN'])
