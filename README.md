# 🚴 naviki-gpx-exporter

> Automated GPX export tool for Naviki routes. One command to backup all your cycling data. Features OAuth2 auto-login, batch download, and incremental sync. Your rides, your files.

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
git clone https://github.com/yourusername/naviki-gpx-exporter.git
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