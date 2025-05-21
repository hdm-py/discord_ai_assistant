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

# IMPROVED traditional FAQ search
def search_faq(query, faq_data):
    query = query.lower().strip()
    
    # Check if it's a complex/comparative question that AI should handle
    complex_indicators = [
        'skillnad', 'skillnader', 'mellan', 'jämför', 'jämförelse', 
        'vs', 'versus', 'kontra', 'mot', 'eller', 'förklara skillnad',
        'vad är bättre', 'vilken', 'hur skiljer', 'hur fungerar'
    ]
    
    # If the question contains comparative words, let AI handle it
    if any(indicator in query for indicator in complex_indicators):
        return None
    
    exact_matches = []
    good_matches = []
    partial_matches = []
    
    for item in faq_data['faq']:
        for keyword in item['keywords']:
            keyword_lower = keyword.lower().strip()
            
            # 1. Exact match (highest priority)
            if keyword_lower == query:
                exact_matches.append((item, 3))  # Score: 3
                break
            
            # 2. Query is in keyword (good match)
            elif query in keyword_lower and len(query) >= 2:
                good_matches.append((item, 2))  # Score: 2
                break
            
            # 3. Keyword is in query (weaker match)
            elif keyword_lower in query and len(keyword_lower) >= 3:
                # Extra check: avoid short keywords in long queries
                if len(keyword_lower) <= 2 and len(query) > 5:
                    continue  # Skip short keywords in long queries
                partial_matches.append((item, 1))  # Score: 1
                break
        
        # Also check against the question itself (for better matching)
        question_lower = item['question'].lower()
        if query in question_lower and len(query) >= 3:
            good_matches.append((item, 2))
    
    # Sort and return best match
    all_matches = exact_matches + good_matches + partial_matches
    
    if all_matches:
        # Sort by score (highest first)
        all_matches.sort(key=lambda x: x[1], reverse=True)
        return all_matches[0][0]  # Return FAQ item with highest score
    
    return None

# AI-assisted search with Ollama
async def ai_search_faq(query, faq_data):
    try:
        # Create context with all FAQ questions
        faq_context = "\n".join([
            f"ID {item['id']}: {item['question']} (keywords: {', '.join(item['keywords'])})"
            for item in faq_data['faq']
        ])
        
        prompt = f"""You are an AI assistant helping students find the right FAQ question.

Available FAQ questions:
{faq_context}

User's question: "{query}"

IMPORTANT RULES:
1. Answer ONLY with the FAQ ID number (e.g. "7") or "0" if none matches
2. Match EXACTLY what the user is asking about, not just related topics
3. If the user asks "what is machine learning" - look for questions that SPECIFICALLY deal with machine learning/ML
4. If the user asks "what is CNN" - look for questions specifically about CNN
5. Be very selective - better to answer "0" than match the wrong question

Which FAQ ID matches EXACTLY for this question? Answer with the number or 0:"""

        response = ollama.generate(
            model='llama3:latest',
            prompt=prompt,
            stream=False
        )
        
        # Try to extract FAQ ID from the answer
        ai_response = response['response'].strip()
        
        # Find numbers in the response
        numbers = re.findall(r'\b\d+\b', ai_response)
        
        if numbers:
            faq_id = int(numbers[0])
            if faq_id > 0:
                for item in faq_data['faq']:
                    if item['id'] == faq_id:
                        return item, True  # True = AI match
        
        return None, False
        
    except Exception as e:
        print(f"Ollama AI search failed: {e}")
        return None, False

# Generate AI answer for questions outside FAQ - STRICT COURSE FOCUS
async def generate_ai_answer(query, faq_data):
    try:
        # Create knowledge context from FAQ
        knowledge_base = "\n".join([
            f"- {item['question']}: {item['answer']}"
            for item in faq_data['faq']
        ])
        
        prompt = f"""You are an AI course assistant for an AI/ML course. Based on the course information below, answer the student's question.

Course information from FAQ:
{knowledge_base}

Student's question: "{query}"

IMPORTANT: You should ONLY answer questions related to the AI/ML course. If the question is not related to the course, answer:
"Den frågan ligger utanför kursens omfattning. Jag hjälper bara med frågor om AI/ML-kursen. Använd !help för att se vad jag kan hjälpa med."

Instructions for course-related questions:
- Answer in Swedish
- Keep the answer short and relevant (max 200 words)
- If the question cannot be answered with the course information, say you don't know
- Reference relevant course material when appropriate
- Be helpful and encouraging

Answer:"""

        response = ollama.generate(
            model='llama3:latest',
            prompt=prompt,
            stream=False
        )
        
        return response['response'].strip()
        
    except Exception as e:
        print(f"AI answer generation failed: {e}")
        return None

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
            prompt="Test",
            stream=False
        )
        print("✅ Ollama works!")
    except Exception as e:
        print(f"❌ Ollama error: {e}")
    
    # Send welcome message to the first channel the bot can write in
    for guild in bot.guilds:
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages:
                welcome_message = f"""🤖 **AI Kursassistent är nu online!**

Hej! Jag hjälper er med frågor om AI-kursen.

**✨ Nu med AI-stöd via Ollama! ✨**
*Fokuserad på kurs-relaterade frågor*

**Skriv `!help` för att se alla kommandon eller ställ frågor direkt!**

Låt oss börja! 🚀"""
                await channel.send(welcome_message)
                break
        break

bot.remove_command('help')

# Help command
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

**Frågor:**
- Ställ frågor direkt! (t.ex. "Vad är CNN?")
- `!betyg` - Info om VG/G krav

**✨ AI-förbättringar:**
- Intelligent matchning av frågor
- AI-genererade svar för kurs-relaterade frågor
- Semantisk förståelse av svenska och engelska
- Strikt fokus på AI/ML-kursen
- Smart hantering av jämförande frågor

**Exempel på frågor:**
`Vad är CNN?`, `När är deadline?`, `Vad är PyTorch?`
`Hur fungerar transformers?`, `Vad är skillnaden mellan bias och varians?`

Totalt {total_questions} frågor tillgängliga för fakta, AI svarar på allt annat!

*Jag svarar bara på frågor relaterade till AI/ML-kursen.*"""
    await ctx.send(help_text)

# Info command
@bot.command(name='info')
async def info_command(ctx):
    faq_data = load_faq()
    info_text = f"""ℹ️ **Om AI Kursassistent**

Jag är en Discord-bot som hjälper studenter med AI-kursen!

**Status:**
- Kunskapsbas: {len(faq_data['faq'])} frågor och svar
- AI-motor: Ollama (lokal AI)

**Vad kan jag hjälpa till med?**
- Kursinformation och deadlines
- AI-begrepp och tekniker  
- Verktyg som Cursor och Colab
- Projektidéer och uppgifter
- Intelligent svar på kurs-relaterade frågor
- Jämförelser mellan olika AI-koncept

**Teknisk fördjupning:**
- Lokal AI-integration med Ollama
- Semantisk sökning och matchning
- Multi-level svarsgenerering
- Smart detektering av komplexa frågor
- Strikt scope-begränsning till kursmaterial

**Begränsningar:**
- Svarar ENDAST på AI/ML-kurs relaterade frågor
- Hänvisar andra frågor till lämpliga kanaler

Använd `!help` för att se alla kommandon!"""
    await ctx.send(info_text)

# AI-status command
@bot.command(name='ai-status')
async def ai_status(ctx):
    try:
        test_response = ollama.generate(
            model='llama3:latest',
            prompt="Test connection",
            stream=False
        )
        await ctx.send("✅ Ollama AI fungerar! Model: llama3:latest")
    except Exception as e:
        await ctx.send(f"❌ Ollama AI ej tillgänglig: {e}")

# Hello command
@bot.command(name='hello')
async def hello(ctx):
    await ctx.send(f'Hej {ctx.author.mention}! Jag är din AI-kursassistent! 🤖\n✨ Nu förstärkt med lokal AI via Ollama!\n🎯 Jag hjälper dig med AI/ML-kursen.\n💬 Du kan ställa frågor direkt utan kommandon!')

# Deadline command
@bot.command(name='deadline')
async def deadline(ctx):
    faq_data = load_faq()
    for item in faq_data['faq']:
        if item['id'] == 1:  # Deadline question
            response = f"""**{item['question']}**

{item['answer']}

*Kategori: {item['category'].replace('-', ' ').title()}*"""
            await ctx.send(response)
            return
    await ctx.send("Deadline-information ej tillgänglig.")

# Grade command
@bot.command(name='betyg')
async def betyg(ctx):
    faq_data = load_faq()
    for item in faq_data['faq']:
        if item['id'] == 2:  # Grade question
            response = f"""**{item['question']}**

{item['answer']}

*Kategori: {item['category'].replace('-', ' ').title()}*"""
            await ctx.send(response)
            return
    await ctx.send("Betygsinformation ej tillgänglig.")

# Updated question command with AI - FIXED LOGIC and COMPLEX QUESTIONS
@bot.command(name='fråga')
async def ask_question(ctx, *, question):
    # Show that the bot is "thinking"
    thinking_msg = await ctx.send("🤔 Tänker... (analyserar fråga)")
    
    faq_data = load_faq()
    
    # Improved traditional FAQ search first
    # (Now automatically skips complex/comparative questions)
    traditional_result = search_faq(question, faq_data)
    
    # If traditional FAQ search found something, use it directly
    if traditional_result:
        await thinking_msg.edit(content="✅ Hittade svar i FAQ!")
        response = f"""**{traditional_result['question']}**

{traditional_result['answer']}

*Kategori: {traditional_result['category'].replace('-', ' ').title()}*"""
        await ctx.send(response)
        return
    
    # If no traditional match, try AI search
    await thinking_msg.edit(content="🔍 Söker med AI...")
    ai_result, is_ai_match = await ai_search_faq(question, faq_data)
    if ai_result:
        await thinking_msg.edit(content="✅ Hittade svar med AI!")
        response = f"""**{ai_result['question']}** *(AI-hittad)*

{ai_result['answer']}

*Kategori: {ai_result['category'].replace('-', ' ').title()}*"""
        await ctx.send(response)
        return
    
    # If no FAQ match, generate AI answer (with course focus)
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

# Event handler for all messages - NATURAL CONVERSATIONS
@bot.event
async def on_message(message):
    # Ignore messages from the bot itself
    if message.author == bot.user:
        return
    
    # Preserve command functionality
    await bot.process_commands(message)
    
    # If the message is already a command (starts with prefix), ignore
    if message.content.startswith(config.COMMAND_PREFIX):
        return
    
    # Check if the message is a question based on content or formatting
    question_indicators = ['?', 'vad', 'hur', 'varför', 'när', 'vilken', 'vem', 'vilket', 'berätta', 'förklara', 'what', 'how', 'why', 'when', 'which', 'who', 'explain']
    
    is_question = False
    content = message.content.lower()
    
    # Check if the message ends with '?'
    if content.endswith('?'):
        is_question = True
    
    # Check if the message starts with a question word
    for indicator in question_indicators:
        if content.startswith(indicator):
            is_question = True
            break
    
    # If it's a question, treat it as !fråga
    if is_question:
        # If the message is short, run direct response with thinking indicator
        if len(content) < 100:  # Max 100 characters for direct response
            # Simulate the question command with the same content
            ctx = await bot.get_context(message)
            await ask_question(ctx, question=content)

# Run bot
if __name__ == "__main__":
    bot.run(config.BOT_TOKEN)