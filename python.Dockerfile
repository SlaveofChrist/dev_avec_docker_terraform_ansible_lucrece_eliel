FROM python:3.9-slim

# Bonnes pratiques : ne pas générer de fichiers .pyc et logs unbuffered
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Installation des dépendances système minimales (si besoin de compiler psycopg2)
# Pour psycopg2-binary, ce n'est souvent pas nécessaire sur slim, mais au cas où :
# RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie du code
COPY app/ .

# CRITIQUE : Création d'un utilisateur non-root
RUN useradd -m appuser && chown -R appuser /app
USER appuser

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]