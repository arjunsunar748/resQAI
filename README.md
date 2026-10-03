# RESQ AGENT

> **AI-Powered Disaster Response & Coordination Platform**  
> Government-ready, multi-organization disaster operations platform engineered for municipal, provincial, and national emergency authorities.

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11%2B-blue)](backend/)
[![React](https://img.shields.io/badge/React-18.3-cyan)](frontend/)
[![PostgreSQL](https://img.shields.io/badge/PostGIS-16-blue)](infrastructure/)

---

## Core Mission & Architectural Principles

1. **Human-in-the-Loop Emergency Governance**: AI never autonomously dispatches emergency teams. It analyzes incoming reports, evaluates spatial proximity, calculates risk, and provides structured response recommendations for authorized human officers to approve or override.
2. **Deterministic Auditability**: Every state-changing operational decision is cryptographically signed using HMAC-SHA256 checksums to guarantee forensic non-repudiation.
3. **Multi-Organization & Administrative Scoping**: Calibrated for Nepal's constitutional federal structure (Federal $\to$ Provincial $\to$ District $\to$ Municipality $\to$ Ward) and adaptable to any jurisdictional hierarchy.
4. **Resilience & Offline Autonomy**: The platform remains fully functional for manual triage and dispatch even if AI inference or external internet connectivity is disrupted.
5. **Zero Hallucination / Zero Fake Data**: Production schemas clearly isolate live data from simulated development drills. No fake government metrics are hard-coded.

---

## Monorepo Structure

```text
resq-agent/
├── frontend/             # React + Vite accessible operational dashboard shell
├── backend/              # Python FastAPI service layer with SQLAlchemy & Alembic
├── infrastructure/       # Container manifests, Dockerfiles, and database configurations
├── docs/                 # System architecture, security, API, and deployment documentation
├── scripts/              # Development automation and setup utilities
├── tests/                # Monorepo-level smoke and integration tests
├── .github/              # GitHub Actions CI/CD workflows
├── .env.example          # Environment variables template
├── docker-compose.yml    # Development multi-container orchestration
├── README.md             # Project documentation
└── LICENSE               # Apache 2.0 License
```

---

## Quickstart

### Option 1: Docker Compose (Recommended)
```bash
cp .env.example .env
docker compose up -d --build
```
Access the application:
- **Frontend Dashboard**: [http://localhost:5173](http://localhost:5173)
- **Backend API Docs**: [http://localhost:8000/api/v1/docs](http://localhost:8000/api/v1/docs)
- **Health Probe**: [http://localhost:8000/health](http://localhost:8000/health)

### Option 2: Local Development
See [`docs/development.md`](docs/development.md) for detailed step-by-step instructions.

---

## Verification & Automated Testing

### Backend Unit & Integration Tests:
```bash
cd backend
pytest -v
```

### Frontend Production Build:
```bash
cd frontend
npm run build
```

---

## Documentation
- [System Architecture](docs/architecture.md)
- [Security & RBAC](docs/security.md)
- [API Reference](docs/api.md)
- [Deployment Guide](docs/deployment.md)
- [Local Development](docs/development.md)

---

## License
Licensed under the [Apache 2.0 License](LICENSE).
