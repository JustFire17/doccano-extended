# Quick Start Guide

Get Doccano running in **5 minutes** on your local machine.

---

## 🪟 Windows

### Option 1: Local Development (Recommended)

**Best for:** First-time users, development work, learning Doccano

```powershell
# Open PowerShell in doccano folder
.\executarDoccanoDevEnv.ps1
```

This opens 3 terminal windows:
- **Backend** - Django API on port 8000
- **Celery** - Task queue
- **Frontend** - Nuxt on port 3000

➜ Open browser: **http://localhost:3000**

### Option 2: Docker Setup

**Best for:** Production-like environment, testing containers

```powershell
.\executarDoccanoDocker.ps1
```

This starts all services in Docker containers (PostgreSQL, RabbitMQ, Redis, etc).

➜ Open browser: **http://localhost** or **http://localhost:3000**

---

## 🍎 macOS

### Local Development

```bash
chmod +x executarDoccanoDevEnv.sh
./executarDoccanoDevEnv.sh
```

Opens 3 terminal windows (same as Windows above).

➜ Open browser: **http://localhost:3000**

### Docker Setup

```bash
cd docker
docker-compose -f docker-compose.prod.yml up -d
```

➜ Open browser: **http://localhost**

---

## 🐧 Linux (Ubuntu/Debian)

### Local Development

```bash
chmod +x executarDoccanoDevEnv.sh
./executarDoccanoDevEnv.sh
```

Opens 3 terminal windows.

➜ Open browser: **http://localhost:3000**

### Docker Setup

```bash
cd docker
docker-compose -f docker-compose.prod.yml up -d
```

➜ Open browser: **http://localhost**

---

## 🔐 Login

**Default credentials:**
- **Username:** `admin`
- **Password:** `admin`

---

## 📍 Default URLs

| Service | URL | Port |
|---------|-----|------|
| Frontend | http://localhost:3000 | 3000 |
| Backend API | http://localhost:8000 | 8000 |
| Flower (Task Monitor) | http://localhost:5555 | 5555 |
| Nginx (Docker only) | http://localhost | 80 |

---

## ✅ What's Running?

### Local Development
- Django backend with SQLite
- Celery worker
- Redis (cache)
- Nuxt frontend (dev server)
- RabbitMQ (local service)

### Docker
- PostgreSQL database
- RabbitMQ message broker
- Redis cache
- Django backend
- Celery worker
- Nuxt frontend
- Nginx web server
- Flower task monitor

---

## 🐛 Common Issues

### "Script won't run" (Windows)
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### "Port already in use"
```bash
# Windows
Stop-Process -Name python -Force

# Mac/Linux
kill -9 $(lsof -t -i:3000)
```

### "Can't login"
Try these in order:
1. Verify admin/admin is correct
2. Hard refresh browser: `Ctrl+Shift+R` (Windows) or `Cmd+Shift+R` (Mac)
3. Wait 30 seconds - first login is slow
4. Check backend logs for errors

### "Services won't start"
- **Windows:** Make sure PowerShell is run as **Administrator**
- **Mac/Linux:** Check Python & Node.js installed: `python --version` and `node --version`
- **Docker:** Make sure Docker Desktop is running

---

## 📚 Next Steps

- **Full setup guide:** See [INSTALLATION.md](INSTALLATION.md)
- **Troubleshooting:** See [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- **Official docs:** https://doccano.github.io/doccano/

---

## ⚡ TL;DR for Experienced Users

```bash
# Windows
.\executarDoccanoDevEnv.ps1

# macOS/Linux
./executarDoccanoDevEnv.sh

# Then
open http://localhost:3000
# Login: admin / admin
```

Get annotating! 🚀
