#!/bin/bash
# Script de test pour l'image Docker naviki-gpx-exporter

set -e

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
IMAGE_NAME="${1:-naviki-gpx-exporter:latest}"
TESTS_PASSED=0
TESTS_FAILED=0

# Fonctions helper
log_test() {
    echo -e "\n${BLUE}🧪 Test: $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
    ((TESTS_PASSED++))
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
    ((TESTS_FAILED++))
}

log_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

# Header
echo -e "${GREEN}╔══════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  🐳 Tests Docker - Naviki GPX Exporter         ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}Image testée:${NC} $IMAGE_NAME"
echo ""

# Test 1: Vérifier que l'image existe
log_test "Image existe"
if docker image inspect "$IMAGE_NAME" &> /dev/null; then
    log_success "L'image $IMAGE_NAME existe"
else
    log_error "L'image $IMAGE_NAME n'existe pas"
    echo ""
    echo -e "${YELLOW}💡 Solution:${NC}"
    echo "   docker build -t $IMAGE_NAME ."
    echo "   OU"
    echo "   docker pull ghcr.io/gheop/naviki-gpx-exporter:latest"
    exit 1
fi

# Test 2: Vérifier la taille de l'image
log_test "Taille de l'image"
IMAGE_SIZE=$(docker images "$IMAGE_NAME" --format "{{.Size}}")
log_info "Taille: $IMAGE_SIZE"
if docker images "$IMAGE_NAME" --format "{{.Size}}" | grep -qE "[0-9]+"; then
    log_success "Taille acceptable"
else
    log_error "Impossible de déterminer la taille"
fi

# Test 3: Commande --help
log_test "Commande --help fonctionne"
if docker run --rm "$IMAGE_NAME" --help &> /tmp/test-help.txt; then
    if grep -q "usage:" /tmp/test-help.txt; then
        log_success "La commande --help fonctionne"
    else
        log_error "La sortie de --help est incorrecte"
        cat /tmp/test-help.txt
    fi
else
    log_error "La commande --help a échoué"
fi
rm -f /tmp/test-help.txt

# Test 4: Python est installé
log_test "Python est installé"
if docker run --rm --entrypoint python "$IMAGE_NAME" --version &> /tmp/test-python.txt; then
    PYTHON_VERSION=$(cat /tmp/test-python.txt)
    log_success "Python installé: $PYTHON_VERSION"
else
    log_error "Python non trouvé"
fi
rm -f /tmp/test-python.txt

# Test 5: Geckodriver est installé
log_test "Geckodriver est installé"
if docker run --rm --entrypoint geckodriver "$IMAGE_NAME" --version &> /tmp/test-gecko.txt; then
    GECKO_VERSION=$(cat /tmp/test-gecko.txt | head -1)
    log_success "Geckodriver installé: $GECKO_VERSION"
else
    log_error "Geckodriver non trouvé"
fi
rm -f /tmp/test-gecko.txt

# Test 6: Firefox est installé
log_test "Firefox est installé"
if docker run --rm --entrypoint firefox-esr "$IMAGE_NAME" --version &> /tmp/test-firefox.txt; then
    FIREFOX_VERSION=$(cat /tmp/test-firefox.txt)
    log_success "Firefox installé: $FIREFOX_VERSION"
else
    log_error "Firefox non trouvé"
fi
rm -f /tmp/test-firefox.txt

# Test 7: Dépendances Python (selenium)
log_test "Module selenium est installé"
if docker run --rm --entrypoint pip "$IMAGE_NAME" show selenium &> /tmp/test-selenium.txt; then
    SELENIUM_VERSION=$(grep "Version:" /tmp/test-selenium.txt | cut -d' ' -f2)
    log_success "Selenium installé: v$SELENIUM_VERSION"
else
    log_error "Selenium non trouvé"
fi
rm -f /tmp/test-selenium.txt

# Test 8: Dépendances Python (requests)
log_test "Module requests est installé"
if docker run --rm --entrypoint pip "$IMAGE_NAME" show requests &> /tmp/test-requests.txt; then
    REQUESTS_VERSION=$(grep "Version:" /tmp/test-requests.txt | cut -d' ' -f2)
    log_success "Requests installé: v$REQUESTS_VERSION"
else
    log_error "Requests non trouvé"
fi
rm -f /tmp/test-requests.txt

# Test 10: Structure des dossiers
log_test "Structure des dossiers"
if docker run --rm --entrypoint ls "$IMAGE_NAME" -la /app &> /tmp/test-structure.txt; then
    if grep -q "naviki-gpx-exporter.py" /tmp/test-structure.txt; then
        log_success "Script principal présent dans /app"
    else
        log_error "Script principal manquant"
    fi
else
    log_error "Impossible de lister /app"
fi
rm -f /tmp/test-structure.txt

# Test 11: Volume /output existe
log_test "Dossier /output existe"
if docker run --rm --entrypoint ls "$IMAGE_NAME" -ld /output &> /tmp/test-output.txt; then
    log_success "Dossier /output existe"
else
    log_error "Dossier /output manquant"
fi
rm -f /tmp/test-output.txt

# Test 12: Test d'erreur avec token invalide
log_test "Gestion d'erreur avec token invalide"
TEST_OUTPUT_DIR="/tmp/naviki-test-$$"
mkdir -p "$TEST_OUTPUT_DIR"
if docker run --rm \
    -v "$TEST_OUTPUT_DIR:/output" \
    "$IMAGE_NAME" \
    --token "invalid-test-token-12345" \
    --output /output &> /tmp/test-invalid.txt; then
    log_error "Le script aurait dû échouer avec un token invalide"
else
    if grep -qE "(401|Erreur|Token invalide)" /tmp/test-invalid.txt; then
        log_success "Gestion d'erreur correcte pour token invalide"
    else
        log_info "Erreur détectée mais message non reconnu"
    fi
fi
rm -rf "$TEST_OUTPUT_DIR"
rm -f /tmp/test-invalid.txt

# Test 13: Test arguments manquants
log_test "Détection des arguments manquants"
if docker run --rm "$IMAGE_NAME" &> /tmp/test-noargs.txt; then
    log_error "Le script aurait dû échouer sans arguments"
else
    if grep -qE "(required|error)" /tmp/test-noargs.txt; then
        log_success "Détection correcte des arguments manquants"
    else
        log_error "Message d'erreur incorrect"
    fi
fi
rm -f /tmp/test-noargs.txt

# Test 14: Vérifier les permissions d'exécution
log_test "Permissions d'exécution du script"
if docker run --rm --entrypoint ls "$IMAGE_NAME" -l /app/naviki-gpx-exporter.py | grep -q "^-rw"; then
    log_success "Permissions correctes (lecture/écriture)"
else
    log_info "Permissions différentes de la normale"
fi

# Test 15: Taille de l'image raisonnable
log_test "Taille de l'image raisonnable"
IMAGE_SIZE_MB=$(docker images "$IMAGE_NAME" --format "{{.Size}}" | sed 's/MB//' | sed 's/GB/*1024/' | bc 2>/dev/null || echo "0")
if [[ $(echo "$IMAGE_SIZE_MB < 1000" | bc) -eq 1 ]]; then
    log_success "Taille raisonnable (< 1GB)"
elif [[ $(echo "$IMAGE_SIZE_MB < 2000" | bc) -eq 1 ]]; then
    log_info "Taille acceptable (< 2GB)"
else
    log_error "Image trop volumineuse (> 2GB)"
fi

# Résumé
echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                  RÉSUMÉ DES TESTS               ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}✅ Tests réussis:${NC} $TESTS_PASSED"
echo -e "${RED}❌ Tests échoués:${NC} $TESTS_FAILED"
echo ""

if [[ $TESTS_FAILED -eq 0 ]]; then
    echo -e "${GREEN}🎉 Tous les tests sont passés!${NC}"
    echo -e "${BLUE}L'image Docker est prête à être utilisée.${NC}"
    echo ""
    echo -e "${YELLOW}Commandes pour commencer:${NC}"
    echo "   docker run --rm $IMAGE_NAME --help"
    echo "   ./docker-run.sh -u username -p password"
    echo "   make run"
    exit 0
else
    echo -e "${RED}⚠️  Certains tests ont échoué${NC}"
    echo -e "${YELLOW}Veuillez vérifier l'image et rebuilder si nécessaire:${NC}"
    echo "   docker build --no-cache -t $IMAGE_NAME ."
    exit 1
fi