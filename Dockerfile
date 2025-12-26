FROM python:3.9-slim

# Install Chrome and dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list' \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Install specific Chromedriver version matching Chrome
# (Usually not strictly needed if using webdriver-manager, but good for stability)

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create downloads directory with permissions
RUN mkdir -p /app/downloads && chmod 777 /app/downloads

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=5000
ENV FLASK_APP=flask_app.py

# Expose port
EXPOSE 5000

# Start command: Run worker in background and flask app in foreground
CMD python sync_worker.py & gunicorn --bind 0.0.0.0:$PORT flask_app:app
