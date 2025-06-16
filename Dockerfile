FROM python:3.12-slim

WORKDIR /app

# Install dependencies and clean up cache in one RUN to reduce layers & issues
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        libglib2.0-0 \
        libsm6 \
        libxext6 \
        libxrender-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn

COPY . .

# Use non-root user for better security (optional but recommended)
RUN addgroup --system appgroup && adduser --system appuser --ingroup appgroup
USER appuser

EXPOSE 5000

ENV FLASK_APP=app.py
ENV FLASK_ENV=production

CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
