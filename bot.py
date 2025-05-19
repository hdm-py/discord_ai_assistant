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

# Förbättrad traditionell FAQ-sökning
def search_faq(query, faq_data):
    query = query.lower().strip()
    exact_matches = []
    good_matches = []
    partial_matches = []
    
    for item in faq_data['faq']:
        for keyword in item['keywords']:
            keyword_lower = keyword.lower().strip()
            
            # 1. Exakt match (högsta prioritet)
            if keyword_lower == query:
                exact_matches.append((item, 3))  # Score: 3
                break
            
            # 2. Keyword innehåller hela query (bra match)
            elif query in keyword_lower and len(query) >= 3:
                good_matches.append((item, 2))  # Score: 2
                break
            
            # 3. Query innehåller keyword (sämre - kan ge fel resultat)
            elif keyword_lower in query and len(keyword_lower) >= 4:
                # Extra kontroll: undvik korta keywords som "ml", "g", "vg" i långa queries
                if len(keyword_lower) <= 2 and len(query) > 5:
                    continue  # Skippa korta keywords i långa queries
                partial_matches.append((item, 1))  # Score: 1
                break
        
        # Kontrollera även mot frågan själv (för bättre matchning)
        question_lower = item['question'].lower()
        if query in question_lower and len(query) >= 4:
            good_matches.append((item, 2))
    
    # Sortera och returnera bästa match
    all_matches = exact_matches + good_matches + partial_matches
    
    if all_matches:
        # Sortera efter score (högst först)
        all_matches.sort(key=lambda x: x[1], reverse=True)
        return all_matches[0][0]  # Returnera FAQ-item med högst score
    
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

VIKTIGA REGLER:
1. Svara ENDAST med FAQ-ID numret (t.ex. "7") eller "0" om ingen passar
2. Matcha EXAKT vad användaren frågar om, inte bara relaterade ämnen
3. Om användaren frågar "vad är machine learning" - leta efter frågor som SPECIFIKT handlar om machine learning/ML
4. Om användaren frågar "vad är CNN" - leta efter frågor specifikt om CNN
5. Var mycket selektiv - hellre svara "0" än matcha fel fråga

Vilket FAQ-ID passar EXAKT för denna fråga? Svara med numret eller 0:"""

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

# Generera AI-svar för frågor utanför FAQ - STRIKT KURS-FOKUS
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

VIKTIGT: Du ska ENDAST svara på frågor relaterade till AI/ML-kursen. Om frågan inte är relaterad till kursen, svara:
"Den frågan ligger utanför kursens omfattning. Jag hjälper bara med frågor om AI/ML-kursen. Använd !help för att se vad jag kan hjälpa med."

Instruktioner för kurs-relaterade frågor:
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
*Fokuserad på kurs-relaterade frågor*

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
- AI-genererade svar för kurs-relaterade frågor
- Semantisk förståelse av svenska och engelska
- Strikt fokus på AI/ML-kursen

**Exempel på frågor:**
`!fråga cursor`, `!fråga cnn`, `!fråga mario coins`
`!fråga hur fungerar transformers`, `!fråga vad är skillnaden mellan bias och varians`

Totalt {total_questions} frågor tillgängliga!

*Jag svarar bara på frågor relaterade till AI/ML-kursen.*"""
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
- Version: 2.1 (strikt kurs-fokus)

**Vad kan jag hjälpa till med?**
- Kursinformation och deadlines
- AI-begrepp och tekniker  
- Verktyg som Cursor och Colab
- Projektidéer och uppgifter
- Intelligent svar på kurs-relaterade frågor

**Teknisk fördjupning:**
- Lokal AI-integration med Ollama
- Semantisk sökning och matchning
- Multi-level svarsgenerering
- Strikt scope-begränsning till kursmaterial

**Begränsningar:**
- Svarar ENDAST på AI/ML-kurs relaterade frågor
- Hänvisar andra frågor till lämpliga kanaler

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
        await ctx.send("✅ Ollama AI fungerar! Model: llama3:latest\n🎯 Konfigurerad för strikt kurs-fokus")
    except Exception as e:
        await ctx.send(f"❌ Ollama AI ej tillgänglig: {e}")

# Hello kommando
@bot.command(name='hello')
async def hello(ctx):
    await ctx.send(f'Hej {ctx.author.mention}! Jag är din AI-kursassistent! 🤖\n✨ Nu förstärkt med lokal AI via Ollama!\n🎯 Jag hjälper dig med AI/ML-kursen.')

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

# Uppdaterat fråge-kommando med AI - FIXAD LOGIK
@bot.command(name='fråga')
async def ask_question(ctx, *, question):
    # Visa att boten "tänker"
    thinking_msg = await ctx.send("🤔 Tänker... (söker med AI)")
    
    faq_data = load_faq()
    
    # 1. Försök förbättrad traditionell FAQ-sökning först
    traditional_result = search_faq(question, faq_data)
    
    # 2. Om traditionell FAQ-sökning hittade något, använd det direkt
    if traditional_result:
        await thinking_msg.edit(content="✅ Hittade svar i FAQ!")
        response = f"""**{traditional_result['question']}**

{traditional_result['answer']}

*Kategori: {traditional_result['category'].replace('-', ' ').title()}*"""
        await ctx.send(response)
        return
    
    # 3. Om ingen traditionell match, försök AI-sökning
    ai_result, is_ai_match = await ai_search_faq(question, faq_data)
    if ai_result:
        await thinking_msg.edit(content="✅ Hittade svar med AI!")
        response = f"""**{ai_result['question']}** *(AI-hittad)*

{ai_result['answer']}

*Kategori: {ai_result['category'].replace('-', ' ').title()}*"""
        await ctx.send(response)
        return
    
    # 4. Om ingen FAQ-match, generera AI-svar (med kurs-fokus)
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