# 📦 Installation & Setup Guide

Complete instructions for all platforms.

---

## Prerequisites Installation

### Windows 10/11

#### Python 3.8+
1. Download: https://www.python.org/downloads/
2. **CHECK:** "Add Python to PATH" during installation
3. Open PowerShell and verify:
   ```powershell
   python --version
   ```

#### Poetry (Package Manager)
1. Open PowerShell **as Administrator**
2. Run:
   ```powershell
   (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
   ```
3. **Close and reopen PowerShell**
4. Verify:
   ```powershell
   poetry --version
   ```

#### Node.js 16+
1. Download: https://nodejs.org/ (LTS)
2. Install, accept defaults
3. **Restart PowerShell**
4. Verify:
   ```powershell
   node --version
   npm --version
   ```

#### Docker Desktop
1. Download: https://www.docker.com/products/docker-desktop/
2. Install and **restart computer**
3. Verify:
   ```powershell
   docker --version
   ```

---

### macOS

```bash
# Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Python
brew install python@3.11

# Poetry
brew install poetry

# Node.js
brew install node

# Docker (optional)
brew install --cask docker
```

Verify:
```bash
python3 --version
poetry --version
node --version
docker --version
```

---

### Linux - Ubuntu/Debian

```bash
# Python
sudo apt update
sudo apt install python3 python3-pip python3-venv

# Poetry
curl -sSL https://install.python-poetry.org | python3 -
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc

# Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Docker
sudo apt install docker.io docker-compose
sudo usermod -aG docker $USER
newgrp docker

# Verify (restart terminal first)
python3 --version && poetry --version && node --version && docker --version
```

---

### Linux - Fedora/RHEL

```bash
# Python & Poetry
sudo dnf install python3 python3-pip
curl -sSL https://install.python-poetry.org | python3 -

# Node.js
sudo dnf install nodejs npm

# Docker
sudo dnf install docker docker-compose
sudo systemctl start docker
sudo usermod -aG docker $USER

# Verify
python3 --version && poetry --version && node --version && docker --version
```

---

## Environment Configuration

The `.env` file is **automatically generated** by scripts.

### For Development (Local)
```
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,192.168.56.1,192.168.1.1
CORS_ALLOWED_ORIGINS=http://localhost:3000,...
DATABASE_URL=sqlite:///db.sqlite3
```

### For Production (Docker)
```
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,doccano-nginx
CORS_ALLOWED_ORIGINS=http://localhost,...
SECURE_SSL_REDIRECT=False (for localhost testing)
DATABASE_URL=postgres://...
```

### Production Security Checklist
- [ ] Change `ADMIN_PASSWORD` (not "admin")
- [ ] Change database passwords
- [ ] Generate new `SECRET_KEY`
- [ ] Set `SECURE_SSL_REDIRECT=True`
- [ ] Use HTTPS (SSL certificates)
- [ ] Use PostgreSQL (not SQLite)

---

## Troubleshooting

### "Command not found" after installation

**Windows:**
- Close PowerShell completely
- Open NEW PowerShell
- Try again

**macOS/Linux:**
```bash
source ~/.bashrc    # or ~/.zshrc
```

### Docker: permission denied (Linux)

```bash
sudo usermod -aG docker $USER
newgrp docker
# Restart terminal
```

### Port already in use

```powershell
# Windows: Find and kill process
Get-NetTCPConnection -LocalPort 3000 | Stop-Process -Force

# Linux/macOS: Find process
lsof -i :3000
kill -9 <PID>
```

### Poetry: "No such file or directory"

```bash
# Reinstall Poetry
pip install --upgrade poetry
```

---

## Next Steps

✅ All prerequisites installed?

→ Go to [QUICK_START.md](QUICK_START.md) to run your first script!
