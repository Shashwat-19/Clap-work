#!/usr/bin/env python3
"""
trigger.py
----------
👏👏  Double clap → Open GitHub in Safari + Open Claude app
👏    Single clap → Close Safari window + Exit program

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

SAMPLE_RATE        = 44100
CHUNK_SIZE         = 512
CLAP_THRESHOLD     = 0.25
DOUBLE_CLAP_WINDOW = 1.2    # seconds to wait for a 2nd clap
SILENCE_RATIO      = 0.4
COOLDOWN           = 3.0

# ─── ACTIONS ───────────────────────────────────────────────────────────────────

def open_github_in_safari():
    script = f'''
        tell application "Safari"
            activate
            make new document with properties {{URL:"{GITHUB_URL}"}}
        end tell
    '''
    subprocess.run(["osascript", "-e", script], check=True)

def open_claude_app():
    subprocess.run(["open", "-a", "Claude"], check=True)

def trigger_open():
    print("\n🎯 Double clap — Opening GitHub + Claude...")
    t1 = threading.Thread(target=open_github_in_safari, daemon=True)
    t2 = threading.Thread(target=open_claude_app, daemon=True)
    t1.start(); t2.start()
    t1.join();  t2.join()
    print("✅ Done. Listening...\n")

def trigger_close():
    print("\n🛑 Single clap — Closing Safari window + Exiting...\n")
    script = '''
        tell application "Safari"
            if (count of windows) > 0 then
                close front window
            end if
        end tell
    '''
    subprocess.run(["osascript", "-e", script])
    # Give osascript a moment, then kill self cleanly
    time.sleep(0.4)
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
        self._timer          = None   # waits to confirm single clap

    def _cancel_timer(self):
        if self._timer and self._timer.is_alive():
            self._timer.cancel()

    def _on_single_clap_confirmed(self):
        """Called when DOUBLE_CLAP_WINDOW expires with only 1 clap."""
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
                print(f"  👏 Clap #{self._clap_count}  (amplitude={amplitude:.3f})")

                if self._clap_count == 1:
                    # Start a timer — if no 2nd clap arrives, it's a single clap
                    self._cancel_timer()
                    self._timer = threading.Timer(
                        DOUBLE_CLAP_WINDOW, self._on_single_clap_confirmed
                    )
                    self._timer.daemon = True
                    self._timer.start()

                elif self._clap_count >= 2:
                    # Double clap confirmed — cancel the single-clap timer
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
    print("   👏👏  Double clap → Open GitHub + Claude")
    print("   👏    Single clap → Close Safari window + Exit")
    print(f"   Threshold={CLAP_THRESHOLD} | Window={DOUBLE_CLAP_WINDOW}s | Cooldown={COOLDOWN}s")
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
        print("\n👋 Exited.")
    except sd.PortAudioError as e:
        print(f"\n❌ Audio error: {e}")
        print("   → System Settings → Privacy → Microphone → enable Terminal")
        sys.exit(1)


if __name__ == "__main__":
    main()