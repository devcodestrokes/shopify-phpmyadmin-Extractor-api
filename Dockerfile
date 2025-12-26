FROM python:3.9

# Install Chrome
RUN apt-get update && apt-get install -y wget unzip && \
    wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    apt install -y ./google-chrome-stable_current_amd64.deb && \
    rm google-chrome-stable_current_amd64.deb && \
    apt-get clean

# No need to install specific Chromedriver separately as we use webdriver-manager 
# which handles it automatically.

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
