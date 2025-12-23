FROM python:3.11-slim

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements FIRST (better cache)
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy ALL application files (current directory content)
COPY . .

# Optional: Verify structure
RUN echo "=== Listing /app ===" && ls -la /app
RUN echo "=== Listing /app/app ===" && ls -la /app/app

# Environment
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production
ENV PORT=5000

EXPOSE 5000

# Run app - ensure run.py exists at /app
CMD ["python", "run.py"]
