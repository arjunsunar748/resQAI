# RESQ AGENT: Deployment & Operations Manual

## 1. Container Architecture
The platform is containerized using Docker and orchestrated with Docker Compose:

```text
Services:
1. resq-backend: FastAPI application (port 8000)
2. resq-postgis: PostgreSQL 16 + PostGIS 3.4 (port 5432)
3. resq-redis: Redis 7 in-memory cache/broker (port 6379)
4. resq-ollama: Local AI inference runtime (port 11434)
5. resq-frontend: React + Vite web client (port 5173)
```

---

## 2. Quickstart with Docker Compose

1. Clone repository and copy environment file:
   ```bash
   cp .env.example .env
   ```
2. Build and start services:
   ```bash
   docker compose up -d --build
   ```
3. Check service health:
   ```bash
   docker compose ps
   curl http://localhost:8000/health
   curl http://localhost:8000/health/ready
   ```
4. Access web command portal:
   ```text
   http://localhost:5173
   ```

---

## 3. Database Migrations in Container
Run migrations against the running container:
```bash
docker compose exec backend alembic upgrade head
```

---

## 4. Production Hardening Checklist
- [ ] Configure TLS 1.3 termination via reverse proxy (Nginx, Caddy, or Cloudflare).
- [ ] Set `APP_ENV=production` and `DEBUG=false` in `.env`.
- [ ] Generate high-entropy 256-bit secrets for `JWT_SECRET` and `JWT_REFRESH_SECRET`.
- [ ] Restrict `CORS_ORIGINS` strictly to authorized command center domain names.
- [ ] Set up continuous automated database volume backups (`pgdata`).
