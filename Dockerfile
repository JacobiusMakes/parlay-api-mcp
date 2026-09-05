FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PARLAYAPI_BASE_URL=https://parlay-api.com

WORKDIR /app
COPY pyproject.toml README.md LICENSE ./
COPY parlayapi_mcp ./parlayapi_mcp
RUN python -m pip install --no-cache-dir . \
    && useradd --create-home --uid 10001 mcp

USER 10001:10001
# Local stdio only: no HTTP listener, published port, or shared account key.
ENTRYPOINT ["parlayapi-mcp"]
