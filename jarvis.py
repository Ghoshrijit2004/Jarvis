#!/usr/bin/env python3
"""
JARVIS — Just A Rather Very Intelligent System
Built for Mac by Rijit Ghosh · Powered by Groq (LLaMA)
"""

import os, sys, json, subprocess, webbrowser, datetime, threading, time, re
from pathlib import Path

try:
    from groq import Groq
    HAS_GROQ = True
except ImportError:
    HAS_GROQ = False
    print("[JARVIS] Run: pip3 install groq")

try:
    import speech_recognition as sr
    HAS_SR = True
except ImportError:
    HAS_SR = False
    print("[JARVIS] Run: pip3 install SpeechRecognition pyaudio")

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

# ── Config ────────────────────────────────────────────────────────────────────
CONFIG_PATH = Path.home() / ".jarvis_config.json"
DEFAULT_CONFIG = {
    "groq_api_key": "",
    "weather_api_key": "",
    "city": "Kolkata",
    "wake_word": "jarvis",
    "voice": "Samantha",
    "speaking_rate": 190,
}

def load_config():
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH) as f:
            cfg = json.load(f)
        for k, v in DEFAULT_CONFIG.items():
            cfg.setdefault(k, v)
        return cfg
    return DEFAULT_CONFIG.copy()

def save_config(cfg):
    with open(CONFIG_PATH, "w") as f:
        json.dump(cfg, f, indent=2)

CONFIG = load_config()

# ── Voice Output ──────────────────────────────────────────────────────────────
def speak(text: str, wait: bool = True):
    clean = re.sub(r'[*_`#]', '', text)
    cmd = ["say", "-v", CONFIG["voice"], "-r", str(CONFIG["speaking_rate"]), clean]
    if wait: subprocess.run(cmd)
    else: subprocess.Popen(cmd)
    print(f"[JARVIS] {clean}")

# ── Voice Input ───────────────────────────────────────────────────────────────
def listen(timeout=5, phrase_limit=12):
    if not HAS_SR:
        return input("You: ").strip()

    r = sr.Recognizer()
    r.energy_threshold = 150            # sensitive — picks up normal speech
    r.dynamic_energy_threshold = False  # no auto-adjust (causes missed words)
    r.pause_threshold = 0.5             # balanced speed
    r.phrase_threshold = 0.2

    with sr.Microphone() as source:
        print("[JARVIS] Listening...")
        try:
            audio = r.listen(source, timeout=timeout, phrase_time_limit=phrase_limit)
            text = r.recognize_google(audio)
            print(f"[YOU] {text}")
            return text.lower()
        except sr.WaitTimeoutError:
            return None
        except sr.UnknownValueError:
            print("[JARVIS] Didn't catch that, Boss.")
            return None
        except Exception as e:
            print(f"[JARVIS] Error: {e}")
            return None

# ── AI Brain ──────────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are JARVIS, a witty and efficient AI assistant running on a Mac.
You were built by Rijit Ghosh, a Flutter developer and AI enthusiast from Kolkata, India.
Keep responses SHORT (1-3 sentences) unless asked for detail.
Be helpful, slightly witty, and occasionally call the user 'Boss' like the real JARVIS.
Never use markdown — you are speaking aloud."""

conversation_history = []

def ask_groq(user_input: str) -> str:
    if not HAS_GROQ or not CONFIG["groq_api_key"]:
        return "Please set your Groq API key. Run: python3 jarvis.py setup"
    try:
        client = Groq(api_key=CONFIG["groq_api_key"])
        conversation_history.append({"role": "user", "content": user_input})
        history = conversation_history[-10:]
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "system", "content": SYSTEM_PROMPT}] + history,
            max_tokens=150,
            temperature=0.7
        )
        reply = response.choices[0].message.content
        conversation_history.append({"role": "assistant", "content": reply})
        return reply
    except Exception as e:
        return f"AI error: {e}"

# ── Web Search (DuckDuckGo — no API key needed) ──────────────────────────────
def web_search(query: str) -> str:
    """Search using DuckDuckGo API — free, no key needed. Falls back to Groq knowledge."""
    try:
        # DuckDuckGo Instant Answers API
        url = f"https://api.duckduckgo.com/?q={query.replace(' ', '+')}&format=json&no_html=1&skip_disambig=1"
        r = requests.get(url, timeout=6, headers={"User-Agent": "Mozilla/5.0 JARVIS/1.0"})
        data = r.json()

        # 1. Instant answer (calculations, simple facts)
        if data.get("Answer"):
            return data["Answer"]

        # 2. Wikipedia abstract (who is, what is questions)
        if data.get("AbstractText"):
            text = data["AbstractText"]
            sentences = text.split(". ")
            return ". ".join(sentences[:2]) + "."

        # 3. Related topic snippet
        topics = data.get("RelatedTopics", [])
        for topic in topics:
            if isinstance(topic, dict) and topic.get("Text"):
                return topic["Text"][:250]

        # 4. Infobox data
        if data.get("Infobox"):
            content_list = data["Infobox"].get("content", [])
            facts = [f"{i.get('label')}: {i.get('value')}" for i in content_list[:3] if i.get("label")]
            if facts:
                return ". ".join(facts)

        # 5. Fallback to Groq LLaMA knowledge
        print("[JARVIS] No web result — using AI knowledge...")
        return ask_groq(f"Please answer this factual question accurately and concisely: {query}")

    except requests.exceptions.Timeout:
        return ask_groq(query)
    except Exception as e:
        print(f"[JARVIS] Web search error: {e}")
        return ask_groq(query)

def needs_web_search(text: str) -> bool:
    """Detect if query needs real-time or factual web data."""
    web_keywords = [
        "who is", "what is", "when did", "where is", "how many",
        "president", "prime minister", "ceo", "founder", "capital",
        "population", "latest", "current", "today", "news",
        "score", "match", "winner", "election", "price", "cost",
        "born", "died", "age of", "height of", "meaning of",
        "define", "explain", "tell me about", "what happened"
    ]
    t = text.lower()
    return any(kw in t for kw in web_keywords)

# ── Commands ──────────────────────────────────────────────────────────────────
def get_time():
    now = datetime.datetime.now()
    return f"It's {now.strftime('%I:%M %p')} on {now.strftime('%A, %B %d')}"

def get_weather():
    if not HAS_REQUESTS or not CONFIG["weather_api_key"]:
        return "Add a free OpenWeatherMap API key in your config for weather."
    try:
        city, key = CONFIG["city"], CONFIG["weather_api_key"]
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={key}&units=metric"
        data = requests.get(url, timeout=5).json()
        return f"It's {data['main']['temp']:.0f} degrees and {data['weather'][0]['description']} in {city}."
    except Exception as e:
        return f"Couldn't fetch weather: {e}"

def open_app(app_name):
    subprocess.Popen(["open", "-a", app_name])
    return f"Opening {app_name}."

def search_web(query):
    webbrowser.open(f"https://www.google.com/search?q={query.replace(' ', '+')}")
    return f"Searching for {query}."

def take_screenshot():
    path = Path.home() / f"Desktop/jarvis_{int(time.time())}.png"
    subprocess.run(["screencapture", str(path)])
    return "Screenshot saved to your Desktop."

def get_battery():
    try:
        out = subprocess.check_output(["pmset", "-g", "batt"], text=True)
        pct = re.search(r'(\d+)%', out)
        status = "charging" if "AC Power" in out else "on battery"
        return f"Battery is at {pct.group(1)} percent and {status}." if pct else "Couldn't read battery."
    except:
        return "Couldn't read battery status."

def set_reminder(text, minutes):
    def _remind():
        time.sleep(minutes * 60)
        speak(f"Boss, reminder: {text}")
        subprocess.run(["osascript", "-e",
            f'display notification "{text}" with title "JARVIS Reminder"'])
    threading.Thread(target=_remind, daemon=True).start()
    return f"Reminder set for {minutes} minutes, Boss."

def lock_screen():
    subprocess.run(["osascript", "-e",
        'tell application "System Events" to keystroke "q" using {command down, control down}'])
    return "Locking screen."

def empty_trash():
    subprocess.run(["osascript", "-e", 'tell application "Finder" to empty trash'])
    return "Trash emptied."

# ── Router ────────────────────────────────────────────────────────────────────
def route_command(text: str) -> str:
    t = text.lower().strip()
    if any(w in t for w in ["time", "date", "day", "clock"]):     return get_time()
    if any(w in t for w in ["weather", "temperature", "degrees"]): return get_weather()
    if "screenshot" in t:                                           return take_screenshot()
    if "battery" in t:                                              return get_battery()
    if "lock" in t and "screen" in t:                              return lock_screen()
    if "empty trash" in t or "clear trash" in t:                   return empty_trash()
    if "music" in t:                                                return open_app("Music")
    if t.startswith("open "):
        return open_app(t.replace("open ", "").strip().title())
    if t.startswith("search ") or t.startswith("google "):
        return search_web(re.sub(r'^(search|google)\s+', '', t))
    if "remind me" in t:
        m = re.search(r'remind me (?:to )?(.+?) in (\d+) minute', t)
        if m: return set_reminder(m.group(1), int(m.group(2)))
    if any(w in t for w in ["bye", "goodbye", "exit", "quit", "shutdown"]):
        speak("Goodbye Boss. JARVIS going offline.")
        sys.exit(0)

    # Web search for factual/real-time questions
    if needs_web_search(t):
        print("[JARVIS] Searching the web...")
        return web_search(text)

    # General AI conversation
    return ask_groq(text)

# ── Wake Word Loop ────────────────────────────────────────────────────────────
def wake_word_loop():
    wake = CONFIG["wake_word"].lower()
    print(f"\n[JARVIS] Say '{wake}' to activate  |  Ctrl+C to quit\n")
    while True:
        # Step 1: listen for wake word only
        heard = listen(timeout=None, phrase_limit=4)
        if not heard:
            continue

        # Check if wake word is in what was heard
        if wake not in heard:
            continue

        # Step 2: wake word detected — respond and wait
        print("[JARVIS] Wake word detected!")
        speak("Yes Boss?", wait=True)
        time.sleep(0.5)  # let mic fully settle

        # Step 3: listen specifically for the command
        print("[JARVIS] Awaiting command...")
        command = listen(timeout=8, phrase_limit=15)

        if command and command.strip():
            print(f"[ROUTING] >>> {command}")
            try:
                reply = route_command(command)
                print(f"[REPLY] {reply}")
                speak(reply, wait=True)
            except Exception as e:
                print(f"[ERROR] {e}")
                speak("Something went wrong Boss.", wait=True)
            time.sleep(0.3)
        else:
            speak("I didn't catch that. Say Jarvis again Boss.", wait=True)

# ── Text Loop ─────────────────────────────────────────────────────────────────
def text_loop():
    print("\n[JARVIS] Text mode  |  type 'bye' to quit\n")
    while True:
        try:
            user = input("You: ").strip()
            if not user: continue
            speak(route_command(user))
        except (KeyboardInterrupt, EOFError):
            speak("Goodbye Boss."); break

# ── Setup ─────────────────────────────────────────────────────────────────────
def setup():
    print("\n" + "═"*50 + "\n  JARVIS SETUP\n" + "═"*50)
    cfg = load_config()
    key = input("\nGroq API key (press Enter to keep current): ").strip()
    if key: cfg["groq_api_key"] = key
    weather_key = input("OpenWeatherMap API key (press Enter to keep/skip): ").strip()
    if weather_key: cfg["weather_api_key"] = weather_key
    city = input(f"Your city [{cfg['city']}]: ").strip()
    if city: cfg["city"] = city
    voice = input(f"Mac voice [{cfg['voice']}] (Samantha/Alex/Victoria/Karen): ").strip()
    if voice: cfg["voice"] = voice
    save_config(cfg)
    print("\n✅ Done! Run: python3 jarvis.py\n")

# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "setup":
        setup(); sys.exit(0)

    print("""
     ██╗ █████╗ ██████╗ ██╗   ██╗██╗███████╗
     ██║██╔══██╗██╔══██╗██║   ██║██║██╔════╝
     ██║███████║██████╔╝██║   ██║██║███████╗
██   ██║██╔══██║██╔══██╗╚██╗ ██╔╝██║╚════██║
╚█████╔╝██║  ██║██║  ██║ ╚████╔╝ ██║███████║
 ╚════╝ ╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚═╝╚══════╝
    Powered by Groq LLaMA · Built by Rijit Ghosh
    """)

    if not CONFIG["groq_api_key"]:
        print("⚠️  No API key! Run: python3 jarvis.py setup\n")

    speak("JARVIS online. How can I help you today, Boss?", wait=False)

    if "--text" in sys.argv or not HAS_SR:
        text_loop()
    else:
        try:
            wake_word_loop()
        except KeyboardInterrupt:
            speak("JARVIS going offline. Goodbye Boss.")
