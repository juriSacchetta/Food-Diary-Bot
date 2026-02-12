#!/bin/bash
# cleanup.sh - Rimuove Food Diary Bot da Kubernetes
#
# Usage: ./k8s/cleanup.sh

set -e

echo "🧹 Food Diary Bot - Kubernetes Cleanup"
echo "======================================"
echo ""

# Colori
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Warning
echo -e "${RED}⚠️  ATTENZIONE! ⚠️${NC}"
echo ""
echo "Questo script eliminerà:"
echo "  - Tutti i Pod (bot e admin)"
echo "  - Tutti i Service"
echo "  - Tutti i PersistentVolumeClaims"
echo "  - Il namespace food-diary"
echo ""
echo -e "${YELLOW}⚠️  I DATI (database, foto, export) SARANNO PERSI!${NC}"
echo ""

# Conferma
read -p "Sei sicuro di voler procedere? Scrivi 'yes' per confermare: " -r
echo
if [[ ! $REPLY == "yes" ]]; then
    echo "Cleanup annullato"
    exit 0
fi

echo ""
echo "Rimozione risorse in corso..."

# Delete namespace (deletes everything inside)
kubectl delete namespace food-diary

echo ""
echo "✅ Cleanup completato!"
echo ""
echo "Per ri-deployare:"
echo "  ./k8s/deploy.sh"
