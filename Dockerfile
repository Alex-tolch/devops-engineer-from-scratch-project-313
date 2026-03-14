FROM node:20-bookworm-slim AS frontend

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm ci --omit=dev 2>/dev/null || npm install --omit=dev

RUN cp -r ./node_modules/@hexlet/project-devops-deploy-crud-frontend/dist/. /app/public/

FROM ghcr.io/astral-sh/uv:python3.14-trixie-slim

RUN apt-get update && apt-get install -y --no-install-recommends nginx \
    && rm -rf /var/lib/apt/lists/* \
    && rm -f /etc/nginx/sites-enabled/default

WORKDIR /app

COPY app/pyproject.toml app/uv.lock* ./
RUN uv sync --no-dev --no-install-project
ENV PATH="/app/.venv/bin:$PATH"

COPY app/main.py app/models.py app/database.py ./

# Frontend static
COPY --from=frontend /app/public /app/public

# Nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Entrypoint: backend + nginx (strip CRLF so it runs in Linux)
COPY entrypoint.sh /entrypoint.sh
RUN sed -i 's/\r$//' /entrypoint.sh && chmod +x /entrypoint.sh

EXPOSE 80

CMD ["/entrypoint.sh"]
