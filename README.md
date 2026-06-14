# 🤖 JARVIS — Just A Rather Very Intelligent System

<div align="center">

![Python](https://img.shields.io/badge/Python-3.9+-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Groq](https://img.shields.io/badge/Groq-LLaMA_3.1-FF6B35?style=for-the-badge&logo=ai&logoColor=white)
![Mac](https://img.shields.io/badge/macOS-Compatible-000000?style=for-the-badge&logo=apple&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

> **"Good morning. I am J.A.R.V.I.S. — Just A Rather Very Intelligent System."**

A fully voice-activated AI assistant for Mac, powered by **Groq LLaMA 3.1**.  
Wake it with your voice, control your Mac, and have full AI conversations — all hands-free.

**Built by [Rijit Ghosh](https://ghoshrijit2004.github.io/Riju-Portfoliyo/) · Flutter Developer & AI Enthusiast**

</div>

---

## ✨ Features

- 🎙️ **Wake word detection** — just say "Jarvis" to activate
- 🧠 **AI conversations** — powered by Groq LLaMA 3.1 (ultra fast)
- 🖥️ **Mac system control** — open apps, screenshots, battery, lock screen
- ⏰ **Smart reminders** — voice-set reminders with Mac notifications
- 🌤️ **Live weather** — real-time weather for your city
- 🔍 **Web search** — search Google by voice
- 🗣️ **Mac native voice** — uses built-in TTS (no extra setup)
- ⚡ **Instant responses** — local commands need no internet

---

## 🚀 Quick Start

### 1. Install dependencies

```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install portaudio for microphone
brew install portaudio

# Install Python packages
pip3 install groq SpeechRecognition pyaudio requests
```

### 2. Get your free Groq API key

1. Go to **[console.groq.com](https://console.groq.com)**
2. Sign in with GitHub
3. Click **API Keys** → **Create API key**
4. Copy the key (starts with `gsk_...`)

### 3. Setup JARVIS

```bash
python3 jarvis.py setup
```

### 4. Run JARVIS

```bash
# Voice mode (recommended)
python3 jarvis.py

# Text mode (no mic needed)
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
| `"Jarvis, [anything]"` | Full AI conversation via LLaMA |

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
Local command? → Execute instantly (time/battery/apps/screenshot)
        ↓
Not local? → Send to Groq LLaMA 3.1 → AI responds
        ↓
Mac `say` command speaks the reply aloud
```

---

## ⚙️ Configuration

Config is stored at `~/.jarvis_config.json` (never committed to Git):

```json
{
  "groq_api_key": "gsk_...",
  "weather_api_key": "optional_openweathermap_key",
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
cd /path/to/jarvis && python3 jarvis.py
```
4. Save as `JARVIS.app`
5. **System Settings → General → Login Items** → add `JARVIS.app`

---

## 📦 Project Structure

```
jarvis/
├── jarvis.py          # Main brain — voice loop, AI, commands
├── requirements.txt   # Python dependencies
├── .gitignore         # Keeps API keys safe
└── README.md          # You are here
```

---

## 🛠️ Tech Stack

- **Python 3.9+** — core language
- **Groq API** — ultra-fast LLaMA 3.1 inference
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
- [ ] GUI dashboard

---

## 👨‍💻 Author

**Rijit Ghosh** — Flutter Developer & AI Enthusiast

[![Portfolio](https://img.shields.io/badge/Portfolio-Visit-000000?style=flat-square&logo=firefox&logoColor=white)](https://ghoshrijit2004.github.io/Riju-Portfoliyo/)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0077B5?style=flat-square&logo=linkedin&logoColor=white)](https://linkedin.com/in/rijit-ghosh-548017287)
[![GitHub](https://img.shields.io/badge/GitHub-Follow-181717?style=flat-square&logo=github&logoColor=white)](https://github.com/Ghoshrijit2004)

---

*If this project helped you, give it a ⭐ — it means a lot!*
