FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml alembic.ini ./
COPY app ./app
COPY alembic ./alembic
COPY tests ./tests
COPY scripts ./scripts
RUN pip install --no-cache-dir -e ".[dev]"

EXPOSE 8000

HEALTHCHECK --interval=10s --timeout=5s --start-period=20s --retries=10 CMD curl -fsS http://localhost:8000/health || exit 1

CMD ["sh", "/app/scripts/start.sh"]
