<div align="center">
  <img src="https://raw.githubusercontent.com/doccano/doccano/master/docs/images/logo/doccano.png" alt="doccano logo" width="300">
</div>

<div align="center">

# doccano-extended

An extended fork of the [original doccano repository](https://github.com/doccano/doccano), developed as part of a Software Engineering Lab course.

[![GitHub](https://img.shields.io/badge/GitHub-doccano--extended-blue?logo=github)](https://github.com/JustFire17/doccano-extended)
[![GitHub stars](https://img.shields.io/github/stars/JustFire17/doccano-extended?style=social)](https://github.com/JustFire17/doccano-extended/stargazers)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)
[![Django](https://img.shields.io/badge/django-4.2%2B-darkgreen)](https://www.djangoproject.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/35ac8625a2bc4eddbff23dbc61bc6abb)](https://www.codacy.com/gh/doccano/doccano/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=doccano/doccano&amp;utm_campaign=Badge_Grade)
[![doccano CI](https://github.com/doccano/doccano/actions/workflows/ci.yml/badge.svg)](https://github.com/doccano/doccano/actions/workflows/ci.yml)

**A powerful text annotation platform for building high-quality labeled datasets**

[Quick Start](#-quick-start-5-minutes) • [Features](#-lab-developed-features) • [Detailed Features](FEATURES.md) • [Documentation](#-documentation) • [Contributing](#-contributing)

Whether you need training data for sentiment analysis, named entity recognition, text classification, or sequence labeling, doccano provides an intuitive workflow. Create projects, upload data, and start annotating production-ready datasets quickly.

### 👥 Project Team

| Name |
|------|
| André Guerreiro |
| Fábio Godinho |
| Rui Saraiva |
| Sérgio Boico |
| Vasco Evaristo |

### 🔧 Lab Contributions

This extended version adds a practical developer workflow with cross-platform startup scripts, improved setup and troubleshooting guides, and a cleaner project structure for collaboration and publication.

**📖 For detailed technical documentation of all custom features, see [FEATURES.md](FEATURES.md)**

### 🎯 Lab-Developed Features

| Area | Included capabilities |
|------|------------------------|
| User and Group Management | User lifecycle operations, profile settings, role-based permissions, and group administration |
| Annotation Perspectives | Multiple views, personalized perspectives, filtered annotation navigation, and perspective metadata tracking |
| Annotation Governance | Rule authoring, collaborative discussion threads, voting workflows, and final rule lifecycle control |
| Analytics and Quality Control | Discrepancy detection, comparison workflows, annotator statistics, filterable history, and quality pattern analysis |

---

## 🚀 Tech Stack

| Layer | Stack |
|------|-------|
| Backend | Django 4.2+ (tested on 4.2.15), Django REST Framework, Celery |
| Frontend | Nuxt.js 2 (v2.18), Vue 2 (v2.6), TypeScript |
| Database | SQLite (local development), PostgreSQL (Docker/production) |
| Message Broker | SQLAlchemy + SQLite (local development), RabbitMQ/Redis (Docker/production) |
| Deployment | Docker, Docker Compose, AWS, Heroku |
| Python | 3.10+ |

## ⚡ Quick Start (5 Minutes)

### Prerequisites

| Platform | Requirements |
|----------|--------------|
| Windows | PowerShell 5.1+, Python 3.10+, Node.js 18+, Poetry, Git |
| macOS/Linux | Bash, Python 3.10+, Node.js 18+, Poetry, Git |

For full setup details, see [INSTALLATION.md](INSTALLATION.md).

### 1️⃣ Clone & Navigate
```bash
git clone https://github.com/JustFire17/doccano-extended.git
cd doccano-extended
```

### 2️⃣ Start Services

**Windows:**
```powershell
.\executarDoccanoDevEnv.ps1        # Local development (recommended)
# OR
.\executarDoccanoDocker.ps1        # Docker production setup
```

**Mac / Linux:**
```bash
chmod +x executarDoccanoDevEnv.sh
./executarDoccanoDevEnv.sh         # Local development
```

> **⏱️ First run takes ~5 minutes** (installing dependencies). Subsequent runs are ~30 seconds.

### 3️⃣ Access Application

| Service | URL | Credentials |
|---------|-----|-------------|
| Frontend | http://localhost:3000 (or local network URL shown by Nuxt, e.g. http://192.168.56.1:3000) | admin / admin |
| Backend Health | http://127.0.0.1:8000/v1/health/ | — |
| Admin Panel | http://localhost:8000/admin/ | admin / admin |
| Swagger | http://127.0.0.1:8000/swagger/ | — |
| API Schema | http://127.0.0.1:8000/api/schema.json | — |

### 4️⃣ Quick Sanity Check

```powershell
.\quickSanityCheck.ps1
```

Expected result: `PASS (healthy environment)`.

> **⚠️ Prerequisites Required:** Ensure Python 3.10+, Node.js 18+, and Poetry are installed. See [INSTALLATION.md](INSTALLATION.md) for setup instructions.

👉 **For detailed setup, see [QUICK_START.md](QUICK_START.md)**

---

## 🧩 Script Reference

| Script | Platform | Purpose |
|--------|----------|---------|
| `executarDoccanoDevEnv.ps1` | Windows | Starts local development services (backend, celery, frontend) |
| `executarDoccanoDevEnv.sh` | macOS/Linux | Starts local development services (backend, celery, frontend) |
| `cleanupDevEnv.ps1` | Windows | Removes database & build artifacts for a fresh start |
| `cleanupDevEnv.sh` | macOS/Linux | Removes database & build artifacts for a fresh start |
| `executarDoccanoDocker.ps1` | Windows | Starts Docker-based environment |
| `executarDoccanoDocker.sh` | macOS/Linux | Starts Docker-based environment |
| `quickSanityCheck.ps1` | Windows | Runs a quick health check with PASS/FAIL output |

## ✅ Verification

Use the commands below to provide visible, reproducible validation in local development:

```powershell
.\executarDoccanoDevEnv.ps1
.\quickSanityCheck.ps1
```

Expected sanity result:

```text
Result: PASS (healthy environment)
```

Expected endpoint status checks:

- `http://127.0.0.1:8000/v1/health/` → `200`
- `http://127.0.0.1:8000/swagger/` → `200`
- `http://127.0.0.1:8000/api/schema.json` → `200`

Note: `http://127.0.0.1:8000/v1/` is not a valid API root endpoint in this setup.

## 📚 Documentation

### Getting Started
| Document | Purpose |
|----------|---------|
| [QUICK_START.md](QUICK_START.md) | 🚀 **Start here** - 2-minute setup guide |
| [INSTALLATION.md](INSTALLATION.md) | 🔧 Prerequisites and detailed installation |
| [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | 🐛 Solutions for common issues |
| [FEATURES.md](FEATURES.md) | 📖 Detailed technical documentation of custom features |

### Additional Resources

| Resource | Link |
|----------|------|
| Official Documentation | [doccano docs](https://doccano.github.io/doccano/) |
| Docker Setup Guide | [docker/](docker/) |
| Developer Guide | [docs/developer_guide.md](docs/developer_guide.md) |
| Contributing Guide | [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) |
| Code of Conduct | [docs/CODE_OF_CONDUCT.md](docs/CODE_OF_CONDUCT.md) |

## ✨ Features

### Core Capabilities
Collaborative annotation supports real-time team workflows with role-based access control, task types such as text classification and sequence labeling, multilingual data, API-based integrations, and multiple export formats.

### User Experience
The interface includes theme support, responsive layouts for tablets and phones, keyboard shortcuts, and rich text handling.

### Platform Features
The platform extends user management, progress tracking, flexible label taxonomy, and annotation version history.

## Installation Methods

There are three options to run doccano:

| Method | Best For | Complexity |
|--------|----------|-----------|
| **pip** | Single user, quick testing | Simple ⭐ |
| **Docker** | Isolated environment | Medium ⭐⭐ |
| **Docker Compose** | Production, full stack | Medium ⭐⭐ |

### 1️⃣ pip Installation

To install doccano, run:

```bash
pip install doccano
```

By default, SQLite 3 is used for the default database. If you want to use PostgreSQL, install the additional dependencies:

```bash
pip install 'doccano[postgresql]'
```

and set the `DATABASE_URL` environment variable according to your PostgreSQL credentials:

```bash
DATABASE_URL="postgres://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}?sslmode=disable"
```

After installation, run the following commands:

```bash
# Initialize database.
doccano init
# Create a super user.
doccano createuser --username admin --password pass
# Start a web server.
doccano webserver --port 8000
```

In another terminal, run the command:

```bash
# Start the task queue to handle file upload/download.
doccano task
```

Go to <http://127.0.0.1:8000/>.

### 2️⃣ Docker

**Create & run a Docker container:**

```bash
# Pull the latest image
docker pull doccano/doccano

# Create container
docker container create --name doccano \
  -e "ADMIN_USERNAME=admin" \
  -e "ADMIN_EMAIL=admin@example.com" \
  -e "ADMIN_PASSWORD=password" \
  -v doccano-db:/data \
  -p 8000:8000 doccano/doccano

# Start the container
docker container start doccano
```

Access at **http://127.0.0.1:8000/**

**Stop & Cleanup:**
```bash
docker container stop doccano -t 5
docker container rm doccano
```

**For latest features:**
```bash
docker pull doccano/doccano:nightly
```

### 3️⃣ Docker Compose (Recommended)

**Clone and setup environment:**

```bash
# Clone the repository
git clone https://github.com/JustFire17/doccano-extended.git
cd doccano-extended

# Windows-specific (correct line endings)
git clone https://github.com/JustFire17/doccano-extended.git --config core.autocrlf=input
```

**Create `.env` file:**

```bash
cat > .env << EOF
# Platform Settings
ADMIN_USERNAME=admin
ADMIN_PASSWORD=password
ADMIN_EMAIL=admin@example.com

# RabbitMQ Settings
RABBITMQ_DEFAULT_USER=doccano
RABBITMQ_DEFAULT_PASS=doccano

# Database Settings
POSTGRES_USER=doccano
POSTGRES_PASSWORD=doccano
POSTGRES_DB=doccano
EOF
```

**Start services:**

```bash
docker-compose -f docker/docker-compose.prod.yml --env-file .env up -d
```

Access at **http://127.0.0.1/**

**Available Services:**
- Frontend: http://127.0.0.1
- API: http://127.0.0.1/api
- Admin: http://127.0.0.1/admin

---

## 🚀 Deployment Options

| Service | Status |
|---------|--------|
| AWS CloudFormation | [![CloudFormation Button](https://cdn.rawgit.com/buildkite/cloudformation-launch-stack-button-svg/master/launch-stack.svg)](https://console.aws.amazon.com/cloudformation/home?#/stacks/new?stackName=doccano&templateURL=https://doccano.s3.amazonaws.com/public/cloudformation/template.aws.yaml) |
| Heroku | [![Heroku Button](https://www.herokucdn.com/deploy/button.svg)](https://dashboard.heroku.com/new?template=https%3A%2F%2Fgithub.com%2Fdoccano%2Fdoccano) |

**AWS Notes:**
- EC2 KeyPair must be pre-created in your region ([How to create](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-key-pairs.html#having-ec2-create-your-key-pair))
- For HTTPS setup: See [AWS HTTPS Configuration](https://github.com/doccano/doccano/wiki/HTTPS-setting-for-doccano-in-AWS)

---

## ❓ FAQ & Support

**Common Questions:**
- [How to create a user](https://doccano.github.io/doccano/faq/#how-to-create-a-user)
- [How to add users to projects](https://doccano.github.io/doccano/faq/#how-to-add-a-user-to-your-project)
- [How to change password](https://doccano.github.io/doccano/faq/#how-to-change-the-password)
- More: [Full FAQ](https://doccano.github.io/doccano/)

**Getting Help:**
1. 📖 Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for known issues
2. 🔍 Search [existing issues](https://github.com/doccano/doccano/issues)
3. ❌ Report new issues with [bug template](.github/ISSUE_TEMPLATE/bug_report.md)
4. 💡 Request features with [feature template](.github/ISSUE_TEMPLATE/feature_request.md)

---

## 🤝 Contributing

We welcome contributions! Whether it's:
- 🐛 **Bug fixes** - Report and fix issues
- ✨ **New features** - Enhance platform capabilities
- 📚 **Documentation** - Improve guides and examples
- 🌍 **Translations** - Support new languages

**Quick Start:**
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit changes: `git commit -am 'Add new feature'`
4. Push to branch: `git push origin feature/my-feature`
5. Submit a Pull Request

See [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) for detailed guidelines.

**Resources:**
- [Developer Guide](docs/developer_guide.md)
- [Code of Conduct](docs/CODE_OF_CONDUCT.md)
- [How to Contribute to Doccano](https://github.com/doccano/doccano/wiki/How-to-Contribute-to-Doccano-Project)

---

## 📄 Citation

If you use doccano in your research, please cite it:

```bibtex
@misc{doccano,
  title={{doccano}: Text Annotation Tool for Human},
  url={https://github.com/doccano/doccano},
  note={Software available from https://github.com/doccano/doccano},
  author={
    Hiroki Nakayama and
    Takahiro Kubo and
    Junya Kamura and
    Yasufumi Taniguchi and
    Xu Liang
  },
  year={2018},
}
```

---

## 📞 Contact & Community

**Get Help & Connect:**
- 💬 [GitHub Discussions](https://github.com/doccano/doccano/discussions) - Ask questions and share ideas
- 🐛 [GitHub Issues](https://github.com/doccano/doccano/issues) - Report bugs and request features
- 👤 [Original Author](https://github.com/Hironsan) - Contact Hironsan for original doccano project
- 📧 **Project Team** - Contact the Software Engineering Lab team via this repository

---

## 📜 License

This project is licensed under the **MIT License** - see [LICENSE](LICENSE) file for details.

The original doccano project is also MIT licensed. This fork extends the original work for educational purposes.

---

## 🗺️ Roadmap

See [ROADMAP.md](docs/roadmap.md) for planned features and improvements.

**Current Focus:**
- ✅ Simplified deployment scripts (Windows/Mac/Linux)
- ✅ Enhanced documentation
- 🔄 Performance optimizations
- 🔄 Additional export formats
- 🔄 Advanced ML integration

---

## 📊 Project Status

| Component | Status | Version |
|-----------|--------|---------|
| Backend | ✅ Stable | Django 4.2+ |
| Frontend | ✅ Stable | Nuxt 2, Vue 2 |
| Docker | ✅ Production Ready | Compose v2 |
| Scripts | ✅ Working | Win/Mac/Linux |

---

## 🔗 Related Resources

- **Original Project**: [doccano/doccano](https://github.com/doccano/doccano)
- **Official Docs**: [doccano.github.io](https://doccano.github.io/doccano/)
- **Example Projects**: [doccano Wiki](https://github.com/doccano/doccano/wiki)
- **Course**: Software Engineering Laboratory

---

<div align="center">

**Made with ❤️ by the Software Engineering Lab Team**

[⬆ Back to top](#doccano-extended)

</div>
