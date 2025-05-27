# Use official Python 3.12 slim image as base
FROM python:3.12-slim

# Set working directory inside the container
WORKDIR /app

# Install system dependencies required for PyTorch and image libs
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Install Gunicorn for production-grade Flask serving
RUN pip install --no-cache-dir gunicorn

# Copy all your app files (including models folder)
COPY . .

# Expose port 5000 to the outside
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# Run the app with Gunicorn server binding to all interfaces on port 5000
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
