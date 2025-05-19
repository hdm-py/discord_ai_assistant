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

# Sök i FAQ baserat på nyckelord
def search_faq(query, faq_data):
    query = query.lower()
    
    for item in faq_data['faq']:
        for keyword in item['keywords']:
            if keyword.lower() in query:
                return item
    return None

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

# Help kommando
@bot.command(name='help')
async def help_command(ctx):
    help_text = """🤖 **AI Kursassistent - Hjälp**

**Grundläggande kommandon:**
- `!hello` - Hälsning från boten
- `!deadline` - Information om projektdeadline  
- `!help` - Visa denna hjälp
- `!info` - Information om boten

**Frågor från FAQ:**
- `!fråga [din fråga]` - Ställ frågor om kursen
- `!betyg` - Info om VG/G krav

**Exempel på frågor:**
`!fråga cursor`, `!fråga cnn`, `!fråga mario coins`

Totalt {len(load_faq()['faq'])} frågor tillgängliga!"""
    await ctx.send(help_text)

# Info kommando
@bot.command(name='info')
async def info_command(ctx):
    faq_data = load_faq()
    info_text = f"""ℹ️ **Om AI Kursassistent**

Jag är en Discord-bot som hjälper studenter med AI-kursen!

**Status:**
- Kunskapsbas: {len(faq_data['faq'])} frågor och svar
- Utvecklad för: AI-1 kurs 2025
- Version: 1.0

**Vad kan jag hjälpa till med?**
- Kursinformation och deadlines
- AI-begrepp och tekniker  
- Verktyg som Cursor och Colab
- Projektidéer och uppgifter

Använd `!help` för att se alla kommandon!"""
    await ctx.send(info_text)

# Hello kommando
@bot.command(name='hello')
async def hello(ctx):
    await ctx.send(f'Hej {ctx.author.mention}! Jag är din AI-kursassistent! 🤖')

# Deadline kommando
@bot.command(name='deadline')
async def deadline(ctx):
    faq_data = load_faq()
    for item in faq_data['faq']:
        if item['id'] == 1:  # Deadline frågan
            response = f"""**{item['question']}**

{item['answer']}

*Kategori: {item['category'].replace('-', ' ').title()}*"""
            await ctx.send(response)
            return
    await ctx.send("Deadline-information ej tillgänglig.")

# Betyg kommando
@bot.command(name='betyg')
async def betyg(ctx):
    faq_data = load_faq()
    for item in faq_data['faq']:
        if item['id'] == 2:  # Betyg frågan
            response = f"""**{item['question']}**

{item['answer']}

*Kategori: {item['category'].replace('-', ' ').title()}*"""
            await ctx.send(response)
            return
    await ctx.send("Betygsinformation ej tillgänglig.")

# Fråge-kommando
@bot.command(name='fråga')
async def ask_question(ctx, *, question):
    faq_data = load_faq()
    answer = search_faq(question, faq_data)
    
    if answer:
        response = f"""**{answer['question']}**

{answer['answer']}

*Kategori: {answer['category'].replace('-', ' ').title()}*"""
        await ctx.send(response)
    else:
        await ctx.send("Ingen matchning hittad. Försök med andra ord eller använd `!help` för att se alla kommandon.")

# Kör bot
if __name__ == "__main__":
    bot.run(config.BOT_TOKEN)