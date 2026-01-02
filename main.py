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
        await self.tree.sync()
        self.update_stats.start()
        print("✅ MEGA TEAM Bot barcha funksiyalar bilan ishga tushdi!")

bot = MyBot()

# --- 3. AVTOMATIK STATISTIKA (Har 10 daqiqada yangilanadi) ---
@tasks.loop(minutes=10)
async def update_stats():
    for guild in bot.guilds:
        for channel in guild.voice_channels:
            if "A'zolar:" in channel.name:
                try:
                    await channel.edit(name=f"📊 A'zolar: {guild.member_count}")
                except:
                    pass

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

# --- 5. VOQEALAR (WELCOME) ---
@bot.event
async def on_member_join(member):
    if bot.welcome_channel_id:
        channel = member.guild.get_channel(bot.welcome_channel_id)
        if channel:
            await channel.send(f"Assalomu Aleykum {member.mention}, ''MEGA TEAM'' serveriga hush kelibsiz.")

# --- 6. SLASH KOMANDALAR ---

# /server-info
@bot.tree.command(name="server-info", description="Server haqida to'liq ma'lumot")
async def server_info(interaction: discord.Interaction):
    guild = interaction.guild
    online = len([m for m in guild.members if m.status != discord.Status.offline])
    embed = discord.Embed(title=f"{guild.name} | ☃️", color=0x2f3136)
    embed.add_field(name="🆔 ID Сервера:", value=f"`{guild.id}`", inline=True)
    embed.add_field(name="📅 Создан:", value=f"{discord.utils.format_dt(guild.created_at, 'R')}", inline=True)
    embed.add_field(name="👑 Владелец:", value=f"{guild.owner.mention}", inline=True)
    embed.add_field(name="👤 Участники:", value=f"**({guild.member_count})**\n{online} В сети\n{guild.premium_subscription_count} Boosts ✨", inline=True)
    embed.add_field(name="💬 Каналы:", value=f"{len(guild.text_channels)} Текстовых | {len(guild.voice_channels)} Голосовых", inline=True)
    embed.add_field(name="🌎 Другое:", value=f"Уровень верификации: {guild.verification_level.value}", inline=True)
    embed.add_field(name="🔐 Роли:", value="Для просмотра списка используйте `/roles` ", inline=False)
    if guild.icon: embed.set_thumbnail(url=guild.icon.url)
    await interaction.response.send_message(embed=embed)

# /roles
@bot.tree.command(name="roles", description="Server rollari ro'yxati")
async def roles_list(interaction: discord.Interaction):
    roles = sorted(interaction.guild.roles, key=lambda r: r.position, reverse=True)
    role_text = "\n".join([f"{r.name:<25} {len(r.members)} members" for r in roles if r.name != "@everyone"])
    role_text += f"\n{'@everyone':<25} {interaction.guild.member_count} members"
    await interaction.response.send_message(f"```\n{role_text[:1900]}\n```")

# /weather
@bot.tree.command(name="weather", description="O'zbekiston viloyatlari bo'yicha ob-havo")
@app_commands.describe(viloyat="Viloyatni tanlang")
@app_commands.choices(viloyat=[
    app_commands.Choice(name="Toshkent", value="Tashkent"), app_commands.Choice(name="Samarqand", value="Samarkand"),
    app_commands.Choice(name="Buxoro", value="Bukhara"), app_commands.Choice(name="Andijon", value="Andijan"),
    app_commands.Choice(name="Farg'ona", value="Fergana"), app_commands.Choice(name="Namangan", value="Namangan"),
    app_commands.Choice(name="Xorazm", value="Urgench"), app_commands.Choice(name="Navoiy", value="Navoiy"),
    app_commands.Choice(name="Qashqadaryo", value="Karshi"), app_commands.Choice(name="Surxondaryo", value="Termez"),
    app_commands.Choice(name="Jizzax", value="Jizzakh"), app_commands.Choice(name="Sirdaryo", value="Guliston"),
    app_commands.Choice(name="Qoraqalpog'iston", value="Nukus")
])
async def weather(interaction: discord.Interaction, viloyat: str):
    await interaction.response.defer()
    try:
        res = requests.get(f"https://wttr.in/{viloyat}?format=j1").json()
        curr = res['current_condition'][0]
        embed = discord.Embed(title=f"🏙 {viloyat} viloyati", color=discord.Color.blue())
        embed.add_field(name="🌡 Harorat", value=f"**{curr['temp_C']}°C**", inline=True)
        embed.add_field(name="☁️ Holat", value=f"**{curr['weatherDesc'][0]['value']}**", inline=True)
        embed.add_field(name="💧 Namlik", value=f"**{curr['humidity']}%**", inline=True)
        await interaction.followup.send(embed=embed)
    except:
        await interaction.followup.send("❌ Ma'lumot olib bo'lmadi.")

# /avatar
@bot.tree.command(name="avatar", description="Foydalanuvchi avatarini ko'rsatadi")
async def avatar(interaction: discord.Interaction, user: discord.Member = None):
    user = user or interaction.user
    embed = discord.Embed(title=f"{user.display_name} avatari", color=discord.Color.random())
    embed.set_image(url=user.display_avatar.url)
    await interaction.response.send_message(embed=embed)

# /rules
@bot.tree.command(name="rules", description="Qoidalar kanalini ko'rsatadi")
async def rules(interaction: discord.Interaction):
    await interaction.response.send_message(f"📖 Server qoidalari: <#1169316659392168076>")

# --- MODERATSIYA KOMANDALARI ---

@bot.tree.command(name="mute", description="Foydalanuvchini mute qilish")
@app_commands.checks.has_permissions(moderate_members=True)
async def mute(interaction: discord.Interaction, user: discord.Member, limit: str, sabab: str = "Ko'rsatilmadi"):
    d = parse_duration(limit)
    if not d: return await interaction.response.send_message("❌ Vaqt xato!", ephemeral=True)
    await user.timeout(d, reason=sabab)
    await interaction.response.send_message(f"🔇 {user.mention} {limit} ga mute qilindi.")
    await send_log(interaction.guild, "🔇 Mute", f"**Kim:** {user}\n**Admin:** {interaction.user}\n**Vaqt:** {limit}")

@bot.tree.command(name="del-mute", description="Xabarni o'chirib mute qilish")
@app_commands.checks.has_permissions(administrator=True)
async def delmute(interaction: discord.Interaction, limit: str):
    target = None
    async for m in interaction.channel.history(limit=5):
        if m.author.id != bot.user.id: target = m; break
    if target:
        d = parse_duration(limit)
        await target.delete()
        await target.author.timeout(d)
        await interaction.response.send_message(f"🔇 {target.author.mention} o'chirildi va mute qilindi.")

@bot.tree.command(name="kick", description="Foydalanuvchini haydash")
@app_commands.checks.has_permissions(kick_members=True)
async def kick(interaction: discord.Interaction, user: discord.Member, sabab: str = "Ko'rsatilmadi"):
    await user.kick(reason=sabab)
    await interaction.response.send_message(f"👢 {user.mention} haydaldi.")

@bot.tree.command(name="del-kick", description="Xabarni o'chirib haydash")
@app_commands.checks.has_permissions(administrator=True)
async def delkick(interaction: discord.Interaction):
    target = None
    async for m in interaction.channel.history(limit=5):
        if m.author.id != bot.user.id: target = m; break
    if target:
        user = target.author
        await target.delete()
        await user.kick()
        await interaction.response.send_message(f"👢 {user.mention} haydaldi.")

@bot.tree.command(name="ban", description="Foydalanuvchini ban qilish")
@app_commands.checks.has_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, user: discord.Member, sabab: str = "Ko'rsatilmadi"):
    await user.ban(reason=sabab)
    await interaction.response.send_message(f"🚫 {user.mention} ban qilindi.")

@bot.tree.command(name="del-ban", description="Xabarni o'chirib ban qilish")
@app_commands.checks.has_permissions(administrator=True)
async def delban(interaction: discord.Interaction):
    target = None
    async for m in interaction.channel.history(limit=5):
        if m.author.id != bot.user.id: target = m; break
    if target:
        user = target.author
        await target.delete()
        await user.ban()
        await interaction.response.send_message(f"🚫 {user.mention} ban qilindi.")

@bot.tree.command(name="del-warn", description="Xabarni o'chirib ogohlantirish")
@app_commands.checks.has_permissions(administrator=True)
async def delwarn(interaction: discord.Interaction, message: str):
    target = None
    async for m in interaction.channel.history(limit=5):
        if m.author.id != bot.user.id: target = m; break
    if target:
        await target.delete()
        await interaction.response.send_message(f"⚠️ {target.author.mention}, {message}")

# --- SOZLAMALAR VA QIZIQARLI ---

@bot.tree.command(name="set-log", description="Log kanalini belgilash")
@app_commands.checks.has_permissions(administrator=True)
async def setlog(interaction: discord.Interaction):
    bot.log_channel_id = interaction.channel_id
    await interaction.response.send_message("✅ Audit Log sozlandi.", ephemeral=True)

@bot.tree.command(name="set-welcome", description="Welcome kanalini belgilash")
@app_commands.checks.has_permissions(administrator=True)
async def setwelcome(interaction: discord.Interaction):
    bot.welcome_channel_id = interaction.channel_id
    await interaction.response.send_message("✅ Welcome sozlandi.", ephemeral=True)

@bot.tree.command(name="stats-setup", description="Statistika kanalini yaratish")
@app_commands.checks.has_permissions(administrator=True)
async def stats_setup(interaction: discord.Interaction):
    category = await interaction.guild.create_category("📊 STATISTIKA")
    await interaction.guild.create_voice_channel(f"📊 A'zolar: {interaction.guild.member_count}", category=category)
    await interaction.response.send_message("✅ Statistika sozlandi.", ephemeral=True)

@bot.tree.command(name="coinflip", description="Tanga tashlash o'yini")
async def coinflip(interaction: discord.Interaction):
    res = random.choice(["Burgut 🦅", "Panjara 🪙"])
    await interaction.response.send_message(f"Natija: **{res}**")

# --- ISHGA TUSHIRISH ---
if __name__ == "__main__":
    keep_alive()
    bot.run(os.getenv("DISCORD_TOKEN"))
