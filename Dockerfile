# Build stage: install dependencies
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

WORKDIR /app

COPY pyproject.toml uv.lock* ./

# Without --frozen so build works when uv.lock is not in context (e.g. not committed)
RUN uv sync --no-dev --no-install-project

# Runtime stage
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

COPY main.py models.py database.py ./

EXPOSE 8080

CMD ["python", "main.py"]
