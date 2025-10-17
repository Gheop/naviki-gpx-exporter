#!/bin/bash
# Script pour scanner localement l'image Docker avec Trivy

set -e

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

IMAGE_NAME="${1:-naviki-gpx-exporter:latest}"

echo -e "${BLUE}╔══════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  🔒 Security Scan - Naviki GPX Exporter         ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}Image à scanner:${NC} $IMAGE_NAME"
echo ""

# Vérifier si Trivy est installé
if ! command -v trivy &> /dev/null; then
    echo -e "${YELLOW}⚠️  Trivy n'est pas installé${NC}"
    echo ""
    echo -e "${BLUE}Installation:${NC}"
    echo "  # Debian/Ubuntu"
    echo "  wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | sudo apt-key add -"
    echo "  echo 'deb https://aquasecurity.github.io/trivy-repo/deb \$(lsb_release -sc) main' | sudo tee /etc/apt/sources.list.d/trivy.list"
    echo "  sudo apt-get update && sudo apt-get install trivy"
    echo ""
    echo "  # macOS"
    echo "  brew install trivy"
    echo ""
    echo "  # Docker"
    echo "  docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy image $IMAGE_NAME"
    exit 1
fi

# Vérifier si l'image existe
if ! docker image inspect "$IMAGE_NAME" &> /dev/null; then
    echo -e "${RED}❌ Image '$IMAGE_NAME' non trouvée${NC}"
    echo ""
    echo -e "${YELLOW}💡 Solution:${NC}"
    echo "   docker build -t $IMAGE_NAME ."
    exit 1
fi

echo -e "${GREEN}🔍 Scan en cours...${NC}"
echo ""

# Scan complet
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}📊 Scan complet (toutes sévérités)${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
trivy image "$IMAGE_NAME" 2>/dev/null || true

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}🔴 Vulnérabilités CRITICAL et HIGH${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
CRITICAL_HIGH=$(trivy image --severity CRITICAL,HIGH --quiet "$IMAGE_NAME" 2>/dev/null)

if [ -z "$CRITICAL_HIGH" ]; then
    echo -e "${GREEN}✅ Aucune vulnérabilité CRITICAL ou HIGH trouvée!${NC}"
else
    echo "$CRITICAL_HIGH"
    echo ""
    echo -e "${YELLOW}⚠️  Des vulnérabilités CRITICAL ou HIGH ont été détectées${NC}"
fi

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}📈 Résumé${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Compter les vulnérabilités
CRITICAL=$(trivy image --severity CRITICAL --quiet "$IMAGE_NAME" 2>/dev/null | wc -l)
HIGH=$(trivy image --severity HIGH --quiet "$IMAGE_NAME" 2>/dev/null | wc -l)
MEDIUM=$(trivy image --severity MEDIUM --quiet "$IMAGE_NAME" 2>/dev/null | wc -l)
LOW=$(trivy image --severity LOW --quiet "$IMAGE_NAME" 2>/dev/null | wc -l)

echo -e "${RED}🔴 CRITICAL:${NC} $CRITICAL"
echo -e "${YELLOW}🟠 HIGH:${NC} $HIGH"
echo -e "${BLUE}🟡 MEDIUM:${NC} $MEDIUM"
echo -e "${GREEN}🟢 LOW:${NC} $LOW"

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}💾 Générer un rapport${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${YELLOW}Commandes utiles:${NC}"
echo "  # Rapport JSON"
echo "  trivy image --format json --output report.json $IMAGE_NAME"
echo ""
echo "  # Rapport SARIF (pour GitHub)"
echo "  trivy image --format sarif --output trivy-results.sarif $IMAGE_NAME"
echo ""
echo "  # Rapport HTML"
echo "  trivy image --format template --template '@contrib/html.tpl' --output report.html $IMAGE_NAME"
echo ""
echo "  # Seulement CRITICAL et HIGH"
echo "  trivy image --severity CRITICAL,HIGH $IMAGE_NAME"

echo ""
if [ "$CRITICAL" -gt 0 ] || [ "$HIGH" -gt 0 ]; then
    echo -e "${YELLOW}⚠️  Action recommandée:${NC}"
    echo "   - Mettre à jour les dépendances système dans le Dockerfile"
    echo "   - Utiliser une image de base plus récente"
    echo "   - Vérifier les dépendances Python dans requirements.txt"
    exit 1
else
    echo -e "${GREEN}✅ Scan de sécurité réussi!${NC}"
    exit 0
fi