import discord
from discord.ext import commands
import json
import config
import ollama
import re

# Load FAQ data
def load_faq():
    try:
        with open('faq.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("FAQ file not found!")
        return {"faq": []}

# Enhanced AI answer generation with comprehensive knowledge
async def generate_ai_answer(query, faq_data):
    try:
        # Create comprehensive knowledge base from FAQ
        knowledge_base = "\n\n".join([
            f"Fråga: {item['question']}\nSvar: {item['answer']}\nKategori: {item['category']}\nNyckelord: {', '.join(item['keywords'])}"
            for item in faq_data['faq']
        ])
        
        # Enhanced prompt with more context and clearer instructions
        prompt = f"""Du är en intelligent AI-kursassistent för en AI/ML-kurs på svenska. Du ska ALLTID ge ett hjälpsamt svar.

FULL KURSINFORMATION:
{knowledge_base}

EXTRA KUNSKAP:
- Cursor är en AI-förstärkt kodeditor/IDE som använder AI för att hjälpa med programmering
- AI-förstärkta IDEer använder språkmodeller för kodkomplettering, debugging och förklaringar
- Transformers är en neural nätverksarkitektur som revolutionerat NLP och AI
- CNN (Convolutional Neural Networks) används främst för bildanalys
- Perceptroner är enkla neurala nätverk med en eller få lager
- Backpropagation är algoritmen som tränar neurala nätverk genom att räkna gradienter baklänges

STUDENTENS FRÅGA: "{query}"

INSTRUKTIONER:
- Svara ALLTID på svenska med ett komplett och pedagogiskt svar
- Använd kursinformationen när den är relevant
- För allmänna AI/ML-frågor: ge tydliga, lätta att förstå förklaringar
- Förklara tekniska termer på ett enkelt sätt
- Håll svaret under 300 ord men gör det fullständigt
- Var uppmuntrande och hjälpsam
- Strukturera svaret tydligt

VIKTIGT: Ge ALDRIG svaret "jag vet inte" - hitta alltid något relevant att säga!

SVAR:"""

        response = ollama.generate(
            model='llama3:latest',
            prompt=prompt,
            stream=False
        )
        
        return response['response'].strip()
        
    except Exception as e:
        print(f"AI answer generation failed: {e}")
        return f"Tyvärr uppstod ett tekniskt fel med AI-svaret. Prova att ställa frågan igen eller använd !help för att se tillgängliga kommandon."

# Main question processing function - simplified without if-statements
async def process_question(ctx, question):
    thinking_msg = await ctx.send("🤔 Tänker...")
    
    faq_data = load_faq()
    
    # Always generate AI answer with all available information
    ai_answer = await generate_ai_answer(question, faq_data)
    
    await thinking_msg.edit(content="✅ Svar klart!")
    
    # Format response
    response = f"""**AI-svar:**

{ai_answer}

*Genererat av AI-kursassistent*"""
    
    # Handle Discord message length limit (2000 chars)
    if len(response) > 1900:
        max_answer_length = 1900 - len("**AI-svar:**\n\n") - len("\n\n*Genererat av AI-kursassistent*") - 10
        truncated_answer = ai_answer[:max_answer_length] + "..."
        response = f"""**AI-svar:**

{truncated_answer}

*Genererat av AI-kursassistent*"""
    
    await ctx.send(response)

# Create bot instance
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=config.COMMAND_PREFIX, intents=intents)

# When bot starts
@bot.event
async def on_ready():
    print(f'{bot.user} is now online!')
    
    # Test Ollama connection
    try:
        test_response = ollama.generate(
            model='llama3:latest',
            prompt="Hej, svara bara 'Ollama fungerar på svenska!'",
            stream=False
        )
        print("✅ Ollama fungerar!")
    except Exception as e:
        print(f"❌ Ollama error: {e}")
    
    # Send welcome message
    for guild in bot.guilds:
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages:
                welcome_message = f"""🤖 **AI Kursassistent är online!**

**Ställ frågor om AI/ML-kursen:**
• `!vad är llm?`
• `!förklara transformers`
• `!vad är CNN?`
• `!deadline`
• `!betyg`

**Kommandon:** `!help` `!info` `!ai-status` """
                await channel.send(welcome_message)
                break
        break

# Remove default help command
bot.remove_command('help')

# Simplified error handler - processes ALL unknown commands as questions
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        message_content = ctx.message.content
        if message_content.startswith(config.COMMAND_PREFIX):
            question_part = message_content[len(config.COMMAND_PREFIX):].strip()
            
            # Process ANY text after the prefix as a question
            await process_question(ctx, question_part)
            return
    
    # Log other errors
    print(f"Command error: {error}")

# Help command
@bot.command(name='help')
async def help_command(ctx):
    faq_data = load_faq()
    total_questions = len(faq_data['faq'])
    
    help_text = f"""🤖 **AI Kursassistent - Hjälp**

**Ställ VILKEN fråga som helst om AI/ML:**
• `!vad är cursor?`
• `!jag skulle vilja veta mer om en ai förstärkt ide`
• `!förklara deep learning för nybörjare`
• `!vad är skillnaden mellan CNN och RNN?`
• `!hur fungerar transformers?`
• `!deadline` - Kurs-specifik info
• `!betyg` - Betygskriterier

**System-kommandon:**
• `!help` - Visa denna hjälp
• `!info` - Information om botten
• `!ai-status` - Kontrollera AI-status

**Så här fungerar det:**
Skriv bara din fråga efter `!` så svarar jag med hjälp av kursinformation och AI-kunskap.

Totalt {total_questions} FAQ-frågor + obegränsad AI-kunskap! 🚀"""
    await ctx.send(help_text)

# Info command
@bot.command(name='info')
async def info_command(ctx):
    faq_data = load_faq()
    info_text = f"""ℹ️ **AI Kursassistent Info**

**Förmågor:**
• Svarar på ALLA frågor om AI/ML
• Använder både kurs-specifik FAQ-data och allmän AI-kunskap
• Förklarar tekniska koncept pedagogiskt
• Svarar alltid på svenska
• Hanterar både korta och långa frågor

**Teknisk info:**
• {len(faq_data['faq'])} FAQ-frågor i databasen
• Använder Ollama med llama3-modellen
• Förstår naturligt språk och synonymer
• Inga begränsningar på frågetyper

Testa att ställa vilken fråga som helst! 🎯"""
    await ctx.send(info_text)

# AI-status command
@bot.command(name='ai-status')
async def ai_status(ctx):
    try:
        test_response = ollama.generate(
            model='llama3:latest',
            prompt="Svara bara 'AI fungerar perfekt!' på svenska",
            stream=False
        )
        await ctx.send(f"✅ **AI-status: Online**\n🧠 Model: llama3")
    except Exception as e:
        await ctx.send(f"❌ **AI-status: Offline**\nFel: {e}")

# Hello command
@bot.command(name='hello')
async def hello(ctx):
    await ctx.send(f'Hej {ctx.author.mention}! 🤖\n\n✨ Jag är din AI-kursassistent!\n🧠 Ställ VILKEN fråga som helst om AI/ML\n💡 Exempel: `!vad är cursor?` eller `!jag skulle vilja veta mer om transformers`')

# Quick FAQ commands - these now also use the AI system
@bot.command(name='deadline')
async def deadline(ctx):
    await process_question(ctx, "deadline för projektet")

@bot.command(name='betyg')
async def betyg(ctx):
    await process_question(ctx, "betygskriterier VG och G")

# Event handler for messages
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    await bot.process_commands(message)

# Run bot
if __name__ == "__main__":
    bot.run(config.BOT_TOKEN)