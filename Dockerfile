FROM node:20-bookworm-slim AS frontend

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm ci --omit=dev 2>/dev/null || npm install --omit=dev

RUN cp -r ./node_modules/@hexlet/project-devops-deploy-crud-frontend/dist/. /app/public/

# Backend: Python deps
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

WORKDIR /app

COPY pyproject.toml uv.lock* ./
RUN uv sync --no-dev --no-install-project

# Runtime stage
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

RUN apt-get update && apt-get install -y --no-install-recommends nginx \
    && rm -rf /var/lib/apt/lists/* \
    && rm -f /etc/nginx/sites-enabled/default

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"
COPY main.py models.py database.py ./

# Frontend static
COPY --from=frontend /app/public /app/public

# Nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Entrypoint: backend + nginx (strip CRLF so it runs in Linux)
COPY entrypoint.sh /entrypoint.sh
RUN sed -i 's/\r$//' /entrypoint.sh && chmod +x /entrypoint.sh

EXPOSE 80

CMD ["/entrypoint.sh"]
