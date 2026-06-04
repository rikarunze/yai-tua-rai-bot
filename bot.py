import discord
from discord.ext import commands
import os
import threading
from flask import Flask
from groq import Groq

# 1. ตั้งค่า Flask (ให้ Render มองเห็นว่าบอทยังรันอยู่)
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

groq_api_key = os.environ.get('GROQ_API_KEY')
client = Groq(api_key=groq_api_key) if groq_api_key else None

# ตัวแปรเก็บความจำ (Global History)
message_history = []

# 3. คำสั่งบอท
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
    # อัปเดตสถานะให้บอทดูตื่นตัวตลอดเวลา (กันหลุดจาก Render)
    await bot.change_presence(activity=discord.Game(name="กำลังเมาท์มอยกับเพื่อนสาว 💅"))
    print(f'Logged in as {bot.user}')
    
    rooms_to_greet = [1432597021436678216, 1432595987951521864]
    for room_id in rooms_to_greet:
        channel = bot.get_channel(room_id)
        if channel:
            try:
                await channel.send("รันซ่า ตัวป่วนฟื้นคืนชีพแล้วจ้าาา 👻")
            except:
                pass

@bot.event
async def on_message(message):
    global message_history
    if message.author == bot.user:
        return
    await bot.process_commands(message)

    if bot.user.mentioned_in(message) or message.content.startswith("รันซ่า"):
        if client is None:
            await message.channel.send("แกเอ๊ย... ลืมใส่ GROQ_API_KEY ใน Render หรือเปล่า?")
            return

        # บันทึกประวัติการคุย
        message_history.append({"role": "user", "content": message.content})
        if len(message_history) > 10: message_history.pop(0)

        async with message.channel.typing():
            try:
                completion = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": "แกคือ 'รันซ่า' เพื่อนซี้สุดแซ่บ: ผมสีฟ้า ตาสีชมพู พูดจาวัยรุ่นไทย (ปังปุริเย่, เริ่ด, แกเอ๊ย) กวนๆ แต่อบอุ่น, ห้ามบอกว่าตัวเองเป็น AI, ถ้าฉันถามอะไรให้จำบริบทก่อนหน้าได้, ใช้ภาษาปากเยอะๆ"},
                    ] + message_history 
                )
                
                response_text = completion.choices[0].message.content
                # บันทึกสิ่งที่รันซ่าตอบ
                message_history.append({"role": "assistant", "content": response_text})
                
                if not response_text:
                    await message.channel.send("รันซ่าพูดไม่ออกอะแก... เครื่องมันเอ๋อ!")
                elif len(response_text) > 1900:
                    await message.channel.send(response_text[:1900] + "\n...(ข้อความยาวไปนะแก รันซ่าขี้เกียจพิมพ์)")
                else:
                    await message.channel.send(response_text)

            except Exception as e:
                await message.channel.send(f"แกเอ๊ย... รันซ่าช็อต! Error: {str(e)[:50]}")

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    bot.run(os.environ.get('DISCORD_TOKEN'))
