# Makefile pour naviki-gpx-exporter
.PHONY: help build run shell clean test

# Variables
IMAGE_NAME=naviki-gpx-exporter
VERSION=0.1.0
OUTPUT_DIR=./output

help: ## Affiche cette aide
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

build: ## Build l'image Docker
	docker build -t $(IMAGE_NAME):$(VERSION) -t $(IMAGE_NAME):latest .

# --env-file : le mot de passe n'apparaît pas dans la ligne de commande
run: ## Lance l'export (identifiants lus dans .env)
	@if [ ! -f .env ]; then \
		echo "⚠️  Fichier .env non trouvé. Créez-le à partir de .env.example"; \
		exit 1; \
	fi
	@echo "🚀 Lancement de l'export Naviki..."
	@mkdir -p $(OUTPUT_DIR)
	docker run --rm \
		--user $$(id -u):$$(id -g) \
		--env-file .env \
		-v $(PWD)/output:/output \
		$(IMAGE_NAME):latest \
		--output /output

run-token: ## Lance l'export avec un token OAuth
	@read -p "Token OAuth: " token; \
	mkdir -p $(OUTPUT_DIR); \
	NAVIKI_TOKEN="$$token" docker run --rm \
		--user $$(id -u):$$(id -g) \
		-e NAVIKI_TOKEN \
		-v $(PWD)/output:/output \
		$(IMAGE_NAME):latest \
		--output /output

run-custom: ## Lance avec des arguments personnalisés (ex: make run-custom ARGS="--help")
	@mkdir -p $(OUTPUT_DIR)
	docker run --rm \
		--user $$(id -u):$$(id -g) \
		-v $(PWD)/output:/output \
		$(IMAGE_NAME):latest \
		$(ARGS)

shell: ## Ouvre un shell dans le container
	docker run --rm -it \
		-v $(PWD)/output:/output \
		--entrypoint /bin/bash \
		$(IMAGE_NAME):latest

# Image non root : dépendances de test installées avec --user
test: ## Lance les tests dans Docker
	docker run --rm \
		-v $(PWD)/tests:/app/tests:ro,z \
		-v $(PWD)/requirements-test.txt:/app/requirements-test.txt:ro,z \
		--entrypoint /bin/bash \
		$(IMAGE_NAME):latest \
		-c "pip install --user -q -r requirements-test.txt && python -m pytest tests/ -q -p no:cacheprovider"

security-scan: ## Scan de sécurité avec Trivy
	@if command -v trivy &> /dev/null; then \
		./security-scan-local.sh $(IMAGE_NAME):latest; \
	else \
		echo "⚠️  Trivy non installé, utilisation de Docker"; \
		docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy image $(IMAGE_NAME):latest; \
	fi

clean: ## Nettoie les images Docker
	docker rmi $(IMAGE_NAME):latest $(IMAGE_NAME):$(VERSION) 2>/dev/null || true
	docker system prune -f

clean-output: ## Supprime tous les fichiers GPX exportés
	rm -rf $(OUTPUT_DIR)/*.gpx

push: ## Push l'image vers Docker Hub (nécessite login)
	docker tag $(IMAGE_NAME):$(VERSION) votre-username/$(IMAGE_NAME):$(VERSION)
	docker tag $(IMAGE_NAME):$(VERSION) votre-username/$(IMAGE_NAME):latest
	docker push votre-username/$(IMAGE_NAME):$(VERSION)
	docker push votre-username/$(IMAGE_NAME):latest

compose-build: ## Build avec docker-compose
	docker-compose build

compose-run: ## Lance avec docker-compose
	docker-compose run --rm naviki-exporter --help

compose-down: ## Arrête les containers docker-compose
	docker-compose down

logs: ## Affiche les logs du dernier container
	docker logs $$(docker ps -lq)

size: ## Affiche la taille de l'image
	@docker images $(IMAGE_NAME) --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"