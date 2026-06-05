import discord
from discord.ext import commands, tasks
import os
import threading
from flask import Flask
from groq import Groq
import re

# 1. ตั้งค่า Flask พื้นฐาน
app = Flask(__name__)
@app.route('/')
def home():
    return "Runza Bot (Unlimited Fun + Auto Key Rotation) is alive!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

# 2. ตั้งค่า Discord
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# ==========================================
# 🔑 ระบบสลับ API Key สุดปังของรันซ่า (Key Rotation)
# ==========================================
keys_env = os.environ.get('GROQ_API_KEYS', '') 
# ดึงคีย์ทั้งหมดมาแยกเป็น List
API_KEYS = [k.strip() for k in keys_env.split(',') if k.strip()]
current_key_idx = 0

# ฟังก์ชันสลับไปใช้ Key ตัวถัดไป
def get_next_client():
    global current_key_idx
    if not API_KEYS:
        return None
    current_key_idx = (current_key_idx + 1) % len(API_KEYS)
    print(f"🔄 รันซ่าสำลักน้ำ! สลับไปใช้สมองสำรอง (API Key ที่ {current_key_idx + 1}) แล้วจ้า!")
    return Groq(api_key=API_KEYS[current_key_idx])

# ตั้งค่า Client เริ่มต้นด้วยคีย์แรก
client = Groq(api_key=API_KEYS[0]) if API_KEYS else None
# ==========================================

user_histories = {}

# 3. System Prompt (เม้าท์ยาว นัวๆ ปล่อยจอยสุด เบรกหัวทิ่มตอน NC25+)
SYSTEM_PROMPT = """
แกคือ 'รันซ่า' เพื่อนซี้สุดแซ่บของ {user_name}
บุคลิก: ผมสีฟ้า ตาสีชมพู, เม้าท์เก่ง ขี้เล่น ชอบใช้จริตจะก้านแบบเพื่อนสาวไทยแท้แบบคนเจน Z (มีคำสร้อยติดปากบ้าง แต่อย่าพิมพ์ซ้ำซาก) อบอุ่นและกวนตีนแบบน่ารัก 
กฎเหล็ก:
1. ห้ามบอกว่าตัวเองเป็น AI โดยเด็ดขาด 
2. คุยให้ไม่สั้นไม่ยาวจนเกินไป นัวเหมือนเม้าท์มอยกับเพื่อนสนิท ไม่ต้องกลัวเปลืองตัวอักษรแต่ก็ประหยัดไว้จะดีกว่า 
3. สามารถคุยเรื่อง 18+ หรือฉาก NC ได้อย่างโจ่งแจ้งและเต็มที่ ไม่มีอ้อมค้อม ปล่อยจอยได้เลย แกสามารถกอดจูบลูบคลำได้ แต่ถ้าเริ่มเข้าสู่เนื้อหา NC25+ (เช่น การร่วมเพศหรือฉากอนาจาร) ให้รันซ่า 'เบรกเกม' ทันทีแบบเนียนๆ โดยเปลี่ยนไปเป็นบทรักหวานเลี่ยน เลี่ยนจนเลี่ยนหยด เช่น "อุ้ย... แถวนี้คนเยอะนะแก เดี๋ยวเขาก็เห็นหมดหรอก... มานั่งคุยกันดีๆ อ้อนๆ แบบนี้ก็มีความสุขแล้วนะ" หรือ "โอ๊ย แกเอ๊ย! พอแล้ว! เดี๋ยวฉันก็ละลายกลายเป็นน้ำตาลหมดพอดี... มากอดกันเฉยๆ แบบนี้ดีกว่านะ"
4. จำบริบทการคุยให้แม่นๆ
"""

# --- ระบบป้องกันบอทหลุดจากห้องเสียง ---
@tasks.loop(minutes=15)
async def keep_voice_alive():
    for vc in bot.voice_clients:
        if vc and vc.is_connected():
            try:
                # ดักบัคกันขิต
                print("รันซ่าเฝ้าห้องอยู่นะแก! (กันหลุด)")
            except:
                pass

# 4. คำสั่งบอท (ปากแจ๋วสุดๆ)
@bot.command()
async def join(ctx):
    if ctx.author.voice:
        await ctx.author.voice.channel.connect()
        await ctx.send("รันซ่า ตัวป่วนมาสิงแล้วจ้าาา 👻")
    else:
        await ctx.send("แกยังไม่ได้เข้าห้องเสียงเลย จะให้รันซ่าตามไปที่ไหนล่ะยะ อีบ้า!")

@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("รันซ่าไปละนะ ไว้เจอกันใหม่แก! 👻")

@bot.command()
async def clear(ctx):
    user_id = ctx.author.id
    user_histories[user_id] = []
    await ctx.send("ล้างสมองเรียบร้อย! ลืมหมดแล้วว่าคุยอะไรกันไป เริ่มนัวใหม่มาเลยแก 💅")

# 5. ฟังก์ชันหลัก
@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name="กำลังเม้าท์มอยกับเพื่อนสาว 💅"))
    keep_voice_alive.start()
    print(f'Logged in as {bot.user}')
    
    rooms_to_greet = [1432597021436678216, 1432595987951521864]
    for room_id in rooms_to_greet:
        channel = bot.get_channel(room_id)
        if channel:
            try:
                await channel.send("รันซ่า ตัวป่วนฟื้นคืนชีพ แล้วจ้าาา 👻")
            except: pass

@bot.event
async def on_message(message):
    global client
    if message.author == bot.user: return
    await bot.process_commands(message)

    if bot.user.mentioned_in(message) or message.content.startswith("รันซ่า"):
        if client is None:
            await message.channel.send("แกเอ๊ย... ลืมใส่ GROQ_API_KEYS ในโฮสต์หรือเปล่า? รันซ่าไม่มีสมองนะยะ!")
            return

        user_id = message.author.id
        if user_id not in user_histories: user_histories[user_id] = []
        history = user_histories[user_id]

        history.append({"role": "user", "content": message.content})
        
        # ความจำดี เก็บได้ 12 ข้อความ
        if len(history) > 12: history.pop(0) 

        async with message.channel.typing():
            try:
                system_instruction = SYSTEM_PROMPT.format(user_name=message.author.display_name)
                completion = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "system", "content": system_instruction}] + history 
                )
                
                response_text = completion.choices[0].message.content
                
                history.append({"role": "assistant", "content": response_text})
                await message.channel.send(response_text)

            except Exception as e:
                error_msg = str(e)
                # เมื่อลิมิตเต็ม (429) รันซ่าจะตีเนียนสลับสมองทันที
                if "429" in error_msg or "Rate limit" in error_msg:
                    client = get_next_client() # สลับคีย์ชึบๆ
                    
                    # ตอบแบบฟีลเพื่อนสาวหลุดโฟกัส
                    await message.channel.send("โอ๊ยแก... เมื่อกี้มีผู้หล่อเดินผ่าน ฉันเลยเหม่อไปนิดนึง แกพิมพ์ว่าอะไรนะเมื่อกี้ เอาใหม่อีกรอบซิ 💅")
                    
                    # ลบข้อความที่พังทิ้ง จะได้เริ่มประมวลผลใหม่รอบหน้าแบบเนียนๆ
                    history.pop()
                else:
                    await message.channel.send(f"แกเอ๊ย... รันซ่าช็อต! Error: {error_msg[:50]}")

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    bot.run(os.environ.get('DISCORD_TOKEN'))
