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
        self.welcome_channel_id = None 

    async def setup_hook(self):
        await self.tree.sync()
        print("✅ MEGA TEAM Bot tayyor!")

bot = MyBot()

# --- 3. VOQEALAR (EVENTS) ---

@bot.event
async def on_member_join(member):
    if bot.welcome_channel_id:
        channel = member.guild.get_channel(bot.welcome_channel_id)
        if channel:
            # [ping user] , ''MEGA TEAM'' serveriga hush kelibsiz.
            await channel.send(f"Assalomu Aleykum {member.mention}, ''MEGA TEAM'' serveriga hush kelibsiz.")

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

# --- 5. SLASH KOMANDALAR ---

# /set-welcome
@bot.tree.command(name="set-welcome", description="Yangi foydalanuvchilarni kutib olish kanalini belgilash")
@app_commands.checks.has_permissions(administrator=True)
async def setwelcome(interaction: discord.Interaction):
    bot.welcome_channel_id = interaction.channel_id
    await interaction.response.send_message(f"✅ Welcome kanali belgilandi: <#{interaction.channel_id}>", ephemeral=True)

# /set-log
@bot.tree.command(name="set-log", description="Moderatsiya jurnali uchun kanalni belgilash")
@app_commands.checks.has_permissions(administrator=True)
async def setlog(interaction: discord.Interaction):
    bot.log_channel_id = interaction.channel_id
    await interaction.response.send_message(f"✅ Audit Log kanali belgilandi.", ephemeral=True)

# /weather - Viloyatlar bilan
@bot.tree.command(name="weather", description="O'zbekiston viloyatlari bo'yicha aniq ob-havo")
@app_commands.describe(viloyat="Viloyatni tanlang")
@app_commands.choices(viloyat=[
    app_commands.Choice(name="Toshkent", value="Tashkent"),
    app_commands.Choice(name="Samarqand", value="Samarkand"),
    app_commands.Choice(name="Buxoro", value="Bukhara"),
    app_commands.Choice(name="Andijon", value="Andijan"),
    app_commands.Choice(name="Farg'ona", value="Fergana"),
    app_commands.Choice(name="Namangan", value="Namangan"),
    app_commands.Choice(name="Xorazm", value="Urgench"),
    app_commands.Choice(name="Navoiy", value="Navoiy"),
    app_commands.Choice(name="Qashqadaryo", value="Karshi"),
    app_commands.Choice(name="Surxondaryo", value="Termez"),
    app_commands.Choice(name="Jizzax", value="Jizzakh"),
    app_commands.Choice(name="Sirdaryo", value="Guliston"),
    app_commands.Choice(name="Qoraqalpog'iston", value="Nukus")
])
async def weather(interaction: discord.Interaction, viloyat: str):
    await interaction.response.defer()
    try:
        # API kalitsiz ishlaydigan eng yaxshi servis
        res = requests.get(f"https://wttr.in/{viloyat}?format=j1").json()
        curr = res['current_condition'][0]
        temp = curr['temp_C']
        # Ob-havo tavsifi (ruscha yoki inglizcha)
        desc = curr['weatherDesc'][0]['value']
        hum = curr['humidity']
        wind = curr['windspeedKmph']

        embed = discord.Embed(title=f"🏙 {viloyat} viloyati", color=discord.Color.blue(), timestamp=datetime.datetime.now())
        embed.add_field(name="🌡 Harorat", value=f"**{temp}°C**", inline=True)
        embed.add_field(name="☁️ Holat", value=f"**{desc}**", inline=True)
        embed.add_field(name="💧 Namlik", value=f"**{hum}%**", inline=True)
        embed.add_field(name="🌬 Shamol", value=f"**{wind} km/soat**", inline=False)
        embed.set_footer(text="MEGA TEAM Weather Service")
        
        await interaction.followup.send(embed=embed)
    except:
        await interaction.followup.send("❌ Ob-havo ma'lumotlarini olishda xatolik yuz berdi.")

# /avatar
@bot.tree.command(name="avatar", description="Foydalanuvchi avatarini ko'rsatadi")
async def avatar(interaction: discord.Interaction, user: discord.Member = None):
    if user is None:
        user = interaction.user
    embed = discord.Embed(title=f"{user.display_name} avatari", color=discord.Color.random())
    embed.set_image(url=user.display_avatar.url)
    await interaction.response.send_message(embed=embed)

# /server-avatar
@bot.tree.command(name="server-avatar", description="Server avatarini ko'rsatadi")
async def server_avatar(interaction: discord.Interaction):
    if interaction.guild.icon:
        embed = discord.Embed(title=f"{interaction.guild.name} avatari", color=discord.Color.blue())
        embed.set_image(url=interaction.guild.icon.url)
        await interaction.response.send_message(embed=embed)
    else:
        await interaction.response.send_message("❌ Serverda icon yo'q.", ephemeral=True)

# /rules
@bot.tree.command(name="rules", description="Qoidalar kanalini ko'rsatadi")
async def rules(interaction: discord.Interaction):
    await interaction.response.send_message(f"📖 Server qoidalari bilan bu yerda tanishishingiz mumkin: <#1169316659392168076>")

# --- MODERATSIYA KOMANDALARI ---

@bot.tree.command(name="mute", description="Foydalanuvchini vaqtinchalik cheklash")
@app_commands.checks.has_permissions(moderate_members=True)
async def mute(interaction: discord.Interaction, user: discord.Member, limit: str, sabab: str = "Ko'rsatilmadi"):
    duration = parse_duration(limit)
    if not duration: return await interaction.response.send_message("❌ Xato vaqt!", ephemeral=True)
    await user.timeout(duration, reason=sabab)
    await interaction.response.send_message(f"🔇 {user.mention} {limit} ga mute qilindi.")
    await send_log(interaction.guild, "🔇 Mute", f"**Kim:** {user}\n**Admin:** {interaction.user}\n**Sabab:** {sabab}")

@bot.tree.command(name="kick", description="Foydalanuvchini haydash")
@app_commands.checks.has_permissions(kick_members=True)
async def kick(interaction: discord.Interaction, user: discord.Member, sabab: str = "Ko'rsatilmadi"):
    await user.kick(reason=sabab)
    await interaction.response.send_message(f"👢 {user.mention} haydaldi.")
    await send_log(interaction.guild, "👢 Kick", f"**Kim:** {user}\n**Admin:** {interaction.user}", discord.Color.red())

@bot.tree.command(name="ban", description="Foydalanuvchini ban qilish")
@app_commands.checks.has_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, user: discord.Member, sabab: str = "Ko'rsatilmadi"):
    await user.ban(reason=sabab)
    await interaction.response.send_message(f"🚫 {user.mention} ban qilindi.")
    await send_log(interaction.guild, "🚫 Ban", f"**Kim:** {user}\n**Admin:** {interaction.user}", discord.Color.dark_red())

@bot.tree.command(name="del", description="Xabarlarni o'chirish")
@app_commands.checks.has_permissions(administrator=True)
async def delete(interaction: discord.Interaction, soni: int):
    await interaction.response.defer(ephemeral=True)
    deleted = await interaction.channel.purge(limit=soni)
    await interaction.followup.send(f"🧹 {len(deleted)} ta xabar o'chirildi.")
    await send_log(interaction.guild, "🧹 Tozalash", f"**Soni:** {len(deleted)}\n**Admin:** {interaction.user}", discord.Color.blue())

# --- ISHGA TUSHIRISH ---
if __name__ == "__main__":
    keep_alive()
    bot.run(os.getenv("DISCORD_TOKEN"))
