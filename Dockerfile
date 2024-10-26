FROM nikolaik/python-nodejs:python3.11-nodejs20

WORKDIR /app

# Install backend dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ .

# Copy frontend files and install dependencies
COPY frontend/ ./frontend/
WORKDIR /app/frontend
RUN npm install

# Back to app root
WORKDIR /app

EXPOSE 8000 3000