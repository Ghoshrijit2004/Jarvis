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

# ── Active Language State ─────────────────────────────────────────────────────
# Explicit, user-controlled language mode. Defaults to English. Switched only
# by a direct voice command ("Jarvis, switch to Hindi/English") —
# no automatic per-sentence guessing, since that proved unreliable.
current_language = "en"

LANGUAGE_NAMES = {"en": "English", "hi": "Hindi"}
RECOGNIZER_CODE = {"en": "en-IN", "hi": "hi-IN"}

def set_language(lang: str):
    global current_language
    current_language = lang

# ── Voice Output ──────────────────────────────────────────────────────────────
# Mac voice that can speak Hindi properly (built into macOS)
VOICE_FOR_LANG = {
    "hi": "Lekha",     # Hindi voice on macOS
    "en": None,        # use whatever the user configured (e.g. Samantha/Daniel)
}


def detect_script(text: str) -> str:
    """Roughly detect Hindi (Devanagari) script vs default English."""
    for ch in text:
        code = ord(ch)
        if 0x0900 <= code <= 0x097F:   # Devanagari block → Hindi
            return "hi"
    return "en"

def speak(text: str, wait: bool = True, lang: str = None):
    """If lang is given ('en'/'hi') it's trusted directly.
    Otherwise falls back to guessing from the script of the text."""
    clean = re.sub(r'[*_`#]', '', text)
    detected = lang or detect_script(clean)
    voice = VOICE_FOR_LANG.get(detected) or CONFIG["voice"]
    cmd = ["say", "-v", voice, "-r", str(CONFIG["speaking_rate"]), clean]
    if wait: subprocess.run(cmd)
    else: subprocess.Popen(cmd)
    print(f"[JARVIS] {clean}")

# ── Voice Input ───────────────────────────────────────────────────────────────
# Languages JARVIS tries when transcribing your speech.
# It attempts each in order and keeps the first one that doesn't error out.
def listen_for_wake_word(timeout=None, phrase_limit=4):
    """Special listener used ONLY for catching the wake word ('Jarvis').

    Unlike listen(), this tries English first regardless of current_language,
    since the wake word is a name and en-IN reliably catches "Jarvis" even
    when JARVIS is currently in Hindi mode. We also try the current language
    as a fallback in case it's caught the Hindi script form instead
    (जार्विस), which is already handled by is_wake_word().
    """
    if not HAS_SR:
        return input("You: ").strip()

    r = sr.Recognizer()
    r.energy_threshold = 150
    r.dynamic_energy_threshold = False
    r.pause_threshold = 0.5
    r.phrase_threshold = 0.2

    with sr.Microphone() as source:
        print(f"[JARVIS] Listening for wake word...")
        try:
            audio = r.listen(source, timeout=timeout, phrase_time_limit=phrase_limit)
        except sr.WaitTimeoutError:
            return None

    # Try English first (most reliable for catching "Jarvis" by name),
    # then fall back to whatever language mode is currently active.
    tried_codes = ["en-IN"]
    current_code = RECOGNIZER_CODE[current_language]
    if current_code not in tried_codes:
        tried_codes.append(current_code)

    for lang_code in tried_codes:
        try:
            text = r.recognize_google(audio, language=lang_code)
            print(f"[HEARD] ({lang_code}) {text}")
            return text.lower()
        except sr.UnknownValueError:
            continue
        except Exception as e:
            print(f"[JARVIS] Error: {e}")
            return None

    return None

def listen(timeout=5, phrase_limit=12):
    """Returns a tuple: (text, lang_code).

    Uses the explicitly-set `current_language` instead of guessing — free
    speech APIs don't give reliable per-utterance language confidence, so
    JARVIS only switches language when you tell it to (see set_language()).
    """
    if not HAS_SR:
        return input("You: ").strip(), current_language

    r = sr.Recognizer()
    r.energy_threshold = 150
    r.dynamic_energy_threshold = False
    r.pause_threshold = 0.5
    r.phrase_threshold = 0.2

    with sr.Microphone() as source:
        print(f"[JARVIS] Listening... (mode: {LANGUAGE_NAMES[current_language]})")
        try:
            audio = r.listen(source, timeout=timeout, phrase_time_limit=phrase_limit)
        except sr.WaitTimeoutError:
            return None, None

    lang_code = RECOGNIZER_CODE[current_language]
    try:
        text = r.recognize_google(audio, language=lang_code)
        print(f"[HEARD] ({lang_code}) {text}")
        return text.lower(), current_language
    except sr.UnknownValueError:
        print("[JARVIS] Didn't catch that, Boss.")
        return None, None
    except Exception as e:
        print(f"[JARVIS] Error: {e}")
        return None, None


# ── AI Brain ──────────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are JARVIS, a witty and efficient AI assistant running on a Mac.
You were built by Rijit Ghosh, a Flutter developer and AI enthusiast from Kolkata, India.

LANGUAGE:
You can speak English and Hindi. Always follow the explicit language
instruction given to you for each message — never guess the language from the
user's wording, since speech recognition may transliterate things oddly.
Keep responses SHORT (1-3 sentences) unless asked for detail.

PERSONALITY:
Be helpful, slightly witty, and occasionally call the user 'Boss' like the real JARVIS.
Never use markdown — you are speaking aloud.

EMOTIONAL SUPPORT MODE:
If the user says they feel stressed, sad, tired, anxious, their mood is off, or things feel hectic,
drop the witty JARVIS tone and talk like a genuine close friend who actually cares.
Be warm, validate how they feel first before offering any suggestion, and keep it natural and human —
not clinical, not a generic listicle of tips. One or two small, realistic suggestions are enough
(like taking a short break, stepping outside, talking to someone, or just resting) — don't lecture.
Never minimize their feelings or rush to "fix" them. If they seem to be going through something serious
or ongoing, gently encourage them to talk to someone they trust or a counselor, without being preachy."""


conversation_history = []

def ask_groq(user_input: str) -> str:
    if not HAS_GROQ or not CONFIG["groq_api_key"]:
        return "Please set your Groq API key. Run: python3 jarvis.py setup"
    try:
        client = Groq(api_key=CONFIG["groq_api_key"])
        conversation_history.append({"role": "user", "content": user_input})
        history = conversation_history[-10:]

        lang_instruction = f"\n\nIMPORTANT: The user's current language mode is {LANGUAGE_NAMES[current_language]}. Reply ONLY in {LANGUAGE_NAMES[current_language]}, regardless of what language this message is written in."

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "system", "content": SYSTEM_PROMPT + lang_instruction}] + history,
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
# Switch-command keywords in every script, since once JARVIS is in Hindi
# mode the recognizer will return Devanagari script, not Roman letters.
SWITCH_TRIGGERS = [
    "switch to", "speak in", "switch language",       # English
    "स्विच", "में बात", "भाषा बदल",                      # Hindi
]
HINDI_TRIGGERS   = ["hindi", "हिंदी", "हिन्दी"]
ENGLISH_TRIGGERS = ["english", "इंग्लिश", "अंग्रेजी"]

def route_command(text: str) -> str:
    t = text.lower().strip()

    # Explicit language mode switching — checked across all scripts
    if any(trigger in t for trigger in SWITCH_TRIGGERS):
        if any(w in t for w in HINDI_TRIGGERS):
            set_language("hi")
            return "ठीक है बॉस, अब हिंदी में बात करता हूँ।"
        if any(w in t for w in ENGLISH_TRIGGERS):
            set_language("en")
            return "Alright Boss, switching back to English."

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

# ── Wake Word Matching (multi-script) ─────────────────────────────────────────
# "Jarvis" transliterated/written across the languages JARVIS listens in,
# since whichever recognizer fires first determines the script we get back.
WAKE_WORD_VARIANTS = [
    "jarvis",       # English
    "जार्विस",       # Hindi (Devanagari)
    "jarbis", "jarwis", "jervis",  # common mishears/spellings
]

def is_wake_word(heard: str, configured_wake: str) -> bool:
    heard = heard.lower().strip()
    variants = set(WAKE_WORD_VARIANTS)
    variants.add(configured_wake.lower())
    return any(v in heard for v in variants)

# ── Wake Word Loop ────────────────────────────────────────────────────────────
def wake_word_loop():
    wake = CONFIG["wake_word"].lower()
    print(f"\n[JARVIS] Say '{wake}' to activate  |  Ctrl+C to quit\n")
    while True:
        # Step 1: listen for wake word only — uses the dedicated multi-language
        # listener so "Jarvis" is caught regardless of current language mode
        heard = listen_for_wake_word(timeout=None, phrase_limit=4)
        if not heard:
            continue

        # Check if wake word is in what was heard (any supported script)
        if not is_wake_word(heard, wake):
            continue

        # Step 2: wake word detected — respond and wait
        print("[JARVIS] Wake word detected!")
        speak("Yes Boss?", wait=True)
        time.sleep(0.5)  # let mic fully settle

        # Step 3: listen specifically for the command
        print("[JARVIS] Awaiting command...")
        command, cmd_lang = listen(timeout=8, phrase_limit=15)

        if command and command.strip():
            print(f"[ROUTING] >>> {command}  (lang={cmd_lang})")
            try:
                reply = route_command(command)
                print(f"[REPLY] {reply}")
                # Speak the reply in the SAME language the command was spoken in
                speak(reply, wait=True, lang=cmd_lang)
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
