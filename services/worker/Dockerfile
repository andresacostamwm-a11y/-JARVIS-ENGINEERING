FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

# Share API code for models + calc (mounted or copied)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Worker package
COPY app ./app

# Also need API package for models — copied in docker-compose build context via monorepo Dockerfile
ENV PYTHONPATH=/app:/api
ENV C_FORCE_ROOT=1

CMD ["celery", "-A", "app.celery_app.celery", "worker", "--loglevel=info"]
