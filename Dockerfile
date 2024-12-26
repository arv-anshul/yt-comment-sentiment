# uv docs: https://docs.astral.sh/uv/guides/integration/docker/
FROM python:3.11-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/

# Install gcc for wordcloud
RUN apt-get update && apt-get install -y gcc && apt-get clean

WORKDIR /app

ADD pyproject.toml uv.lock /app
# Install dependencies with `--extra=backend` dependencies
RUN uv sync --extra=backend --frozen --compile-bytecode --no-install-project

# Copy only necessary files/folders to reduce image size
COPY params.yaml /app
COPY backend /app/backend
COPY ml /app/ml

RUN uv sync --extra=backend --locked

# Final stage
FROM python:3.11-slim AS final
COPY --from=builder /app /app

WORKDIR /app

# Run backend using fastapi-cli
CMD [".venv/bin/fastapi", "run", "--host", "0.0.0.0", "--port", "8000", "backend/app.py"]
