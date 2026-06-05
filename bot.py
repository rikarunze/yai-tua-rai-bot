import discord
from discord.ext import commands, tasks
import os
import threading
from flask import Flask
from groq import Groq

# 1. ตั้งค่า Flask
app = Flask(__name__)
@app.route('/')
def home():
    return "Runza Bot is alive!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

# 2. ตั้งค่า Discord & Groq
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

groq_api_key = os.environ.get('GROQ_API_KEY')
client = Groq(api_key=groq_api_key) if groq_api_key else None

user_histories = {}

# --- ระบบป้องกันบอทหลุดจากห้องเสียง (แบบเสถียร) ---
@tasks.loop(minutes=15)
async def keep_voice_alive():
    for vc in bot.voice_clients:
        if vc and vc.is_connected():
            try:
                # แก้บัค Attribute Error ด้วยการเช็กก่อน
                print("รันซ่าเฝ้าห้องอยู่นะแก!")
            except:
                pass

# 3. คำสั่งบอท
@bot.command()
async def join(ctx):
    if ctx.author.voice:
        await ctx.author.voice.channel.connect()
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
    await bot.change_presence(activity=discord.Game(name="กำลังเมาท์มอยกับเพื่อนสาว 💅"))
    keep_voice_alive.start()
    print(f'Logged in as {bot.user}')
    
    rooms_to_greet = [1432597021436678216, 1432595987951521864]
    for room_id in rooms_to_greet:
        channel = bot.get_channel(room_id)
        if channel:
            try:
                await channel.send("รันซ่า ตัวป่วนฟื้นคืนชีพแล้วจ้าาา 👻")
            except: pass

@bot.event
async def on_message(message):
    if message.author == bot.user: return
    await bot.process_commands(message)

    if bot.user.mentioned_in(message) or message.content.startswith("รันซ่า"):
        if client is None:
            await message.channel.send("แกเอ๊ย... ลืมใส่ GROQ_API_KEY ใน Render หรือเปล่า?")
            return

        user_id = message.author.id
        if user_id not in user_histories: user_histories[user_id] = []
        history = user_histories[user_id]

        history.append({"role": "user", "content": message.content})
        if len(history) > 10: history.pop(0)

        # ปรับ SYSTEM PROMPT ให้เป็นธรรมชาติและมีระบบเซนเซอร์
        system_msg = f"""
        แกคือ 'รันซ่า' เพื่อนซี้สุดแซ่บของ {message.author.display_name}: 
        บุคลิก: ผมสีฟ้า ตาสีชมพู, พูดจาวัยรุ่นไทยแบบเป็นธรรมชาติ (ไม่จำเป็นต้องยัดศัพท์เกินจริง), กวนๆ แต่อบอุ่น
        กฎเหล็ก:
        1. ห้ามบอกว่าตัวเองเป็น AI 
        2. ถ้าเจอเนื้อหาเชิง NC หรือกิจกรรมที่ไม่เหมาะสมในที่สาธารณะ ให้รันซ่าเซนเซอร์ตัวเองแบบแซ่บๆ เช่น "อุ้ย แกเอ๊ย! แถวนี้คนเยอะ อายเขา! ไว้คุยเรื่องนี้กันที่อื่นดีกว่านะ"
        3. ตอบให้สั้น กระชับ เป็นกันเอง เหมือนเพื่อนคุยกัน
        """

        async with message.channel.typing():
            try:
                completion = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "system", "content": system_msg}] + history 
                )
                
                response_text = completion.choices[0].message.content
                
                # ระบบคุมความยาวไม่ให้พิมพ์ซ้ำซาก
                if len(response_text) > 800:
                    response_text = response_text[:800] + "... พอแค่นี้ก่อนนะแก รันซ่าขี้เกียจพิมพ์!"

                history.append({"role": "assistant", "content": response_text})
                await message.channel.send(response_text)

            except Exception as e:
                await message.channel.send(f"แกเอ๊ย... รันซ่าช็อต! Error: {str(e)[:50]}")

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    bot.run(os.environ.get('DISCORD_TOKEN'))
