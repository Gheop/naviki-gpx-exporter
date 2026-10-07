# Dockerfile pour naviki-gpx-exporter
FROM python:3.13-slim-bookworm

# Variables d'environnement pour éviter les prompts interactifs
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    # Désactiver le cache pip
    PIP_NO_CACHE_DIR=1

# Installation des dépendances système pour Firefox et Selenium
RUN apt-get update && apt-get install -y --no-install-recommends \
    firefox-esr \
    wget \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Installation de geckodriver (version fixe pour éviter les problèmes d'API).
# Empreintes publiées par GitHub pour les assets de la release : une archive
# modifiée fait échouer le build
RUN GECKODRIVER_VERSION="v0.37.1" && \
    ARCH=$(dpkg --print-architecture) && \
    case "$ARCH" in \
        amd64) GECKODRIVER_ARCH="linux64"; \
               GECKODRIVER_SHA256="e815130ea95983e162ae91843b48d3a3ce991735635fce83a647afde21e09f7e" ;; \
        arm64) GECKODRIVER_ARCH="linux-aarch64"; \
               GECKODRIVER_SHA256="8fd90b951422fbad5b56539fb344dff66eb3f986d615d8d6fde9f1f62dad610c" ;; \
        *) echo "Architecture non prise en charge: $ARCH" >&2; exit 1 ;; \
    esac && \
    wget -q "https://github.com/mozilla/geckodriver/releases/download/${GECKODRIVER_VERSION}/geckodriver-${GECKODRIVER_VERSION}-${GECKODRIVER_ARCH}.tar.gz" -O /tmp/geckodriver.tar.gz && \
    echo "${GECKODRIVER_SHA256}  /tmp/geckodriver.tar.gz" | sha256sum -c - && \
    tar -xzf /tmp/geckodriver.tar.gz -C /usr/local/bin && \
    chmod +x /usr/local/bin/geckodriver && \
    rm /tmp/geckodriver.tar.gz && \
    geckodriver --version

# Création du répertoire de travail
WORKDIR /app

# Dépendances verrouillées avec empreintes : image reproductible, et un
# paquet altéré sur PyPI fait échouer le build
COPY requirements-lock.txt .
RUN pip install --no-cache-dir --require-hashes -r requirements-lock.txt

# Copie du script principal
COPY naviki-gpx-exporter.py .

# Utilisateur non root, uid 1000 comme le premier utilisateur d'un hôte Linux
# courant : les fichiers écrits dans /output lui appartiennent. HOME sert au
# profil Firefox du repli Selenium, /config au .env et au cache de token.
RUN useradd --create-home --uid 1000 naviki && \
    mkdir -p /output /config && \
    chown naviki:naviki /output /config
ENV NAVIKI_CONFIG_DIR=/config
USER naviki

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