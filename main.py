import discord
from discord import app_commands
from discord.ext import commands
import os
import datetime
import re
from flask import Flask
from threading import Thread

# 1. Render uchun Web Server (Doimiy onlayn turish uchun)
app = Flask('')

@app.route('/')
def home():
    return "Bot is online!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# 2. Bot sozlamalari
intents = discord.Intents.default()
intents.members = True  # Mute va Kick uchun kerak
intents.message_content = True

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # Slash komandalarni sinxronizatsiya qilish
        await self.tree.sync()
        print(f"Slash komandalar sinxronizatsiya qilindi.")

bot = MyBot()

# Vaqtni hisoblash funksiyasi (10m, 1h, 2d uchun)
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

# --- KOMANDALAR ---

# /del
@bot.tree.command(name="del", description="Xabarlarni o'chirish")
@app_commands.checks.has_permissions(administrator=True)
async def delete_messages(interaction: discord.Interaction, soni: int):
    if soni < 1 or soni > 100:
        return await interaction.response.send_message("1 dan 100 gacha son yozing", ephemeral=True)
    
    await interaction.channel.purge(limit=soni)
    await interaction.response.send_message(f"🧹 {soni} ta xabar o'chirildi", ephemeral=True)

# /delmute
@bot.tree.command(name="delmute", description="Userni mute qilish")
@app_commands.checks.has_permissions(administrator=True)
async def delmute(interaction: discord.Interaction, user: discord.Member, limit: str):
    duration = parse_duration(limit)
    if not duration:
        return await interaction.response.send_message("Xato format! Masalan: 10m, 1h, 2d", ephemeral=True)

    try:
        await user.timeout(duration)
        await interaction.response.send_message(f"🔇 {user.mention} {limit} muddatga mute qilindi.")
    except Exception as e:
        await interaction.response.send_message(f"Xatolik: {e}", ephemeral=True)

# /delwarn
@bot.tree.command(name="delwarn", description="Xabarni o'chirib ogohlantirish berish")
@app_commands.checks.has_permissions(administrator=True)
async def delwarn(interaction: discord.Interaction, user: discord.Member, message: str):
    # Bu yerda oxirgi xabarni o'chirish (ixtiyoriy)
    await interaction.response.send_message(f"⚠️ {user.mention}, {message}")

# Xatoliklarni ushlash (Admin bo'lmaganlar uchun)
@delete_messages.error
@delmute.error
@delwarn.error
async def admin_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message("❌ Bu komandani faqat Adminlar ishlata oladi!", ephemeral=True)

# Botni ishga tushirish
keep_alive()
token = os.getenv("DISCORD_TOKEN")
bot.run(token)
