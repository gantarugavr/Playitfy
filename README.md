<div align="center">

<img src="https://img.shields.io/badge/Playitfy-Music%20Player-A31616?style=for-the-badge&logo=music&logoColor=white"/>

# ▶ PLAYITFY
### Open Source Music Player · v1.3

**A clean, lightweight desktop music player built with Python & Tkinter.**  
No ads. No telemetry. No nonsense. Just your music.

[![License: GPLv3](https://img.shields.io/badge/License-GPLv3-blue.svg?style=flat-square)](LICENSE.txt)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Platform](https://img.shields.io/badge/Platform-Windows-0078D4?style=flat-square&logo=windows&logoColor=white)]()
[![Author](https://img.shields.io/badge/Author-gantarugavr.me-A31616?style=flat-square)](https://gantarugavr.me)

[Download Installer](#-installation) · [View Source](app.py) · [Report Bug](../../issues) · [Changelog](../../releases)

</div>

---

## 📸 Preview

> _Screenshot coming soon — feel free to contribute one!_

---

## ✨ Features

| Feature | Description |
|---|---|
| 📂 **Folder Library** | Load your entire MP3 / WAV folder in one click |
| 🖼 **Album Art** | Reads embedded ID3 artwork and displays it automatically |
| 🔍 **Live Search** | Filter tracks by title or artist instantly as you type |
| ⏩ **Precise Seekbar** | Click or drag the progress bar to jump anywhere in a track |
| ⏪⏩ **±10s Skip** | Skip backward or forward 10 seconds with a single click |
| 🔀 **Shuffle** | Randomize playback order |
| 🔁 **Repeat Modes** | Off → Repeat All → Repeat One |
| 🔊 **App Volume** | Internal volume slider, independent of your system volume |
| 🖥 **System Volume** | Live display of your Windows master volume level |
| 🪟 **Mini Player** | Compact overlay mode — drag anywhere on screen |
| 🛡 **Integrity Guard** | SHA-256 checksum protects the official binary from tampering |

---

## 🚀 Installation

### Option A — Installer (Recommended for end users)

1. Go to [**Releases**](../../releases) and download the latest `Playitfy - Music Player Setup vX.X.exe`
2. Run the installer and follow the on-screen steps
3. Launch **Playitfy** from the Start Menu or Desktop shortcut

### Option B — Run from Source

**Requirements:** Python 3.10 or later (Windows)

```bash
# 1. Clone the repository
git clone https://github.com/gantarugavr/Playitfy.git
cd Playitfy

# 2. Install dependencies
pip install pygame mutagen Pillow pycaw comtypes

# 3. Run
pythonw app.py
```

> **Tip:** Use `pythonw` instead of `python` to suppress the terminal window.

---

## 🎮 How to Use

### Step 1 — Load Your Music
Click **📂 Select Folder** on the left sidebar. Playitfy will scan the folder and load all `.mp3` and `.wav` files automatically.

### Step 2 — Play a Track
**Single-click** any track in the list to start playback immediately. The currently playing track is highlighted in red.

### Step 3 — Control Playback

| Control | Action |
|---|---|
| `▶ PLAY / ⏸ PAUSE` | Toggle playback |
| `⏮` / `⏭` | Previous / Next track |
| `⏪` / `⏩` | Rewind / Fast-forward 10 seconds |
| `🔀` | Toggle shuffle mode |
| `🔁` | Cycle repeat: Off → All → One |
| Seekbar | Click or drag to jump to any position |
| Volume Slider | Adjust application volume (0–100%) |

### Step 4 — Mini Player
Click **[Mini]** in the top-right corner to switch to compact overlay mode.  
The mini player stays on top of all windows. **Left-click and drag** to move it anywhere on your screen.  
Click **✕** to close mini mode and return to the full player.

### Step 5 — Search
Type in the search box on the sidebar to filter tracks in real time by title or artist name.

---

## 🏗 Build from Source (Developers)

### Compile to .exe with PyInstaller

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name app app.py
```

The compiled binary will be output to `dist/app.exe`.

> ⚠️ **Important:** After compiling, calculate the SHA-256 hash of your new `app.exe` and update the `EXPECTED_HASH` constant in `app.py` before redistributing. This ensures the integrity check works correctly for your build.

```bash
# Get the SHA-256 hash of your compiled binary (PowerShell)
Get-FileHash dist\app.exe -Algorithm SHA256
```

### Build Installer with Inno Setup

1. Install [Inno Setup](https://jrsoftware.org/isinfo.php)
2. Open `setup.iss` in the Inno Setup Compiler
3. Press **Compile** (`Ctrl+F9`)
4. The installer will be output to the `Output/` folder

---

## 📋 License & Terms

Playitfy is released under the **GNU General Public License v3.0** with supplementary clauses.  
See [LICENSE.txt](LICENSE.txt) for the full legal text.

### Short Version

```
✔  Free to use personally — no conditions.
✔  Free to read, study, and learn from the source code.
✔  Free to fork and modify — as long as your fork stays open-source (GPLv3).
✘  You may NOT sell a closed-source version of this software.
✘  You may NOT redistribute the official binary after injecting external code.
✘  You may NOT claim authorship by removing attribution without replacing it.
```

### Three Built-in Protections

**I. Copyleft Inheritance (GPLv3)**  
Any derivative work you distribute must be released under GPLv3 and include the full source code. No proprietary forks allowed.

**II. Forced Attribution (Anti-Plagiarism Logic)**  
The footer string `© 2026 Project ❄️ gantarugavr.me` is checked every 200ms at runtime. If removed or altered in a distributed build without proper credit, the application terminates automatically. This is a logical filter — developers who read the code will understand it; those who blindly copy without reading will encounter automatic failure.

**III. Distribution Integrity (End-User Safety)**  
The official `.exe` binary is protected by a SHA-256 hash. If a third party injects malware into the binary and redistributes it under the Playitfy name, the integrity check will refuse to run it. This protects both the end-user and the author's reputation.

---

## 🛠 Tech Stack

- **[Python 3](https://python.org)** — Core language
- **[Tkinter](https://docs.python.org/3/library/tkinter.html)** — GUI framework
- **[Pygame](https://pygame.org)** — Audio engine
- **[Mutagen](https://mutagen.readthedocs.io)** — ID3 tag & audio metadata reader
- **[Pillow](https://python-pillow.org)** — Image processing (album art, thumbnails)
- **[pycaw](https://github.com/AndreMiras/pycaw)** — Windows system volume API
- **[comtypes](https://github.com/enthought/comtypes)** — Windows COM interface

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Commit your changes: `git commit -m "Add: your feature description"`
4. Push to your fork: `git push origin feature/your-feature-name`
5. Open a Pull Request

> Please ensure your fork remains GPLv3-licensed and that you credit the original project in your README.

---

## 🐛 Known Issues & Roadmap

- [ ] Playlist save/load (`.m3u` support)
- [ ] Dark/light theme toggle
- [ ] Equalizer
- [ ] Linux & macOS support (volume API is Windows-only currently)
- [ ] Keyboard shortcut bindings

Found a bug? [Open an issue](../../issues) with steps to reproduce.

---

<div align="center">

Made with ❤️ by **[gantarugavr.me](https://gantarugavr.me)**

[![Website](https://img.shields.io/badge/Website-gantarugavr.me-A31616?style=flat-square)](https://gantarugavr.me)
[![GitHub](https://img.shields.io/badge/GitHub-gantarugavr-181717?style=flat-square&logo=github)](https://github.com/gantarugavr)

_© 2026 Project ❄️ gantarugavr.me · Released under GPLv3_

</div>
