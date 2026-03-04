# Quick Start Guide

Get Doccano running in **5 minutes** on your local machine.

---

## ⏱️ First Run (Expected Duration)

On first run, the setup script automatically:

1. ✅ Install Python dependencies via Poetry (~2-3 minutes)
2. ✅ Run database migrations (~30 seconds)
3. ✅ Install Node.js packages via npm (~1-2 minutes)
4. ✅ Create admin user (admin/admin)
5. ✅ Start all services (~30 seconds)

**Estimated first run duration: ~5 minutes**

Subsequent runs are faster (~30 seconds) because dependencies are cached.

> **Prerequisites required:** Python 3.10+, Node.js 18+, Poetry
> Missing something? See [INSTALLATION.md](INSTALLATION.md) for setup instructions.

> **Note:** The startup scripts now auto-install backend/frontend dependencies on first run.

---

## 🪟 Windows

### Option 1: Local Development (Recommended)

```powershell
# Open PowerShell in doccano folder
.\executarDoccanoDevEnv.ps1
```

This opens 3 terminal windows:
- **Backend** - Django API on port 8000
- **Celery** - Task queue
- **Frontend** - Nuxt on port 3000

➜ Open browser: **http://localhost:3000**

If Nuxt shows a local network URL (for example `http://192.168.56.1:3000`), you can use it as an alternative.

Run quick health validation:

```powershell
.\quickSanityCheck.ps1
```

**If Backend Fails (e.g., "181 unapplied migrations"):**

```powershell
# Clean up and try again
.\cleanupDevEnv.ps1
.\executarDoccanoDevEnv.ps1
```

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for more solutions.

### Option 2: Docker Setup

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

If Nuxt shows a local network URL (for example `http://192.168.56.1:3000`), you can use it as an alternative.

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

Starts backend, celery, and frontend processes in the background (same terminal session).

➜ Open browser: **http://localhost:3000**

If Nuxt shows a local network URL (for example `http://192.168.56.1:3000`), you can use it as an alternative.

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

> **Note:** First login may take 10-15 seconds.

---

## 🛑 Stopping Services

### Local Development

**Windows/macOS:**
1. Go to each of the 3 terminal windows
2. Press `Ctrl+C` in each window to stop the service
3. Close the terminal windows

Or simply close all terminal windows (services will auto-terminate).

**Linux:**
1. Return to the terminal where `./executarDoccanoDevEnv.sh` is running
2. Press `Ctrl+C` once to stop all background services

### Docker

**Windows:**
```powershell
cd docker
docker compose -f docker-compose.prod.yml down
# OR if using older Docker:
docker-compose -f docker-compose.prod.yml down
```

**macOS/Linux:**
```bash
cd docker
docker-compose -f docker-compose.prod.yml down
```

---

## 📍 Default URLs

| Service | URL | Port |
|---------|-----|------|
| Frontend | http://localhost:3000 (or local network URL shown by Nuxt) | 3000 |
| Backend Health | http://127.0.0.1:8000/v1/health/ | 8000 |
| Swagger | http://127.0.0.1:8000/swagger/ | 8000 |
| API Schema | http://127.0.0.1:8000/api/schema.json | 8000 |
| Nginx (Docker only) | http://localhost | 80 |

---

## ✅ What's Running?

### Local Development
- Django backend with SQLite
- Celery worker
- SQLAlchemy + SQLite message broker
- Nuxt frontend (dev server)

> On Windows, Celery runs with `--pool=solo` for compatibility.

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

### "nuxt is not recognized"
This means frontend dependencies are missing.

```bash
cd frontend
npm install
npm run dev
```

### `Environment variable "SECRET_KEY" not set`
If this appears, regenerate development `.env` using the startup script:

```powershell
# Windows
.\executarDoccanoDevEnv.ps1
```

```bash
# macOS/Linux
./executarDoccanoDevEnv.sh
```

### Non-blocking development warnings
Warnings like the TypeScript compatibility notice from ESLint do not block local execution.

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

# Then open in browser: http://localhost:3000
# Login: admin / admin
```

Setup complete.
