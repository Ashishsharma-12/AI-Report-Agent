# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the whole project
COPY . .

# Set environment variables (optional)
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8080

# Set entrypoint
CMD ["adk", "web"]
