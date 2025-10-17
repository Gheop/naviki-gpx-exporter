# Dockerfile pour naviki-gpx-exporter
FROM python:3.10-slim-bullseye

# Variables d'environnement pour éviter les prompts interactifs
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    # Désactiver le cache pip
    PIP_NO_CACHE_DIR=1

# Installation des dépendances système pour Firefox et Selenium
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Firefox et geckodriver
    firefox-esr \
    # Dépendances pour Selenium et Firefox headless
    wget \
    ca-certificates \
    # Nettoyage
    && rm -rf /var/lib/apt/lists/*

# Installation de geckodriver (version compatible avec Firefox ESR)
RUN GECKODRIVER_VERSION=$(wget -qO- "https://api.github.com/repos/mozilla/geckodriver/releases/latest" | grep -Po '"tag_name": "\K.*?(?=")') && \
    wget -q "https://github.com/mozilla/geckodriver/releases/download/${GECKODRIVER_VERSION}/geckodriver-${GECKODRIVER_VERSION}-linux64.tar.gz" && \
    tar -xzf geckodriver-${GECKODRIVER_VERSION}-linux64.tar.gz -C /usr/local/bin && \
    chmod +x /usr/local/bin/geckodriver && \
    rm geckodriver-${GECKODRIVER_VERSION}-linux64.tar.gz

# Création du répertoire de travail
WORKDIR /app

# Copie des fichiers de dépendances
COPY requirements.txt .

# Installation des dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copie du script principal
COPY naviki-gpx-exporter.py .

# Création du dossier de sortie par défaut
RUN mkdir -p /output

# Définir le volume pour les fichiers exportés
VOLUME ["/output"]

# Script d'entrée par défaut
ENTRYPOINT ["python", "/app/naviki-gpx-exporter.py"]

# Arguments par défaut (afficher l'aide)
CMD ["--help"]

# Labels pour la metadata
LABEL maintainer="votre@email.com" \
      description="Naviki GPX Exporter - Automated backup tool for Naviki routes" \
      version="0.1.0"