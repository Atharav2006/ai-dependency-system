# Multi-stage build for React frontend + FastAPI backend
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend

# Copy frontend package files
COPY frontend/package*.json ./

# Install frontend dependencies
RUN npm install

# Copy frontend source
COPY frontend/ ./

# Pass environment variables at build time
ENV VITE_SUPABASE_URL=https://ltdmrgpvisfyrxwrwbev.supabase.co
ENV VITE_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imx0ZG1yZ3B2aXNmeXJ4d3J3YmV2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk0OTQzMzksImV4cCI6MjA4NTA3MDMzOX0.JfzxrVUvucpVNyKSjU9OEVE8xKeKNTacN82BZVccnR4
ENV VITE_BACKEND_URL=https://vgsarqvgha.dev.ap-jt.com/api

# Build frontend
RUN npm run build

# Backend stage
FROM python:3.11-slim

WORKDIR /app

# Install backend dependencies
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source
COPY backend/ ./backend/

# Copy built frontend from builder stage
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Install nginx to serve both frontend and backend
RUN apt-get update && apt-get install -y nginx && rm -rf /var/lib/apt/lists/*

# Create nginx config
RUN echo 'server {\n\
    listen 80;\n\
    server_name _;\n\
\n\
    # Remove default X-Frame-Options header to allow iframe embedding\n\
    proxy_hide_header X-Frame-Options;\n\
    add_header X-Frame-Options "";\n\
\n\
    # Serve frontend\n\
    location /ai-dependency-system/ {\n\
        alias /app/frontend/dist/;\n\
        try_files $uri $uri/ /ai-dependency-system/index.html;\n\
        add_header X-Frame-Options "";\n\
    }\n\
\n\
    # Proxy API requests to backend\n\
    location /api/ {\n\
        proxy_pass http://localhost:8000/;\n\
        proxy_http_version 1.1;\n\
        proxy_set_header Upgrade $http_upgrade;\n\
        proxy_set_header Connection "upgrade";\n\
        proxy_set_header Host $host;\n\
        proxy_set_header X-Real-IP $remote_addr;\n\
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;\n\
        proxy_set_header X-Forwarded-Proto $scheme;\n\
        proxy_hide_header X-Frame-Options;\n\
        add_header X-Frame-Options "";\n\
    }\n\
}\n' > /etc/nginx/sites-available/default

# Create startup script
RUN echo '#!/bin/bash\n\
cd /app/backend\n\
uvicorn app.main:app --host 0.0.0.0 --port 8000 &\n\
nginx -g "daemon off;"\n' > /start.sh && chmod +x /start.sh

EXPOSE 80

CMD ["/start.sh"]
