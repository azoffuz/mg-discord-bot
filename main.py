import os
import discord
from discord.ext import commands
from flask import Flask
import threading

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ {bot.user} ishga tushdi!")

# ---- Slash Command ----
@bot.tree.command(name="channels", description="Serverdagi barcha kanallar ro'yxatini ko'rsatadi")
async def channels(interaction: discord.Interaction):
    chlist = "\n".join([f"📌 {c.name}" for c in interaction.guild.channels])
    await interaction.response.send_message(
        f"**{interaction.guild.name} kanallari:**\n```\n{chlist}\n```"
    )

def run_flask():
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

threading.Thread(target=run_flask).start()

bot.run(os.getenv("DISCORD_TOKEN"))
