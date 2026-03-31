# 👏 Clap Work

<p align="center">
  <img src="https://img.shields.io/badge/Platform-macOS-black?style=for-the-badge&logo=apple&logoColor=white"/>
  <img src="https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/Status-Active-brightgreen?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/Voice-Bad-red?style=for-the-badge&logo=apple&logoColor=white"/>
</p>

<p align="center">
  A hands-free macOS automation tool that listens for clap gestures via microphone<br/>
  and triggers actions using real-time audio spike detection.
</p>

---

## ✨ Features

| Gesture | Action |
|---|---|
| 👏👏 Double Clap | Speaks greeting → Opens GitHub profile in a new Safari window |
| 👏 Single Clap | Speaks farewell → Exits the program |

- 🎙️ Real-time microphone audio processing
- 🔊 Deep voice feedback using macOS built-in `say` engine
- 🧠 Debounced spike detection — no false triggers from keyboard or ambient noise
- ⚡ Non-blocking — audio callback never stalls
- 🔒 Cooldown system to prevent accidental re-triggering

---

## 🚀 Quick Start

### 1. Clone the repo
```bash
git clone https://github.com/Shashwat-19/clap-trigger.git
cd clap-trigger
```

### 2. Install dependencies
```bash
pip3 install sounddevice numpy
```

### 3. Grant microphone permission
```
System Settings → Privacy & Security → Microphone → enable Terminal
```

### 4. Run
```bash
python3 trigger.py
```

---

## 🛠️ How It Works
```
Microphone Audio Stream
        │
        ▼
  Amplitude Spike?
        │
       YES
        │
   ┌────▼─────┐
   │  Clap #1  │──── start 1.2s timer
   └────┬──────┘
        │
   2nd spike         Timer expires
   within 1.2s?      (no 2nd clap)
        │                  │
        ▼                  ▼
   DOUBLE CLAP        SINGLE CLAP
        │                  │
  Speak greeting      Speak farewell
  Open GitHub         Exit program
  in Safari
```

---

## ⚙️ Configuration

All tunable parameters are at the top of `trigger.py`:
```python
GITHUB_URL         = "https://github.com/Shashwat-19"
VOICE              = "Bad"          # macOS voice
VOICE_RATE         = 130            # words per minute
AUDIO_DEVICE       = "MacBook Air Speakers"
CLAP_THRESHOLD     = 0.25           # 0.0–1.0 amplitude sensitivity
DOUBLE_CLAP_WINDOW = 1.2            # seconds between two claps
COOLDOWN           = 3.0            # seconds before re-triggering
```

### Tuning Guide

| Issue | Fix |
|---|---|
| False triggers from typing/noise | Raise `CLAP_THRESHOLD` to `0.35–0.45` |
| Claps not detected | Lower `CLAP_THRESHOLD` to `0.15` |
| Double clap too strict | Raise `DOUBLE_CLAP_WINDOW` to `1.5` |
| Re-triggers too fast | Raise `COOLDOWN` |

---

## 🔊 Voice Options

Test different voices in Terminal:
```bash
say -v Bad      -a "MacBook Air Speakers" -r 130 "Hello Zerox"
say -v Eddy     -a "MacBook Air Speakers" -r 130 "Hello Zerox"
say -v Reed     -a "MacBook Air Speakers" -r 130 "Hello Zerox"
say -v Rocko    -a "MacBook Air Speakers" -r 130 "Hello Zerox"
say -v Trinoids -a "MacBook Air Speakers" -r 130 "Hello Zerox"
say -v Zarvox   -a "MacBook Air Speakers" -r 130 "Hello Zerox"
```

---

## 📦 Dependencies

| Package | Purpose |
|---|---|
| `sounddevice` | Real-time microphone audio stream |
| `numpy` | Amplitude calculation from audio buffer |
| `osascript` | macOS AppleScript bridge (built-in) |
| `say` | macOS text-to-speech engine (built-in) |

---

## 🖥️ Requirements

- macOS 12+ (Monterey or later recommended)
- Python 3.8+
- Microphone access granted to Terminal

---

## 📁 Project Structure
```
clap-trigger/
├── trigger.py       # Main script
└── README.md        # You are here
```

---

## 👤 Author

**Shashwat**

[![GitHub](https://img.shields.io/badge/GitHub-Shashwat--19-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/Shashwat-19)

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

<p align="center">Made with 👏 and Python on macOS</p>