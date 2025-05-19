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

# Fråge-kommando
@bot.command(name='fråga')
async def ask_question(ctx, *, question):
    faq_data = load_faq()
    answer = search_faq(question, faq_data)
    
    if answer:
        await ctx.send(f"**{answer['question']}**\n{answer['answer']}")
    else:
        await ctx.send("Ingen matchning hittad. Försök med andra ord.")

# Kör bot
if __name__ == "__main__":
    bot.run(config.BOT_TOKEN)