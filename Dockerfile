FROM python:3.12-slim

WORKDIR /app


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

COPY images/image1.jpg images/image1.jpg
COPY images/image2.jpg images/image2.jpg


RUN mkdir -p static images && \
    chmod -R 777 static images

RUN addgroup --system appgroup && adduser --system appuser --ingroup appgroup


RUN chown -R appuser:appgroup /app


USER appuser

EXPOSE 5000

ENV FLASK_APP=app.py
ENV FLASK_ENV=production

CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
