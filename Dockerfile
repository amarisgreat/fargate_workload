FROM python:3.12-slim

WORKDIR /app

# Install OS dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        libglib2.0-0 \
        libsm6 \
        libxext6 \
        libxrender-dev \
        ca-certificates \
        curl && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn

# Copy code
COPY . .

# Optional: Skip user switch for now
# If needed later:
# RUN adduser --disabled-password --gecos '' appuser && chown -R appuser /app
# USER appuser

EXPOSE 5000

# Environment and launch
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
