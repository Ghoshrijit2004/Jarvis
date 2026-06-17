#!/usr/bin/env python3
"""
JARVIS GUI — Floating AI Assistant for Mac
Run this instead of jarvis.py for the visual experience
"""

import tkinter as tk
from tkinter import font as tkfont
import threading
import math
import time
import subprocess
import sys
import os
from pathlib import Path

# Add jarvis directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Import core jarvis brain
from jarvis import load_config, speak, listen, route_command

CONFIG = load_config()

class JARVISApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("JARVIS")
        self.root.overrideredirect(True)          # no title bar
        self.root.attributes('-topmost', True)     # always on top
        self.root.attributes('-alpha', 0.0)        # start invisible
        self.root.configure(bg='#000000')

        # Window size & center position
        W, H = 420, 420
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = (sw - W) // 2
        y = (sh - H) // 2
        self.root.geometry(f"{W}x{H}+{x}+{y}")

        # Make window rounded/transparent on Mac
        try:
            self.root.attributes('-transparent', True)
            self.root.configure(bg='systemTransparent')
        except:
            self.root.configure(bg='#000010')

        self.state = "idle"       # idle | listening | thinking | speaking
        self.angle = 0
        self.pulse = 0
        self.rings = [0, 0.33, 0.66]
        self.text_queue = []

        self._build_ui(W, H)
        self._init_orb_items()
        self._start_animation()
        self._fade_in()
        self._start_jarvis()

    def _build_ui(self, W, H):
        # Canvas for animated orb
        self.canvas = tk.Canvas(
            self.root, width=W, height=H,
            bg='#000010', highlightthickness=0
        )
        self.canvas.pack(fill='both', expand=True)

        # Status text at bottom
        self.status_var = tk.StringVar(value="JARVIS ONLINE")
        self.status_label = tk.Label(
            self.canvas, textvariable=self.status_var,
            font=('Courier New', 11, 'bold'),
            fg='#00D4FF', bg='#000010'
        )
        self.status_label.place(relx=0.5, rely=0.82, anchor='center')

        # Subtitle / response text
        self.reply_var = tk.StringVar(value="Say 'Jarvis' to activate")
        self.reply_label = tk.Label(
            self.canvas, textvariable=self.reply_var,
            font=('Courier New', 9),
            fg='#4488AA', bg='#000010',
            wraplength=340, justify='center'
        )
        self.reply_label.place(relx=0.5, rely=0.91, anchor='center')

        # Close button (top right)
        close_btn = tk.Label(
            self.canvas, text='✕',
            font=('Arial', 13), fg='#334455', bg='#000010',
            cursor='hand2'
        )
        close_btn.place(relx=0.93, rely=0.04, anchor='center')
        close_btn.bind('<Button-1>', lambda e: self._shutdown())
        close_btn.bind('<Enter>', lambda e: close_btn.config(fg='#FF4466'))
        close_btn.bind('<Leave>', lambda e: close_btn.config(fg='#334455'))

        # Drag to move
        self.canvas.bind('<Button-1>', self._start_drag)
        self.canvas.bind('<B1-Motion>', self._drag)
        self._drag_x = 0
        self._drag_y = 0

    def _start_drag(self, e):
        self._drag_x = e.x
        self._drag_y = e.y

    def _drag(self, e):
        dx = e.x - self._drag_x
        dy = e.y - self._drag_y
        x = self.root.winfo_x() + dx
        y = self.root.winfo_y() + dy
        self.root.geometry(f"+{x}+{y}")

    def _get_colors(self):
        if self.state == "idle":
            return '#001830', '#003366', '#00D4FF', '#0088CC'
        elif self.state == "listening":
            return '#001830', '#004400', '#00FF88', '#00AA55'
        elif self.state == "thinking":
            return '#1A0030', '#330066', '#AA44FF', '#6600CC'
        elif self.state == "speaking":
            return '#1A1000', '#443300', '#FFAA00', '#FF6600'
        return '#001830', '#003366', '#00D4FF', '#0088CC'

    def _init_orb_items(self):
        """Create all canvas items ONCE. Animation updates them in place — no delete/recreate."""
        W, H = 420, 420
        cx, cy = W // 2, H // 2 - 20
        r = 150
        self._cx, self._cy, self._r = cx, cy, r
        bg, ring_c, core_c, glow_c = self._get_colors()

        self._bg_item = self.canvas.create_oval(cx-r, cy-r, cx+r, cy+r, fill=bg, outline='')

        for y_line in range(cy-r+5, cy+r, 12):
            self.canvas.create_line(cx-r+5, y_line, cx+r-5, y_line, fill='#001830', width=1)

        self._ring_arcs = []
        for i in range(len(self.rings)):
            ring_r = r - 10 - i*8
            arcs = []
            for d in range(0, 360, 20):
                aid = self.canvas.create_arc(
                    cx-ring_r, cy-ring_r, cx+ring_r, cy+ring_r,
                    start=d, extent=10, style='arc', outline=ring_c, width=2+i
                )
                arcs.append(aid)
            self._ring_arcs.append(arcs)

        self._pulse_items = [self.canvas.create_oval(cx, cy, cx, cy, outline=glow_c, width=1) for _ in range(3)]

        self._core_items = []
        for cr in (80, 60, 40, 20):
            cid = self.canvas.create_oval(cx-cr, cy-cr, cx+cr, cy+cr, fill=core_c, outline='')
            self._core_items.append(cid)

        self._dot_items = [self.canvas.create_oval(0, 0, 4, 4, fill=glow_c, outline='') for _ in range(8)]

        self._icon_item = self.canvas.create_text(cx, cy, text="\u25c8", font=('Arial', 28), fill='#FFFFFF')

        self._label_item = self.canvas.create_text(cx, cy - r - 18, text="J.A.R.V.I.S",
            font=('Courier New', 12, 'bold'), fill=core_c)

    def _draw_orb(self):
        """Cheap per-frame update — only moves/recolors existing items."""
        cx, cy, r = self._cx, self._cy, self._r
        bg, ring_c, core_c, glow_c = self._get_colors()

        self.canvas.itemconfig(self._bg_item, fill=bg)

        for i, arcs in enumerate(self._ring_arcs):
            phase = (self.angle + self.rings[i] * 360) % 360
            for j, aid in enumerate(arcs):
                d = j * 20
                self.canvas.itemconfig(aid, outline=ring_c, start=d + phase)

        pulse_r = r * (0.5 + 0.5 * abs(math.sin(self.pulse)))
        for k, pr in enumerate([pulse_r * 0.6, pulse_r * 0.8, pulse_r]):
            self.canvas.coords(self._pulse_items[k], cx-pr, cy-pr, cx+pr, cy+pr)
            self.canvas.itemconfig(self._pulse_items[k], outline=glow_c)

        for idx, cid in enumerate(self._core_items):
            fill = '#FFFFFF' if idx == 3 else (glow_c if idx == 2 else core_c)
            self.canvas.itemconfig(cid, fill=fill)

        for i, dot in enumerate(self._dot_items):
            a = math.radians(self.angle * 2 + i * 45)
            dr = r + 15 + 10 * math.sin(self.pulse + i)
            dx = cx + dr * math.cos(a)
            dy = cy + dr * math.sin(a)
            self.canvas.coords(dot, dx-2, dy-2, dx+2, dy+2)
            self.canvas.itemconfig(dot, fill=glow_c)

        icon = {"idle": "\u25c8", "listening": "\u25c9", "thinking": "\u27f3", "speaking": "\u25ce"}.get(self.state, "\u25c8")
        self.canvas.itemconfig(self._icon_item, text=icon)
        self.canvas.itemconfig(self._label_item, fill=core_c)

    def _start_animation(self):
        speed = {'idle': 0.8, 'listening': 2.2, 'thinking': 3.5, 'speaking': 1.6}

        def tick():
            self.angle = (self.angle + speed.get(self.state, 1.0)) % 360
            self.pulse += 0.06
            for i in range(len(self.rings)):
                self.rings[i] = (self.rings[i] + 0.003) % 1.0
            self._draw_orb()
            self.root.after(16, tick)  # ~60fps, driven by Tk's own loop

        self.root.after(16, tick)

    def _set_state(self, state, status="", reply=""):
        self.state = state
        if status:
            self.root.after(0, lambda: self.status_var.set(status))
        if reply:
            self.root.after(0, lambda: self.reply_var.set(reply))

    def _fade_in(self):
        alpha = [0.0]
        def step():
            alpha[0] = min(alpha[0] + 0.05, 0.95)
            self.root.attributes('-alpha', alpha[0])
            if alpha[0] < 0.95:
                self.root.after(30, step)
        self.root.after(100, step)

    def _shutdown(self):
        speak("Goodbye Boss. JARVIS going offline.", wait=False)
        time.sleep(1.5)
        self.root.destroy()
        sys.exit(0)

    def _start_jarvis(self):
        def run():
            time.sleep(1.2)
            speak("JARVIS online. How can I help you today, Boss?", wait=True)
            wake = load_config().get("wake_word", "jarvis")

            while True:
                self._set_state("idle", "SAY 'JARVIS'", "Waiting for wake word...")
                heard = listen(timeout=None, phrase_limit=4)
                if not heard or wake not in heard.lower():
                    continue

                self._set_state("listening", "LISTENING...", "Yes Boss?")
                speak("Yes Boss?", wait=True)
                time.sleep(0.4)

                self._set_state("listening", "SPEAK NOW", "I'm listening...")
                command = listen(timeout=7, phrase_limit=15)

                if not command:
                    self._set_state("idle", "JARVIS ONLINE", "Didn't catch that. Try again.")
                    speak("I didn't catch that. Try again Boss.", wait=True)
                    continue

                self._set_state("thinking", "THINKING...", f'"{command}"')
                reply = route_command(command)

                self._set_state("speaking", "SPEAKING", reply[:80] + ("..." if len(reply) > 80 else ""))
                speak(reply, wait=True)
                time.sleep(0.3)

        threading.Thread(target=run, daemon=True).start()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = JARVISApp()
    app.run()
