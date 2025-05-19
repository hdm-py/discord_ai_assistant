# bot.py
import discord
from discord.ext import commands
import json
import config

# Läs FAQ-data
def load_faq():
    try:
        with open('faq.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("FAQ-fil inte hittad!")
        return {"faq": []}

# Skapa bot instans
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=config.COMMAND_PREFIX, intents=intents)

# När bot startar
@bot.event
async def on_ready():
    print(f'{bot.user} är nu online!')
    
    # Skicka välkomstmeddelande till första kanalen boten kan skriva i
    for guild in bot.guilds:
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages:
                welcome_message = f"""🤖 **AI Kursassistent är nu online!**

Hej! Jag hjälper er med frågor om AI-kursen.

**Skriv `!help` för att se alla kommandon!**

Låt oss börja! 🚀"""
                await channel.send(welcome_message)
                break
        break

bot.remove_command('help')

# Help kommando - nu med aliases
@bot.command(name='help', aliases=['hjälp', 'hjalp'])
async def help_command(ctx):
    help_text = """🤖 **AI Kursassistent - Hjälp**

**Tillgängliga kommandon:**
- `!hello` (eller `!hej`) - Hälsning från boten
- `!deadline` (eller `!tid`) - Information om projektdeadline  
- `!help` (eller `!hjälp`) - Visa denna hjälp

**Tips:** Du kan använda de kortare versionerna inom parentes!

Fler kommandon kommer snart!"""
    await ctx.send(help_text)

# Hello kommando - nu med aliases
@bot.command(name='hello', aliases=['hej'])
async def hello(ctx):
    await ctx.send(f'Hej {ctx.author.mention}! Jag är din AI-kursassistent! 🤖')

# Deadline kommando - nu med aliases
@bot.command(name='deadline', aliases=['tid'])
async def deadline(ctx):
    faq_data = load_faq()
    for item in faq_data['faq']:
        if item['id'] == 1:  # Första frågan är deadline
            # Förbättrat format med kategori
            response = f"""**{item['question']}**

{item['answer']}

*Kategori: {item['category'].replace('-', ' ').title()}*"""
            await ctx.send(response)
            return
    await ctx.send("Deadline-information ej tillgänglig.")

# Kör bot
if __name__ == "__main__":
    bot.run(config.BOT_TOKEN)