import discord
from discord.ext import commands
import os
import threading
from flask import Flask
import google.generativeai as genai

# 1. ตั้งค่า Flask (เพื่อหลอก Render ว่าเราเป็นเว็บ)
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

# 3. ส่วนของการคุยโต้ตอบ
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # ถ้าพิมพ์คำว่า "ส้ม" หรืออยากให้บอทตอบ ให้ AI ทำงาน
    # ตรงนี้คือส่วนที่แกคุยกับบอทได้เลย!
    if bot.user.mentioned_in(message) or message.content.startswith("ส้ม"):
        async with message.channel.typing():
            response = model.generate_content(f"แกคือเพื่อนซี้เจน Z ของฉัน ชอบพูดจาผ่อนคลาย ใช้คำศัพท์วัยรุ่น กวนประสาทนิดๆ: {message.content}")
            await message.channel.send(response.text)

    await bot.process_commands(message)

# 4. รันพร้อมกัน 2 อย่าง
if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    bot.run(os.environ['DISCORD_TOKEN'])
