import discord
from discord import app_commands
from discord.ext import commands
import os
import datetime
import re
from flask import Flask
from threading import Thread

# --- 1. RENDER UCHUN WEB SERVER ---
app = Flask('')

@app.route('/')
def home():
    return "Bot onlayn!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- 2. BOT SOZLAMALARI ---
intents = discord.Intents.default()
intents.members = True 
intents.message_content = True

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # Slash komandalarni serverlarga yuklash
        await self.tree.sync()
        print("✅ Slash komandalar tayyor!")

bot = MyBot()

# Vaqt formatini tahlil qilish (masalan: 10m, 1h, 1d)
def parse_duration(duration_str):
    match = re.match(r"(\d+)([smhd])", duration_str.lower())
    if not match:
        return None
    amount, unit = match.groups()
    amount = int(amount)
    if unit == 's': return datetime.timedelta(seconds=amount)
    if unit == 'm': return datetime.timedelta(minutes=amount)
    if unit == 'h': return datetime.timedelta(hours=amount)
    if unit == 'd': return datetime.timedelta(days=amount)
    return None

# --- 3. SLASH KOMANDALAR ---

# /ping
@bot.tree.command(name="ping", description="Bot tezligini tekshirish")
async def ping(interaction: discord.Interaction):
    latency = round(bot.latency * 1000)
    await interaction.response.send_message(f"🏓 Pong! Kechikish: {latency}ms")

# /del
@bot.tree.command(name="del", description="Xabarlarni ommaviy o'chirish")
@app_commands.checks.has_permissions(administrator=True)
async def delete(interaction: discord.Interaction, soni: int):
    if soni < 1 or soni > 100:
        return await interaction.response.send_message("❌ 1 dan 100 gacha son yozing!", ephemeral=True)
    
    await interaction.response.defer(ephemeral=True)
    deleted = await interaction.channel.purge(limit=soni)
    await interaction.followup.send(f"🧹 {len(deleted)} ta xabar o'chirildi.")

# /delmute (Reply orqali ishlaydi)
@bot.tree.command(name="delmute", description="Xabarni o'chirib, foydalanuvchini mute qilish")
@app_commands.checks.has_permissions(administrator=True)
async def delmute(interaction: discord.Interaction, limit: str):
    # Reply qilingan xabarni aniqlash
    # Discord slash komandada reply qilingan xabarni olish uchun history ishlatamiz
    target_msg = None
    async for m in interaction.channel.history(limit=10):
        # Bu yerda komandani yuborgan odam javob bergan (reply) xabarini qidiramiz
        if interaction.message and interaction.message.reference:
            target_msg = await interaction.channel.fetch_message(interaction.message.reference.message_id)
            break
        # Agar oddiy slash bo'lsa, eng oxirgi xabarni oladi (komandadan oldingisini)
        if m.author.id != bot.user.id:
            target_msg = m
            break

    if not target_msg:
        return await interaction.response.send_message("❌ Xabarni aniqlab bo'lmadi. Reply qiling!", ephemeral=True)

    duration = parse_duration(limit)
    if not duration:
        return await interaction.response.send_message("❌ Xato format! Masalan: 10m, 1h, 1d", ephemeral=True)

    user = target_msg.author
    try:
        await target_msg.delete()
        await user.timeout(duration)
        await interaction.response.send_message(f"🔇 {user.mention}ning xabari o'chirildi va o'zi {limit}ga mute qilindi.")
    except:
        await interaction.response.send_message("❌ Xatolik: Ruxsat yetmadi (Bot roli past bo'lishi mumkin).", ephemeral=True)

# /delwarn (Reply orqali ishlaydi)
@bot.tree.command(name="delwarn", description="Xabarni o'chirib, ogohlantirish berish")
@app_commands.checks.has_permissions(administrator=True)
async def delwarn(interaction: discord.Interaction, message: str):
    target_msg = None
    async for m in interaction.channel.history(limit=5):
        if m.author.id != bot.user.id:
            target_msg = m
            break

    if target_msg:
        user = target_msg.author
        await target_msg.delete()
        await interaction.response.send_message(f"⚠️ {user.mention}, {message}")
    else:
        await interaction.response.send_message("❌ O'chirish uchun xabar topilmadi.", ephemeral=True)

# Xatolikni ushlash (Admin bo'lmaganlar uchun)
@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message("❌ Bu komandani faqat Adminlar ishlata oladi!", ephemeral=True)

# --- 4. ISHGA TUSHIRISH ---
if __name__ == "__main__":
    keep_alive() # Render uchun
    token = os.getenv("DISCORD_TOKEN")
    if token:
        bot.run(token)
    else:
        print("❌ XATO: DISCORD_TOKEN topilmadi!")
