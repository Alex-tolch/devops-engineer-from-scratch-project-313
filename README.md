### CI status

[![CI](https://github.com/Alex-tolch/devops-engineer-from-scratch-project-313/actions/workflows/ci.yml/badge.svg)](https://github.com/Alex-tolch/devops-engineer-from-scratch-project-313/actions/workflows/ci.yml)

**Live:** [https://devops-engineer-from-scratch-project-313-zxph.onrender.com](https://devops-engineer-from-scratch-project-313-zxph.onrender.com)

## Running the application

Requirements: [uv](https://docs.astral.sh/uv/) (Python project manager).

1. Install dependencies (uv will create a virtual environment and install dependencies):

   ```bash
   uv sync
   ```

2. Run the application:
   ```bash
   make run
   ```

The application will be available at http://localhost:8080. The `GET /ping` route returns the string `pong`.

**Environment variables (optional):**

- `DATABASE_URL` — PostgreSQL connection string (e.g. `postgres://user:pass@host:5432/dbname`). If not set, SQLite is used locally.
- `BASE_URL` — base URL for short links (e.g. `https://short.io`). Used to build `short_url` in API responses.

To verify (with the app running): `curl http://localhost:8080/ping` — expected response: `pong`.

### Links API (CRUD)

- `GET /api/links` — list all links
- `POST /api/links` — create link (body: `{"original_url": "...", "short_name": "..."}`)
- `GET /api/links/<id>` — get link by id
- `PUT /api/links/<id>` — update link
- `DELETE /api/links/<id>` — delete link

## Docker

The image includes Nginx (port 80), the backend (proxied on `/api/`, `/ping`), and the built frontend (static from `/`).

Build the image:

```bash
docker build -t devops-app .
```

Run the container (pass env at runtime; secrets are not stored in the image):

```bash
docker run -p 80:80 \
  -e SENTRY_DSN="<your-sentry-dsn>" \
  -e DATABASE_URL="postgres://..." \
  -e BASE_URL="https://your-domain.com" \
  devops-app
```

- Root (http://localhost:80/) — web UI (static)
- API — http://localhost:80/api/..., http://localhost:80/ping

**Render:** set `PORT=80` in the service environment so the container listens on port 80.

## Development

### Frontend and backend together

Install Node dependencies (`npm install`). Then run both via the **Makefile** with the `FRAMEWORK` parameter, or via npm:

```bash
make run FRAMEWORK=frontend
# or: npm run dev
```

- **make run** — only backend (port 8080)
- **make run FRAMEWORK=frontend** — backend and frontend (concurrently); frontend at http://localhost:5173, backend at http://localhost:8080 (CORS allowed for http://localhost:5173)

### Tests and lint

Run tests: `make test`

Run linter (Ruff): `make lint`

---

### Hexlet tests and linter status:

[![Actions Status](https://github.com/Alex-tolch/devops-engineer-from-scratch-project-313/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/Alex-tolch/devops-engineer-from-scratch-project-313/actions)
