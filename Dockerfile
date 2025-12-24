# Combined Dockerfile for Heroku Backend
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY backend/python/requirements.txt ./requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir jaseci

# Download Spacy model
RUN python -m spacy download en_core_web_sm

# Copy application code
COPY backend/ ./backend/

# Copy startup script
COPY backend/start_heroku.sh ./start_heroku.sh
RUN chmod +x ./start_heroku.sh

# Create a user for security (Heroku runs as non-root)
RUN useradd -m myuser
USER myuser

# Run the startup script
CMD ["./start_heroku.sh"]
