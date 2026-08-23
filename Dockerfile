# ------------------------------------------------------------------------------
# Stage 1: Build the Vite Single-Page Application (Frontend)
# ------------------------------------------------------------------------------
FROM node:20-alpine AS frontend-builder

WORKDIR /app/web
COPY web/package*.json ./
RUN npm ci || npm install --no-audit --no-fund
COPY web/ ./
RUN npm run build

# ------------------------------------------------------------------------------
# Stage 2: Production Container (Python FastAPI + Bundled Static Frontend)
# ------------------------------------------------------------------------------
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies for PostgreSQL and build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy backend dependencies
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application
COPY backend/ ./

# Copy built frontend assets into the expected web/dist path
COPY --from=frontend-builder /app/web/dist ./web/dist

# Configure environment defaults (Render sets $PORT dynamically)
ENV PORT=8000
ENV HOST=0.0.0.0
ENV PYTHONUNBUFFERED=1
ENV ENVIRONMENT=production
ENV DEMO_MODE=false

EXPOSE 8000

# Production startup: Uvicorn binds to 0.0.0.0 and dynamic $PORT
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
