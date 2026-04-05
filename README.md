<div align="center">
  <img src="https://raw.githubusercontent.com/doccano/doccano/master/docs/images/logo/doccano.png" alt="doccano logo" width="300">
</div>

# doccano-extended

An extended fork of the original doccano repository, developed for a Software Engineering Lab project.
This version focuses on practical product enhancements for annotation governance, perspective workflows, and team operations.

Project completion: March 2025.

[![Codacy Badge](https://app.codacy.com/project/badge/Grade/35ac8625a2bc4eddbff23dbc61bc6abb)](https://www.codacy.com/gh/JustFire17/doccano-extended/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=JustFire17/doccano-extended&amp;utm_campaign=Badge_Grade)

## What This Extension Adds

This repository keeps core doccano capabilities and extends them with a stronger workflow for collaborative annotation projects.

## Implemented Extras

| Area | Extra capabilities added in this extension |
|------|--------------------------------------------|
| User and Group Management | Extended user lifecycle operations, profile settings, role-based permissions, and group administration |
| Annotation Perspectives | Perspective association, filtered perspective navigation, and perspective metadata handling |
| Annotation Governance | Rule authoring, discussion workflows, voting mechanisms, and rule lifecycle controls |
| Analytics and Quality Control | Discrepancy analysis, comparison workflows, annotator statistics, and quality-oriented report views |

## Project Team

| Name |
|------|
| Andre Guerreiro |
| Fabio Godinho |
| Rui Saraiva |
| Sergio Boico |
| Vasco Evaristo |

## Tech Stack

| Layer | Stack |
|------|-------|
| Backend | Django, Django REST Framework, Celery |
| Frontend | Nuxt 2, Vue 2, TypeScript |
| Database | SQLite (dev), PostgreSQL (Docker) |
| Messaging | RabbitMQ and Redis (Docker) |
| Deployment | Docker and Docker Compose |

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- Docker Desktop (for Docker mode)
- Git

### 1. Clone

```bash
git clone https://github.com/JustFire17/doccano-extended.git
cd doccano-extended
```

### 2. Start the platform

Windows (PowerShell):

```powershell
.\executarDoccanoDocker.ps1
```

Mac/Linux:

```bash
chmod +x executarDoccanoDocker.sh
./executarDoccanoDocker.sh
```

For local development mode:

```powershell
.\executarDoccanoDevEnv.ps1
```

```bash
chmod +x executarDoccanoDevEnv.sh
./executarDoccanoDevEnv.sh
```

### 3. Validate quickly

After startup, validate with simple HTTP checks.

Windows (PowerShell):

```powershell
(Invoke-WebRequest http://localhost -UseBasicParsing).StatusCode
(Invoke-WebRequest http://localhost/v1/health/ -UseBasicParsing).StatusCode
```

Expected: both return 200.

## Available Services

- App: http://localhost
- API health: http://localhost/v1/health/
- Flower: http://localhost:5555

## Script Reference

| Script | Platform | Purpose |
|--------|----------|---------|
| executarDoccanoDevEnv.ps1 | Windows | Start local development services |
| executarDoccanoDevEnv.sh | macOS/Linux | Start local development services |
| executarDoccanoDocker.ps1 | Windows | Start Docker environment |
| executarDoccanoDocker.sh | macOS/Linux | Start Docker environment |

## FAQ

- Original doccano documentation: https://doccano.github.io/doccano/
- Original project: https://github.com/doccano/doccano

## License

This project is licensed under the MIT License. See LICENSE for details.

The original doccano project is also MIT licensed.
