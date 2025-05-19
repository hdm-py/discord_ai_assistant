import discord
from discord.ext import commands
import json
import config
import ollama
import re

# Läs FAQ-data
def load_faq():
    try:
        with open('faq.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("FAQ-fil inte hittad!")
        return {"faq": []}

# Traditionell FAQ-sökning
def search_faq(query, faq_data):
    query = query.lower()
    
    for item in faq_data['faq']:
        for keyword in item['keywords']:
            if keyword.lower() in query:
                return item
    return None

# AI-assisterad sökning med Ollama
async def ai_search_faq(query, faq_data):
    try:
        # Skapa kontext med alla FAQ-frågor
        faq_context = "\n".join([
            f"ID {item['id']}: {item['question']} (nyckelord: {', '.join(item['keywords'])})"
            for item in faq_data['faq']
        ])
        
        prompt = f"""Du är en AI-assistent som hjälper studenter hitta rätt FAQ-fråga.

Tillgängliga FAQ-frågor:
{faq_context}

Användarens fråga: "{query}"

Analysera användarens fråga och hitta det FAQ-ID som bäst matchar. Svara ENDAST med numret (t.ex. "5") eller "0" om ingen fråga passar bra.

Tänk på:
- Leta efter liknande begrepp och synonymer
- Förstå intentionen bakom frågan
- Svenska och engelska varianter av begrepp"""

        response = ollama.generate(
            model='llama3:latest',
            prompt=prompt,
            stream=False
        )
        
        # Försök extrahera FAQ-ID från svaret
        ai_response = response['response'].strip()
        
        # Hitta nummer i svaret
        numbers = re.findall(r'\b\d+\b', ai_response)
        
        if numbers:
            faq_id = int(numbers[0])
            if faq_id > 0:
                for item in faq_data['faq']:
                    if item['id'] == faq_id:
                        return item, True  # True = AI-matchning
        
        return None, False
        
    except Exception as e:
        print(f"Ollama AI-sökning misslyckades: {e}")
        return None, False

# Generera AI-svar för frågor utanför FAQ
async def generate_ai_answer(query, faq_data):
    try:
        # Skapa kunskapskontext från FAQ
        knowledge_base = "\n".join([
            f"- {item['question']}: {item['answer']}"
            for item in faq_data['faq']
        ])
        
        prompt = f"""Du är en AI-kursassistent för en AI/ML-kurs. Baserat på kursinformationen nedan, svara på studentens fråga.

Kursinformation från FAQ:
{knowledge_base}

Studentens fråga: "{query}"

Instruktioner:
- Svara på svenska
- Håll svaret kort och relevant (max 200 ord)
- Om frågan inte kan besvaras med kursinformationen, säg att du inte vet
- Referera till relevant kursmaterial när det är lämpligt
- Var hjälpsam och uppmuntrande

Svar:"""

        response = ollama.generate(
            model='llama3:latest',
            prompt=prompt,
            stream=False
        )
        
        return response['response'].strip()
        
    except Exception as e:
        print(f"AI-svarsgenerering misslyckades: {e}")
        return None

# Skapa bot instans
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=config.COMMAND_PREFIX, intents=intents)

# När bot startar
@bot.event
async def on_ready():
    print(f'{bot.user} är nu online!')
    
    # Testa Ollama-anslutning
    try:
        test_response = ollama.generate(
            model='llama3:latest',
            prompt="Test",
            stream=False
        )
        print("✅ Ollama fungerar!")
    except Exception as e:
        print(f"❌ Ollama-fel: {e}")
    
    # Skicka välkomstmeddelande till första kanalen boten kan skriva i
    for guild in bot.guilds:
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages:
                welcome_message = f"""🤖 **AI Kursassistent är nu online!**

Hej! Jag hjälper er med frågor om AI-kursen.

**✨ Nu med AI-stöd via Ollama! ✨**

**Skriv `!help` för att se alla kommandon!**

Låt oss börja! 🚀"""
                await channel.send(welcome_message)
                break
        break

bot.remove_command('help')

# Help kommando
@bot.command(name='help')
async def help_command(ctx):
    faq_data = load_faq()
    total_questions = len(faq_data['faq'])
    
    help_text = f"""🤖 **AI Kursassistent - Hjälp**

**Grundläggande kommandon:**
- `!hello` - Hälsning från boten
- `!deadline` - Information om projektdeadline  
- `!help` - Visa denna hjälp
- `!info` - Information om boten
- `!ai-status` - Kontrollera AI-status

**Frågor från FAQ:**
- `!fråga [din fråga]` - Ställ frågor om kursen (nu med AI!)
- `!betyg` - Info om VG/G krav

**✨ AI-förbättringar:**
- Intelligent matchning av frågor
- AI-genererade svar för frågor utanför FAQ
- Semantisk förståelse av svenska och engelska

**Exempel på frågor:**
`!fråga cursor`, `!fråga cnn`, `!fråga mario coins`
`!fråga hur fungerar transformers`, `!fråga vad är skillnaden mellan bias och varians`

Totalt {total_questions} frågor tillgängliga!"""
    await ctx.send(help_text)

# Info kommando
@bot.command(name='info')
async def info_command(ctx):
    faq_data = load_faq()
    info_text = f"""ℹ️ **Om AI Kursassistent**

Jag är en Discord-bot som hjälper studenter med AI-kursen!

**Status:**
- Kunskapsbas: {len(faq_data['faq'])} frågor och svar
- AI-motor: Ollama (lokal AI)
- Utvecklad för: AI-1 kurs 2025
- Version: 2.0 (med AI-stöd)

**Vad kan jag hjälpa till med?**
- Kursinformation och deadlines
- AI-begrepp och tekniker  
- Verktyg som Cursor och Colab
- Projektidéer och uppgifter
- Intelligent svar på komplicerade frågor

**Teknisk fördjupning:**
- Lokal AI-integration med Ollama
- Semantisk sökning och matchning
- Multi-level svarsgenerering

Använd `!help` för att se alla kommandon!"""
    await ctx.send(info_text)

# AI-status kommando
@bot.command(name='ai-status')
async def ai_status(ctx):
    try:
        test_response = ollama.generate(
            model='llama3:latest',
            prompt="Test connection",
            stream=False
        )
        await ctx.send("✅ Ollama AI fungerar! Model: llama3")
    except Exception as e:
        await ctx.send(f"❌ Ollama AI ej tillgänglig: {e}")

# Hello kommando
@bot.command(name='hello')
async def hello(ctx):
    await ctx.send(f'Hej {ctx.author.mention}! Jag är din AI-kursassistent! 🤖\n✨ Nu förstärkt med lokal AI via Ollama!')

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

# Uppdaterat fråge-kommando med AI
@bot.command(name='fråga')
async def ask_question(ctx, *, question):
    # Visa att boten "tänker"
    thinking_msg = await ctx.send("🤔 Tänker... (söker med AI)")
    
    faq_data = load_faq()
    
    # 1. Försök traditionell FAQ-sökning först
    traditional_result = search_faq(question, faq_data)
    
    # 2. Om ingen match, försök AI-sökning
    if not traditional_result:
        ai_result, is_ai_match = await ai_search_faq(question, faq_data)
        if ai_result:
            await thinking_msg.edit(content="✅ Hittade svar med AI!")
            response = f"""**{ai_result['question']}** *(AI-hittad)*

{ai_result['answer']}

*Kategori: {ai_result['category'].replace('-', ' ').title()}*"""
            await ctx.send(response)
            return
    
    # 3. Om FAQ-match finns, använd den
    if traditional_result:
        await thinking_msg.edit(content="✅ Hittade svar i FAQ!")
        response = f"""**{traditional_result['question']}**

{traditional_result['answer']}

*Kategori: {traditional_result['category'].replace('-', ' ').title()}*"""
        await ctx.send(response)
        return
    
    # 4. Om ingen FAQ-match, generera AI-svar
    await thinking_msg.edit(content="🧠 Genererar AI-svar...")
    ai_answer = await generate_ai_answer(question, faq_data)
    if ai_answer:
        await thinking_msg.edit(content="✅ AI-svar genererat!")
        response = f"""**AI-Svar:**

{ai_answer}

*Detta är ett AI-genererat svar baserat på kursmaterialet. För exakta detaljer, kolla kursdokumenten.*"""
        await ctx.send(response)
    else:
        await thinking_msg.edit(content="❌ Kunde inte hitta svar")
        await ctx.send("Tyvärr kunde jag inte hitta något svar på din fråga. Försök omformulera eller använd `!help` för att se tillgängliga kommandon.")

# Kör bot
if __name__ == "__main__":
    bot.run(config.BOT_TOKEN)