# 🤖 JARVIS — Just A Rather Very Intelligent System

<div align="center">

![Python](https://img.shields.io/badge/Python-3.9+-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Groq](https://img.shields.io/badge/Groq-LLaMA_3.1-FF6B35?style=for-the-badge&logo=ai&logoColor=white)
![Mac](https://img.shields.io/badge/macOS-Compatible-000000?style=for-the-badge&logo=apple&logoColor=white)
![Tkinter](https://img.shields.io/badge/GUI-Tkinter-3776AB?style=for-the-badge&logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

> **"Good morning. I am J.A.R.V.I.S. — Just A Rather Very Intelligent System."**

A fully voice-activated AI assistant for Mac, powered by **Groq LLaMA 3.1** — with a glowing animated HUD interface.  
Wake it with your voice, control your Mac, check live weather, and have full AI conversations — all hands-free.

**Built by [Rijit Ghosh](https://ghoshrijit2004.github.io/Riju-Portfoliyo/) · Flutter Developer & AI Enthusiast**

</div>

---

## 🎬 Two Ways to Run JARVIS

| Mode | File | Description |
|------|------|-------------|
| 🖥️ **GUI Mode** (recommended) | `jarvis_app.py` | Animated floating orb HUD, pulses & rotates with state |
| ⌨️ **Terminal Mode** | `jarvis.py` | Lightweight, runs fully in Terminal, no GUI overhead |

---

## ✨ Features

- 🎙️ **Wake word detection** — just say "Jarvis" to activate
- 🧠 **AI conversations** — powered by Groq LLaMA 3.1 (ultra fast)
- 🌐 **Real-time web search** — factual questions answered via DuckDuckGo + AI fallback
- 🗣️ **Multilingual** — understands and replies in English, Hindi, and Bengali, with matching native Mac voices
- 💙 **Friend mode** — if you're stressed or having a rough day, JARVIS drops the witty tone and talks like a real friend
- 🖥️ **Mac system control** — open apps, screenshots, battery, lock screen
- ⏰ **Smart reminders** — voice-set reminders with Mac notifications
- 🌤️ **Live weather** — real-time weather for your city via OpenWeatherMap
- 🔍 **Web search** — search Google by voice
- 🗣️ **Mac native voice** — uses built-in TTS (no extra setup)
- ⚡ **Instant responses** — local commands need no internet
- 🎨 **Animated HUD** — glowing rotating orb that changes color by state (idle/listening/thinking/speaking)
- 🖱️ **Draggable floating window** — always-on-top, move it anywhere on screen

---

## 🚀 Quick Start

### 1. Install dependencies

```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install portaudio for microphone
brew install portaudio

# Create a virtual environment (recommended on modern macOS)
python3 -m venv venv
source venv/bin/activate

# Install Python packages
pip install groq SpeechRecognition pyaudio requests
```

> 💡 If you plan to use GUI mode and Tkinter isn't bundled with your Python version:
> ```bash
> brew install python-tk
> ```

### 2. Get your free Groq API key

1. Go to **[console.groq.com](https://console.groq.com)**
2. Sign in with GitHub
3. Click **API Keys** → **Create API key**
4. Copy the key (starts with `gsk_...`)

### 3. (Optional) Get a free weather API key

1. Go to **[openweathermap.org/api](https://openweathermap.org/api)**
2. Sign up → **API keys** tab → copy your default key
3. ⏳ New keys take 10–15 minutes to activate

### 4. Setup JARVIS

```bash
python3 jarvis.py setup
```

You'll be asked for your Groq key, weather key (optional), city, and preferred Mac voice.

### 5. Run JARVIS

```bash
# GUI mode — animated floating orb (recommended)
python3 jarvis_app.py

# Terminal mode — text/voice in Terminal only
python3 jarvis.py

# Text mode — no microphone needed
python3 jarvis.py --text
```

---

## 🎙️ Voice Commands

| Command | What happens |
|---------|-------------|
| `"Jarvis, what time is it?"` | Current time & date |
| `"Jarvis, what's the weather?"` | Live weather for your city |
| `"Jarvis, take a screenshot"` | Saves to Desktop |
| `"Jarvis, open Safari"` | Opens any Mac app by name |
| `"Jarvis, search Flutter tutorials"` | Google search |
| `"Jarvis, what's my battery?"` | Battery % & charge status |
| `"Jarvis, remind me to eat in 30 minutes"` | Mac notification reminder |
| `"Jarvis, lock the screen"` | Locks your Mac |
| `"Jarvis, empty the trash"` | Empties Finder trash |
| `"Jarvis, play music"` | Opens Apple Music |
| `"Jarvis, who is the president of India?"` | Real-time web search answer |
| Speak in Hindi or Bengali | JARVIS replies in the same language, using a matching native voice |
| `"Jarvis, my mood isn't good today, things feel hectic"` | Switches to warm friend mode instead of generic assistant replies |
| `"Jarvis, [anything else]"` | Full AI conversation via LLaMA |

---

## 🧠 How it works

```
You say "Jarvis"
        ↓
Wake word detected
        ↓
JARVIS says "Yes Boss?"
        ↓
You give your command
        ↓
Local command? → Execute instantly (time/battery/apps/screenshot/weather)
        ↓
Factual question? → DuckDuckGo search → AI fallback if no result
        ↓
General chat? → Groq LLaMA 3.1 responds
        ↓
Mac `say` command speaks the reply aloud
        ↓
(GUI mode) Orb pulses orange while speaking, blue when idle
```

---

## 🗣️ Multilingual Voice Setup

JARVIS detects the script of its own reply and automatically switches Mac voices:

| Language | Mac Voice Used |
|----------|----------------|
| English | Your configured voice (e.g. `Samantha`, `Daniel`) |
| Hindi | `Lekha` |
| Bengali | `Priya` |

If a reply comes out sounding wrong, make sure these voices are downloaded on your Mac:

1. **System Settings → Accessibility → Spoken Content → System voice**
2. Click the voice dropdown → scroll to find **Hindi** and **Bengali** language groups
3. Click the download icon next to **Lekha** (Hindi) and **Priya** (Bengali)
4. If they don't appear, add Hindi/Bengali under **System Settings → General → Language & Region** first, then check the voice list again

Speech recognition also tries multiple languages automatically (English, then Hindi, then Bengali) so you can simply start talking in whichever language you're comfortable with.

---

## ⚙️ Configuration

Config is stored at `~/.jarvis_config.json` (never committed to Git):

```json
{
  "groq_api_key": "gsk_...",
  "weather_api_key": "your_openweathermap_key",
  "city": "Kolkata",
  "wake_word": "jarvis",
  "voice": "Samantha",
  "speaking_rate": 190
}
```

**Available Mac voices:** Samantha · Alex · Victoria · Karen · Moira

---

## 🚀 Auto-start on Mac Login

1. Open **Automator** → New Document → **Application**
2. Add **"Run Shell Script"**
3. Paste:
```bash
cd /path/to/jarvis && source venv/bin/activate && python3 jarvis_app.py
```
4. Save as `JARVIS.app`
5. **System Settings → General → Login Items** → add `JARVIS.app`

---

## 📦 Project Structure

```
jarvis/
├── jarvis.py          # Core brain — voice loop, AI, commands, web search
├── jarvis_app.py       # GUI wrapper — animated floating orb HUD
├── requirements.txt   # Python dependencies
├── .gitignore          # Keeps API keys safe
└── README.md           # You are here
```

---

## 🛠️ Tech Stack

- **Python 3.9+** — core language
- **Tkinter** — animated GUI orb interface
- **Groq API** — ultra-fast LLaMA 3.1 inference
- **DuckDuckGo Instant Answer API** — free real-time factual search
- **OpenWeatherMap API** — live weather data
- **SpeechRecognition** — Google Speech-to-Text
- **PyAudio** — microphone input
- **Mac `say` command** — native text-to-speech
- **osascript** — Mac system control

---

## 🔮 Roadmap

- [ ] Custom wake word training
- [ ] Spotify / Apple Music control
- [ ] WhatsApp message sending
- [ ] Email reading
- [ ] Smart home integration
- [ ] Sound effects (startup, activation chime)
- [ ] Menu bar mini-mode

---

## 👨‍💻 Author

**Rijit Ghosh** — Flutter Developer & AI Enthusiast from Kolkata, India 🇮🇳

[![Portfolio](https://img.shields.io/badge/Portfolio-Visit-000000?style=flat-square&logo=firefox&logoColor=white)](https://ghoshrijit2004.github.io/Riju-Portfoliyo/)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0077B5?style=flat-square&logo=linkedin&logoColor=white)](https://linkedin.com/in/rijit-ghosh-548017287)
[![GitHub](https://img.shields.io/badge/GitHub-Follow-181717?style=flat-square&logo=github&logoColor=white)](https://github.com/Ghoshrijit2004)

---

<div align="center">

⭐ **If this project helped you, give it a star — it means a lot!**

</div>
