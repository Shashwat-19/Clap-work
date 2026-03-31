#!/usr/bin/env python3
"""
trigger.py
----------
👏👏  Double clap → Heavy voice greeting + Opens GitHub in Safari
👏    Single clap → Heavy voice farewell + Closes Safari window + Exits

Dependencies:
    pip install sounddevice numpy
"""

import sounddevice as sd
import numpy as np
import subprocess
import threading
import time
import sys
import os
import signal

# ─── CONFIG ────────────────────────────────────────────────────────────────────

GITHUB_URL         = "https://github.com/Shashwat-19"

# Voice settings — Fred is the deepest built-in macOS voice
VOICE              = "Bad"
VOICE_RATE         = 130       # words per minute — lower = slower & heavier (default is 175)

OPEN_LINE          = "Hello sir... lets get back to work!"
CLOSE_LINE         = "Have a great day... master."

SAMPLE_RATE        = 44100
CHUNK_SIZE         = 512
CLAP_THRESHOLD     = 0.25
DOUBLE_CLAP_WINDOW = 1.2
SILENCE_RATIO      = 0.4    
COOLDOWN           = 3.0

# ─── ACTIONS ───────────────────────────────────────────────────────────────────

def speak(line: str):
    subprocess.Popen(["say", "-v", "Fred", "-r", str(VOICE_RATE), "-a", "MacBook Air Speakers", line])

def open_github_in_safari():
    script = f'''
        tell application "Safari"
            activate
            make new document with properties {{URL:"{GITHUB_URL}"}}
        end tell
    '''
    subprocess.run(["osascript", "-e", script], check=True)

def trigger_open():
    print("\n🎯 Double clap — Opening GitHub...")
    speak(OPEN_LINE)
    open_github_in_safari()
    print("Done. Listening...\n")

def trigger_close():
    print("\nSingle clap — Exiting...\n")
    speak(CLOSE_LINE)
    time.sleep(2.5)
    os.kill(os.getpid(), signal.SIGINT)

# ─── DETECTOR ──────────────────────────────────────────────────────────────────

class ClapDetector:
    """
    State machine:
        IDLE ──(spike)──► ARMED ──(spike within window)──► DOUBLE → open
                              └──(timeout, no 2nd spike)──► SINGLE → close + exit
    """

    def __init__(self):
        self._lock           = threading.Lock()
        self._clap_count     = 0
        self._last_clap_time = 0.0
        self._in_spike       = False
        self._cooldown_until = 0.0
        self._timer          = None

    def _cancel_timer(self):
        if self._timer and self._timer.is_alive():
            self._timer.cancel()

    def _on_single_clap_confirmed(self):
        with self._lock:
            if self._clap_count == 1:
                self._clap_count = 0
                self._cooldown_until = time.monotonic() + COOLDOWN
        threading.Thread(target=trigger_close, daemon=True).start()

    def process(self, indata: np.ndarray, *_):
        with self._lock:
            now       = time.monotonic()
            amplitude = float(np.max(np.abs(indata)))

            if now < self._cooldown_until:
                return

            # Rising edge
            if amplitude >= CLAP_THRESHOLD and not self._in_spike:
                self._in_spike = True
                elapsed        = now - self._last_clap_time

                if elapsed <= DOUBLE_CLAP_WINDOW:
                    self._clap_count += 1
                else:
                    self._clap_count = 1

                self._last_clap_time = now
                print(f"  Clap #{self._clap_count}  (amplitude={amplitude:.3f})")

                if self._clap_count == 1:
                    self._cancel_timer()
                    self._timer = threading.Timer(
                        DOUBLE_CLAP_WINDOW, self._on_single_clap_confirmed
                    )
                    self._timer.daemon = True
                    self._timer.start()

                elif self._clap_count >= 2:
                    self._cancel_timer()
                    self._clap_count     = 0
                    self._cooldown_until = now + COOLDOWN
                    threading.Thread(target=trigger_open, daemon=True).start()

            # Falling edge
            elif amplitude < CLAP_THRESHOLD * SILENCE_RATIO:
                self._in_spike = False

# ─── ENTRY POINT ───────────────────────────────────────────────────────────────

def main():
    detector = ClapDetector()

    print("🎙  Clap Trigger ready")
    print("   Double clap → Open GitHub + Heavy voice greeting")
    print("   Single clap → Heavy voice farewell + Close Safari + Exit")
    print(f"   Voice={VOICE} | Rate={VOICE_RATE} | Threshold={CLAP_THRESHOLD}")
    print("   Ctrl+C to force quit\n")

    try:
        with sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=1,
            dtype="float32",
            blocksize=CHUNK_SIZE,
            callback=detector.process,
        ):
            while True:
                time.sleep(0.1)

    except KeyboardInterrupt:
        print("\nExited.")
    except sd.PortAudioError as e:
        print(f"\nAudio error: {e}")
        print("   → System Settings → Privacy → Microphone → enable Terminal")
        sys.exit(1)

if __name__ == "__main__":
    main()