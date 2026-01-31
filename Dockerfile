FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements from backend folder
COPY backend/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend code
COPY backend/ .

# Expose the port (Railway provides PORT env var)
EXPOSE 8000

# Start the application using a shell to expand the $PORT variable
# Using uvicorn directly to rule out gunicorn configuration issues
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
