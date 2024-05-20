FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt /app

# Create and activate virtual environment
RUN python -m venv venv
ENV PATH="/app/venv/bin:$PATH"

# Install Python dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy application files
COPY . /app

# Expose port
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=app

# Run the application
CMD exec gunicorn --bind 0.0.0.0:$PORT app:app
