# Start with a base image that has Python and Node.js
FROM python:3.11-slim AS base

# Install Node.js
RUN apt-get update && apt-get install -y nodejs npm && rm -rf /var/lib/apt/lists/*

# Install Supervisor to manage multiple processes
RUN apt-get update && apt-get install -y supervisor

# Copy supervisor configuration file
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Setup Backend
WORKDIR /app/backend
COPY backend/ .
RUN pip install -r requirements.txt

# Setup Frontend
WORKDIR /app/frontend
COPY frontend/ .
RUN npm install

# Expose the necessary ports
EXPOSE 8000 3000

# Start Supervisor
CMD ["/usr/bin/supervisord"]
