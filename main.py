import os
import discord
from flask import Flask
import threading

# ---- Flask qismi (Render Web Service uchun) ----
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

# ---- Bot intents ----
intents = discord.Intents.default()
bot = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(bot)

# ---- Ready event ----
@bot.event
async def on_ready():
    await tree.sync()  # Slash komandalarni Discord bilan sinxron qilish
    print(f"✅ {bot.user} ishga tushdi!")

# ---- /ping komandasi ----
@tree.command(name="ping", description="Botning pingini ko'rsatadi")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f"🏓 Pong! `{round(bot.latency*1000)}ms`")

# ---- /channels komandasi ----
@tree.command(name="channels", description="Serverdagi barcha kanallar ro'yxatini chiqaradi")
async def channels(interaction: discord.Interaction):
    text_channels = [f"💬 {c.name}" for c in interaction.guild.text_channels]
    voice_channels = [f"🔊 {c.name}" for c in interaction.guild.voice_channels]

    result = "**📋 Server kanallari:**\n"
    if text_channels:
        result += "\n".join(text_channels) + "\n"
    if voice_channels:
        result += "\n" + "\n".join(voice_channels)

    await interaction.response.send_message(f"```\n{result}\n```")

# ---- Flaskni ishga tushirish ----
def run_flask():
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

threading.Thread(target=run_flask).start()

# ---- Botni ishga tushirish ----
bot.run(os.getenv("DISCORD_TOKEN"))
