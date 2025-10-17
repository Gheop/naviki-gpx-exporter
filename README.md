# 🚴 naviki-gpx-exporter

> Automated GPX export tool for Naviki routes. One command to backup all your cycling data. Features OAuth2 auto-login, batch download, and incremental sync. Your rides, your files.
[![Naviki](https://img.shields.io/badge/Naviki-supported-FF6600?style=flat)](https://www.naviki.org)
[![Python](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Selenium](https://img.shields.io/badge/selenium-4.0+-green.svg)](https://www.selenium.dev/)

## 📋 Table of Contents

- [Features](#-features)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Usage](#-usage)
- [Examples](#-examples)
- [Command-Line Options](#-command-line-options)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

## ✨ Features

- 🤖 **Fully automated authentication** using Selenium WebDriver
- 📦 **Batch download** all your Naviki routes in one command
- 🔄 **Incremental sync** - skips already downloaded files
- 📅 **Smart date parsing** - handles multiple date formats
- 🎯 **Flexible filtering** - export recorded, planned, or shared routes
- 🔐 **OAuth2 support** - secure authentication flow
- 💾 **Standard GPX format** - compatible with Strava, Komoot, Garmin, etc.
- 🌐 **Headless mode** - run in background without UI
- 📸 **Debug screenshots** - automatic error diagnosis

## 🔧 Prerequisites

- **Python 3.7+**
- **Firefox browser** (for Selenium)
- **geckodriver** (Firefox WebDriver)
- A Naviki account with recorded routes

## 📥 Installation

### 1. Clone the repository

```bash
git clone https://github.com/Gheop/naviki-gpx-exporter.git
cd naviki-gpx-exporter
```

### 2. Install Python dependencies

```bash
pip install -r requirements.txt
```

Or install manually:

```bash
pip install selenium requests beautifulsoup4
```

### 3. Install geckodriver (Firefox WebDriver)

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install firefox-geckodriver
```

**Arch Linux:**
```bash
sudo pacman -S geckodriver
```

**macOS (Homebrew):**
```bash
brew install geckodriver
```

**Windows or manual installation:**
1. Download from [geckodriver releases](https://github.com/mozilla/geckodriver/releases)
2. Extract and add to your PATH

**Verify installation:**
```bash
geckodriver --version
```

## 🚀 Usage

### Basic Usage (Automated Authentication)

```bash
python naviki_gpx_download.py --username YourUsername --password 'YourPassword'
```

**Output:**
```
🤖 Lancement de l'authentification automatique avec Selenium...
   Username: YourUsername
   Mode: Headless (invisible)

🌐 Ouverture du navigateur Firefox...

📋 Étape 1: Chargement de la page de connexion OAuth2...
   ✓ Page chargée

🔑 Étape 2: Saisie des identifiants...
   ✓ Identifiants saisis

🚀 Étape 3: Soumission du formulaire...

⏳ Étape 4: Attente du token dans localStorage...
   ✓ Token récupéré: 79bb6f8e-23b6-38c4-b...

✅ Authentification réussie!

🔒 Fermeture du navigateur...

==================================================
📁 Destination: /tmp
🔍 Types de routes: routedAll,recordedMy,recordedOthers
==================================================

Début du téléchargement...

Traitement: 16/10/2025, 07:20
UUID: 8252D5EB-42FD-4022-A545-244F305D03DE
✅ Sauvegardé: /tmp/2025-10-16_07-20_Naviki.gpx

Traitement: 15/10/2025, 08:15
UUID: 9363E6FC-53GE-5133-B656-355F416E04EF
✅ Sauvegardé: /tmp/2025-10-15_08-15_Naviki.gpx

==================================================
Téléchargement terminé!
✅ Téléchargés: 45
⏭️  Ignorés (déjà présents): 12
❌ Erreurs: 0
📊 Total traité: 57
📁 Fichiers sauvegardés dans: /tmp
```

### Using a Pre-existing Token

If you already have an OAuth token:

```bash
python naviki_gpx_download.py --token YOUR-OAUTH-TOKEN-HERE
```

### Custom Output Directory

```bash
python naviki_gpx_download.py --username YourUsername --password 'YourPassword' --output ~/cycling/naviki-backup
```

### Visible Browser Mode (for debugging)

```bash
python naviki_gpx_download.py --username YourUsername --password 'YourPassword' --visible
```

## 📚 Examples

### Example 1: First-time backup
```bash
python naviki_gpx_download.py \
  --username MyUsername \
  --password 'MySecurePass123!' \
  --output ~/naviki-backup
```

### Example 2: Daily sync (incremental)
```bash
python naviki_gpx_download.py \
  --username MyUsername \
  --password 'MySecurePass123!' \
  --output ~/naviki-backup \
  --headless
```

### Example 3: Only recorded routes
```bash
python naviki_gpx_download.py \
  --username MyUsername \
  --password 'MySecurePass123!' \
  --types recordedMy \
  --output ~/recorded-only
```

### Example 4: Using stored token
```bash
# Get your token once (lasts for session)
python naviki_gpx_download.py --username MyUsername --password 'pass' --output /tmp

# Reuse token for multiple runs
python naviki_gpx_download.py --token abc123-def456-ghi789 --output ~/backup1
python naviki_gpx_download.py --token abc123-def456-ghi789 --output ~/backup2
```

### Example 5: Automated daily backup (cron job)
```bash
# Add to crontab (crontab -e)
0 2 * * * /usr/bin/python3 /path/to/naviki_gpx_download.py --username USER --password 'PASS' --output ~/naviki-backup >> ~/naviki.log 2>&1
```

## ⚙️ Command-Line Options

| Option | Alias | Required | Description |
|--------|-------|----------|-------------|
| `--username` | `--login` | Yes* | Your Naviki username/login |
| `--password` | - | Yes* | Your Naviki password |
| `--token` | - | Yes* | OAuth token (alternative to username/password) |
| `--output` | `-o` | No | Output directory (default: `/tmp`) |
| `--types` | - | No | Route types to export (default: all) |
| `--headless` | - | No | Run browser in headless mode (default) |
| `--visible` | - | No | Show browser during authentication |

*Either `--username`/`--password` OR `--token` is required.

### Route Types

Valid values for `--types` (comma-separated):
- `recordedMy` - Routes you recorded
- `routedAll` - Routes you planned
- `recordedOthers` - Routes from other users you saved

Default: `routedAll,recordedMy,recordedOthers` (all types)

## 🐛 Troubleshooting

### Issue: "geckodriver not found"

**Solution:**
```bash
# Ubuntu/Debian
sudo apt install firefox-geckodriver

# Or download manually
wget https://github.com/mozilla/geckodriver/releases/download/v0.33.0/geckodriver-v0.33.0-linux64.tar.gz
tar -xvzf geckodriver-v0.33.0-linux64.tar.gz
sudo mv geckodriver /usr/local/bin/
```

### Issue: "Token invalide ou expiré"

**Solution:** Tokens expire after some time. Re-authenticate:
```bash
python naviki_gpx_download.py --username YourUsername --password 'YourPassword'
```

### Issue: Authentication fails silently

**Solution:** Run in visible mode to see what's happening:
```bash
python naviki_gpx_download.py --username YourUsername --password 'YourPassword' --visible
```

Check the screenshot saved at `/tmp/naviki_debug.png` for visual debugging.

### Issue: Special characters in password

**Solution:** Always quote your password:
```bash
# Correct
python naviki_gpx_download.py --username user --password 'P@ss!w0rd#123'

# Wrong (shell will interpret special chars)
python naviki_gpx_download.py --username user --password P@ss!w0rd#123
```

### Issue: Downloads are slow

**Solution:** This is normal - each GPX file requires an API call. For 100 routes, expect 2-5 minutes.

### Issue: Some routes have generic names like "2024-11-24_06-18_UTC_Naviki.gpx"

**Explanation:** Routes without a date in the title use the creation timestamp (UTC timezone). This is expected behavior.

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

### Reporting Bugs

1. Check if the issue already exists in [Issues](https://github.com/yourusername/naviki-gpx-exporter/issues)
2. Create a new issue with:
   - Description of the problem
   - Steps to reproduce
   - Expected vs actual behavior
   - Output logs
   - Screenshot from `/tmp/naviki_debug.png` if applicable

### Suggesting Features

Open an issue with the `enhancement` label and describe:
- The feature you'd like to see
- Why it would be useful
- How it should work

### Pull Requests

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Test thoroughly
5. Commit: `git commit -m 'Add amazing feature'`
6. Push: `git push origin feature/amazing-feature`
7. Open a Pull Request

### Development Setup

```bash
# Clone your fork
git clone https://github.com/Gheop/naviki-gpx-exporter.git
cd naviki-gpx-exporter

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run tests
python naviki_gpx_download.py --help
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Naviki](https://www.naviki.org/) for providing an excellent cycling navigation app
- [Selenium](https://www.selenium.dev/) for browser automation
- The cycling community for inspiration

## 📧 Contact

- Create an [issue](https://github.com/yourusername/naviki-gpx-exporter/issues) for bugs or features
- For questions, use [Discussions](https://github.com/yourusername/naviki-gpx-exporter/discussions)

---

**⚠️ Disclaimer:** This tool is not affiliated with or endorsed by Naviki. Use responsibly and respect Naviki's terms of service. This tool is for personal backup purposes only.

**🌟 If this tool helped you, consider giving it a star!**

[![Naviki](https://img.shields.io/badge/Naviki-supported-FF6600?style=flat&logo=data:image/svg+xml;base64,PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiPz4KPHN2ZyB2ZXJzaW9uPSIxLjEiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIgd2lkdGg9IjQ4MCIgaGVpZ2h0PSI0ODAiPgo8cGF0aCBkPSJNMCAwIEMxNTguNCAwIDMxNi44IDAgNDgwIDAgQzQ4MCAxNTguNCA0ODAgMzE2LjggNDgwIDQ4MCBDMzIxLjYgNDgwIDE2My4yIDQ4MCAwIDQ4MCBDMCAzMjEuNiAwIDE2My4yIDAgMCBaICIgZmlsbD0iI0ZFRkVGRSIgdHJhbnNmb3JtPSJ0cmFuc2xhdGUoMCwwKSIvPgo8cGF0aCBkPSJNMCAwIEMxLjE2MjI0MDkxIDAuMDA1NjU5NzkgMi4zMjQ0ODE4MSAwLjAxMTMxOTU4IDMuNTIxOTQyMTQgMC4wMTcxNTA4OCBDNy4xOTk5NTk2MSAwLjAzOTM3MzggMTAuODc2OTY5MTIgMC4wODk1NDU1OCAxNC41NTQ2ODc1IDAuMTQwNjI1IEMxNy4wNjI0ODU4NCAwLjE2MDcwODEyIDE5LjU3MDI5OTU5IDAuMTc4OTU1NjkgMjIuMDc4MTI1IDAuMTk1MzEyNSBDMjguMTk1NjUwOTcgMC4yMzkxOTIzOCAzNC4zMTI1OTcxOSAwLjMwNTk2MjcxIDQwLjQyOTY4NzUgMC4zOTA2MjUgQzM4LjMxMzQyMjQzIDIuNTczNjk3MjYgMzYuNTA1NzgxMjMgNC4wMjg5MjA0NiAzMy43Njk1MzEyNSA1LjM3MTA5Mzc1IEMzMy4wNjI4ODMzIDUuNzI2MzkxNiAzMi4zNTYyMzUzNSA2LjA4MTY4OTQ1IDMxLjYyODE3MzgzIDYuNDQ3NzUzOTEgQzMwLjUwODk4NTYgNy4wMDcyODc2IDMwLjUwODk4NTYgNy4wMDcyODc2IDI5LjM2NzE4NzUgNy41NzgxMjUgQzE4LjIxOTcwNDMyIDEzLjMyNTM2NTk5IDUuODk1OTAzNjcgMjAuOTg0NDY4OTggMS40Mjk2ODc1IDMzLjM5MDYyNSBDMC4xNzY3NTczMyA0MS40MDMxOTA3OCAyLjc0OTI3NDE0IDQ4LjEzNDI5MDIyIDYuOTg0Mzc1IDU0Ljg1OTM3NSBDMTUuOTYwOTE3NjIgNjcuMDMzNTcwMTQgMjguOTQyODkzNDIgNzUuMDUwOTEyIDQyLjQyOTY4NzUgODEuMzkwNjI1IEM0My4wNTA4NTQ0OSA4MS42ODkyMDQxIDQzLjY3MjAyMTQ4IDgxLjk4Nzc4MzIgNDQuMzEyMDExNzIgODIuMjk1NDEwMTYgQzYzLjIzNzE3Mzk3IDkxLjI0MzUzNTA1IDg0LjM1MjczNzIxIDk1LjQxNzE0MzEzIDEwNC44Nzc5Mjk2OSA5OC45Mzg5NjQ4NCBDMTA3LjM4NTQzNDUyIDk5LjM4Mjc5MjI0IDEwOS44Nzg4MTgyNyA5OS44NzU2NTE3MSAxMTIuMzc1IDEwMC4zNzg5MDYyNSBDMTQ0LjM2MDI1MTczIDEwNi41NjQzOTQ5NSAxNzcuNjIzNTg3NTQgMTA3LjM5MzExOTc1IDIxMC4wNzQ5NTExNyAxMDkuNDM5Njk3MjcgQzIxMC45NzQ2MTYwOSAxMDkuNDk2OTI5NjMgMjExLjg3NDI4MTAxIDEwOS41NTQxNjE5OSAyMTIuODAxMjA4NSAxMDkuNjEzMTI4NjYgQzIxNC40NTg5MTk3NCAxMDkuNzE4MDk4NyAyMTYuMTE2NzQ4MTQgMTA5LjgyMTI0NDk1IDIxNy43NzQ3MTkyNCAxMDkuOTIyMDI3NTkgQzIyMy4wMjk2NjM5NyAxMTAuMjU0Mjk1MzYgMjI4LjE4MjMwNDY1IDExMC44MDc1ODI0NiAyMzMuNDI5Njg3NSAxMTEuMzkwNjI1IEMyMzMuNDI5Njg3NSAxMjkuMjEwNjI1IDIzMy40Mjk2ODc1IDE0Ny4wMzA2MjUgMjMzLjQyOTY4NzUgMTY1LjM5MDYyNSBDMjIzLjY0NjI5Mjk1IDE2NC43MzgzOTg3IDIxMy45MjQ2MTU0NiAxNjQuMDI5MDA3MjUgMjA0LjE3OTY4NzUgMTYzLjAxNTYyNSBDMjAyLjkyMTg4NDc3IDE2Mi44ODU1MTAyNSAyMDEuNjY0MDgyMDMgMTYyLjc1NTM5NTUxIDIwMC4zNjgxNjQwNiAxNjIuNjIxMzM3ODkgQzE5Mi42MDcyNDUyNyAxNjEuNzk0MDY5NjYgMTg0Ljg5Mzg5MTc2IDE2MC44MzMyNzA3OCAxNzcuMjA2MDU0NjkgMTU5LjQ4MDk1NzAzIEMxNzMuMDQwNDAyNjcgMTU4Ljc1NjU0MDQ5IDE2OC44ODY0MzIxOSAxNTguMjE3OTYxNDIgMTY0LjY4MDQzNTE4IDE1Ny43NzQ5NDgxMiBDMTU1LjQ3NjU0NTU0IDE1Ni43ODY4ODM1OSAxNDYuNTUzNzUzMjYgMTU1LjExMTQ3OTIxIDEzNy41MzU0MDAzOSAxNTMuMDQxNTAzOTEgQzEzNS4yMzQ2OTAzNiAxNTIuNTEzOTA1NzYgMTMyLjkzMTIxNDUgMTUyLjAwMDEyMjQ3IDEzMC42MjY5NTMxMiAxNTEuNDg4MjgxMjUgQzEyMi41MjM1ODEwNCAxNDkuNjY5NTY1IDExNC41NTg3Mzk3MSAxNDcuNTk5NDgwNzUgMTA2LjU4OTExMTMzIDE0NS4yNTE5NTMxMiBDMTAzLjc0MDQxMTM4IDE0NC40NzUzMzUxMyAxMDAuOTU3MzQ2OTEgMTQzLjg5NTc2NTk5IDk4LjA0Njg3NSAxNDMuNDE0MDYyNSBDOTEuNDM4MDI2OTQgMTQyLjI5NzY1Mzk0IDg1LjAzOTA1NDYgMTQwLjU1NjUxNjgxIDc4LjYyOTg4MjgxIDEzOC42MjY0NjQ4NCBDNzcuMjQxMjQ4MDggMTM4LjIxNzcxNjEyIDc1Ljg0NjczMTMgMTM3LjgyODQ2NjA1IDc0LjQ0NzI2NTYyIDEzNy40NTg0OTYwOSBDNjIuNzk0MjUwMTIgMTM0LjM2NjA0ODYgNjIuNzk0MjUwMTIgMTM0LjM2NjA0ODYgNTkuNDcyOTAwMzkgMTI5LjU1Nzg2MTMzIEM1OC4yMTg1MjYyNyAxMjYuNTI3NzIwODQgNTcuMzE3Nzg1NjUgMTIzLjU0MzY3MTQ1IDU2LjQyOTY4NzUgMTIwLjM5MDYyNSBDNDcuODI4MTgwNiAxMDIuMjc5NjE2NzYgMzQuMTMxNjE0MDkgODcuNTgwMjc4NTMgMTguNDI5Njg3NSA3NS4zOTA2MjUgQzE2LjYzNTg5MTI4IDczLjg5MzE3MjMxIDE0Ljg0NDI1MDY2IDcyLjM5MzEzMzk1IDEzLjA1NDY4NzUgNzAuODkwNjI1IEM1LjAwMTgzNzAyIDY0LjMxOTY4MjgxIC0zLjM0NzQzMjQyIDU4LjEyODgxNDY4IC0xMi43ODkwNjI1IDUzLjY5OTIxODc1IEMtMTQuOTgyMjg0MzggNTIuNjY3Mjk1NTQgLTE3LjEzNTM3ODg3IDUxLjU5ODE2NDk5IC0xOS4yODkwNjI1IDUwLjQ4ODI4MTI1IEMtMzUuNjQ4NDM2NTIgNDEuOTQxODQyODcgLTM1LjY0ODQzNjUyIDQxLjk0MTg0Mjg3IC01My41NzAzMTI1IDM4LjM5MDYyNSBDLTU1LjE0Mzg2NTk2IDUwLjMyMzQwNTQyIC01MC4yMTcxMDU4MSA1OC4wODcyOTY2IC00My40MzM1OTM3NSA2Ny4yODkwNjI1IEMtNDEuNTI5NTY3OTUgNjkuNzA0NDU1MjMgLTM5LjU2OTE1NzA2IDcyLjA1MzU4MTE0IC0zNy41NzAzMTI1IDc0LjM5MDYyNSBDLTM2LjkxMDk1NzAzIDc1LjIzMTczODI4IC0zNi45MTA5NTcwMyA3NS4yMzE3MzgyOCAtMzYuMjM4MjgxMjUgNzYuMDg5ODQzNzUgQy0zMi44MTY5OTI4OCA4MC40NDk0MTE4OCAtMjguODQ4MzcxMDEgODMuOTA4MTgxMDMgLTI0LjU3MDMxMjUgODcuMzkwNjI1IEMtMjQuMDc3ODkwNjMgODcuODAwMjI0NjEgLTIzLjU4NTQ2ODc1IDg4LjIwOTgyNDIyIC0yMy4wNzgxMjUgODguNjMxODM1OTQgQy02LjU0NjE1NDU3IDEwMi4yNDY5ODE0NCAxNC4yNDE2NDA5NCAxMTQuMzkyNDQyNTkgMzQuMzY3MTg3NSAxMjEuNzAzMTI1IEMzNS40NDM1NTQ2OSAxMjIuMTE0MzM1OTQgMzYuNTE5OTIxODggMTIyLjUyNTU0Njg4IDM3LjYyODkwNjI1IDEyMi45NDkyMTg3NSBDMzkuNjk4MTQ5MzEgMTIzLjczODY1NzI3IDQxLjc3MDYzMjU5IDEyNC41MTU1OTkyMiA0My44NTAwOTc2NiAxMjUuMjc3ODMyMDMgQzQ2LjQ3MTIwOTg5IDEyNi4yNDY0MDc2IDQ5LjA3NTIwMDk3IDEyNy4yNTMyOTY3NiA1MS42Nzk2ODc1IDEyOC4yNjU2MjUgQzUyLjUyNjUyMSAxMjguNTY4OTU3NTIgNTMuMzczMzU0NDkgMTI4Ljg3MjI5MDA0IDU0LjI0NTg0OTYxIDEyOS4xODQ4MTQ0NSBDNTYuNTEzNzU3NDQgMTMwLjA4NTUyOSA1OC40NTA1OTQ3MiAxMzAuOTYzMjkzNDcgNjAuNDI5Njg3NSAxMzIuMzkwNjI1IEM2MS40MzM3MTQ4NCAxMzUuMTk3MzM3NzkgNjEuNTE1MDUwMzEgMTM2LjQ5NjMzMDg5IDYxLjQyOTY4NzUgMTM5LjM5MDYyNSBDNjEuNDYxNTkxOCAxNDAuMzkzMzU0NDkgNjEuNDkzNDk2MDkgMTQxLjM5NjA4Mzk4IDYxLjUyNjM2NzE5IDE0Mi40MjkxOTkyMiBDNjEuOTUzNTk4NzEgMTU2LjMyMjA2MjgzIDYyLjI1OTAyNTUzIDE2OS45NDEyNDI2NCA1OC40Mjk2ODc1IDE4My4zOTA2MjUgQzU4LjEwNjU1OTExIDE4NC43MjMyNzg3MSA1Ny43ODYzOTI1NSAxODYuMDU2NjUzMDggNTcuNDY4NzUgMTg3LjM5MDYyNSBDNTQuNTQ4MjMzMDUgMTk5LjAxMDc1NDY3IDQ5LjMzMjgzMzg3IDIwOS4wMjU5NTcxMiA0My40Mjk2ODc1IDIxOS4zOTA2MjUgQzQyLjcxMDgyNjg2IDIyMC42OTEzNDUxMSA0MS45OTIwNzAyOSAyMjEuOTkyMTIyNzQgNDEuMjczNDM3NSAyMjMuMjkyOTY4NzUgQzM1Ljc3MjkwNTA2IDIzMy4wMzA4MTUwMSAyOS4wMjg2MDMzMiAyNDEuNzE0Nzc4ODIgMjIuMDIzNDM3NSAyNTAuNDEwNjQ0NTMgQzIwLjY3ODgwNDY4IDI1Mi4wODExMzY1OSAxOS4zNDkzNTgxNSAyNTMuNzYzODM1ODQgMTguMDIzNDM3NSAyNTUuNDQ5MjE4NzUgQzEzLjE2MzQ2Mzk0IDI2MS41NTEzODcwNCA3LjkyNjYxMzU2IDI2Ny4yNTU0ODg5NiAyLjU2NDQ1MzEyIDI3Mi45MTQ3OTQ5MiBDLTAuMjkxMjg2MTkgMjc1LjkyOTU5NTMxIC0zLjA4NDc1MTggMjc4Ljk2OTg3NTc2IC01Ljc4NTE1NjI1IDI4Mi4xMjUgQy0xMC4xMjQxMTc0IDI4Ny4xMTgwNjY3OSAtMTQuODAxMDYyNDcgMjkxLjc3MTM3NTA1IC0xOS40ODU1OTU3IDI5Ni40MzYyNzkzIEMtMjEuMDA1MjI5MTggMjk3Ljk1MDU1MDggLTIyLjUxOTQzNzY3IDI5OS40NzAwOTkzIC0yNC4wMzMyMDMxMiAzMDAuOTkwMjM0MzggQy0yOC44NjcxMzQzMyAzMDUuODI3MTI2NjcgLTMzLjc1NjM3NDU1IDMxMC41NDQzNjA1IC0zOC45NTQ4MzM5OCAzMTQuOTkzNDA4MiBDLTQwLjg2MDgzODIzIDMxNi42NDE4OTg4IC00Mi42MzU2NTUxOSAzMTguMzg3OTUxODMgLTQ0LjM4MjgxMjUgMzIwLjIwMzEyNSBDLTQ3LjQzNjMxOTQ4IDMyMy4zNzI2Nzk3NiAtNDkuNTMzMjk0NyAzMjUuMjU1MDU5NTQgLTU0LjA2NjQwNjI1IDMyNS44NDc2NTYyNSBDLTU5LjkwODUyNTA2IDMyNS42ODQwMDc3NCAtNjQuNTg2NDg0MDcgMzIyLjc4MjYxNzg1IC02OS42MzI4MTI1IDMyMC4wNzgxMjUgQy03MS43NjE5NjE4NyAzMTguOTczMjE3NCAtNzMuODkyMTk5OTYgMzE3Ljg3MDQwNTYzIC03Ni4wMjM0Mzc1IDMxNi43Njk1MzEyNSBDLTc3LjEwNTYwNTQ3IDMxNi4yMDYzNzIwNyAtNzguMTg3NzczNDQgMzE1LjY0MzIxMjg5IC03OS4zMDI3MzQzOCAzMTUuMDYyOTg4MjggQy04NS4zNDU4OTk3OCAzMTEuOTcwMDY1MTYgLTkxLjQ5Njk0NjkxIDMwOS4xMDMyODI5OCAtOTcuNjQyODIyMjcgMzA2LjIyMTQzNTU1IEMtMTAzLjI0MjYzOTcyIDMwMy41NzM1ODcwNyAtMTA4LjY4ODEzNDkxIDMwMC43MzU5MjExMiAtMTE0LjA4ODEzNDc3IDI5Ny42OTk5NTExNyBDLTExNi40MjAwMzU3NCAyOTYuNDY5ODk0NjIgLTExOC43MjM2ODA5OSAyOTUuNDg3NzQ4NDQgLTEyMS4xOTUzMTI1IDI5NC41NzgxMjUgQy0xMjYuOTIzNDg3MzQgMjkyLjQxMDQ1ODE5IC0xMzIuMjIzMzM0MTkgMjg5LjQ4MzQ5MTA1IC0xMzcuNTk0MjM4MjggMjg2LjU2MzIzMjQyIEMtMTQxLjE5MjM3MzI0IDI4NC42MTMzNzk2NCAtMTQ0LjcxNTUxNjUgMjgyLjc5OTI1Mzc5IC0xNDguNTcwMzEyNSAyODEuMzkwNjI1IEMtMTQ4LjI0MjM1MzE1IDI3OC40ODQwMDQ4NCAtMTQ3LjcwNjQ1NjQ0IDI3Ny41MTIyMDk0NiAtMTQ1LjQ4ODI4MTI1IDI3NS41MzEyNSBDLTE0NC41ODcyMjY1NiAyNzQuOTA3MzQzNzUgLTE0My42ODYxNzE4OCAyNzQuMjgzNDM3NSAtMTQyLjc1NzgxMjUgMjczLjY0MDYyNSBDLTE0MS43NTYyMTA5NCAyNzIuOTQwNjY0MDYgLTE0MC43NTQ2MDkzOCAyNzIuMjQwNzAzMTIgLTEzOS43MjI2NTYyNSAyNzEuNTE5NTMxMjUgQy0xMzYuNzY1NzE4OTMgMjY5LjUyMjU5MDkzIC0xMzMuNzk3MTc5NCAyNjcuNTQ1MTk5ODcgLTEzMC44MjAzMTI1IDI2NS41NzgxMjUgQy0xMjMuNTQ3MTU3NjQgMjYwLjc3MDEyNzQxIC0xMTYuNTQ3MTM0OTEgMjU1LjYxNTM2MjA2IC0xMDkuNTcwMzEyNSAyNTAuMzkwNjI1IEMtMTA5LjAwMTM1MjU0IDI0OS45NjQ5MTIxMSAtMTA4LjQzMjM5MjU4IDI0OS41MzkxOTkyMiAtMTA3Ljg0NjE5MTQxIDI0OS4xMDA1ODU5NCBDLTg5Ljc0MjQyNjk2IDIzNS41MDAxNjYxMyAtNzEuMDkxOTY4MjUgMjIwLjY5Njg2NjYzIC01Ny41NzAzMTI1IDIwMi4zOTA2MjUgQy01Ni43NzYyNSAyMDEuMzM4NzUgLTU1Ljk4MjE4NzUgMjAwLjI4Njg3NSAtNTUuMTY0MDYyNSAxOTkuMjAzMTI1IEMtNDYuMzQzMzgyOTYgMTg3LjMyODgwNDUxIC0zNy43OTkzNDI3OSAxNzQuNjcwMjM3NzUgLTMzLjU3MDMxMjUgMTYwLjM5MDYyNSBDLTMzLjA2MjM0MTczIDE1OC43NjY1Njg4OCAtMzIuNTUzMTAyODYgMTU3LjE0MjkwOTE0IC0zMi4wNDI5Njg3NSAxNTUuNTE5NTMxMjUgQy0zMS40ODc3Mzg4OCAxNTMuNzI3MTMyODIgLTMwLjkzNDM2OTM5IDE1MS45MzQxNTcwOSAtMzAuMzgyODEyNSAxNTAuMTQwNjI1IEMtMzAuMTIwMTY2MDIgMTQ5LjI4ODE1MTg2IC0yOS44NTc1MTk1MyAxNDguNDM1Njc4NzEgLTI5LjU4NjkxNDA2IDE0Ny41NTczNzMwNSBDLTI0LjAzNDQzMzU4IDEyOS4wMTQ2Mjg1OCAtMjUuNjYwNDYzMTQgMTExLjg1MzI3ODM3IC0zNC41MTk1MzEyNSA5NC43NDIxODc1IEMtMzcuMTY2MzYwNSA5MC40MTY1MTIyNiAtNDAuMjg1NTUwOTEgODYuODczMDg5MTEgLTQzLjg0NzY1NjI1IDgzLjI4MTI1IEMtNDUuNTcwMzEyNSA4MS4zOTA2MjUgLTQ1LjU3MDMxMjUgODEuMzkwNjI1IC00NS41NzAzMTI1IDc5LjM5MDYyNSBDLTQ2LjQ0ODA0MzIxIDc4Ljk4MjYzNjcyIC00Ni40NDgwNDMyMSA3OC45ODI2MzY3MiAtNDcuMzQzNTA1ODYgNzguNTY2NDA2MjUgQy00OS41MzIxMTMyMyA3Ny40MTA3OTQ2OCAtNTEuMjc1ODIxMzcgNzYuMTI3Njc3NTEgLTUzLjE5OTIxODc1IDc0LjU3ODEyNSBDLTU3LjY4MTM2NjUxIDcxLjE2NTUyMTg2IC02Mi40MTA3OTMyOSA2OC43NTUyNDEwMyAtNjcuNTA3ODEyNSA2Ni4zOTA2MjUgQy02OC40MjgwNDE5OSA2NS45NjA1NjE1MiAtNjkuMzQ4MjcxNDggNjUuNTMwNDk4MDUgLTcwLjI5NjM4NjcyIDY1LjA4NzQwMjM0IEMtODMuOTA2MDQ5OCA1OC44MzE4OTc3NCAtOTcuMjc5MzMxNDUgNTQuNzE3MjA5MTkgLTExMS45NzAyMTQ4NCA1MS45MDU3NjE3MiBDLTExNC42ODYzNzI0NiA1MS4zNjc2MzA5NiAtMTE3LjM4NzI0NDk5IDUwLjc3ODE4NzU1IC0xMjAuMDg5ODQzNzUgNTAuMTc1NzgxMjUgQy0xMzQuOTIyOTIwMjggNDYuODk5OTcxNTMgLTE0OS43Njk5NDMzNCA0NC42ODAzNjQ4NyAtMTY0LjgzNDk2MDk0IDQyLjc5MTk5MjE5IEMtMTY3LjU3MDMxMjUgNDIuMzkwNjI1IC0xNjcuNTcwMzEyNSA0Mi4zOTA2MjUgLTE2OS42NTM4MDg1OSA0MS44NTgzOTg0NCBDLTE3MS44NDEwMjYxNCA0MS4zMjQ1NTAxOCAtMTczLjg3NTk2OTkxIDQxLjE5Njg2MDU1IC0xNzYuMTI1IDQxLjEwOTM3NSBDLTE3Ny40MTg1NzQyMiA0MS4wNTMzMDA3OCAtMTc3LjQxODU3NDIyIDQxLjA1MzMwMDc4IC0xNzguNzM4MjgxMjUgNDAuOTk2MDkzNzUgQy0xNzkuNjMxNjAxNTYgNDAuOTYxMjg5MDYgLTE4MC41MjQ5MjE4OCA0MC45MjY0ODQzOCAtMTgxLjQ0NTMxMjUgNDAuODkwNjI1IEMtMTg2Ljg5NjkxODExIDQwLjY3NjM2OTc2IC0xOTIuMjAyMDQ1NTggNDAuNDUzNjQ4MTUgLTE5Ny41NzAzMTI1IDM5LjM5MDYyNSBDLTE5Ny41NzAzMTI1IDM4LjczMDYyNSAtMTk3LjU3MDMxMjUgMzguMDcwNjI1IC0xOTcuNTcwMzEyNSAzNy4zOTA2MjUgQy0xOTYuMjI2NjI1NCAzNi42MjA5ODM5MiAtMTk0Ljg4Mjg1NzE2IDM1Ljg1MTQ4NDUxIC0xOTMuNTM5MDYyNSAzNS4wODIwMzEyNSBDLTE5Mi4yNDA0MTI2IDM0LjMzNzk2MDIxIC0xOTIuMjQwNDEyNiAzNC4zMzc5NjAyMSAtMTkwLjkxNTUyNzM0IDMzLjU3ODg1NzQyIEMtMTg5LjAwNjUxNDAyIDMyLjQ4ODA2Mjg3IC0xODcuMDk1MzQ3MTcgMzEuNDAxMDI5MjUgLTE4NS4xODIxMjg5MSAzMC4zMTc2MjY5NSBDLTE4MC43NDA4ODk0IDI3Ljc5OTU4NjE3IC0xNzYuMzI2MTcyNDggMjUuMjY2NTI5ODQgLTE3MiAyMi41NTQ2ODc1IEMtMTcwLjk2NDU2MDU1IDIxLjkyMzI0ODI5IC0xNzAuOTY0NTYwNTUgMjEuOTIzMjQ4MjkgLTE2OS45MDgyMDMxMiAyMS4yNzkwNTI3MyBDLTE2OC42NDU2MDEzMSAyMC41MDY1NzI4NCAtMTY3LjM5NTQxODg2IDE5LjcxMzIxMDY0IC0xNjYuMTYyMTA5MzggMTguODk0Nzc1MzkgQy0xNjAuNTg2ODE0NTEgMTUuNTQ1MTAyMjcgLTE1NS44MDMzNTgwMiAxNi4zNzMzMjE3OSAtMTQ5LjU3MDMxMjUgMTcuMzkwNjI1IEMtMTQ4LjMyNTA3ODEzIDE3LjU4Njk2NTMzIC0xNDcuMDc5ODQzNzUgMTcuNzgzMzA1NjYgLTE0NS43OTY4NzUgMTcuOTg1NTk1NyBDLTE0MS40ODQ4ODk5OCAxOC42ODM5NDUyNyAtMTM3LjE4NDEyOTY3IDE5LjQ0MjI4MjA4IC0xMzIuODgyODEyNSAyMC4yMDMxMjUgQy0xMjkuNzY0NTkxMzYgMjAuNzQ4OTM2NjYgLTEyNi42NDU5NDQyNCAyMS4yOTIyOTgyIC0xMjMuNTI3MzQzNzUgMjEuODM1OTM3NSBDLTEyMi43NTk1MTU2OSAyMS45NzAyNzY5NSAtMTIxLjk5MTY4NzYyIDIyLjEwNDYxNjM5IC0xMjEuMjAwNTkyMDQgMjIuMjQzMDI2NzMgQy0xMTYuNTgyMzQxNTUgMjMuMDQ4OTE0MzggLTExMS45NjA1MzY3MyAyMy44MjQ5ODM2MSAtMTA3LjMzMjAzMTI1IDI0LjU3MDMxMjUgQy0xMDYuMjYxMDYyMDEgMjQuNzQzMjg4NTcgLTEwNS4xOTAwOTI3NyAyNC45MTYyNjQ2NSAtMTA0LjA4NjY2OTkyIDI1LjA5NDQ4MjQyIEMtMTAyLjE1NjU3ODI4IDI1LjQwMzk1MzIxIC0xMDAuMjI1ODAzMTYgMjUuNzA5MjA5MjUgLTk4LjI5NDE4OTQ1IDI2LjAwOTAzMzIgQy05Mi44Njg5ODAwMyAyNi44ODQ3ODE3NiAtODcuNjU1NTgzMDcgMjguMTIxMDIxNiAtODIuMzY4NjUyMzQgMjkuNjE2OTQzMzYgQy03Ny42NTgwNTc2NSAzMC45MTkzMjI5MyAtNzIuODk3ODY0MjQgMzEuOTk1NjA0NjcgLTY4LjEzMjgxMjUgMzMuMDc4MTI1IEMtNjcuMTY2NjYwMTYgMzMuMzAzMDY2NDEgLTY2LjIwMDUwNzgxIDMzLjUyODAwNzgxIC02NS4yMDUwNzgxMiAzMy43NTk3NjU2MiBDLTY0LjI3NTAxOTUzIDMzLjk3MTgxNjQxIC02My4zNDQ5NjA5NCAzNC4xODM4NjcxOSAtNjIuMzg2NzE4NzUgMzQuNDAyMzQzNzUgQy02MS41NTU5OTg1NCAzNC41OTI3MjIxNyAtNjAuNzI1Mjc4MzIgMzQuNzgzMTAwNTkgLTU5Ljg2OTM4NDc3IDM0Ljk3OTI0ODA1IEMtNTcuMzAzMzMyODIgMzUuNTA4MDQ3ODggLTU3LjMwMzMzMjgyIDM1LjUwODA0Nzg4IC01My41NzAzMTI1IDM1LjM5MDYyNSBDLTUzLjI3NjQwNjI1IDM0LjczNTc4MTI1IC01Mi45ODI1IDM0LjA4MDkzNzUgLTUyLjY3OTY4NzUgMzMuNDA2MjUgQy00NS4wMzY0MzI3OCAxNy44NTYxODAwNSAtMzEuNDAyMDc1MDYgNy41MzcwMzMyNSAtMTUuNDU1MjkxNzUgMS4yNDczMTQ0NSBDLTEwLjMzOTk4NDQyIC0wLjI3MTY2Njk2IC01LjI5NjAyODE4IC0wLjA5ODcwNjc4IDAgMCBaICIgZmlsbD0iIzZBNkE2QSIgdHJhbnNmb3JtPSJ0cmFuc2xhdGUoMjIxLjU3MDMxMjUsODUuNjA5Mzc1KSIvPgo8cGF0aCBkPSJNMCAwIEMxLjE2MjI0MDkxIDAuMDA1NjU5NzkgMi4zMjQ0ODE4MSAwLjAxMTMxOTU4IDMuNTIxOTQyMTQgMC4wMTcxNTA4OCBDNy4xOTk5NTk2MSAwLjAzOTM3MzggMTAuODc2OTY5MTIgMC4wODk1NDU1OCAxNC41NTQ2ODc1IDAuMTQwNjI1IEMxNy4wNjI0ODU4NCAwLjE2MDcwODEyIDE5LjU3MDI5OTU5IDAuMTc4OTU1NjkgMjIuMDc4MTI1IDAuMTk1MzEyNSBDMjguMTk1NjUwOTcgMC4yMzkxOTIzOCAzNC4zMTI1OTcxOSAwLjMwNTk2MjcxIDQwLjQyOTY4NzUgMC4zOTA2MjUgQzM4LjMxMzQyMjQzIDIuNTczNjk3MjYgMzYuNTA1NzgxMjMgNC4wMjg5MjA0NiAzMy43Njk1MzEyNSA1LjM3MTA5Mzc1IEMzMy4wNjI4ODMzIDUuNzI2MzkxNiAzMi4zNTYyMzUzNSA2LjA4MTY4OTQ1IDMxLjYyODE3MzgzIDYuNDQ3NzUzOTEgQzMwLjUwODk4NTYgNy4wMDcyODc2IDMwLjUwODk4NTYgNy4wMDcyODc2IDI5LjM2NzE4NzUgNy41NzgxMjUgQzE4LjIxOTcwNDMyIDEzLjMyNTM2NTk5IDUuODk1OTAzNjcgMjAuOTg0NDY4OTggMS40Mjk2ODc1IDMzLjM5MDYyNSBDMC4xNzY3NTczMyA0MS40MDMxOTA3OCAyLjc0OTI3NDE0IDQ4LjEzNDI5MDIyIDYuOTg0Mzc1IDU0Ljg1OTM3NSBDMTUuOTYwOTE3NjIgNjcuMDMzNTcwMTQgMjguOTQyODkzNDIgNzUuMDUwOTEyIDQyLjQyOTY4NzUgODEuMzkwNjI1IEM0My4wNTA4NTQ0OSA4MS42ODkyMDQxIDQzLjY3MjAyMTQ4IDgxLjk4Nzc4MzIgNDQuMzEyMDExNzIgODIuMjk1NDEwMTYgQzYzLjIzNzE3Mzk3IDkxLjI0MzUzNTA1IDg0LjM1MjczNzIxIDk1LjQxNzE0MzEzIDEwNC44Nzc5Mjk2OSA5OC45Mzg5NjQ4NCBDMTA3LjM4NTQzNDUyIDk5LjM4Mjc5MjI0IDEwOS44Nzg4MTgyNyA5OS44NzU2NTE3MSAxMTIuMzc1IDEwMC4zNzg5MDYyNSBDMTQ0LjM2MDI1MTczIDEwNi41NjQzOTQ5NSAxNzcuNjIzNTg3NTQgMTA3LjM5MzExOTc1IDIxMC4wNzQ5NTExNyAxMDkuNDM5Njk3MjcgQzIxMC45NzQ2MTYwOSAxMDkuNDk2OTI5NjMgMjExLjg3NDI4MTAxIDEwOS41NTQxNjE5OSAyMTIuODAxMjA4NSAxMDkuNjEzMTI4NjYgQzIxNC40NTg5MTk3NCAxMDkuNzE4MDk4NyAyMTYuMTE2NzQ4MTQgMTA5LjgyMTI0NDk1IDIxNy43NzQ3MTkyNCAxMDkuOTIyMDI3NTkgQzIyMy4wMjk2NjM5NyAxMTAuMjU0Mjk1MzYgMjI4LjE4MjMwNDY1IDExMC44MDc1ODI0NiAyMzMuNDI5Njg3NSAxMTEuMzkwNjI1IEMyMzMuNDI5Njg3NSAxMjkuMjEwNjI1IDIzMy40Mjk2ODc1IDE0Ny4wMzA2MjUgMjMzLjQyOTY4NzUgMTY1LjM5MDYyNSBDMjIzLjY0NjI5Mjk1IDE2NC43MzgzOTg3IDIxMy45MjQ2MTU0NiAxNjQuMDI5MDA3MjUgMjA0LjE3OTY4NzUgMTYzLjAxNTYyNSBDMjAyLjkyMTg4NDc3IDE2Mi44ODU1MTAyNSAyMDEuNjY0MDgyMDMgMTYyLjc1NTM5NTUxIDIwMC4zNjgxNjQwNiAxNjIuNjIxMzM3ODkgQzE5Mi42MDcyNDUyNyAxNjEuNzk0MDY5NjYgMTg0Ljg5Mzg5MTc2IDE2MC44MzMyNzA3OCAxNzcuMjA2MDU0NjkgMTU5LjQ4MDk1NzAzIEMxNzMuMDQwNDAyNjcgMTU4Ljc1NjU0MDQ5IDE2OC44ODY0MzIxOSAxNTguMjE3OTYxNDIgMTY0LjY4MDQzNTE4IDE1Ny43NzQ5NDgxMiBDMTU1LjQ3NjU0NTU0IDE1Ni43ODY4ODM1OSAxNDYuNTUzNzUzMjYgMTU1LjExMTQ3OTIxIDEzNy41MzU0MDAzOSAxNTMuMDQxNTAzOTEgQzEzNS4yMzQ2OTAzNiAxNTIuNTEzOTA1NzYgMTMyLjkzMTIxNDUgMTUyLjAwMDEyMjQ3IDEzMC42MjY5NTMxMiAxNTEuNDg4MjgxMjUgQzEyMi41MjM1ODEwNCAxNDkuNjY5NTY1IDExNC41NTg3Mzk3MSAxNDcuNTk5NDgwNzUgMTA2LjU4OTExMTMzIDE0NS4yNTE5NTMxMiBDMTAzLjc0MDQxMTM4IDE0NC40NzUzMzUxMyAxMDAuOTU3MzQ2OTEgMTQzLjg5NTc2NTk5IDk4LjA0Njg3NSAxNDMuNDE0MDYyNSBDOTEuNDM4MDI2OTQgMTQyLjI5NzY1Mzk0IDg1LjAzOTA1NDYgMTQwLjU1NjUxNjgxIDc4LjYyOTg4MjgxIDEzOC42MjY0NjQ4NCBDNzcuMjQxMjQ4MDggMTM4LjIxNzcxNjEyIDc1Ljg0NjczMTMgMTM3LjgyODQ2NjA1IDc0LjQ0NzI2NTYyIDEzNy40NTg0OTYwOSBDNjIuNzk0MjUwMTIgMTM0LjM2NjA0ODYgNjIuNzk0MjUwMTIgMTM0LjM2NjA0ODYgNTkuNDcyOTAwMzkgMTI5LjU1Nzg2MTMzIEM1OC4yMTg1MjYyNyAxMjYuNTI3NzIwODQgNTcuMzE3Nzg1NjUgMTIzLjU0MzY3MTQ1IDU2LjQyOTY4NzUgMTIwLjM5MDYyNSBDNDcuODI4MTgwNiAxMDIuMjc5NjE2NzYgMzQuMTMxNjE0MDkgODcuNTgwMjc4NTMgMTguNDI5Njg3NSA3NS4zOTA2MjUgQzE2LjYzNTg5MTI4IDczLjg5MzE3MjMxIDE0Ljg0NDI1MDY2IDcyLjM5MzEzMzk1IDEzLjA1NDY4NzUgNzAuODkwNjI1IEM1LjAwMTgzNzAyIDY0LjMxOTY4MjgxIC0zLjM0NzQzMjQyIDU4LjEyODgxNDY4IC0xMi43ODkwNjI1IDUzLjY5OTIxODc1IEMtMTQuOTgyMjg0MzggNTIuNjY3Mjk1NTQgLTE3LjEzNTM3ODg3IDUxLjU5ODE2NDk5IC0xOS4yODkwNjI1IDUwLjQ4ODI4MTI1IEMtMzAuMzI2MTQxNDIgNDQuODE1MDAzOTIgLTQxLjI4NDk0MjQ1IDM5LjY4MTExNzcyIC01My41NzAzMTI1IDM3LjM5MDYyNSBDLTQ5Ljk2Njk1ODYyIDIzLjMzNzU0NDg3IC0zNy45MjEzMjM4IDEzLjM3NjQxNzkzIC0yNi4wMzkwNjI1IDYuMTc5Njg3NSBDLTE3LjA5Njk0MzcyIDEuNTY3NjQ4NzYgLTEwLjEwOTk0MjUyIC0wLjE4ODQyNzk4IDAgMCBaICIgZmlsbD0iI0U5NUQwMiIgdHJhbnNmb3JtPSJ0cmFuc2xhdGUoMjIxLjU3MDMxMjUsODUuNjA5Mzc1KSIvPgo8L3N2Zz4K)](https://www.naviki.org)

