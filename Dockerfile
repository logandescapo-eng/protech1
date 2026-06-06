# Use Python 3.11 slim image (more stable than 3.14 for Docker)
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Production entrypoint (Railway sets PORT; strip CRLF from Windows checkouts)
RUN sed -i 's/\r$//' entrypoint.sh && chmod +x entrypoint.sh

# Create non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=app.py
ENV PYTHONUNBUFFERED=1
ENV PORT=5000

# Run with gunicorn (Railway injects PORT at runtime)
CMD ["sh", "entrypoint.sh"]
