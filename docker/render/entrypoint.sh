#!/bin/bash
set -e

PORT="${PORT:-10000}"
export PORT

echo "[SkyBlend] Initializing single-container deployment on PORT=${PORT}..."

# Substitute PORT into Nginx configuration
envsubst '${PORT}' < /etc/nginx/render.conf.template > /etc/nginx/sites-available/default
ln -sf /etc/nginx/sites-available/default /etc/nginx/sites-enabled/default
rm -f /etc/nginx/sites-enabled/default.dpkg-old 2>/dev/null || true

# Test Nginx syntax
nginx -t

# Process IDs
UVICORN_PID=""
NGINX_PID=""

# Graceful termination handler
cleanup() {
    echo "[SkyBlend] Received shutdown signal. Terminating processes gracefully..."
    if [ -n "$UVICORN_PID" ]; then
        kill -TERM "$UVICORN_PID" 2>/dev/null || true
    fi
    if [ -n "$NGINX_PID" ]; then
        kill -TERM "$NGINX_PID" 2>/dev/null || true
    fi
    wait "$UVICORN_PID" 2>/dev/null || true
    wait "$NGINX_PID" 2>/dev/null || true
    echo "[SkyBlend] Shutdown complete."
    exit 0
}

trap cleanup SIGTERM SIGINT

# Start Uvicorn in the background on localhost:8000 with exactly 1 worker
echo "[SkyBlend] Starting FastAPI backend (1 worker) on 127.0.0.1:8000..."
uvicorn src.api.main:app --host 127.0.0.1 --port 8000 --workers 1 &
UVICORN_PID=$!

# Health check loop: wait for backend models to load (max 30 seconds)
echo "[SkyBlend] Waiting for FastAPI to become healthy..."
HEALTHY=0
for i in $(seq 1 30); do
    # Check if Uvicorn process died prematurely
    if ! kill -0 "$UVICORN_PID" 2>/dev/null; then
        echo "[SkyBlend] ERROR: FastAPI process terminated unexpectedly during startup."
        exit 1
    fi

    if python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/health', timeout=2)" > /dev/null 2>&1; then
        echo "[SkyBlend] FastAPI is healthy and models are initialized (attempt $i)."
        HEALTHY=1
        break
    fi
    sleep 1
done

if [ "$HEALTHY" -ne 1 ]; then
    echo "[SkyBlend] FATAL: FastAPI failed to become healthy within 30s timeout. Aborting startup."
    kill -TERM "$UVICORN_PID" 2>/dev/null || true
    wait "$UVICORN_PID" 2>/dev/null || true
    exit 1
fi

# Start Nginx in the background
echo "[SkyBlend] Starting Nginx on port ${PORT}..."
nginx -g "daemon off;" &
NGINX_PID=$!

echo "[SkyBlend] All services operational. Ready to serve traffic on port ${PORT}."

# Wait for either process to terminate
wait -n "$UVICORN_PID" "$NGINX_PID"
EXIT_STATUS=$?

echo "[SkyBlend] A core process exited with status ${EXIT_STATUS}. Shutting down remaining services..."
if [ -n "$UVICORN_PID" ]; then
    kill -TERM "$UVICORN_PID" 2>/dev/null || true
fi
if [ -n "$NGINX_PID" ]; then
    kill -TERM "$NGINX_PID" 2>/dev/null || true
fi
wait "$UVICORN_PID" 2>/dev/null || true
wait "$NGINX_PID" 2>/dev/null || true

# If the process exited with 0 (unexpected for a daemon), ensure non-zero exit code
if [ "$EXIT_STATUS" -eq 0 ]; then
    EXIT_STATUS=1
fi

exit "$EXIT_STATUS"
