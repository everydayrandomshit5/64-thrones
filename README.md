# 64-Thrones: High-Glamour Edition (v3.2)

<div align="center">
  <h1>64-Thrones: High-Glamour Edition</h1>
  <p>
    <strong>Tactical Visual Novel & High-Fantasy Story Chess RPG</strong>
    <br />
    Dual Campaigns • War Council Tactical Advisors • Sovereign Spells • Interactive Wardrobe Codex
  </p>
  <p>
    Author: <strong>random guy</strong> • 
    <a href="https://github.com/everydayrandomshit5">GitHub</a> • 
    <a href="https://www.instagram.com/everyday_randomshit/">Instagram</a>
    <br />
    Licensed under <strong>GNU General Public License v3.0 (GPL-3.0)</strong>
  </p>
</div>

---

## 📖 Overview

**64-Thrones: High-Glamour Edition** is a tactical fantasy visual novel and casual-friendly chess RPG built in **Ren'Py 8.3** with embedded **python-chess**. 

Across the shattered rift valley of Ashgate, the celestial Monoliths have awakened. Players command the forces of either **House Aurelis (The Solar Dawn)** or **House Vael (The Umbral Dusk)**, waging tactical chess battles guided by royal court advisors, unlocking sovereign magic, and forging deep bonds in the War Tent Pavilion.

---

## ✨ Key Features

### 👑 Dual Faction Campaigns & Grand Finale
- **House Aurelis (Solar Dawn)**: 8 narrative chapters following High Sovereign Aurelian, Grand Marshal Lysandra Verel, and the Paladins of the Sun.
- **House Vael (Umbral Dusk)**: 8 narrative chapters following Shadow Sovereign Malachar, Inquisitor General Nyssara, and the Nightbound Vanguard.
- **Grand Alliance Finale**: *The Unbroken Concord* — unite both factions against the corrupted Arbiter of the Hollow.
- **8 Dynamic Endings**: Includes faction hegemony, catastrophic breach, and character-specific bond epilogues.

### ♟️ War Council Tactical Advisors
- Three distinct court advisors provide real-time vector advice directly on the board:
  - **The Queen's Gambit** (Lysandra / Nyssara): Offensive material strikes & aggressive initiative (Gold vector).
  - **The Warden's Bulwark** (Brannoch / Dravok): Fortified piece defense & king safety (Blue vector).
  - **The Seer's Path** (Ilyara / Veyra): Tactical geometry, pins, and knight forks (Violet vector).

### 🔮 Sovereign Spells & Tactical Parleys
- **Oracle Gaze**: Clones the board state to forecast the opponent's counter-strategy.
- **Aegis Ward**: Enchants a piece with a magical barrier that absorbs a single capture.
- **Tactical Parley**: Interactive mid-battle dialogue choices to sway enemy morale and exploit tactical vulnerabilities.

### 👗 Interactive Codex Archive & Wardrobe States
- Explore high-resolution production character art across multiple visual states:
  - **State A**: Battle Armor & Regalia.
  - **State B**: Battle-Worn / Damaged combat attire.
  - **State C**: Sensual Camp Loungewear.
  - **State D**: Ascension / Grand Concord Attire.
- Full story CG gallery and character lore dossiers.

### ⛺ War Tent Pavilion Hub
- Intersperse battles with camp hub phases:
  - **Tactical Counsel**: Spend camp downtime with your chosen advisor to increase bond rank and unlock character cut-ins.
  - **Reconnaissance Scouting**: Scout enemy vanguard weaknesses to gain bonus Aether for upcoming matches.

---

## 🚀 Download & Play

### Pre-Built Standalone Releases
Download ready-to-play packages directly from the [GitHub Releases](https://github.com/everydayrandomshit5/64-thrones/releases) page:
- **Windows Standalone**: `64-thrones-sfwv2-1.0-win.zip` (extract and double-click `64-thrones-sfwv2.exe`)
- **Linux Standalone**: `64-thrones-sfwv2-1.0-linux.tar.bz2`
- **Universal PC**: `64-thrones-sfwv2-1.0-pc.zip`

### Running from Source
To run or develop the game from source:
1. Download or install [Ren'Py 8.3+](https://www.renpy.org/).
2. Clone this repository:
   ```bash
   git clone https://github.com/everydayrandomshit5/64-thrones.git
   ```
3. Launch via Ren'Py:
   - Open the Ren'Py Launcher, add the project folder, and press **Launch Project**.
   - Or run the included launcher script:
     ```powershell
     .\run_game.bat
     ```

### Running Tests
The project includes a comprehensive verification suite:
```powershell
# Run the 61-test pytest suite
pytest

# Run the strict asset audit
python tools/audit_production_assets.py --strict

# Run the 17-chapter campaign simulator
python tools/simulate_full_campaign.py
```

---

## 🤖 AI Transparency Disclosure

In the spirit of complete transparency:
- **AI-Assisted Development**: This project was conceived, authored, and assembled with the assistance of artificial intelligence tools (including LLMs for narrative orchestration and code integration, as well as AI image generation pipelines such as Grok and FLUX for illustrations).
- **Known Quirks & Bugs**: Because this game was created with AI assistance and rapid prototyping, you may encounter occasional graphical artifacts, dialogue idiosyncrasies, or engine edge-cases. 
- **Feedback & PRs Welcome**: Constructive feedback, bug reports, and community pull requests are very welcome! Feel free to open an issue or reach out via Instagram.

---

## 📜 Credits & Acknowledgements

- **Creator & Project Lead**: **random guy**
  - GitHub: [@everydayrandomshit5](https://github.com/everydayrandomshit5)
  - Instagram: [@everyday_randomshit](https://www.instagram.com/everyday_randomshit/)
- **Ren'Py Visual Novel Engine**:
  - Developed by **Tom Rothamel (PyTom)** and the Ren'Py contributors ([renpy.org](https://www.renpy.org/)).
  - Licensed under the MIT License.
- **python-chess**:
  - Authored by **Niklas Fiekas** and contributors ([github.com/niklasf/python-chess](https://github.com/niklasf/python-chess)).
  - Licensed under the GNU General Public License v3.0 (GPL-3.0).

---

## ⚖️ License

This project is free software licensed under the **GNU General Public License v3.0 (GPL-3.0)**. See the [`LICENSE`](./LICENSE) file for the full text.
