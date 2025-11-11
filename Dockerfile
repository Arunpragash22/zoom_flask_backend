# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all app files
COPY . .

# Cloud Run expects $PORT
ENV PORT=8080
EXPOSE 8080

# Run Flask app
CMD ["python", "app.py"]
