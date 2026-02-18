# 🐛 Troubleshooting Guide

Solutions for common issues when setting up or running Doccano.

---

## 🚀 Setup Script Issues

### Script Won't Run

**Windows - "cannot be loaded because running scripts is disabled"**
```powershell
# Open PowerShell as Administrator and run:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then try again:
```powershell
.\executarDoccanoDevEnv.ps1
```

**macOS/Linux - "Permission denied"**
```bash
chmod +x executarDoccanoDevEnv.sh
./executarDoccanoDevEnv.sh
```

---

### Missing Prerequisites

| Error | Solution |
|-------|----------|
| `python: command not found` | Install Python 3.8+ from [python.org](https://www.python.org/downloads/) |
| `poetry: command not found` | Install from [poetry.io](https://python-poetry.org/docs/#installation) or `pip install poetry` |
| `node: command not found` | Install Node.js 16+ from [nodejs.org](https://nodejs.org/) |
| `docker: command not found` | Install [Docker Desktop](https://www.docker.com/products/docker-desktop/) |

See [INSTALLATION.md](INSTALLATION.md) for detailed instructions.

---

## 🌐 Port Issues

### Port Already in Use

**Windows:**
```powershell
# Find what's using port 3000
Get-NetTCPConnection -LocalPort 3000

# Kill it
Stop-Process -Id <PID> -Force
```

**macOS/Linux:**
```bash
# Find what's using port 3000
lsof -i :3000

# Kill it
kill -9 <PID>
```

**Alternative: Use Different Port**

Edit `.env`:
```env
FRONTEND_PORT=3001
BACKEND_PORT=8001
```

---

## 🐳 Docker Issues

### "Docker daemon is not running"

- **Windows/Mac:** Open Docker Desktop app and wait 2 minutes
- **Linux:** `sudo systemctl start docker`

### "Cannot connect to Docker daemon"

**Linux only:**
```bash
# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Restart Docker
sudo systemctl restart docker
```

---

### Container Exits Immediately

**Check logs:**
```bash
docker-compose -f docker-compose.prod.yml logs backend
docker-compose -f docker-compose.prod.yml logs postgres
```

**Common causes:**
- Database connection failed → Verify `DATABASE_URL` in `.env`
- Port in use → Change port or kill process
- Permissions issue → Check file permissions

---

## 🔐 Login Issues

### "Incorrect username or password" or Can't Login

**Solution 1: Reset Admin Password**

Docker:
```bash
docker-compose -f docker-compose.prod.yml exec backend python manage.py shell -c \
  "from django.contrib.auth import get_user_model; User = get_user_model(); u = User.objects.get(username='admin'); u.set_password('admin'); u.save(); print('✓ Password reset')"
```

Local development:
```bash
cd backend
poetry run python manage.py shell -c \
  "from django.contrib.auth import get_user_model; User = get_user_model(); u = User.objects.get(username='admin'); u.set_password('admin'); u.save(); print('✓ Password reset')"
```

**Solution 2: Create New Admin User**

Docker:
```bash
docker-compose -f docker-compose.prod.yml exec backend python manage.py createsuperuser
```

Local:
```bash
cd backend
poetry run python manage.py createsuperuser
```

**Solution 3: Wait for Services**

- First-time startup can be slow (30-60 seconds)
- Refresh page and try again
- Check backend is running: `docker-compose logs backend`

---

### "Login page doesn't load"

**Check if services are running:**
```bash
# Docker
docker-compose -f docker-compose.prod.yml ps

# Local - check terminal windows for "Starting development server..."
```

**Check backend logs:**
```bash
docker-compose logs -f backend
```

---

## 🗄️ Database Issues

### "Database connection refused"

**Docker:**
```bash
# Check if database is running
docker-compose -f docker-compose.prod.yml ps postgres

# View database logs
docker-compose logs postgres

# Restart database
docker-compose restart postgres
```

**Local:**
```bash
# Check SQLite database exists
ls -la backend/db.sqlite3

# Run migrations fresh
cd backend
poetry run python manage.py migrate
```

---

### "Database connection pooling issues"

Edit `.env`:
```env
DATABASE_CONN_MAX_AGE=600
```

---

## 🎨 Frontend Issues

### "Frontend page won't load or is blank"

**Hard refresh browser:**
- Windows/Linux: `Ctrl+Shift+R`
- Mac: `Cmd+Shift+R`
- Or use incognito/private window

**Check browser console:** Press `F12` → "Console" tab for errors

---

### "CSS/assets are missing (404 errors)"

**Collect static files:**

Docker (automatic, but can force):
```bash
docker-compose -f docker-compose.prod.yml exec backend python manage.py collectstatic --no-input
docker-compose restart backend
```

Local:
```bash
cd backend
poetry run poetry run python manage.py collectstatic --no-input
```

---

### "Frontend won't start in local development"

```bash
cd frontend

# Clear cache and reinstall dependencies
rm -rf node_modules package-lock.json
npm install

# Try again
npm run dev
```

---

## ⚡ Performance Issues

### "Everything is very slow"

**Check available resources:**

Docker is taking too much memory/CPU:
```bash
# See Docker resource usage
docker stats

# Clean up unused Docker resources
docker system prune -a --volumes
```

**Restart services:**
```bash
docker-compose restart
```

**Check disk space:**
```bash
# Windows
Get-Volume

# macOS/Linux
df -h
```

---

### "Migrations stuck or failing"

**Docker:**
```bash
# Nuke database and rebuild (WARNING: deletes all data)
docker-compose down -v
docker-compose up -d --build
```

**Local:**
```bash
cd backend
poetry run python manage.py migrate --fake-initial
```

---

## 📋 Celery / Task Queue Issues

### "Background tasks not running"

**Check Celery worker:**

Docker:
```bash
docker-compose ps celery
docker-compose logs celery
```

Local:
- Is the Celery terminal window still open?
- You should see "ready to accept tasks"

**Check message broker (RabbitMQ in Docker):**
```bash
docker-compose ps rabbitmq
docker-compose logs rabbitmq
```

---

## 🌐 Network & Connectivity

### "Can't reach localhost or 127.0.0.1"

**Try these URLs in order:**
1. http://localhost:3000 (usually works on all platforms)
2. http://127.0.0.1:3000 (Windows alternative)
3. http://192.168.1.X:3000 (from another machine on same network)

**Get your actual IP:**
```bash
# Windows
ipconfig | findstr "IPv4"

# macOS/Linux
ifconfig | grep "inet "
```

**If on Mac M1/M2:**
- `localhost` sometimes doesn't work
- Use `127.0.0.1` instead

---

### "Firewall blocking connection"

**Windows Defender Firewall:**
1. Go to Windows Defender Firewall
2. Click "Allow an app through firewall"
3. Allow Docker Desktop
4. Try again

**Linux firewall:**
```bash
# Allow ports
sudo ufw allow 3000/tcp
sudo ufw allow 8000/tcp
```

---

## 🔧 Advanced Debugging

### Enable Verbose Logging

```bash
cd backend

# Set debug mode
export DEBUG=True
export LOG_LEVEL=DEBUG

# Run with verbose output
poetry run python manage.py runserver --verbosity 3
```

---

### Check Database Connection

**SQLite (local development):**
```bash
sqlite3 backend/db.sqlite3 ".tables"
```

**PostgreSQL (Docker):**
```bash
docker-compose exec postgres psql -U doccano_user -d doccano_db -c "\dt"
```

---

### Check Network Listeners

**Windows:**
```powershell
netstat -ano | findstr "3000 8000 5432"
```

**macOS/Linux:**
```bash
lsof -i | grep "3000\|8000\|5432"
```

---

## ❌ Still Having Issues?

**Checklist:**
1. ✅ Followed [QUICK_START.md](QUICK_START.md)
2. ✅ Installed all prerequisites from [INSTALLATION.md](INSTALLATION.md)
3. ✅ Checked Docker/services are running: `docker-compose ps`
4. ✅ Checked logs: `docker-compose logs -f backend`
5. ✅ Tried a restart: `docker-compose restart`

**Last resort - nuclear restart:**
```bash
# WARNING: This deletes all database data!
docker-compose down -v
docker-compose up -d --build
```

---

## 📞 Getting Help

When reporting an issue, include:

```bash
# System info
python --version
poetry --version
node --version
docker --version
docker-compose --version

# Running services
docker-compose ps
docker-compose logs --tail=100 backend

# Sanitized environment (hide secrets)
cat .env | grep -v "PASSWORD\|SECRET\|KEY"
```

Good luck! 🚀
