# =====================================================================
# SkyBlend AI — All-in-One Single-Container Production Image
# Builds frontend + backend together, serves via Nginx + Uvicorn.
# =====================================================================

# --- Stage 1: Build React/Vite Frontend ---
FROM node:22-alpine AS frontend-builder

WORKDIR /app

COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build

# --- Stage 2: Combined Production Runtime ---
FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Install Python runtime dependencies
COPY requirements.runtime.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install Nginx, envsubst, and curl
RUN apt-get update && \
    apt-get install -y --no-install-recommends nginx gettext-base curl && \
    rm -rf /var/lib/apt/lists/*

# Copy built frontend assets from Stage 1
COPY --from=frontend-builder /app/dist /usr/share/nginx/html

# Copy backend source, models, and data
COPY src ./src
COPY models ./models
COPY data ./data

# Copy Nginx config template and entrypoint
COPY docker/render/nginx.conf.template /etc/nginx/render.conf.template
COPY docker/render/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Default PORT
ENV PORT=10000

EXPOSE 10000

HEALTHCHECK --interval=30s --timeout=5s --start-period=45s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/health', timeout=3)"

CMD ["/app/entrypoint.sh"]
