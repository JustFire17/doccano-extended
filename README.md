<div align="center">
  <img src="https://raw.githubusercontent.com/doccano/doccano/master/docs/images/logo/doccano.png" alt="doccano logo" width="300">
</div>

<div align="center">

# doccano-extended

An extended fork of the [original doccano repository](https://github.com/doccano/doccano), developed as part of the **Laboratório de Engenharia de Software** (Software Engineering Lab) course.

[![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)
[![Django](https://img.shields.io/badge/django-4.0%2B-darkgreen)](https://www.djangoproject.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/35ac8625a2bc4eddbff23dbc61bc6abb)](https://www.codacy.com/gh/doccano/doccano/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=doccano/doccano&amp;utm_campaign=Badge_Grade)
[![doccano CI](https://github.com/doccano/doccano/actions/workflows/ci.yml/badge.svg)](https://github.com/doccano/doccano/actions/workflows/ci.yml)

**A powerful text annotation platform for building high-quality labeled datasets**

[Quick Start](#-quick-start-5-minutes) • [Features](#features) • [Documentation](#documentation) • [Contributing](#contribution) • [Lab Contributions](#-lab-developed-features) Whether you need to build training data for sentiment analysis, named entity recognition, text classification, or sequence labeling tasks, doccano provides an intuitive interface to streamline the annotation workflow. Create projects, upload data, and start annotating—build production-ready datasets in hours, not weeks.

### 👥 Project Team

| Name | Role |
|------|------|
| André Guerreiro | Developer |
| Fábio Godinho | Developer |
| Rui Saraiva | Developer |
| Sérgio Boico | Developer |
| Vasco Evaristo | Developer |

### 🔧 Lab Contributions

This extended version includes improvements by the Software Engineering Lab team:

- **Automated Setup Scripts**: Cross-platform PowerShell & Bash scripts for rapid deployment
  - `executarDoccanoDevEnv.ps1/sh` - Local development environment
  - `executarDoccanoDocker.ps1/sh` - Production Docker setup
- **Enhanced Documentation**: Comprehensive guides for Windows, Mac, and Linux
- **Simplified Deployment**: One-command setup on any OS with Docker
- **GitHub-ready Project**: Professional .gitignore, README, and contribution guidelines

### 🎯 Lab-Developed Features

**User & Group Management**
- User lifecycle management (create, update, view, delete)
- User profile management with customizable settings
- Role-based access control with granular permissions
- Group/Profile creation and administration

**Annotation Perspectives & Views**
- Multiple annotation perspectives for flexible data visualizations
- Personal perspective definitions for individual annotators
- View annotations based on different filtering criteria
- Track annotation metadata across perspectives

**Annotation Governance**
- Define and manage annotation rules collaboratively
- Discussion system for rule refinement and consensus
- Rule voting mechanism for team consensus
- Final rule configuration and deployment

**Analytics & Quality Control**
- Annotation discrepancy detection and visualization
- Comparative analysis of annotations across datasets
- Annotator performance statistics and reports
- Annotation history tracking with multiple filters
- Pattern analysis for data quality insights

---

## 🚀 Tech Stack

- **Backend**: Django 4.0+, Django REST Framework, Celery
- **Frontend**: Nuxt.js, Vue 3, TypeScript
- **Database**: PostgreSQL, SQLite (optional)
- **Message Broker**: RabbitMQ
- **Cache**: Redis
- **Deployment**: Docker, Docker Compose, AWS, Heroku
- **Python**: 3.8+

## ⚡ Quick Start (5 Minutes)

### Prerequisites
- **Windows**: PowerShell 5.1+, Docker Desktop, Git
- **Mac/Linux**: Bash, Docker, Docker Compose, Git
- See [INSTALLATION.md](INSTALLATION.md) for detailed setup

### 1️⃣ Clone & Navigate
```bash
git clone https://github.com/doccano/doccano.git
cd doccano
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

### 3️⃣ Access Application

| Service | URL | Credentials |
|---------|-----|-------------|
| Frontend | http://localhost:3000 | admin / admin |
| Backend API | http://localhost:8000/api/ | — |
| Admin Panel | http://localhost:8000/admin/ | admin / admin |

**Note:** PowerShell scripts are minimal wrappers—ensure prerequisites from [INSTALLATION.md](INSTALLATION.md) are installed.

👉 **For detailed setup, see [QUICK_START.md](QUICK_START.md)**

---

## Demo

Try the [annotation demo](http://doccano.herokuapp.com).

![Demo image](https://raw.githubusercontent.com/doccano/doccano/master/docs/images/demo/demo.gif)

## 📚 Documentation

### Getting Started
| Document | Purpose |
|----------|---------|
| [QUICK_START.md](QUICK_START.md) | 🚀 **Start here** - 2-minute setup guide |
| [INSTALLATION.md](INSTALLATION.md) | 🔧 Prerequisites and detailed installation |
| [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | 🐛 Solutions for common issues |

### Additional Resources
- 📖 [Official Documentation](https://doccano.github.io/doccano/)
- 🐳 [Docker Setup Guide](docker/)
- 👨‍💻 [Developer Guide](docs/developer_guide.md)
- 🤝 [Contributing Guide](CONTRIBUTING.md)
- 📋 [Code of Conduct](CODE_OF_CONDUCT.md)

## ✨ Features

### Core Capabilities
- ✅ **Collaborative Annotation** - Real-time multi-user collaboration with role-based access control
- ✅ **Multiple Task Types** - Text classification, sequence labeling, sequence-to-sequence
- ✅ **Multi-language Support** - Annotate content in any language
- ✅ **REST API** - Programmatic access to all platform features
- ✅ **Export Formats** - JSON, JSONL, CSV, and more

### User Experience
- 🎨 **Dark Theme** - Eye-friendly interface with light/dark mode toggle
- 📱 **Mobile Support** - Responsive design works on tablets and phones
- ⌚ **Keyboard Shortcuts** - Speed up annotation with custom hotkeys
- 😊 **Rich Text Support** - Emoji and special character support

### Platform Features
- 🔐 **User Management** - Team collaboration with granular permissions
- 📊 **Progress Tracking** - Real-time annotation statistics and insights
- 🏷️ **Label Management** - Flexible labeling schemes and taxonomy
- 🔄 **Version Control** - Track annotation history and revisions

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
git clone https://github.com/doccano/doccano.git
cd doccano

# Windows-specific (correct line endings)
git clone https://github.com/doccano/doccano.git --config core.autocrlf=input
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

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

**Resources:**
- [Developer Guide](docs/developer_guide.md)
- [Code of Conduct](CODE_OF_CONDUCT.md)
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
| Backend | ✅ Stable | Django 4.0+ |
| Frontend | ✅ Stable | Nuxt 3, Vue 3 |
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
