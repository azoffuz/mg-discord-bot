import discord
from discord.ext import commands

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

bot.run("TOKENINGIZNI_BU_YERGA_QO'YING")
