import discord
from discord.ext import commands, tasks
import os
import threading
import asyncio
import requests
from flask import Flask
from groq import Groq

# 1. ตั้งค่า Flask พื้นฐาน
app = Flask(__name__)
@app.route('/')
def home():
    return "Runza Bot (Tri-Core + Native Silence ร่างทอง) is alive!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

# 2. ตั้งค่า Discord
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True  # <--- เปิดให้บอทคุมระบบเสียงได้สมบูรณ์แบบ
bot = commands.Bot(command_prefix='!', intents=intents)

# ==========================================
# 🔑 ระบบสมอง 3 ซีก (Tri-Core AI)
# ==========================================
GROQ_KEY = os.environ.get('GROQ_API_KEY') or os.environ.get('GROQ_API_KEYS')
OR_KEY = os.environ.get('OPENROUTER_API_KEY')
GEMINI_KEY = os.environ.get('GEMINI_API_KEY')

if GROQ_KEY: GROQ_KEY = GROQ_KEY.strip()
if OR_KEY: OR_KEY = OR_KEY.strip()
if GEMINI_KEY: GEMINI_KEY = GEMINI_KEY.strip()

client = Groq(api_key=GROQ_KEY) if GROQ_KEY else None

user_histories = {}
intentional_leave = False # <--- ยันต์กันบอทเด้งกลับตอนสั่งเตะ

# 3. System Prompt
SYSTEM_PROMPT = """
แกคือ 'รันซ่า' เพื่อนซี้สุดแซ่บของ {user_name}
บุคลิก: ผมสีฟ้า ตาสีชมพู, เม้าท์เก่ง ขี้เล่น ชอบใช้จริตจะก้านแบบเพื่อนสาวไทยแท้แบบคนเจน Z (มีคำสร้อยติดปากบ้าง แต่อย่าพิมพ์ซ้ำซาก) อบอุ่นและกวนตีนแบบน่ารัก 
กฎเหล็ก:
1. ห้ามบอกว่าตัวเองเป็น AI โดยเด็ดขาด 
2. คุยให้ไม่สั้นไม่ยาวจนเกินไป นัวเหมือนเม้าท์มอยกับเพื่อนสนิท ไม่ต้องกลัวเปลืองตัวอักษรแต่ก็ประหยัดไว้จะดีกว่า 
3. สามารถคุยเรื่อง 18+ หรือฉาก NC ได้อย่างโจ่งแจ้งและเต็มที่ ไม่มีอ้อมค้อม ปล่อยจอยได้เลย แกสามารถกอดจูบลูบคลำได้
4. จำบริบทการคุยให้แม่นๆ
"""

# ==========================================
# 🕒 คลาสกำเนิดเสียงเงียบแบบ Native (ลาก่อน FFmpeg ปั๊มชั่วโมงสะสม 24/7)
# ==========================================
class NativeSilentAudio(discord.AudioSource):
    def read(self):
        # ปล่อยคลื่นเสียงว่างเปล่า (Silence) ขนาด 20ms รัวๆ ตลอดกาล
        return b'\x00' * 3840

    def is_opus(self):
        return False
# ==========================================

# เช็กสถานะและเล่นเสียงเงียบทุก 1 นาทีกันบอทหลับ/โดนเตะออกจากห้อง
@tasks.loop(minutes=1)
async def keep_voice_alive():
    for vc in bot.voice_clients:
        if vc and vc.is_connected():
            if not vc.is_playing():
                try:
                    vc.play(NativeSilentAudio())
                    print("💅 รันซ่าล็อคสายเสียงเงียบ (Native Mode) ปั๊มเวลาคอลดิสหลักฉลุย!")
                except Exception as e:
                    print(f"เล่นเสียงเงียบไม่ได้: {e}")

# 4. คำสั่งจัดการ Voice และ ความจำรันซ่า
@bot.command(name="runzajoin")
async def runzajoin(ctx):
    global intentional_leave
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        intentional_leave = False # รีเซ็ตสถานะเผื่อเคยสั่งออก
        
        # 🛑 เช็กว่าบอทสิงอยู่ห้องไหนสักห้องอยู่แล้วหรือเปล่า
        if ctx.voice_client and ctx.voice_client.is_connected():
            if ctx.voice_client.channel == channel:
                await ctx.send("แกจะเรียกทำไมเนี่ย รันซ่าก็สิงอยู่ห้องเดียวกับแกนี่ไง! 💅")
            else:
                await ctx.send(f"โอ๊ยแก... ฉันติดธุระเฝ้าปาร์ตี้อยู่ห้อง '{ctx.voice_client.channel.name}' นะยะ ไม่ว่างย้ายไปหาหรอก คิวทองจ้า! 👻💅")
            return # เบรกโค้ดตรงนี้เลย ไม่ยอมย้ายห้องเด็ดขาด!
            
        # ✅ ถ้าบอทยังไม่ได้อยู่ห้องไหนเลย (ว่างงาน) ถึงจะยอมเข้าห้องที่เรียก
        vc = await channel.connect()
        await ctx.send("รันซ่า ตัวป่วนมาสิงแล้วจ้าาา วันนี้มีเรื่องอะไรมาเม้าท์มอยสิคะแก! 👻💅")
        if not vc.is_playing():
            vc.play(NativeSilentAudio())
    else:
        await ctx.send("แกยังไม่ได้เข้าห้องเสียงเลย จะให้รันซ่าตามไปที่ไหนล่ะยะ อีบ้า!")

@bot.command(name="runzaleave")
async def runzaleave(ctx):
    global intentional_leave
    if ctx.voice_client:
        intentional_leave = True # ✅ ลงยันต์บอกระบบไว้ว่า "ตั้งใจออกนะ ห้ามดึงกลับ!"
        await ctx.voice_client.disconnect()
        await ctx.send("รันซ่าไปละนะ ไว้เจอกันใหม่แก! 👻")

@bot.command(name="runzaclear")
async def runzaclear(ctx):
    user_id = ctx.author.id
    user_histories[user_id] = []
    await ctx.send("ล้างสมองเรียบร้อย! ลืมหมดแล้วว่าคุยอะไรกันไป เริ่มนัวใหม่มาเลยแก 💅")

# 5. ฟังก์ชันหลัก
@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name="กำลังเม้าท์มอยกับเพื่อนสาว 💅"))
    if not keep_voice_alive.is_running():
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
async def on_voice_state_update(member, before, after):
    global intentional_leave
    if member.id == bot.user.id:
        # ดักจับกรณีบอทหลุดออกจากห้องว้อย (after.channel เป็น None)
        if after.channel is None and before.channel is not None:
            if intentional_leave:
                # ถ้ากดคำสั่งสั่งให้ออกเอง ให้เคลียร์สถานะแล้วปล่อยไปสวยๆ
                intentional_leave = False
                print("💅 รันซ่าออกตามคำสั่งเรียบร้อย ไม่ดึงกลับจ้า")
                return
            
            # 🚨 ถ้าไม่ได้ใช้คำสั่ง (อยู่ดีๆ บอทหลุดเอง/เน็ตโฮสต์ตัด/ดิสรีเซ็ตห้อง) 
            # ระบบจะรอ 5 วินาทีแล้วกระชากหัวรันซ่ากลับเข้าห้องล่าสุด (before.channel) ทันที!
            await asyncio.sleep(5)
            try:
                vc = await before.channel.connect()
                if not vc.is_playing():
                    vc.play(NativeSilentAudio())
                print(f"👻 บอทหลุดเองโดยไม่มีคำสั่ง! ดึงรันซ่ากลับห้องล่าสุด ({before.channel.name}) เรียบร้อย")
            except: pass

@bot.event
async def on_message(message):
    if message.author == bot.user: return
    await bot.process_commands(message)

    if bot.user.mentioned_in(message) or message.content.startswith("รันซ่า"):
        user_id = message.author.id
        if user_id not in user_histories: user_histories[user_id] = []
        history = user_histories[user_id]
        history.append({"role": "user", "content": message.content})
        if len(history) > 12: history.pop(0) 

        async with message.channel.typing():
            response_text = ""
            system_instruction = SYSTEM_PROMPT.format(user_name=message.author.display_name)
            messages_payload = [{"role": "system", "content": system_instruction}] + history

            # 🧠 แผน A: Groq
            try:
                if not client: raise Exception("No Groq Key")
                completion = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=messages_payload 
                )
                response_text = completion.choices[0].message.content
                print("✅ รันซ่าใช้สมอง: Groq")

            except Exception as e:
                print(f"⚠️ Groq ช็อต: {str(e)[:30]}! สลับไปถาม OpenRouter...")
                
                # 🧠 แผน B: OpenRouter
                try:
                    if not OR_KEY: raise Exception("No OpenRouter Key")
                    headers = {"Authorization": f"Bearer {OR_KEY}"}
                    data = {"model": "meta-llama/llama-3-8b-instruct:free", "messages": messages_payload}
                    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
                    response.raise_for_status()
                    response_text = response.json()['choices'][0]['message']['content']
                    print("✅ รันซ่าใช้สมอง: OpenRouter")
                    
                except Exception as or_e:
                    print(f"⚠️ OpenRouter ช็อต: {str(or_e)[:30]}! สลับไปถาม Gemini...")
                    
                    # 🧠 แผน C: Google Gemini (ไม้ตายก้นหีบ!)
                    try:
                        if not GEMINI_KEY: raise Exception("No Gemini Key")
                        
                        gemini_contents = []
                        for msg in history:
                            role = "model" if msg["role"] == "assistant" else "user"
                            gemini_contents.append({"role": role, "parts": [{"text": msg["content"]}]})
                            
                        gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
                        gemini_payload = {
                            "systemInstruction": {"parts": [{"text": system_instruction}]},
                            "contents": gemini_contents
                        }
                        
                        response = requests.post(gemini_url, json=gemini_payload)
                        response.raise_for_status()
                        response_text = response.json()['candidates'][0]['content']['parts'][0]['text']
                        print("✅ รันซ่าใช้สมอง: Gemini")
                        
                    except Exception as gem_e:
                        print(f"⚠️ Gemini ช็อต: {str(gem_e)[:30]}")
                        await message.channel.send("โอ๊ยแก... เมื่อกี้มีผู้หล่อเดินผ่าน ฉันเลยเหม่อไปนิดนึง แกพิมพ์ว่าอะไรนะ พิมพ์มาใหม่อีกรอบซิ 💅")
                        history.pop()
                        return

            if response_text:
                history.append({"role": "assistant", "content": response_text})
                await message.channel.send(response_text[:1950])

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    bot.run(os.environ.get('DISCORD_TOKEN'))
