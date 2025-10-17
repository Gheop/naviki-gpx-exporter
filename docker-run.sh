#!/bin/bash
# Script helper pour lancer naviki-gpx-exporter avec Docker facilement

set -e

# Couleurs pour l'output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration par défaut
IMAGE_NAME="naviki-gpx-exporter:latest"
OUTPUT_DIR="/tmp/output"

# Fonction d'aide
show_help() {
    cat << EOF
${BLUE}🚴 Naviki GPX Exporter - Docker Helper${NC}

Usage: $0 [OPTIONS]

Options:
    -u, --username USERNAME    Nom d'utilisateur Naviki
    -p, --password PASSWORD    Mot de passe Naviki
    -t, --token TOKEN         Token OAuth (alternative à username/password)
    -o, --output DIR          Dossier de sortie (défaut: ./output)
    -i, --image IMAGE         Image Docker à utiliser (défaut: $IMAGE_NAME)
    --types TYPES            Types de routes (défaut: tous)
    --visible                Mode visible (debug, nécessite X11)
    --pull                   Télécharger la dernière image avant de lancer
    -h, --help               Afficher cette aide

Exemples:
    # Avec username/password
    $0 -u MonUsername -p 'MonPassword!'
    
    # Avec token OAuth
    $0 -t abc123-def456-ghi789
    
    # Avec dossier de sortie personnalisé
    $0 -u MonUsername -p 'MonPassword!' -o ~/naviki-backup
    
    # Utiliser l'image officielle de GitHub
    $0 -u MonUsername -p 'MonPassword!' -i ghcr.io/gheop/naviki-gpx-exporter:latest --pull
    
    # Mode debug visible
    $0 -u MonUsername -p 'MonPassword!' --visible
    
    # Seulement les routes enregistrées
    $0 -u MonUsername -p 'MonPassword!' --types recordedMy

Variables d'environnement:
    NAVIKI_USERNAME    Username par défaut
    NAVIKI_PASSWORD    Password par défaut
    NAVIKI_TOKEN       Token par défaut

EOF
}

# Parsing des arguments
USERNAME="${NAVIKI_USERNAME:-}"
PASSWORD="${NAVIKI_PASSWORD:-}"
TOKEN="${NAVIKI_TOKEN:-}"
TYPES="routedAll,recordedMy,recordedOthers"
VISIBLE=false
PULL=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -u|--username)
            USERNAME="$2"
            shift 2
            ;;
        -p|--password)
            PASSWORD="$2"
            shift 2
            ;;
        -t|--token)
            TOKEN="$2"
            shift 2
            ;;
        -o|--output)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        -i|--image)
            IMAGE_NAME="$2"
            shift 2
            ;;
        --types)
            TYPES="$2"
            shift 2
            ;;
        --visible)
            VISIBLE=true
            shift
            ;;
        --pull)
            PULL=true
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo -e "${RED}❌ Option inconnue: $1${NC}"
            show_help
            exit 1
            ;;
    esac
done

# Vérifications
if [[ -z "$TOKEN" ]] && [[ -z "$USERNAME" || -z "$PASSWORD" ]]; then
    echo -e "${RED}❌ Erreur: Vous devez fournir soit:${NC}"
    echo "   - Un token OAuth avec -t/--token"
    echo "   - Username ET password avec -u/--username et -p/--password"
    echo ""
    show_help
    exit 1
fi

# Pull de l'image si demandé
if [[ "$PULL" == true ]]; then
    echo -e "${BLUE}📥 Téléchargement de l'image $IMAGE_NAME...${NC}"
    docker pull "$IMAGE_NAME"
fi

# Vérifier que l'image existe
if ! docker image inspect "$IMAGE_NAME" &> /dev/null; then
    echo -e "${YELLOW}⚠️  Image $IMAGE_NAME non trouvée localement${NC}"
    echo -e "${BLUE}📥 Tentative de téléchargement...${NC}"
    if ! docker pull "$IMAGE_NAME"; then
        echo -e "${RED}❌ Impossible de télécharger l'image${NC}"
        echo "   Essayez de la builder localement avec: make build"
        exit 1
    fi
fi

# Créer le dossier de sortie
mkdir -p "$OUTPUT_DIR"

# Préparer les arguments Docker
DOCKER_ARGS=(
    "run"
    "--rm"
    "-v" "$(realpath "$OUTPUT_DIR"):/output"
)

# Mode visible (X11)
if [[ "$VISIBLE" == true ]]; then
    if [[ -z "$DISPLAY" ]]; then
        echo -e "${YELLOW}⚠️  Variable DISPLAY non définie, mode visible désactivé${NC}"
    else
        echo -e "${BLUE}👁️  Mode visible activé${NC}"
        DOCKER_ARGS+=("-e" "DISPLAY=$DISPLAY")
        DOCKER_ARGS+=("-v" "/tmp/.X11-unix:/tmp/.X11-unix")
        
        # Autoriser les connexions X11 (nécessaire sur certains systèmes)
        xhost +local:docker &> /dev/null || true
    fi
fi

# Image
DOCKER_ARGS+=("$IMAGE_NAME")

# Arguments du script Python
SCRIPT_ARGS=()

if [[ -n "$TOKEN" ]]; then
    SCRIPT_ARGS+=("--token" "$TOKEN")
else
    SCRIPT_ARGS+=("--username" "$USERNAME" "--password" "$PASSWORD")
fi

SCRIPT_ARGS+=("--output" "/output")
SCRIPT_ARGS+=("--types" "$TYPES")

if [[ "$VISIBLE" == true ]]; then
    SCRIPT_ARGS+=("--visible")
else
    SCRIPT_ARGS+=("--headless")
fi

# Affichage de la configuration
echo -e "${GREEN}┌─────────────────────────────────────────────┐${NC}"
echo -e "${GREEN}│  🚴 Naviki GPX Exporter - Docker           │${NC}"
echo -e "${GREEN}└─────────────────────────────────────────────┘${NC}"
echo ""
echo -e "${BLUE}📁 Dossier de sortie:${NC} $(realpath "$OUTPUT_DIR")"
echo -e "${BLUE}🐳 Image Docker:${NC} $IMAGE_NAME"
if [[ -n "$TOKEN" ]]; then
    echo -e "${BLUE}🔑 Authentification:${NC} Token OAuth"
else
    echo -e "${BLUE}🔑 Authentification:${NC} Username/Password"
fi
echo -e "${BLUE}🔍 Types de routes:${NC} $TYPES"
echo ""

# Lancement
echo -e "${GREEN}🚀 Lancement de l'export...${NC}"
echo ""

# Exécuter Docker
docker "${DOCKER_ARGS[@]}" "${SCRIPT_ARGS[@]}"

EXIT_CODE=$?

# Nettoyage X11
if [[ "$VISIBLE" == true ]]; then
    xhost -local:docker &> /dev/null || true
fi

# Message final
echo ""
if [[ $EXIT_CODE -eq 0 ]]; then
    echo -e "${GREEN}✅ Export terminé avec succès!${NC}"
    echo -e "${BLUE}📁 Fichiers disponibles dans:${NC} $(realpath "$OUTPUT_DIR")"
    
    # Afficher le nombre de fichiers GPX
    GPX_COUNT=$(find "$OUTPUT_DIR" -name "*.gpx" 2>/dev/null | wc -l)
    if [[ $GPX_COUNT -gt 0 ]]; then
        echo -e "${BLUE}📊 Nombre de fichiers GPX:${NC} $GPX_COUNT"
    fi
else
    echo -e "${RED}❌ L'export a échoué (code: $EXIT_CODE)${NC}"
fi

exit $EXIT_CODE