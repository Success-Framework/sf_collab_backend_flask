FROM python:3.11-slim

WORKDIR /app

# System dependencies
# --- SYSTEM DEPENDENCIES FOR WEASYPRINT ---
RUN apt-get update && apt-get install -y --no-install-recommends \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    libffi-dev \
    shared-mime-info \
    fonts-dejavu \
    fonts-liberation \
    fonts-freefont-ttf \
    libglib2.0-0 \
    curl \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps first (cache-friendly)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY . .

# Environment
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production
ENV PORT=5000
ENV GUNICORN_CMD_ARGS="\
    --bind=0.0.0.0:5000 \
    --workers=2 \
    --worker-class=geventwebsocket.gunicorn.workers.GeventWebSocketWorker \
    --worker-connections=1000 \
    --timeout=120"

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

CMD ["gunicorn", "run:app"]