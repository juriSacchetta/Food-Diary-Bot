#!/bin/bash
# deploy.sh - Script per deployare Food Diary Bot su Kubernetes
#
# Usage: ./k8s/deploy.sh

set -e  # Exit on error

echo "🚀 Food Diary Bot - Kubernetes Deployment"
echo "=========================================="
echo ""

# Colori per output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Directory k8s
K8S_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check se kubectl è installato
if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}❌ kubectl non trovato! Installalo prima: https://kubernetes.io/docs/tasks/tools/${NC}"
    exit 1
fi

echo -e "${GREEN}✓ kubectl trovato${NC}"

# Check se il file secrets reale esiste
if [ ! -f "$K8S_DIR/01-secrets-real.yaml" ]; then
    echo -e "${YELLOW}⚠️  File secrets non trovato!${NC}"
    echo ""
    echo "Devi creare il file con i tuoi secrets:"
    echo "  1. cp k8s/01-secrets.yaml.template k8s/01-secrets-real.yaml"
    echo "  2. Modifica il file con i valori reali codificati in base64"
    echo ""
    echo "Come codificare in base64:"
    echo "  echo -n 'YOUR_VALUE' | base64"
    echo ""
    exit 1
fi

echo -e "${GREEN}✓ Secrets file trovato${NC}"

# Check connessione al cluster
if ! kubectl cluster-info &> /dev/null; then
    echo -e "${RED}❌ Impossibile connettersi al cluster Kubernetes!${NC}"
    echo "Verifica che kubectl sia configurato correttamente"
    exit 1
fi

echo -e "${GREEN}✓ Connesso al cluster Kubernetes${NC}"
echo ""

# Mostra info cluster
echo "📊 Info cluster:"
kubectl cluster-info | head -1
echo ""

# Conferma deploy
read -p "Vuoi procedere con il deploy? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Deploy annullato"
    exit 0
fi

echo ""
echo "🔧 Applicando manifest Kubernetes..."
echo ""

# Apply in ordine
echo "1/7 Creando namespace..."
kubectl apply -f "$K8S_DIR/00-namespace.yaml"

echo "2/7 Creando secrets..."
kubectl apply -f "$K8S_DIR/01-secrets-real.yaml"

echo "3/7 Creando configmap..."
kubectl apply -f "$K8S_DIR/02-configmap.yaml"

echo "4/7 Creando PersistentVolumeClaims..."
kubectl apply -f "$K8S_DIR/03-pvc.yaml"

echo "5/7 Deploying bot..."
kubectl apply -f "$K8S_DIR/04-deployment-bot.yaml"

echo "6/7 Deploying admin panel..."
kubectl apply -f "$K8S_DIR/05-deployment-admin.yaml"

echo "7/7 Creando service..."
kubectl apply -f "$K8S_DIR/06-service-admin.yaml"

echo ""
echo -e "${GREEN}✅ Deploy completato!${NC}"
echo ""

# Wait for pods
echo "⏳ Aspettando che i Pod siano pronti..."
kubectl wait --for=condition=ready pod -l app=food-diary-bot -n food-diary --timeout=120s

echo ""
echo -e "${GREEN}✅ Tutti i Pod sono pronti!${NC}"
echo ""

# Mostra stato
echo "📊 Stato risorse:"
echo ""
kubectl get all -n food-diary

echo ""
echo "🌐 Accesso Admin Panel:"
echo ""

# Info sul service
kubectl get svc -n food-diary food-diary-admin-service

echo ""
echo -e "${YELLOW}Per accedere all'admin panel:${NC}"
echo ""

# Check se è minikube
if kubectl config current-context | grep -q "minikube"; then
    echo "Stai usando minikube, usa questo comando:"
    echo "  minikube service food-diary-admin-service -n food-diary"
else
    NODE_PORT=$(kubectl get svc -n food-diary food-diary-admin-service -o jsonpath='{.spec.ports[0].nodePort}')
    echo "Trova l'IP del tuo nodo con:"
    echo "  kubectl get nodes -o wide"
    echo ""
    echo "Poi accedi via browser:"
    echo "  http://<NODE_IP>:$NODE_PORT"
fi

echo ""
echo -e "${GREEN}🎉 Deploy completato con successo!${NC}"
echo ""
echo "Comandi utili:"
echo "  kubectl logs -f -n food-diary deployment/food-diary-bot    # Vedi logs bot"
echo "  kubectl logs -f -n food-diary deployment/food-diary-admin  # Vedi logs admin"
echo "  kubectl get pods -n food-diary                             # Lista Pod"
echo "  kubectl describe pod -n food-diary <POD_NAME>              # Dettagli Pod"
