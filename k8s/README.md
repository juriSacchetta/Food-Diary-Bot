# Food Diary Bot - Kubernetes Deployment

Questa guida ti aiuta a deployare il Food Diary Bot su Kubernetes.

## 📋 Prerequisiti

- **Kubernetes cluster** funzionante (minikube, k3s, GKE, EKS, AKS, etc.)
- **kubectl** installato e configurato
- **Immagine Docker** del bot pushata su un registry (ghcr.io, Docker Hub, etc.)

## 🎯 Architettura

```
┌─────────────────────────────────────────┐
│         KUBERNETES CLUSTER              │
│                                         │
│  ┌───────────┐      ┌──────────────┐   │
│  │    Bot    │      │ Admin Panel  │   │
│  │ (1 Pod)   │      │   (1 Pod)    │   │
│  └─────┬─────┘      └──────┬───────┘   │
│        │                   │            │
│        └───────┬───────────┘            │
│                │                        │
│        ┌───────▼────────┐               │
│        │ PersistentVols │               │
│        │                │               │
│        │ - database.db  │               │
│        │ - photos/      │               │
│        │ - exports/     │               │
│        └────────────────┘               │
│                                         │
│  Service: NodePort :30500              │
│  (espone admin panel)                  │
└─────────────────────────────────────────┘
```

## 🚀 Quick Start

### 1. Crea i Secrets

Prima di tutto, devi creare un file con i tuoi secrets reali:

```bash
# Copia il template
cp k8s/01-secrets.yaml.template k8s/01-secrets-real.yaml

# Codifica i tuoi valori in base64
echo -n "YOUR_TELEGRAM_BOT_TOKEN" | base64
echo -n "admin" | base64
echo -n "your_password" | base64
echo -n "your_secret_key_very_long_random_string" | base64

# Modifica il file 01-secrets-real.yaml con i valori codificati
nano k8s/01-secrets-real.yaml
```

**IMPORTANTE:** Aggiungi `01-secrets-real.yaml` a `.gitignore` per non committare secrets!

### 2. Deploy su Kubernetes

```bash
# Applica tutti i manifest in ordine
kubectl apply -f k8s/00-namespace.yaml
kubectl apply -f k8s/01-secrets-real.yaml
kubectl apply -f k8s/02-configmap.yaml
kubectl apply -f k8s/03-pvc.yaml
kubectl apply -f k8s/04-deployment-bot.yaml
kubectl apply -f k8s/05-deployment-admin.yaml
kubectl apply -f k8s/06-service-admin.yaml

# Oppure applica tutto insieme
kubectl apply -f k8s/
```

### 3. Verifica il Deployment

```bash
# Controlla lo stato del namespace
kubectl get all -n food-diary

# Vedi i Pod
kubectl get pods -n food-diary

# Vedi i logs del bot
kubectl logs -f -n food-diary deployment/food-diary-bot

# Vedi i logs dell'admin
kubectl logs -f -n food-diary deployment/food-diary-admin

# Controlla i PVC
kubectl get pvc -n food-diary

# Descrivi un Pod per vedere dettagli
kubectl describe pod -n food-diary <POD_NAME>
```

### 4. Accedi all'Admin Panel

```bash
# Trova la porta NodePort
kubectl get svc -n food-diary food-diary-admin-service

# Trova l'IP del nodo
kubectl get nodes -o wide

# Accedi via browser
http://<NODE_IP>:30500
```

Per **minikube**:
```bash
minikube service food-diary-admin-service -n food-diary
```

## 📁 File Kubernetes

| File | Descrizione |
|------|-------------|
| `00-namespace.yaml` | Crea il namespace `food-diary` |
| `01-secrets.yaml.template` | Template per secrets (token, password) |
| `02-configmap.yaml` | Configurazioni non sensibili |
| `03-pvc.yaml` | Richieste di storage persistente |
| `04-deployment-bot.yaml` | Deployment del bot Telegram |
| `05-deployment-admin.yaml` | Deployment del pannello admin |
| `06-service-admin.yaml` | Service per esporre admin panel |

## 🔧 Configurazione

### Personalizza replicas

Modifica `replicas: 1` nei Deployment se vuoi più copie (solo per admin, non bot):

```yaml
# k8s/05-deployment-admin.yaml
spec:
  replicas: 2  # Due copie dell'admin panel
```

### Modifica risorse (CPU/RAM)

```yaml
# k8s/04-deployment-bot.yaml
resources:
  requests:
    memory: "512Mi"  # Aumenta se necessario
    cpu: "200m"
  limits:
    memory: "1Gi"
    cpu: "1000m"
```

### Cambia storage size

```yaml
# k8s/03-pvc.yaml
resources:
  requests:
    storage: 20Gi  # Aumenta per più foto
```

## 🔄 Aggiornamenti

### Update dell'immagine Docker

```bash
# 1. Builda e pusha nuova immagine
docker build -t ghcr.io/jurisacchetta/food-diary-bot:v2.0.0 .
docker push ghcr.io/jurisacchetta/food-diary-bot:v2.0.0

# 2. Aggiorna l'immagine nei Deployment
kubectl set image deployment/food-diary-bot bot=ghcr.io/jurisacchetta/food-diary-bot:v2.0.0 -n food-diary
kubectl set image deployment/food-diary-admin admin=ghcr.io/jurisacchetta/food-diary-bot:v2.0.0 -n food-diary

# 3. Verifica il rollout
kubectl rollout status deployment/food-diary-bot -n food-diary
kubectl rollout status deployment/food-diary-admin -n food-diary
```

### Rollback

Se qualcosa va storto:

```bash
# Torna alla versione precedente
kubectl rollout undo deployment/food-diary-bot -n food-diary

# Vedi la cronologia dei rollout
kubectl rollout history deployment/food-diary-bot -n food-diary
```

## 🐛 Troubleshooting

### Pod non si avvia

```bash
# Vedi i dettagli del Pod
kubectl describe pod -n food-diary <POD_NAME>

# Vedi i logs
kubectl logs -n food-diary <POD_NAME>

# Se il Pod crasha immediatamente
kubectl logs -n food-diary <POD_NAME> --previous
```

### PVC in stato Pending

```bash
# Controlla i PVC
kubectl get pvc -n food-diary

# Descrivi il PVC per vedere l'errore
kubectl describe pvc -n food-diary food-diary-db-pvc

# Verifica che ci siano PersistentVolumes disponibili
kubectl get pv
```

**Soluzione:** Il tuo cluster potrebbe non avere uno StorageClass di default.

Per **minikube**:
```bash
minikube addons enable default-storageclass
minikube addons enable storage-provisioner
```

Per **k3s**: è già incluso.

Per **cloud provider**: di solito è già configurato.

### Admin panel non raggiungibile

```bash
# Verifica il Service
kubectl get svc -n food-diary food-diary-admin-service

# Testa dall'interno del cluster
kubectl run -it --rm debug --image=curlimages/curl --restart=Never -n food-diary -- curl http://food-diary-admin-service:5000
```

### Secrets non trovati

```bash
# Verifica che i secrets esistano
kubectl get secrets -n food-diary

# Verifica il contenuto (codificato)
kubectl get secret food-diary-secrets -n food-diary -o yaml

# Decodifica un valore per verificare
kubectl get secret food-diary-secrets -n food-diary -o jsonpath='{.data.telegram-bot-token}' | base64 -d
```

## 🧹 Cleanup

Per rimuovere tutto:

```bash
# Elimina il namespace (elimina tutto al suo interno)
kubectl delete namespace food-diary

# Oppure elimina le risorse una per una
kubectl delete -f k8s/
```

**ATTENZIONE:** Questo eliminerà anche i PersistentVolumes con tutti i dati!

## 📚 Comandi Utili

```bash
# Vedi tutti i Pod in tutti i namespace
kubectl get pods --all-namespaces

# Entra in un Pod per debugging
kubectl exec -it -n food-diary <POD_NAME> -- /bin/bash

# Port forward per testare localmente
kubectl port-forward -n food-diary svc/food-diary-admin-service 8080:5000
# Poi apri: http://localhost:8080

# Vedi eventi recenti
kubectl get events -n food-diary --sort-by='.lastTimestamp'

# Monitora risorse
kubectl top pods -n food-diary
kubectl top nodes

# Scala il numero di repliche
kubectl scale deployment/food-diary-admin --replicas=3 -n food-diary
```

## 🎓 Prossimi Passi

Dopo aver deployato con successo:

1. **Monitoring**: Aggiungi Prometheus/Grafana per monitoraggio
2. **Ingress**: Usa un Ingress Controller per HTTPS e domini custom
3. **Backup**: Configura backup automatici dei PersistentVolumes
4. **CI/CD**: Automatizza il deploy con GitHub Actions
5. **HorizontalPodAutoscaler**: Scala automaticamente in base al carico

## 🔗 Risorse

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [kubectl Cheat Sheet](https://kubernetes.io/docs/reference/kubectl/cheatsheet/)
- [Minikube Start](https://minikube.sigs.k8s.io/docs/start/)
- [K3s Documentation](https://k3s.io/)
