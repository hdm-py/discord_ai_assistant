import discord
from discord.ext import commands
import json
import config

# Skapa bot instans
intents = discord.Intents.default()
intents.message_content = True
intents.guild_messages = True

bot = commands.Bot(command_prefix=config.COMMAND_PREFIX, intents=intents)

# När bot startar
@bot.event
async def on_ready():
    print(f'{bot.user} är nu online!')
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.watching, 
        name=config.BOT_STATUS
    ))

# Hello World kommando för test
@bot.command(name='hello')
async def hello(ctx):
    await ctx.send(f'Hej {ctx.author.mention}! Jag är din AI-kursassistent! 🤖')

# Kör bot
if __name__ == "__main__":
    bot.run(config.BOT_TOKEN)