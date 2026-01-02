import discord
from discord import app_commands
from discord.ext import commands, tasks
import os
import datetime
import re
import requests
import psutil
import random
from flask import Flask
from threading import Thread

# --- 1. RENDER UCHUN WEB SERVER ---
app = Flask('')
@app.route('/')
def home(): return "MEGA TEAM Bot onlayn!"
def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive():
    t = Thread(target=run)
    t.start()

# --- 2. BOT SOZLAMALARI ---
intents = discord.Intents.default()
intents.members = True 
intents.message_content = True
intents.presences = True

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)
        self.log_channel_id = None 
        self.welcome_channel_id = None 

    async def setup_hook(self):
        # Global sinxronizatsiya
        await self.tree.sync()
        self.update_stats.start()
        print(f"✅ {self.user} sifatida tizimga kirildi!")
        print("✅ Slash komandalar global sinxronizatsiya qilindi!")

bot = MyBot()

# --- 3. AVTOMATIK STATISTIKA ---
@tasks.loop(minutes=10)
async def update_stats():
    for guild in bot.guilds:
        for channel in guild.voice_channels:
            if "A'zolar:" in channel.name:
                try:
                    await channel.edit(name=f"📊 A'zolar: {guild.member_count}")
                except Exception as e:
                    print(f"Statistika xatosi: {e}")

# --- 4. YORDAMCHI FUNKSIYALAR ---
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

# --- 5. VOQEALAR ---
@bot.event
async def on_member_join(member):
    if bot.welcome_channel_id:
        channel = member.guild.get_channel(bot.welcome_channel_id)
        if channel:
            await channel.send(f"Assalomu Aleykum {member.mention}, ''MEGA TEAM'' serveriga hush kelibsiz.")

# --- 6. SLASH KOMANDALAR ---

@bot.tree.command(name="server-info", description="Server haqida to'liq ma'lumot")
async def server_info(interaction: discord.Interaction):
    await interaction.response.defer() # 3 soniyalik limitni chetlab o'tish
    guild = interaction.guild
    online = len([m for m in guild.members if m.status != discord.Status.offline])
    embed = discord.Embed(title=f"{guild.name} | 📊", color=0x2f3136)
    embed.add_field(name="🆔 ID Сервера:", value=f"`{guild.id}`", inline=True)
    embed.add_field(name="📅 Создан:", value=f"{discord.utils.format_dt(guild.created_at, 'R')}", inline=True)
    embed.add_field(name="👑 Владелец:", value=f"{guild.owner.mention}", inline=True)
    embed.add_field(name="👤 Участники:", value=f"**({guild.member_count})**\n{online} В сети", inline=True)
    if guild.icon: embed.set_thumbnail(url=guild.icon.url)
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="weather", description="Ob-havo ma'lumoti")
@app_commands.describe(viloyat="Viloyatni tanlang")
@app_commands.choices(viloyat=[
    app_commands.Choice(name="Toshkent", value="Tashkent"),
    app_commands.Choice(name="Samarqand", value="Samarkand"),
    app_commands.Choice(name="Buxoro", value="Bukhara")
])
async def weather(interaction: discord.Interaction, viloyat: str):
    await interaction.response.defer()
    try:
        res = requests.get(f"https://wttr.in/{viloyat}?format=j1").json()
        curr = res['current_condition'][0]
        temp = curr['temp_C']
        embed = discord.Embed(title=f"🏙 {viloyat} ob-havosi", description=f"Harorat: **{temp}°C**", color=discord.Color.blue())
        await interaction.followup.send(embed=embed)
    except:
        await interaction.followup.send("❌ Ma'lumotni yuklashda xatolik.")

@bot.tree.command(name="avatar", description="Foydalanuvchi avatarini ko'rsatadi")
async def avatar(interaction: discord.Interaction, user: discord.Member = None):
    user = user or interaction.user
    embed = discord.Embed(title=f"{user.display_name} avatari", color=discord.Color.random())
    embed.set_image(url=user.display_avatar.url)
    await interaction.response.send_message(embed=embed)

# --- MODERATSIYA (Dinamik javoblar bilan) ---

@bot.tree.command(name="mute", description="Foydalanuvchini mute qilish")
@app_commands.checks.has_permissions(moderate_members=True)
async def mute(interaction: discord.Interaction, user: discord.Member, limit: str, sabab: str = "Ko'rsatilmadi"):
    await interaction.response.defer(ephemeral=True)
    d = parse_duration(limit)
    if not d: return await interaction.followup.send("❌ Vaqt formati noto'g'ri (misol: 10m, 1h).")
    try:
        await user.timeout(d, reason=sabab)
        await interaction.followup.send(f"🔇 {user.mention} {limit} ga cheklandi.")
        await send_log(interaction.guild, "🔇 Mute", f"Kim: {user}\nAdmin: {interaction.user}")
    except:
        await interaction.followup.send("❌ Botda ushbu foydalanuvchini mute qilish uchun yetarli huquq yo'q.")

@bot.tree.command(name="set-log", description="Log kanalini belgilash")
@app_commands.checks.has_permissions(administrator=True)
async def setlog(interaction: discord.Interaction):
    bot.log_channel_id = interaction.channel_id
    await interaction.response.send_message("✅ Audit Log kanali sozlandi!", ephemeral=True)

# --- QOLGAN KOMANDALARNI HAM SHU TARZDA DEFER BILAN QO'SHISH MUMKIN ---

if __name__ == "__main__":
    keep_alive()
    bot.run(os.getenv("DISCORD_TOKEN"))
