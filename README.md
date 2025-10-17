# 🚴 naviki-gpx-exporter

> Automated GPX export tool for [Naviki](https://www.naviki.org) routes. One command to backup all your cycling data. Features OAuth2 auto-login, batch download, and incremental sync. Your rides, your files.


[![Naviki](https://img.shields.io/badge/Naviki-supported-FF6600?style=flat&logo=data:image/svg%2bxml;base64,PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiPz4KPHN2ZyB2ZXJzaW9uPSIxLjEiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIgd2lkdGg9IjE2IiBoZWlnaHQ9IjE2Ij4KPHBhdGggZD0iTTAgMCBDNS4yOCAwIDEwLjU2IDAgMTYgMCBDMTYgNS4yOCAxNiAxMC41NiAxNiAxNiBDMTAuNzIgMTYgNS40NCAxNiAwIDE2IEMwIDEwLjcyIDAgNS40NCAwIDAgWiAiIGZpbGw9IiNGQkZBRjkiIHRyYW5zZm9ybT0idHJhbnNsYXRlKDAsMCkiLz4KPHBhdGggZD0iTTAgMCBDNS4yOCAwIDEwLjU2IDAgMTYgMCBDMTYgMi4zMSAxNiA0LjYyIDE2IDcgQzEzLjM2IDYuMzQgMTAuNzIgNS42OCA4IDUgQzggNC4zNCA4IDMuNjggOCAzIEM3LjEwMjgxMjUgMy4yNzg0Mzc1IDcuMTAyODEyNSAzLjI3ODQzNzUgNi4xODc1IDMuNTYyNSBDNCA0IDQgNCAxIDMgQzAuNjcgMy42NiAwLjM0IDQuMzIgMCA1IEMwIDMuMzUgMCAxLjcgMCAwIFogIiBmaWxsPSIjRkVGREZEIiB0cmFuc2Zvcm09InRyYW5zbGF0ZSgwLDApIi8+CjxwYXRoIGQ9Ik0wIDAgQzEuOTggMCAzLjk2IDAgNiAwIEM2IDAuNjYgNiAxLjMyIDYgMiBDOC4zMSAyLjMzIDEwLjYyIDIuNjYgMTMgMyBDMTMgMy42NiAxMyA0LjMyIDEzIDUgQzEwLjAzIDQuNTA1IDEwLjAzIDQuNTA1IDcgNCBDNi42NyA1LjY1IDYuMzQgNy4zIDYgOSBDNC4zNSA5LjMzIDIuNyA5LjY2IDEgMTAgQzEgOS4zNCAxIDguNjggMSA4IEMxLjY2IDcuNjcgMi4zMiA3LjM0IDMgNyBDMyA1LjY4IDMgNC4zNiAzIDMgQzIuMDEgMi42NyAxLjAyIDIuMzQgMCAyIEMwIDEuMzQgMCAwLjY4IDAgMCBaICIgZmlsbD0iI0UwQjJBMCIgdHJhbnNmb3JtPSJ0cmFuc2xhdGUoMiwzKSIvPgo8cGF0aCBkPSJNMCAwIEMtMC4zMyAxLjY1IC0wLjY2IDMuMyAtMSA1IEMtMi42NSA1LjMzIC00LjMgNS42NiAtNiA2IEMtNiA0IC02IDQgLTQuMTI1IDEuODc1IEMtMiAwIC0yIDAgMCAwIFogIiBmaWxsPSIjNzY3Njc2IiB0cmFuc2Zvcm09InRyYW5zbGF0ZSg5LDcpIi8+Cjwvc3ZnPgo=)](https://www.naviki.org)
[![Python](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Selenium](https://img.shields.io/badge/selenium-4.0+-green.svg)](https://www.selenium.dev/)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg?logo=docker)](https://hub.docker.com)

[![Tests](https://github.com/Gheop/naviki-gpx-exporter/actions/workflows/tests.yml/badge.svg)](https://github.com/Gheop/naviki-gpx-exporter/actions)
[![Docker Build](https://github.com/Gheop/naviki-gpx-exporter/actions/workflows/docker.yml/badge.svg)](https://github.com/Gheop/naviki-gpx-exporter/actions/workflows/docker.yml)
[![Security Scan](https://img.shields.io/badge/security-trivy-blue.svg?logo=aqua)](https://github.com/Gheop/naviki-gpx-exporter/security)
[![codecov](https://codecov.io/gh/Gheop/naviki-gpx-exporter/branch/main/graph/badge.svg)](https://codecov.io/gh/Gheop/naviki-gpx-exporter)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## 📋 Table of Contents

- [Features](#-features)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
  - [Standard Installation (Python)](#standard-installation-python)
  - [Docker Installation (Recommended)](#docker-installation-recommended)
- [Usage](#-usage)
  - [Standard Usage](#standard-usage)
  - [Docker Usage](#docker-usage)
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
- 🐳 **Docker ready** - zero dependency hassle, works everywhere

## 🔧 Prerequisites

### Standard Installation
- **Python 3.7+**
- **Firefox browser** (for Selenium)
- **geckodriver** (Firefox WebDriver)
- A Naviki account with recorded routes

### Docker Installation (Recommended)
- **Docker** (that's it!)

## 📥 Installation

Choose your preferred installation method:

### Standard Installation (Python)

#### 1. Clone the repository

```bash
git clone https://github.com/Gheop/naviki-gpx-exporter.git
cd naviki-gpx-exporter
```

#### 2. Install Python dependencies

```bash
pip install -r requirements.txt
```

Or install manually:

```bash
pip install selenium requests beautifulsoup4
```

#### 3. Install geckodriver (Firefox WebDriver)

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

### Docker Installation (Recommended)

#### Option 1: Use pre-built image (easiest)

```bash
# Pull the latest image from GitHub Container Registry
docker pull ghcr.io/gheop/naviki-gpx-exporter:latest

# You're ready to go! See Docker Usage below.
```

#### Option 2: Build locally

```bash
# Clone the repository
git clone https://github.com/Gheop/naviki-gpx-exporter.git
cd naviki-gpx-exporter

# Build the Docker image
docker build -t naviki-gpx-exporter:latest .

# Or use make (simpler)
make build
```

#### Option 3: Using docker-compose

```bash
# Clone and setup
git clone https://github.com/Gheop/naviki-gpx-exporter.git
cd naviki-gpx-exporter

# Copy and edit configuration
cp .env.example .env
nano .env  # Add your credentials

# Build
docker-compose build
```

## 🚀 Usage

### Standard Usage

#### Basic Usage (Automated Authentication)

```bash
python naviki-gpx-exporter.py --username YourUsername --password 'YourPassword'
```

#### Using a Pre-existing Token

```bash
python naviki-gpx-exporter.py --token YOUR-OAUTH-TOKEN-HERE
```

#### Custom Output Directory

```bash
python naviki-gpx-exporter.py --username YourUsername --password 'YourPassword' --output ~/cycling/naviki-backup
```

#### Visible Browser Mode (for debugging)

```bash
python naviki-gpx-exporter.py --username YourUsername --password 'YourPassword' --visible
```

### Docker Usage

#### Quick Start (One Command)

```bash
# Linux/macOS
docker run --rm \
  --user $(id -u):$(id -g) \
  -v $(pwd)/output:/output \
  ghcr.io/gheop/naviki-gpx-exporter:latest \
  --username YourUsername --password 'YourPassword' --output /output

# Windows (PowerShell) - Note: --user option not needed on Windows
docker run --rm -v ${PWD}/output:/output `
  ghcr.io/gheop/naviki-gpx-exporter:latest `
  --username YourUsername --password "YourPassword" --output /output

# Windows (CMD) - Note: --user option not needed on Windows
docker run --rm -v %cd%/output:/output ^
  ghcr.io/gheop/naviki-gpx-exporter:latest ^
  --username YourUsername --password "YourPassword" --output /output
```

Your GPX files will be in the `output/` folder! 🎉

**Note:** The `--user $(id -u):$(id -g)` option ensures files are created with your user permissions on Linux/macOS.

#### Using the Helper Script (Easiest)

```bash
# Make script executable
chmod +x docker-run.sh

# Run with username/password
./docker-run.sh -u YourUsername -p 'YourPassword'

# Run with OAuth token
./docker-run.sh -t your-oauth-token

# Custom output directory
./docker-run.sh -u YourUsername -p 'YourPassword' -o ~/backup
```

#### Using Makefile (Simplest)

```bash
# Setup once
cp .env.example .env
nano .env  # Add your credentials

# Build and run
make build  # First time only
make run    # Every time you want to export

# Other useful commands
make run-token    # Use with OAuth token
make shell        # Open shell in container
make test         # Run tests in Docker
make clean        # Clean up images
```

#### Using docker-compose

```bash
# Setup once
cp .env.example .env
nano .env  # Add your credentials

# Run
docker-compose run --rm naviki-exporter \
  --username "$NAVIKI_USERNAME" \
  --password "$NAVIKI_PASSWORD" \
  --output /output
```

## 📚 Examples

### Standard Python Examples

#### Example 1: First-time backup
```bash
python naviki-gpx-exporter.py \
  --username MyUsername \
  --password 'MySecurePass123!' \
  --output ~/naviki-backup
```

#### Example 2: Daily sync (incremental)
```bash
python naviki-gpx-exporter.py \
  --username MyUsername \
  --password 'MySecurePass123!' \
  --output ~/naviki-backup \
  --headless
```

#### Example 3: Only recorded routes
```bash
python naviki-gpx-exporter.py \
  --username MyUsername \
  --password 'MySecurePass123!' \
  --types recordedMy \
  --output ~/recorded-only
```

#### Example 4: Using stored token
```bash
# Get your token once (lasts for session)
python naviki-gpx-exporter.py --username MyUsername --password 'pass' --output /tmp

# Reuse token for multiple runs
python naviki-gpx-exporter.py --token abc123-def456-ghi789 --output ~/backup1
python naviki-gpx-exporter.py --token abc123-def456-ghi789 --output ~/backup2
```

### Docker Examples

#### Example 1: Basic export with Docker
```bash
docker run --rm \
  --user $(id -u):$(id -g) \
  -v $(pwd)/output:/output \
  ghcr.io/gheop/naviki-gpx-exporter:latest \
  --username MyUsername \
  --password 'MyPassword!' \
  --output /output
```

#### Example 2: Using OAuth token
```bash
docker run --rm \
  --user $(id -u):$(id -g) \
  -v $(pwd)/output:/output \
  ghcr.io/gheop/naviki-gpx-exporter:latest \
  --token abc123-def456-ghi789 \
  --output /output
```

#### Example 3: Specific route types only
```bash
docker run --rm \
  --user $(id -u):$(id -g) \
  -v $(pwd)/output:/output \
  ghcr.io/gheop/naviki-gpx-exporter:latest \
  --username MyUsername \
  --password 'MyPassword!' \
  --types recordedMy \
  --output /output
```

#### Example 4: Custom output location
```bash
# Linux/macOS
docker run --rm \
  --user $(id -u):$(id -g) \
  -v ~/naviki-backup:/output \
  ghcr.io/gheop/naviki-gpx-exporter:latest \
  --username MyUsername \
  --password 'MyPassword!' \
  --output /output

# Windows (no --user needed)
docker run --rm \
  -v C:\Users\YourName\naviki-backup:/output \
  ghcr.io/gheop/naviki-gpx-exporter:latest \
  --username MyUsername \
  --password "MyPassword!" \
  --output /output
```

#### Example 5: Automated daily backup (cron)

**Standard Python:**
```bash
# Add to crontab (crontab -e)
0 2 * * * /usr/bin/python3 /path/to/naviki-gpx-exporter.py --username USER --password 'PASS' --output ~/naviki-backup >> ~/naviki.log 2>&1
```

**Docker:**
```bash
# Add to crontab (crontab -e)
0 2 * * * docker run --rm --user $(id -u):$(id -g) -v /home/user/naviki-backup:/output ghcr.io/gheop/naviki-gpx-exporter:latest --token YOUR_TOKEN --output /output >> /var/log/naviki.log 2>&1
```

#### Example 6: Automated backup on Synology NAS
```bash
# Via Task Scheduler in DSM
docker run --rm \
  --user $(id -u):$(id -g) \
  -v /volume1/backups/naviki:/output \
  ghcr.io/gheop/naviki-gpx-exporter:latest \
  --token YOUR_TOKEN \
  --output /output
```

#### Example 7: Using with Raspberry Pi
```bash
# ARM64 supported automatically
docker pull ghcr.io/gheop/naviki-gpx-exporter:latest

docker run --rm \
  --user $(id -u):$(id -g) \
  -v /home/pi/naviki-backup:/output \
  ghcr.io/gheop/naviki-gpx-exporter:latest \
  --username MyUsername \
  --password 'MyPassword!' \
  --output /output
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

### Standard Python Issues

#### Issue: "geckodriver not found"

**Solution:**
```bash
# Ubuntu/Debian
sudo apt install firefox-geckodriver

# Or download manually
wget https://github.com/mozilla/geckodriver/releases/download/v0.33.0/geckodriver-v0.33.0-linux64.tar.gz
tar -xvzf geckodriver-v0.33.0-linux64.tar.gz
sudo mv geckodriver /usr/local/bin/
```

#### Issue: "Token invalide ou expiré"

**Solution:** Tokens expire after some time. Re-authenticate:
```bash
python naviki-gpx-exporter.py --username YourUsername --password 'YourPassword'
```

#### Issue: Authentication fails silently

**Solution:** Run in visible mode to see what's happening:
```bash
python naviki-gpx-exporter.py --username YourUsername --password 'YourPassword' --visible
```

Check the screenshot saved at `/tmp/naviki_debug.png` for visual debugging.

#### Issue: Special characters in password

**Solution:** Always quote your password:
```bash
# Correct
python naviki-gpx-exporter.py --username user --password 'P@ss!w0rd#123'

# Wrong (shell will interpret special chars)
python naviki-gpx-exporter.py --username user --password P@ss!w0rd#123
```

### Docker Issues

#### Issue: "Cannot connect to Docker daemon"

**Solution:**
```bash
# Verify Docker is running
docker --version
docker ps

# Start Docker
# Linux: sudo systemctl start docker
# macOS/Windows: Start Docker Desktop
```

#### Issue: Permission denied on exported files

This issue occurs when Docker creates files as root. The solution is already included in all examples above using `--user $(id -u):$(id -g)`.

**If you still have permission issues:**

```bash
# Solution 1: Change owner after export (if needed)
sudo chown -R $USER:$USER output/

# Solution 2: Ensure you're using the --user flag
docker run --rm \
  --user $(id -u):$(id -g) \
  -v $(pwd)/output:/output \
  ghcr.io/gheop/naviki-gpx-exporter:latest \
  --username YourUsername --password 'YourPassword' --output /output
```

**On Windows:** The `--user` flag is not needed and should be omitted.

#### Issue: Image not found or outdated

**Solution:**
```bash
# Pull latest version
docker pull ghcr.io/gheop/naviki-gpx-exporter:latest

# Or with helper script
./docker-run.sh --pull -u YourUsername -p 'YourPassword'

# Or rebuild locally
make build
```

#### Issue: Container exits immediately

**Solution:**
```bash
# Check logs
docker logs $(docker ps -lq)

# Test the image
docker run --rm --entrypoint /bin/bash \
  ghcr.io/gheop/naviki-gpx-exporter:latest \
  -c "geckodriver --version && firefox-esr --version"
```

### General Issues

#### Issue: Downloads are slow

**Solution:** This is normal - each GPX file requires an API call. For 100 routes, expect 2-5 minutes.

#### Issue: Some routes have generic names like "2024-11-24_06-18_UTC_Naviki.gpx"

**Explanation:** Routes without a date in the title use the creation timestamp (UTC timezone). This is expected behavior.

## 🐳 Advanced Docker Usage

### Using Named Volumes

```bash
# Create a volume
docker volume create naviki-backup

# Use the volume
docker run --rm \
  --user $(id -u):$(id -g) \
  -v naviki-backup:/output \
  ghcr.io/gheop/naviki-gpx-exporter:latest \
  --username MyUsername \
  --password 'MyPassword!' \
  --output /output

# View files in volume
docker run --rm -v naviki-backup:/output alpine ls -lah /output
```

### Resource Limits

```bash
docker run --rm \
  --user $(id -u):$(id -g) \
  --memory="512m" \
  --cpus="1.0" \
  -v $(pwd)/output:/output \
  ghcr.io/gheop/naviki-gpx-exporter:latest \
  --username MyUsername \
  --password 'MyPassword!' \
  --output /output
```

### Custom Timezone

```bash
docker run --rm \
  --user $(id -u):$(id -g) \
  -e TZ=Europe/Paris \
  -v $(pwd)/output:/output \
  ghcr.io/gheop/naviki-gpx-exporter:latest \
  --username MyUsername \
  --password 'MyPassword!' \
  --output /output
```

### Using Environment Variables

```bash
# Set environment variables
export NAVIKI_USERNAME="MyUsername"
export NAVIKI_PASSWORD="MyPassword"

# Run without exposing credentials
docker run --rm \
  --user $(id -u):$(id -g) \
  -e NAVIKI_USERNAME \
  -e NAVIKI_PASSWORD \
  -v $(pwd)/output:/output \
  ghcr.io/gheop/naviki-gpx-exporter:latest \
  --username "$NAVIKI_USERNAME" \
  --password "$NAVIKI_PASSWORD" \
  --output /output
```

### Integration with CI/CD

```yaml
# Example GitHub Actions workflow
name: Backup Naviki Routes

on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM
  workflow_dispatch:

jobs:
  backup:
    runs-on: ubuntu-latest
    steps:
      - name: Backup routes
        run: |
          docker run --rm \
            -v ${{ github.workspace }}/naviki-backup:/output \
            ghcr.io/gheop/naviki-gpx-exporter:latest \
            --token ${{ secrets.NAVIKI_TOKEN }} \
            --output /output
      
      - name: Upload artifacts
        uses: actions/upload-artifact@v3
        with:
          name: naviki-routes
          path: naviki-backup/*.gpx
          retention-days: 90
```

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

### Reporting Bugs

1. Check if the issue already exists in [Issues](https://github.com/Gheop/naviki-gpx-exporter/issues)
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
4. Test thoroughly (including Docker if applicable)
5. Commit: `git commit -m 'Add amazing feature'`
6. Push: `git push origin feature/amazing-feature`
7. Open a Pull Request

### Development Setup

#### Standard Python Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/naviki-gpx-exporter.git
cd naviki-gpx-exporter

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run tests
pytest tests/ -v
```

#### Docker Development

```bash
# Build image
make build

# Run tests in Docker
make test

# Test the Docker build
./test-docker.sh

# Open shell in container for debugging
make shell
```

### Running Tests

```bash
# Standard tests
pytest tests/ -v --cov=. --cov-report=term

# Docker tests
./test-docker.sh

# Integration tests
pytest tests/test_integration.py -v

# All tests with make
make test

# Security scan
./security-scan-local.sh
# or
make security-scan
```

## 🔒 Security

This project takes security seriously. Docker images are automatically scanned for vulnerabilities using [Trivy](https://github.com/aquasecurity/trivy).

### Scanning Locally

```bash
# Make the script executable
chmod +x security-scan-local.sh

# Run security scan
./security-scan-local.sh

# Or with make
make security-scan
```

### Viewing Security Reports

Security scan results are automatically uploaded to GitHub Security tab after each build. You can view them at:
`https://github.com/Gheop/naviki-gpx-exporter/security`

### Reporting Security Issues

If you discover a security vulnerability, please email [votre@email.com](mailto:votre@email.com) instead of using the issue tracker.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Naviki](https://www.naviki.org/) for providing an excellent cycling navigation app
- [Selenium](https://www.selenium.dev/) for browser automation
- The cycling community for inspiration
- Docker community for containerization best practices

## 📧 Contact

- Create an [issue](https://github.com/Gheop/naviki-gpx-exporter/issues) for bugs or features
- For questions, use [Discussions](https://github.com/Gheop/naviki-gpx-exporter/discussions)
- Docker images: [GitHub Container Registry](https://github.com/Gheop/naviki-gpx-exporter/pkgs/container/naviki-gpx-exporter)

## 🚀 Quick Links

- **Docker Quick Start**: See [DOCKER_QUICKSTART.md](DOCKER_QUICKSTART.md)
- **Tests**: Run `make test` or `pytest tests/`
- **CI/CD**: GitHub Actions automatically builds and publishes Docker images
- **Latest Docker Image**: `ghcr.io/gheop/naviki-gpx-exporter:latest`

---

**⚠️ Disclaimer:** This tool is not affiliated with or endorsed by Naviki. Use responsibly and respect Naviki's terms of service. This tool is for personal backup purposes only.

**🌟 If this tool helped you, consider giving it a star!**

**🐳 Docker users**: This project is Docker-ready! See the Docker sections above for zero-hassle installation.