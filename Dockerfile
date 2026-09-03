# Singh Ji Voice AI v3.0 - Dockerfile
# Base: Python 3.11 slim for lightweight container

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for audio processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libportaudio2 \
    libportaudiocpp0 \
    portaudio19-dev \
    build-essential \
    libsndfile1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for Docker layer caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all 24 Voice AI files
COPY . .

# Create non-root user for security
RUN useradd -m -u 1000 singhji && chown -R singhji:singhji /app
USER singhji

# Expose port (FastAPI default)
EXPOSE 8000

# Healthcheck endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start the application
CMD ["python", "main.py"]
