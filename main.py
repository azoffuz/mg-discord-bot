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
intents.members = True 
intents.message_content = True

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await self.tree.sync()
        print("✅ Slash komandalar sinxronizatsiya qilindi.")

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

# /ping
@bot.tree.command(name="ping", description="Bot tezligini tekshirish")
async def ping(interaction: discord.Interaction):
    latency = round(bot.latency * 1000)
    await interaction.response.send_message(f"🏓 Pong! {latency}ms")

# /delmute - Reply qilingan xabarni o'chirib, egasini mute qilish
@bot.tree.command(name="delmute", description="Xabarni o'chirib foydalanuvchini mute qilish")
@app_commands.checks.has_permissions(administrator=True)
async def delmute(interaction: discord.Interaction, limit: str):
    # Reply qilingan xabarni olish
    message = interaction.channel.last_message # Bu har doim ham aniq emas, shuning uchun quyidagicha tekshiramiz
    
    # Discord API orqali interaction kontekstini tekshirish
    target_msg = interaction.message # Agar bu context menu bo'lsa
    
    # Lekin slash komandada replyni aniqlash uchun bizga interaction.data kerak bo'ladi
    # Eng yaxshi yo'li: agar xabarga javob berib yozilsa
    resolved = interaction.data.get('resolved', {})
    
    # Mute muddatini aniqlash
    duration = parse_duration(limit)
    if not duration:
        return await interaction.response.send_message("❌ Xato format! Masalan: 10m, 1h", ephemeral=True)

    # Agar reply qilingan bo'lsa (Discord Slash Commands orqali reply qilingan xabarni ushlash)
    # Eslatma: Slash command ishlatilganda 'resolved' ichida xabarlar bo'lmasligi mumkin.
    # Shuning uchun foydalanuvchi qaysi xabarni o'chirishni xohlasa, Context Menu ishlatish qulayroq.
    # Lekin biz hozirgi slash komandani reply qilingan xabarga moslashtiramiz:
    
    reference = await interaction.channel.fetch_message(interaction.reference.message_id) if interaction.reference else None

    if reference:
        user = reference.author
        await reference.delete()
        try:
            await user.timeout(duration)
            await interaction.response.send_message(f"🔇 {user.mention}ning xabari o'chirildi va o'zi {limit}ga mute qilindi.")
        except:
            await interaction.response.send_message(f"⚠️ Xabar o'chirildi, lekin {user.mention}ni mute qilishga ruxsat yetmadi.")
    else:
        await interaction.response.send_message("❌ Iltimos, ushbu komandani biron bir xabarga **Javob berish (Reply)** orqali yozing!", ephemeral=True)

# /delwarn - Reply qilingan xabarni o'chirib ogohlantirish
@bot.tree.command(name="delwarn", description="Xabarni o'chirib ogohlantirish berish")
@app_commands.checks.has_permissions(administrator=True)
async def delwarn(interaction: discord.Interaction, message: str):
    if interaction.reference:
        target_msg = await interaction.channel.fetch_message(interaction.reference.message_id)
        user = target_msg.author
        await target_msg.delete()
        await interaction.response.send_message(f"⚠️ {user.mention}, {message}")
    else:
        await interaction.response.send_message("❌ Iltimos, biron bir xabarga **Reply** qiling!", ephemeral=True)

# /del
@bot.tree.command(name="del", description="Xabarlarni ommaviy o'chirish")
@app_commands.checks.has_permissions(administrator=True)
async def delete(interaction: discord.Interaction, soni: int):
    await interaction.channel.purge(limit=soni)
    await interaction.response.send_message(f"🧹 {soni} ta xabar tozalandi.", ephemeral=True)

# Xatoliklar
@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message("❌ Sizda adminlik huquqi yo'q!", ephemeral=True)

keep_alive()
bot.run(os.getenv("DISCORD_TOKEN"))
