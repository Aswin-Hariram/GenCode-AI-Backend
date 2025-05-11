FROM python:3.11-slim-bullseye

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create logs directory
RUN mkdir -p logs

# Set environment variables
ENV FLASK_ENV=production
ENV PORT=8080

# Expose the port
EXPOSE 8080

# Run with Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:$PORT", "--timeout", "120", "app:app"]
