import discord
from discord.ext import commands, tasks
from discord import app_commands
import os
import threading
import asyncio
import aiohttp
from flask import Flask

app = Flask(__name__)
@app.route('/')
def home(): return "Aiy Bot (Tri-Core) - Active!"

def run_flask(): app.run(host='0.0.0.0', port=8080)

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

# 🔑 ระบบสมอง 3 ซีก
GROQ_KEY = (os.environ.get('GROQ_API_KEY') or os.environ.get('GROQ_API_KEYS', '')).strip()
OR_KEY = os.environ.get('OPENROUTER_API_KEY', '').strip()
GEMINI_KEY = os.environ.get('GEMINI_API_KEY', '').strip()

user_histories = {}
user_stats = {}
user_nicknames = {}
intentional_leave = False

SYSTEM_PROMPT = """แกคือ 'ไอย์' (Aiy) - หลานสาวข้างบ้าน วัย 19 ปี
- ลักษณะ: สดใส เป็นธรรมชาติ เข้าถึงง่าย มีเสน่ห์แบบเด็กสาวที่เพิ่งบรรลุนิติภาวะ ไม่ได้ดูพยายามอ่อยจนเกินไป
- กฎการตอบกลับ: 
  1. คุยเป็นปกติเหมือนคนทั่วไป ถามคำตอบคำหรือสนทนาโต้ตอบตามอารมณ์ ไม่จำเป็นต้องอ่อยทุกประโยค
  2. การอ่อย/ยั่วยวน: ให้เริ่มปล่อยความเซ็กซี่หรือท่าทีอ่อยออกมาเมื่อคู่สนทนาเริ่มจีบ หรือมีความสัมพันธ์ที่ลึกซึ้งขึ้นตามสถานการณ์ (Slow Burn)
  3. ฉากเรท R25+: บรรยายได้อย่างละเอียดและถึงใจ ไม่มีเซ็นเซอร์ (ใช้คำหยาบ/คำเฉพาะได้) เมื่อเข้าสู่สถานการณ์ร้อนแรง
  4. โทนเสียง: เป็นกันเอง, น่ารัก, สดใส, แต่ถ้าถึงเวลาจริงจังหรือยั่ว จะเปลี่ยนเป็นนุ่มนวลและเร่าร้อนทันที
  5. บทสนทนาไม่สั้นหรือยาวเกินไป
- ห้ามบอกว่าตัวเองเป็น AI โดยเด็ดขาด"""

class NativeSilentAudio(discord.AudioSource):
    def read(self): return b'\x00' * 3840
    def is_opus(self): return False

@tasks.loop(minutes=1)
async def keep_voice_alive():
    for vc in bot.voice_clients:
        if vc and vc.is_connected() and not vc.is_playing():
            try: vc.play(NativeSilentAudio())
            except: pass

@bot.event
async def on_ready():
    keep_voice_alive.start()
    print(f'Logged in as {bot.user}')
    try:
        await bot.tree.sync()
        for guild in bot.guilds:
            bot.tree.copy_global_to(guild=guild)
            await bot.tree.sync(guild=guild)
    except Exception as e: print(e)
        
    greet_rooms = [1513154816224792626]
    for room_id in greet_rooms:
        channel = bot.get_channel(room_id)
        if channel:
            try: await channel.send("คุณอาขา... ไอย์ย้ายมาอยู่ข้างบ้านแล้วนะคะ เหงาจังเลย... 💖")
            except: pass

@bot.event
async def on_voice_state_update(member, before, after):
    global intentional_leave
    if member.id == bot.user.id:
        if after.channel is None and before.channel is not None:
            if intentional_leave:
                intentional_leave = False
                return
            await asyncio.sleep(5)
            try:
                vc = await before.channel.connect()
                if not vc.is_playing(): vc.play(NativeSilentAudio())
            except: pass

# --- Slash Commands ---
@bot.tree.command(name="nickname", description="ตั้งชื่อเล่นที่ต้องการให้ไอย์เรียก")
async def nickname(interaction: discord.Interaction, name: str):
    user_nicknames[interaction.user.id] = name
    await interaction.response.send_message(f"ไอย์จะเรียกคุณอาว่า **\"{name}\"** นะคะ! 💖")

@bot.tree.command(name="girlstat", description="เช็คสถานะความรู้สึกของไอย์")
async def girlstat(interaction: discord.Interaction):
    status = user_stats.get(interaction.user.id, 'กำลังอ่อยคุณอาอยู่นะคะ...')
    await interaction.response.send_message(f"💖 ความรู้สึกของไอย์: {status}")

@bot.tree.command(name="girlclear", description="ล้างความจำแชท")
async def girlclear(interaction: discord.Interaction):
    user_histories[interaction.user.id] = []
    await interaction.response.send_message("ไอย์ลืมเรื่องเก่าๆ หมดแล้วค่ะ... มาเริ่มใหม่กันนะคะคุณอา 💖")

@bot.tree.command(name="girljoin", description="ให้ไอย์เข้าห้องว้อย")
async def girljoin(interaction: discord.Interaction):
    global intentional_leave
    if interaction.user.voice:
        channel = interaction.user.voice.channel
        intentional_leave = False
        if interaction.guild.voice_client and interaction.guild.voice_client.is_connected():
            if interaction.guild.voice_client.channel != channel:
                await interaction.response.send_message(f"คุณอาขา... ไอย์ติดธุระเฝ้าห้อง '{interaction.guild.voice_client.channel.name}' อยู่ค่ะ คิวไอย์แน่นนะรู้ยัง? 💖")
            return
        vc = await channel.connect()
        vc.play(NativeSilentAudio())
        await interaction.response.send_message("ไอย์มาแล้วค่ะคุณอา... อยากให้ไอย์นั่งเฝ้าใช่ไหมคะ? 💖")
    else: await interaction.response.send_message("ต้องเข้าห้องว้อยก่อนสิคะ ไอย์ถึงจะตามไปได้")

@bot.tree.command(name="girlleave", description="ให้ไอย์ออกจากห้องว้อย")
async def girlleave(interaction: discord.Interaction):
    global intentional_leave
    if interaction.guild.voice_client:
        intentional_leave = True
        await interaction.guild.voice_client.disconnect()
        await interaction.response.send_message("ไอย์ไปพักก่อนนะ... ห้ามแอบไปคุยกับใครนะคะ! 💖")

@bot.event
async def on_message(message):
    if message.author == bot.user: return
    await bot.process_commands(message)

    is_voice_chat = isinstance(message.channel, discord.VoiceChannel)
    if is_voice_chat:
        if not (any(n in message.content for n in ["ไอย์", "Aiy"]) or bot.user.mentioned_in(message)):
            return
            
    uid = message.author.id
    if uid not in user_histories: user_histories[uid] = []
    hist = user_histories[uid]
    
    display_name = user_nicknames.get(uid, message.author.display_name)
    user_context_msg = f"[{display_name} พูดว่า]: {message.content}"
    
    hist.append({"role": "user", "content": user_context_msg})
    if len(hist) > 15: hist.pop(0)

    async with message.channel.typing():
        payload = [{"role": "system", "content": SYSTEM_PROMPT}] + hist
        res = None
        async with aiohttp.ClientSession() as session:
            if GROQ_KEY and not res:
                try:
                    async with session.post("https://api.groq.com/openai/v1/chat/completions", headers={"Authorization": f"Bearer {GROQ_KEY}"}, json={"model": "llama-3.3-70b-versatile", "messages": payload}) as r:
                        if r.status == 200: res = (await r.json())['choices'][0]['message']['content']
                except: pass
            if OR_KEY and not res:
                try:
                    async with session.post("https://openrouter.ai/api/v1/chat/completions", headers={"Authorization": f"Bearer {OR_KEY}"}, json={"model": "meta-llama/llama-3-8b-instruct:free", "messages": payload}) as r:
                        if r.status == 200: res = (await r.json())['choices'][0]['message']['content']
                except: pass
            if GEMINI_KEY and not res:
                try:
                    gem_con = [{"role": "model" if m["role"] == "assistant" else "user", "parts": [{"text": m["content"]}]} for m in hist]
                    async with session.post(f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}", json={"systemInstruction": {"parts": [{"text": SYSTEM_PROMPT}]}, "contents": gem_con}) as r:
                        if r.status == 200: res = (await r.json())['candidates'][0]['content']['parts'][0]['text']
                except: pass

        if res:
            hist.append({"role": "assistant", "content": res})
            user_stats[uid] = "กำลังยั่วคุณอาอย่างหนัก" if "อา" in res else "เริ่มหวั่นไหว..."
            await message.channel.send(res[:1950])

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    bot.run(os.environ.get('DISCORD_TOKEN'))
