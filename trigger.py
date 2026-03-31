#!/usr/bin/env python3
"""
clap_trigger.py
---------------
Listens for a double-clap via microphone and triggers:
  1. Opens your GitHub profile in a new Safari window
  2. Brings Claude app to focus (or launches it)

Dependencies:
    pip install sounddevice numpy

macOS Permission required:
    System Settings → Privacy & Security → Microphone → allow Terminal/iTerm
"""

import sounddevice as sd
import numpy as np
import subprocess
import threading
import time
import sys

# ─── CONFIG ────────────────────────────────────────────────────────────────────

GITHUB_URL        = "https://github.com/Shashwat-19"  # ← Change this

SAMPLE_RATE       = 44100   # Hz
CHUNK_SIZE        = 512     # Smaller = more responsive detection

# Clap = amplitude spike above this (0.0–1.0). Raise if false positives, lower if misses.
CLAP_THRESHOLD    = 0.25

# Max seconds between two claps to count as a double-clap
DOUBLE_CLAP_WINDOW = 1.2

# Silence threshold — below this, we consider the clap "over" (debounce)
SILENCE_RATIO     = 0.4     # fraction of CLAP_THRESHOLD

# Seconds to ignore input after a trigger fires (prevents re-triggering)
COOLDOWN          = 3.0

# ─── ACTIONS ───────────────────────────────────────────────────────────────────

def open_github_in_safari():
    """Open GitHub profile in a new Safari window."""
    script = f'''
        tell application "Safari"
            activate
            make new document with properties {{URL:"{GITHUB_URL}"}}
        end tell
    '''
    subprocess.run(["osascript", "-e", script], check=True)


def open_claude_app():
    """Launch or focus the Claude desktop app."""
    subprocess.run(["open", "-a", "Claude"], check=True)


def trigger_actions():
    """Run both actions concurrently."""
    print("\n🎯 Double clap detected! Triggering actions...")
    t1 = threading.Thread(target=open_github_in_safari, daemon=True)
    t2 = threading.Thread(target=open_claude_app, daemon=True)
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    print("✅ Done. Listening again...\n")


# ─── DETECTOR ──────────────────────────────────────────────────────────────────

class ClapDetector:
    """
    State machine:
        IDLE → (spike) → ARMED (waiting for 2nd clap) → (spike within window) → TRIGGER
        Any timeout resets to IDLE.
    """

    def __init__(self):
        self._lock           = threading.Lock()
        self._clap_count     = 0
        self._last_clap_time = 0.0
        self._in_spike       = False          # debounce: are we mid-clap?
        self._cooldown_until = 0.0

    def process(self, indata: np.ndarray, *_):
        with self._lock:
            now       = time.monotonic()
            amplitude = float(np.max(np.abs(indata)))

            # ── Cooling down after a trigger ──
            if now < self._cooldown_until:
                return

            # ── Rising edge: new spike ──
            if amplitude >= CLAP_THRESHOLD and not self._in_spike:
                self._in_spike = True
                elapsed        = now - self._last_clap_time

                if elapsed <= DOUBLE_CLAP_WINDOW:
                    self._clap_count += 1
                else:
                    # Too slow — reset, count this as clap #1
                    self._clap_count = 1

                self._last_clap_time = now
                print(f"  👏 Clap #{self._clap_count} detected  (amplitude={amplitude:.3f})")

                if self._clap_count >= 2:
                    self._clap_count     = 0
                    self._cooldown_until = now + COOLDOWN
                    # Fire off in a separate thread — never block the audio callback
                    threading.Thread(target=trigger_actions, daemon=True).start()

            # ── Falling edge: clap transient is over ──
            elif amplitude < CLAP_THRESHOLD * SILENCE_RATIO:
                self._in_spike = False


# ─── ENTRY POINT ───────────────────────────────────────────────────────────────

def main():
    if GITHUB_URL == "https://github.com/Your-Username":
        print("⚠️  Set your GITHUB_URL in the CONFIG section before running.")
        sys.exit(1)

    detector = ClapDetector()

    print("🎙  Clap Trigger running — double-clap to open GitHub + Claude")
    print(f"   Threshold : {CLAP_THRESHOLD}  |  Window : {DOUBLE_CLAP_WINDOW}s  |  Cooldown : {COOLDOWN}s")
    print("   Press Ctrl+C to quit.\n")

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
        print("\n👋 Stopped.")
    except sd.PortAudioError as e:
        print(f"\n❌ Audio error: {e}")
        print("   → Check microphone permissions: System Settings → Privacy → Microphone")
        sys.exit(1)


if __name__ == "__main__":
    main()