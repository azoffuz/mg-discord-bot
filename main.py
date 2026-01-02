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
        self.log_channel_id = None 

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

async def send_log(guild, title, description, color=discord.Color.orange()):
    if bot.log_channel_id:
        channel = guild.get_channel(bot.log_channel_id)
        if channel:
            embed = discord.Embed(title=title, description=description, color=color, timestamp=datetime.datetime.now())
            await channel.send(embed=embed)

# --- 3. SLASH KOMANDALAR ---

# /avatar - Foydalanuvchi avatarini ko'rsatish
@bot.tree.command(name="avatar", description="Foydalanuvchi avatarini ko'rsatadi")
async def avatar(interaction: discord.Interaction, user: discord.Member = None):
    # Agar user tanlanmagan bo'lsa, Reply qilingan xabarni tekshirish
    if user is None:
        if interaction.message and interaction.message.reference:
            ref_msg = await interaction.channel.fetch_message(interaction.message.reference.message_id)
            user = ref_msg.author
        else:
            user = interaction.user

    embed = discord.Embed(title=f"{user.display_name} avatari", color=discord.Color.random())
    embed.set_image(url=user.display_avatar.url)
    await interaction.response.send_message(embed=embed)

# /server-avatar - Server avatarini ko'rsatish
@bot.tree.command(name="server-avatar", description="Server avatarini ko'rsatadi")
async def server_avatar(interaction: discord.Interaction):
    guild = interaction.guild
    if guild.icon:
        embed = discord.Embed(title=f"{guild.name} server avatari", color=discord.Color.blue())
        embed.set_image(url=guild.icon.url)
        await interaction.response.send_message(embed=embed)
    else:
        await interaction.response.send_message("❌ Bu serverda avatar (icon) o'rnatilmagan.", ephemeral=True)

# /rules
@bot.tree.command(name="rules", description="Qoidalar kanalini ko'rsatadi")
async def rules(interaction: discord.Interaction):
    rules_channel_id = 1169316659392168076
    await interaction.response.send_message(f"📖 Server qoidalari bilan bu yerda tanishishingiz mumkin: <#{rules_channel_id}>")

# /setlog
@bot.tree.command(name="setlog", description="Moderatsiya jurnali uchun kanalni belgilash")
@app_commands.checks.has_permissions(administrator=True)
async def setlog(interaction: discord.Interaction):
    bot.log_channel_id = interaction.channel_id
    await interaction.response.send_message(f"✅ Ushbu kanal moderatsiya jurnali sifatida belgilandi.", ephemeral=True)

# /weather
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

# /mute
@bot.tree.command(name="mute", description="Foydalanuvchini vaqtinchalik cheklash")
@app_commands.checks.has_permissions(moderate_members=True)
async def mute(interaction: discord.Interaction, user: discord.Member, limit: str, sabab: str = "Ko'rsatilmadi"):
    duration = parse_duration(limit)
    if not duration: return await interaction.response.send_message("❌ Xato vaqt!", ephemeral=True)
    await user.timeout(duration, reason=sabab)
    await interaction.response.send_message(f"🔇 {user.mention} {limit} ga mute qilindi.")
    await send_log(interaction.guild, "🔇 Mute Amali", f"**Kim:** {user}\n**Admin:** {interaction.user}")

# /kick, /ban, /del, /delmute, /delwarn funksiyalari o'zgarishsiz qoladi... (avvalgi koddagidek davom etadi)

# --- ISHGA TUSHIRISH ---
keep_alive()
bot.run(os.getenv("DISCORD_TOKEN"))
