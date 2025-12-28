import discord
from discord import app_commands
from discord.ext import commands
import os
import datetime
import re
import requests
from flask import Flask
from threading import Thread

# --- 1. RENDER UCHUN WEB SERVER ---
app = Flask('')
@app.route('/')
def home(): return "Bot onlayn!"
def run(): app.run(host='0.0.0.0', port=8080)
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
        self.log_channel_id = None # Log kanali ID'si

    async def setup_hook(self):
        await self.tree.sync()
        print("✅ Barcha komandalar sinxronizatsiya qilindi!")

bot = MyBot()

# Vaqt formatini tahlil qilish
def parse_duration(duration_str):
    match = re.match(r"(\d+)([smhd])", duration_str.lower())
    if not match: return None
    amount, unit = match.groups()
    amount = int(amount)
    if unit == 's': return datetime.timedelta(seconds=amount)
    if unit == 'm': return datetime.timedelta(minutes=amount)
    if unit == 'h': return datetime.timedelta(hours=amount)
    if unit == 'd': return datetime.timedelta(days=amount)
    return None

# Log yuborish funksiyasi
async def send_log(guild, title, description, color=discord.Color.orange()):
    if bot.log_channel_id:
        channel = guild.get_channel(bot.log_channel_id)
        if channel:
            embed = discord.Embed(title=title, description=description, color=color, timestamp=datetime.datetime.now())
            await channel.send(embed=embed)

# --- 3. SLASH KOMANDALAR ---

# /setlog - Log kanalini belgilash
@bot.tree.command(name="setlog", description="Moderatsiya jurnali uchun kanalni belgilash")
@app_commands.checks.has_permissions(administrator=True)
async def setlog(interaction: discord.Interaction):
    bot.log_channel_id = interaction.channel_id
    await interaction.response.send_message(f"✅ Ushbu kanal moderatsiya jurnali (Audit Log) sifatida belgilandi.", ephemeral=True)

# /weather - Toshkent ob-havosi
@bot.tree.command(name="weather", description="Toshkentdagi ob-havoni ko'rsatadi")
async def weather(interaction: discord.Interaction):
    await interaction.response.defer()
    try:
        res = requests.get("https://wttr.in/Tashkent?format=j1").json()
        curr = res['current_condition'][0]
        temp, desc = curr['temp_C'], curr['weatherDesc'][0]['value']
        embed = discord.Embed(title="🏙 Toshkent Ob-havosi", description=f"Holat: **{desc}**\nHarorat: **{temp}°C**", color=discord.Color.blue())
        await interaction.followup.send(embed=embed)
    except:
        await interaction.followup.send("❌ Ob-havoni olib bo'lmadi.")

# /mute - Foydalanuvchini jazolash
@bot.tree.command(name="mute", description="Foydalanuvchini vaqtinchalik cheklash")
@app_commands.checks.has_permissions(moderate_members=True)
async def mute(interaction: discord.Interaction, user: discord.Member, limit: str, sabab: str = "Ko'rsatilmadi"):
    duration = parse_duration(limit)
    if not duration: return await interaction.response.send_message("❌ Xato vaqt! (10m, 1h, 1d)", ephemeral=True)
    
    await user.timeout(duration, reason=sabab)
    await interaction.response.send_message(f"🔇 {user.mention} {limit} ga mute qilindi.")
    await send_log(interaction.guild, "🔇 Mute Amali", f"**Kim:** {user}\n**Muddat:** {limit}\n**Admin:** {interaction.user}\n**Sabab:** {sabab}")

# /kick - Serverdan haydash
@bot.tree.command(name="kick", description="Foydalanuvchini serverdan haydash")
@app_commands.checks.has_permissions(kick_members=True)
async def kick(interaction: discord.Interaction, user: discord.Member, sabab: str = "Ko'rsatilmadi"):
    await user.kick(reason=sabab)
    await interaction.response.send_message(f"👢 {user.mention} serverdan haydaldi.")
    await send_log(interaction.guild, "👢 Kick Amali", f"**Kim:** {user}\n**Admin:** {interaction.user}\n**Sabab:** {sabab}", discord.Color.red())

# /ban - Serverdan butunlay haydash
@bot.tree.command(name="ban", description="Foydalanuvchini serverdan ban qilish")
@app_commands.checks.has_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, user: discord.Member, sabab: str = "Ko'rsatilmadi"):
    await user.ban(reason=sabab)
    await interaction.response.send_message(f"🚫 {user.mention} serverdan ban qilindi.")
    await send_log(interaction.guild, "🚫 Ban Amali", f"**Kim:** {user}\n**Admin:** {interaction.user}\n**Sabab:** {sabab}", discord.Color.dark_red())

# /del - Xabarlarni o'chirish
@bot.tree.command(name="del", description="Xabarlarni ommaviy o'chirish")
@app_commands.checks.has_permissions(administrator=True)
async def delete(interaction: discord.Interaction, soni: int):
    await interaction.response.defer(ephemeral=True)
    deleted = await interaction.channel.purge(limit=soni)
    await interaction.followup.send(f"🧹 {len(deleted)} ta xabar o'chirildi.")
    await send_log(interaction.guild, "🧹 Tozalash", f"**Kanal:** {interaction.channel.name}\n**Soni:** {len(deleted)}\n**Admin:** {interaction.user}", discord.Color.blue())

# /delmute (Reply orqali)
@bot.tree.command(name="delmute", description="Xabarni o'chirib mute qilish")
@app_commands.checks.has_permissions(administrator=True)
async def delmute(interaction: discord.Interaction, limit: str):
    duration = parse_duration(limit)
    target_msg = None
    async for m in interaction.channel.history(limit=5):
        if m.author.id != bot.user.id:
            target_msg = m
            break
    if target_msg and duration:
        user = target_msg.author
        await target_msg.delete()
        await user.timeout(duration)
        await interaction.response.send_message(f"🔇 {user.mention} xabari o'chirildi va mute qilindi.")
        await send_log(interaction.guild, "🔇 DelMute", f"**Kim:** {user}\n**Xabar o'chirildi**\n**Vaqt:** {limit}\n**Admin:** {interaction.user}")

# /delwarn (Reply orqali)
@bot.tree.command(name="delwarn", description="Xabarni o'chirib ogohlantirish")
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
        await send_log(interaction.guild, "⚠️ Ogohlantirish", f"**Kim:** {user}\n**Xabar:** {message}\n**Admin:** {interaction.user}")

# --- ISHGA TUSHIRISH ---
keep_alive()
bot.run(os.getenv("DISCORD_TOKEN"))
