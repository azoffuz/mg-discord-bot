import discord
from discord import app_commands
from discord.ext import commands, tasks
import os
import datetime
import re
import requests
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

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)
        self.log_channel_id = None 
        self.welcome_channel_id = None 

    async def setup_hook(self):
        await self.tree.sync()
        print(f"✅ {self.user} tayyor!")

bot = MyBot()

# --- 3. YORDAMCHI FUNKSIYALAR ---
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

# --- 4. VOQEALAR ---
@bot.event
async def on_member_join(member):
    if bot.welcome_channel_id:
        channel = member.guild.get_channel(bot.welcome_channel_id)
        if channel:
            await channel.send(f"Assalomu Aleykum {member.mention}, ''MEGA TEAM'' serveriga hush kelibsiz.")

# --- 5. SLASH KOMANDALAR ---

# /remove-role-from
@bot.tree.command(name="remove-role-from", description="1-rolni 2-roli bor a'zolardan olib tashlaydi")
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(
    target_role="Olib tashlanadigan rol (1-rol)",
    filter_role="Qaysi roli borlardan olib tashlansin? (2-rol)"
)
async def remove_role_from(interaction: discord.Interaction, target_role: discord.Role, filter_role: discord.Role):
    await interaction.response.defer(ephemeral=True)
    
    count = 0
    # Faqat filter_role ga ega bo'lgan a'zolar ichidan qidiramiz
    for member in filter_role.members:
        # Agar a'zoda olib tashlanishi kerak bo'lgan rol ham bo'lsa
        if target_role in member.roles:
            try:
                await member.remove_roles(target_role, reason=f"Filtr bo'yicha tozalandi: {filter_role.name}")
                count += 1
            except Exception as e:
                print(f"Xatolik {member.name} bilan: {e}")

    embed = discord.Embed(
        title="🧹 Rol filtri bajarildi",
        description=f"**{filter_role.mention}** roli bor a'zolardan **{target_role.mention}** roli olib tashlandi.",
        color=discord.Color.green()
    )
    embed.add_field(name="Natija:", value=f"**{count}** ta foydalanuvchidan rol olindi.")
    
    await interaction.followup.send(embed=embed)
    await send_log(interaction.guild, "🧹 Rol Filtr Tozalash", f"**Admin:** {interaction.user}\n**Olingan rol:** {target_role.name}\n**Filtr roli:** {filter_role.name}\n**Soni:** {count}")
    
# /server-info
@bot.tree.command(name="server-info", description="Server haqida to'liq ma'lumot")
async def server_info(interaction: discord.Interaction):
    await interaction.response.defer()
    guild = interaction.guild
    online = len([m for m in guild.members if m.status != discord.Status.offline])
    embed = discord.Embed(title=f"{guild.name} | 📊", color=0x2f3136)
    embed.add_field(name="🆔 ID:", value=f"`{guild.id}`", inline=True)
    embed.add_field(name="📅 Yaratilgan:", value=f"{discord.utils.format_dt(guild.created_at, 'R')}", inline=True)
    embed.add_field(name="👑 Ega:", value=f"{guild.owner.mention}", inline=True)
    embed.add_field(name="👤 A'zolar:", value=f"**({guild.member_count})**\n{online} Onlayn", inline=True)
    if guild.icon: embed.set_thumbnail(url=guild.icon.url)
    await interaction.followup.send(embed=embed)

# /roles
@bot.tree.command(name="roles", description="Server rollari ro'yxati")
async def roles_list(interaction: discord.Interaction):
    roles = sorted(interaction.guild.roles, key=lambda r: r.position, reverse=True)
    role_text = "\n".join([f"{r.name:<25} {len(r.members)} members" for r in roles if r.name != "@everyone"])
    role_text += f"\n{'@everyone':<25} {interaction.guild.member_count} members"
    await interaction.response.send_message(f"```\n{role_text[:1900]}\n```")

# /weather
@bot.tree.command(name="weather", description="Ob-havo ma'lumoti")
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
        res = requests.get(f"https://wttr.in/{viloyat}?format=j1").json()
        curr = res['current_condition'][0]
        temp = curr['temp_C']
        embed = discord.Embed(title=f"🏙 {viloyat} ob-havosi", description=f"Harorat: **{temp}°C**\nHolat: **{curr['weatherDesc'][0]['value']}**", color=discord.Color.blue())
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
    
# /clean-role
@bot.tree.command(name="clean-role", description="Belgilangan roldagi barcha a'zolardan rolni olib tashlaydi")
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(role="Tozalanadigan rolni tanlang")
async def clean_role(interaction: discord.Interaction, role: discord.Role):
    await interaction.response.defer(ephemeral=True) # Jarayon uzoq cho'zilishi mumkinligi uchun defer qilamiz
    
    count = 0
    members = role.members # Ushbu rolga ega barcha a'zolar ro'yxati
    
    if not members:
        return await interaction.followup.send(f"⚠️ **{role.name}** rolida hech kim yo'q.")

    for member in members:
        try:
            await member.remove_roles(role, reason=f"{interaction.user} tomonidan /clean-role ishlatildi")
            count += 1
        except Exception as e:
            print(f"Xatolik: {member.name} dan rolni olib bo'lmadi: {e}")

    await interaction.followup.send(f"✅ **{role.name}** roli {count} ta a'zodan muvaffaqiyatli olib tashlandi.")
    await send_log(interaction.guild, "🧹 Rol Tozalandi", f"**Rol:** {role.name}\n**Admin:** {interaction.user}\n**A'zolar soni:** {count}")
    
# --- MODERATSIYA KOMANDALARI ---

@bot.tree.command(name="mute", description="Foydalanuvchini mute qilish")
@app_commands.checks.has_permissions(moderate_members=True)
async def mute(interaction: discord.Interaction, user: discord.Member, limit: str, sabab: str = "Ko'rsatilmadi"):
    await interaction.response.defer(ephemeral=True)
    d = parse_duration(limit)
    if not d: return await interaction.followup.send("❌ Vaqt xato!")
    await user.timeout(d, reason=sabab)
    await interaction.followup.send(f"🔇 {user.mention} {limit} ga mute qilindi.")
    await send_log(interaction.guild, "🔇 Mute", f"**Kim:** {user}\n**Admin:** {interaction.user}")

@bot.tree.command(name="kick", description="Foydalanuvchini haydash")
@app_commands.checks.has_permissions(kick_members=True)
async def kick(interaction: discord.Interaction, user: discord.Member, sabab: str = "Ko'rsatilmadi"):
    await user.kick(reason=sabab)
    await interaction.response.send_message(f"👢 {user.mention} haydaldi.")

@bot.tree.command(name="ban", description="Foydalanuvchini ban qilish")
@app_commands.checks.has_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, user: discord.Member, sabab: str = "Ko'rsatilmadi"):
    await user.ban(reason=sabab)
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

# --- SOZLAMALAR ---

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

@bot.tree.command(name="coinflip", description="Tanga tashlash")
async def coinflip(interaction: discord.Interaction):
    res = random.choice(["Burgut 🦅", "Panjara 🪙"])
    await interaction.response.send_message(f"Natija: **{res}**")

# --- ISHGA TUSHIRISH ---
if __name__ == "__main__":
    keep_alive()
    bot.run(os.getenv("DISCORD_TOKEN"))
