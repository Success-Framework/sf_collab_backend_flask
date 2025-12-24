FROM python:3.11-slim

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for Docker layer caching)
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy all app files
COPY . .

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production
ENV PORT=5000
ENV GUNICORN_CMD_ARGS="--bind=0.0.0.0:5000 --workers=4 --threads=2 --timeout=120"

EXPOSE 5000

# Healthcheck for Docker
HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD curl -f http://localhost:5000/health || exit 1

# Run app using Gunicorn
CMD ["gunicorn", "run:app"]
