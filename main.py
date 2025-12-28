import discord
from discord import app_commands
from discord.ext import commands
import os
import datetime
import re
from flask import Flask
from threading import Thread

# 1. Render uchun Web Server
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
intents.members = True 
intents.message_content = True

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await self.tree.sync()
        print(f"Slash komandalar sinxronizatsiya qilindi.")

bot = MyBot()

# Vaqtni hisoblash funksiyasi
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

# /ping - Botning ishlashini tekshirish
@bot.tree.command(name="ping", description="Bot tezligini tekshirish")
async def ping(interaction: discord.Interaction):
    latency = round(bot.latency * 1000)
    await interaction.response.send_message(f"🏓 Pong! Kechikish: {latency}ms")

# /del - Xabarlarni o'chirish
@bot.tree.command(name="del", description="Xabarlarni o'chirish")
@app_commands.checks.has_permissions(administrator=True)
async def delete_messages(interaction: discord.Interaction, soni: int):
    await interaction.response.defer(ephemeral=True)
    deleted = await interaction.channel.purge(limit=soni)
    await interaction.followup.send(f"🧹 {len(deleted)} ta xabar o'chirildi.")

# /delmute - Userni mute qilish (vaqtli)
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

# /delwarn - Xabarni o'chirib ogohlantirish berish
@bot.tree.command(name="delwarn", description="Ogohlantirish berish")
@app_commands.checks.has_permissions(administrator=True)
async def delwarn(interaction: discord.Interaction, user: discord.Member, message: str):
    await interaction.response.send_message(f"⚠️ {user.mention}, {message}")

# Xatoliklarni ushlash
@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message("❌ Sizda admin huquqi yo'q!", ephemeral=True)

# Botni ishga tushirish
keep_alive()
token = os.getenv("DISCORD_TOKEN")
bot.run(token)
