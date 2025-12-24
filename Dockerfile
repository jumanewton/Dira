# Combined Dockerfile for Heroku Backend (JAC + NLP + Database API)
# Using python 3.12 to ensure jaclang compatibility
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies including PostgreSQL client
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY backend/python/requirements.txt ./requirements.txt

# Upgrade pip and install CPU-only torch to save space/time
RUN pip install --upgrade pip && \
    pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Download Spacy model
RUN python -m spacy download en_core_web_sm

# Copy application code
COPY backend/ ./backend/

# Copy startup script
COPY backend/start_heroku.sh ./start_heroku.sh
RUN chmod +x ./start_heroku.sh

# Create a user for security (Heroku runs as non-root)
RUN useradd -m myuser

# Change ownership of app directory
RUN chown -R myuser:myuser /app

USER myuser

# Run the startup script
CMD ["./start_heroku.sh"]
