# === STAGE 1 : Build des dépendances ===
FROM python:3.11-slim AS builder

WORKDIR /build

COPY requirements.txt .

RUN python -m pip install --upgrade pip && \
    pip install --prefix=/install -r requirements.txt

# === STAGE 2 : Image minimale d'exécution ===
FROM python:3.11-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Copie uniquement les dépendances nécessaires
COPY --from=builder /install /usr/local

ENV PATH=/root/.local/bin:$PATH

# === STAGE 3 : Image finale avec les services web ===
FROM base AS web

WORKDIR /app

COPY . .

EXPOSE 8000

CMD ["flask", "--app", "../app", "run", "--host=0.0.0.0", "--port=8000"]