# Discord AI Kursassistent 🤖

En intelligent Discord-bot som hjälper studenter få svar på frågor om AI/ML-kursen. Botten använder Ollama med LLaMA 3-modellen för att ge pedagogiska och hjälpsamma svar på svenska.

## ✨ Funktioner

- **Intelligent AI-svar**: Svarar på alla typer av AI/ML-frågor med hjälp av LLaMA 3
- **Kursspecifik kunskap**: Innehåller FAQ-databas med kursinfo, deadlines och betygskriterier
- **Naturligt språk**: Förstår frågor på svenska i naturligt språk
- **Alltid hjälpsam**: Ger aldrig "jag vet inte" som svar - hittar alltid något relevant att säga
- **Pedagogisk**: Förklarar tekniska koncept på ett lättförstått sätt

## 🚀 Snabbstart

### Förutsättningar

- Python 3.8+
- Discord Bot Token
- Ollama installerat med LLaMA 3-modellen

### Installation

1. **Klona repositoryt**:
   ```bash
   git clone https://github.com/yourusername/discord_ai_assistant.git
   cd discord_ai_assistant
   ```

2. **Installera dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Skapa .env-fil** med din Discord bot token:
   ```env
   BOT_TOKEN=your_discord_bot_token_here
   ```

4. **Installera och starta Ollama** med LLaMA 3:
   ```bash
   # Installera Ollama (https://ollama.ai)
   ollama pull llama3:latest
   ollama serve
   ```

5. **Kör botten**:
   ```bash
   python bot.py
   ```

## 🎯 Användning

### Grundläggande kommandon

- `!help` - Visa hjälpmeddelande
- `!info` - Information om botten
- `!ai-status` - Kontrollera AI-status
- `!hello` - Hälsning från botten

### Snabbkommandon

- `!deadline` - Visa projektdeadline
- `!betyg` - Visa betygskriterier

### Ställ frågor

Skriv bara din fråga efter `!` så svarar botten:

```
!vad är transformers?
!förklara deep learning för nybörjare
!skillnad mellan CNN och RNN?
!hur fungerar backpropagation?
!vad är PyTorch?
```

## 📚 Kursinnehåll

Botten har kunskap om:

- **Kursinfo**: Deadlines, betygskriterier, schema
- **AI/ML-koncept**: Transformers, CNN, RNN, Deep Learning
- **Matematik**: Linjäralgebra, calculus, backpropagation
- **Verktyg**: PyTorch, Cursor, AI-förstärkta IDEer
- **Projektidéer**: RAG-lösningar, chatbots, AI-spel

## 📁 Projektstruktur

```
discord_ai_assistant/
├── bot.py              # Huvudbottkod
├── config.py           # Konfiguration och miljövariabler
├── faq.json           # FAQ-databas med kursinfo
├── requirements.txt    # Python-dependencies
├── README.md          # Denna fil
└── .env               # Discord bot token (skapa själv)
```

## ⚙️ Konfiguration

### config.py
- `BOT_TOKEN`: Discord bot token från .env
- `COMMAND_PREFIX`: Kommandoprefix (standard: "!")
- `BOT_STATUS`: Bottstatus som visas i Discord

### faq.json
JSON-databas med kursspecifik information:
- Kursdatum och deadlines
- Betygskriterier
- Projektförslag
- Tekniska koncept
- Homework och assignments

## 🤖 AI-funktionalitet

### Ollama Integration
- Använder LLaMA 3-modellen via Ollama
- Intelligent promptengineering för pedagogiska svar
- Kombinerar FAQ-data med allmän AI-kunskap
- Svarar alltid på svenska

### Smarta funktioner
- Förstår synonymer och naturligt språk
- Anpassar svarslängd efter Discord-begränsningar
- Hanterar tekniska fel elegant
- Ger strukturerade och tydliga svar

## 🛠️ Utveckling

### Lägga till nya FAQ-frågor

Redigera `faq.json`:

```json
{
  "id": 13,
  "category": "ny-kategori",
  "keywords": ["nyckelord1", "nyckelord2"],
  "question": "Din fråga här?",
  "answer": "Ditt svar här"
}
```

### Anpassa AI-beteende

Redigera `generate_ai_answer()` funktionen i `bot.py` för att:
- Ändra prompt-instruktioner
- Justera svarslängd
- Lägga till nya kunskapsområden

## 📋 Systemkrav

- **Python**: 3.8 eller senare
- **Minne**: Minst 4GB RAM för Ollama
- **Disk**: ~5GB för LLaMA 3-modellen
- **Nätverk**: Internetanslutning för Discord API

## 🔧 Felsökning

### Vanliga problem

1. **Bot svarar inte**:
   - Kontrollera att bot token är korrekt
   - Verifiera bot-permissions i Discord

2. **AI svarar inte**:
   - Kontrollera att Ollama körs: `ollama serve`
   - Verifiera att LLaMA 3 är nedladdat: `ollama list`

3. **Import-fel**:
   - Installera dependencies: `pip install -r requirements.txt`

### Loggar och debugging

Botten loggar automatiskt:
- Startup-status för Ollama
- Command errors
- AI-genereringsfel

## 📄 Licens

Detta projekt är open source. Använd och modifiera fritt för utbildningssyfte.

## 🤝 Bidrag

Bidrag välkomnas! Skapa gärna pull requests för:
- Nya FAQ-frågor
- Förbättrade AI-prompts
- Buggfixar
- Nya funktioner

## 📞 Support

För frågor om botten eller teknisk support:
- Skapa en issue i GitHub-repositoryt
- Testa `!ai-status` kommandot för att diagnostisera AI-problem

---

*Utvecklad för AI/ML-kursen 2025 🎓*