import os
import discord
from discord.ext import commands
from flask import Flask

# ---- Flask qismi (Web Service uchun) ----
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

# ---- Discord bot qismi ----
intents = discord.Intents.default()
intents.guilds = True
intents.messages = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ {bot.user} ishga tushdi!")

@bot.command()
async def channels(ctx):
    chlist = "\n".join([f"📌 {c.name}" for c in ctx.guild.channels])
    await ctx.send(f"**{ctx.guild.name} kanallari:**\n```\n{chlist}\n```")

# ---- Botni va Flaskni birga ishga tushirish ----
import threading

def run_flask():
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

threading.Thread(target=run_flask).start()

bot.run(os.getenv("DISCORD_TOKEN"))
