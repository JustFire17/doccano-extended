# Doccano Extended - Advanced Annotation Platform

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-4.2-green.svg)](https://www.djangoproject.com/)
[![Vue.js](https://img.shields.io/badge/Vue.js-2.6-brightgreen.svg)](https://vuejs.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> 🎓 **Academic Project** - Extended version of [doccano](https://github.com/doccano/doccano) with advanced features for collaborative annotation and quality assurance.

This is an enhanced fork of the original Doccano annotation tool, developed as part of a university project. We've added powerful features for improving annotation quality, team collaboration, and project management.

---

## 🆕 What's New? Our Custom Features

### 🔄 **1. Project Versioning System**
Create multiple versions of your annotation projects while maintaining data integrity.

- **Version Control**: Track changes across different project iterations
- **Version History**: Access and compare previous versions
- **Smart Cloning**: Duplicate projects with all configurations preserved
- **Rollback Support**: Reopen closed projects with new versions

**Use Case**: Perfect for iterative annotation workflows where guidelines evolve over time.

### 📊 **2. Inter-Annotator Agreement Analysis**
Advanced discrepancy detection to ensure annotation quality.

- **Automatic Discrepancy Detection**: Identifies disagreements between annotators
- **Configurable Thresholds**: Set custom percentage thresholds per project
- **Manual Discrepancy Management**: Create and track specific disagreement cases
- **Label-Level Statistics**: Detailed breakdown of discrepancies by label type
- **Comment System**: Discuss and resolve discrepancies within the platform

**Use Case**: Essential for maintaining high-quality datasets and identifying ambiguous cases.

### 👥 **3. Multi-Perspective Annotation**
Support for multiple annotation perspectives within the same project.

- **Perspective Projects**: Group related projects under different viewpoints
- **Flexible Member Assignment**: Assign annotators to specific perspectives
- **Cross-Perspective Analysis**: Compare annotations across different perspectives
- **Perspective Inheritance**: Version control maintains perspective associations

**Use Case**: Ideal for subjective tasks where different viewpoints are valuable (e.g., sentiment analysis, bias detection).

### 🗳️ **4. Collaborative Rule System**
Democratic approach to establishing annotation guidelines.

- **Rule Proposals**: Team members can propose annotation rules
- **Voting Mechanism**: Democratic voting on proposed rules
- **Rule Versioning**: Rules are version-specific and inherit across versions
- **Status Tracking**: Monitor rule approval status

**Use Case**: Foster team consensus on difficult annotation cases.

### 💬 **5. Enhanced Discussion System**
Integrated communication for annotation teams.

- **Project-Level Discussions**: Contextual conversations per project version
- **Discrepancy Comments**: Thread discussions on specific disagreements
- **Real-Time Updates**: Stay informed about team communications

**Use Case**: Reduce external communication overhead and keep discussions contextual.

### 🎫 **6. User Groups Management System**
Flexible access control and team organization.

- **Custom Groups**: Create meaningful user groups (e.g., "Senior Annotators", "QA Team")
- **Permission Management**: Assign specific permissions to each group
- **User Association**: Easy user-to-group assignment
- **Role-Based Access**: Control who can access projects, annotate, review, or approve

**Use Case**: Scale team management efficiently - assign permissions to groups instead of individual users.

---

## ⚡ Quick Start

### Prerequisites
- Python 3.8+
- Node.js 14+
- Poetry (Python package manager)
- npm or Yarn

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/YOUR_USERNAME/doccano-extended.git
cd doccano-extended
```

2. **Backend Setup**
```bash
cd backend
poetry install
poetry run python manage.py migrate
poetry run python manage.py create_roles
poetry run python manage.py create_admin --noinput --username "admin" --email "admin@example.com" --password "password"
```

3. **Frontend Setup**
```bash
cd frontend
npm install
```

4. **Run the Application**

Terminal 1 - Backend:
```bash
cd backend
poetry run python manage.py runserver
```

Terminal 2 - Celery Worker:
```bash
cd backend
poetry run celery --app=config worker --loglevel=INFO --concurrency=1
```

Terminal 3 - Frontend:
```bash
cd frontend
npm run dev
```

5. **Access the Application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Default credentials: `admin` / `password`

📖 For detailed installation instructions, see [INSTALLATION.md](INSTALLATION.md)

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (Nuxt.js)                    │
│              Vue 2 + Vuetify + TypeScript                │
└────────────────────┬────────────────────────────────────┘
                     │ REST API
┌────────────────────┴────────────────────────────────────┐
│                 Backend (Django)                         │
│       Django REST Framework + Celery + Channels         │
├──────────────────────────────────────────────────────────┤
│  📦 Core Models Extended:                                │
│  • Project (with versioning)                             │
│  • ManualDiscrepancy                                     │
│  • PerspectiveProject & Perspective                      │
│  • Rule & RuleVote                                       │
│  • DiscrepancyComment & Discussion                       │
│  • Group (custom user groups)                            │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────┴────────────────────────────────────┐
│              Database (PostgreSQL/SQLite)                │
└──────────────────────────────────────────────────────────┘
```

---

## 📸 Screenshots

### Discrepancy Analysis Dashboard
*Show inter-annotator agreement metrics and identify problematic cases*

### Project Versioning
*Manage multiple versions of annotation projects*

### Perspective Management
*Organize annotation teams by different viewpoints*

---

## 🎯 Use Cases

### Academic Research
- Maintain version history for reproducibility
- Track inter-annotator reliability
- Support multiple annotation paradigms

### Commercial NLP Projects
- Quality assurance through discrepancy analysis
- Team collaboration with perspectives
- Iterative guideline refinement

### Multi-Annotator Workflows
- Democratic rule establishment
- Systematic disagreement resolution
- Perspective-based task assignment

---

## 🛠️ Technology Stack

**Backend:**
- Django 4.2.15
- Django REST Framework
- Celery (async tasks)
- Channels (WebSocket support)
- PostgreSQL / SQLite

**Frontend:**
- Nuxt.js 2.18
- Vue.js 2.6
- Vuetify 2.x
- TypeScript
- Axios

**Infrastructure:**
- Docker & Docker Compose support
- Redis (caching & message broker)
- RabbitMQ (task queue)
- Nginx (production)

---

## 📚 Documentation

- [Installation Guide](INSTALLATION.md) - Detailed setup instructions
- [Features Documentation](FEATURES.md) - In-depth feature explanations
- [API Documentation](http://localhost:8000/swagger/) - Interactive API docs
- [Original Doccano Docs](https://doccano.github.io/doccano/) - Base functionality

---

## 🤝 Team & Contributions

This project was developed by:
- **[Your Name]** - Backend Development, Versioning System
- **[Colleague 1]** - Discrepancy Analysis, Frontend
- **[Colleague 2]** - Perspective Management, UI/UX
- **[Colleague 3]** - Rule System, Testing

Based on the excellent work by the [Doccano team](https://github.com/doccano/doccano).

---

## 📊 Key Differences from Original Doccano

| Feature | Original Doccano | Our Extension |
|---------|------------------|---------------|
| Project Versioning | ❌ | ✅ Full version control |
| Discrepancy Analysis | ❌ | ✅ Automatic + Manual |
| Multiple Perspectives | ❌ | ✅ Complete system |
| Rule Voting | ❌ | ✅ Democratic governance |
| Discussion Threads | ❌ | ✅ Integrated chat |
| User Groups Management | ❌ | ✅ Custom groups & permissions |
| Version-Aware Comments | ❌ | ✅ Context-preserved |

---

## 🔒 Security Notes

⚠️ **Before deploying to production:**
1. Change default admin password
2. Set strong `SECRET_KEY` in environment variables
3. Configure `ALLOWED_HOSTS` properly
4. Enable HTTPS
5. Review CORS settings
6. Set `DEBUG=False`

See [SECURITY.md](SECURITY.md) for detailed security guidelines.

---

## 📝 License

This project maintains the MIT License from the original Doccano project.

```
MIT License - see LICENSE file for details
```

---

## 🙏 Acknowledgments

- Original [Doccano Project](https://github.com/doccano/doccano) by Hiroki Nakayama and team
- Our university supervisors and mentors
- The open-source community

---

## 📬 Contact

For questions or feedback about our extensions:
- Create an issue on GitHub
- Email: [your-email@example.com]

For questions about the original Doccano:
- Visit: https://doccano.github.io/doccano/
- Original repo: https://github.com/doccano/doccano

---

## ⭐ Star History

If you find this project useful, please consider giving it a star!

---

**Made with ❤️ for the annotation community**
