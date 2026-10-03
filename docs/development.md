# RESQ AGENT: Development Guide

## 1. Prerequisites
- **Python**: 3.11+ (Tested on Python 3.13)
- **Node.js**: v18+ (Tested on Node v22.14)
- **PostgreSQL**: 15+ with PostGIS extension (or Docker container)
- **Redis**: 7+ (or Docker container)
- **Docker**: Docker 24+ and Docker Compose v2+

---

## 2. Local Setup Steps

### Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a Python virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On Linux/macOS:
   source venv/bin/activate
   ```
3. Install required dependencies:
   ```bash
   pip install -r requirements/dev.txt
   ```
4. Copy the environment configuration template:
   ```bash
   cp ../.env.example .env
   # Adjust credentials to match your local database
   ```
5. Apply database migrations:
   ```bash
   alembic upgrade head
   ```
6. (Optional for development) Seed base administrative structure:
   ```bash
   python -m app.db.seed
   ```
7. Start the development API server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

### Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install npm packages:
   ```bash
   npm install
   ```
3. Run the development server:
   ```bash
   npm run dev
   ```
   Open `http://localhost:5173` in your browser.

---

## 3. Running Automated Tests

### Backend Unit & Integration Tests:
```bash
cd backend
pytest -v
```

### Frontend Production Build Verification:
```bash
cd frontend
npm run build
```

---

## 4. Coding Standards & Conventions
- **Zero Secrets in Code**: Never commit passwords, tokens, API keys, or `.env` files.
- **Strict Typing**: Use Pydantic v2 schemas and Python type hints throughout.
- **Fail-Closed Security**: All new endpoints require explicit authentication and RBAC dependency checks unless intentionally declared public.
- **Audit Logging**: Any state-mutating operation (create, update, delete, verify) must record an HMAC-signed audit log via `audit_service`.
