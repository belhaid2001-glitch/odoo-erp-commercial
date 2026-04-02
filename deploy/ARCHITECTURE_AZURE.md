# Architecture Azure pour Odoo ERP Commercial

## Sommaire
1. [Comparatif des architectures](#1-comparatif-des-architectures)
2. [Architecture Budget Étudiant (recommandée)](#2-architecture-budget-étudiant)
3. [Déploiement étape par étape](#3-déploiement-étape-par-étape)
4. [Erreurs à éviter](#4-erreurs-à-éviter)
5. [Architecture avancée (scalable)](#5-architecture-avancée)

---

## 1. Comparatif des architectures

### Pourquoi App Service Free Tier ne fonctionne PAS pour Odoo

| Limitation App Service Free | Impact sur Odoo |
|---|---|
| 1 Go RAM partagé | Odoo a besoin de ~512 Mo minimum |
| 60 min CPU/jour | Odoo tourne en continu |
| Pas de PostgreSQL intégré | Odoo EXIGE PostgreSQL |
| Pas de volumes persistants | Les fichiers uploadés sont perdus |
| Pas de Docker Compose | On a 4 services (Odoo + PG + Nginx + Certbot) |

### Comparatif des 3 architectures possibles

```
┌─────────────────────────────────────────────────────────────────────┐
│                    OPTION A : VM + Docker (RECOMMANDÉ)              │
│                                                                     │
│  ┌──────────────────────────────────────────────────┐              │
│  │        Azure VM (Ubuntu 22.04 LTS)               │              │
│  │        Standard_B1s / B2s                         │              │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐         │              │
│  │  │  Nginx   │ │  Odoo    │ │ Postgres │         │              │
│  │  │  :80/443 │→│  :8069   │→│  :5432   │         │              │
│  │  └──────────┘ └──────────┘ └──────────┘         │              │
│  │       ↑            ↑            ↑                │              │
│  │  Docker Compose (orchestration)                  │              │
│  └──────────────────────────────────────────────────┘              │
│                        ↑                                            │
│                   IP Publique                                       │
│                   + DNS (optionnel)                                  │
│                                                                     │
│  Coût : 0€ (B1s gratuit 12 mois) → ~8€/mois après                │
│  Difficulté : ★★☆☆☆                                               │
│  Adapté : Étudiant, startup, PME < 20 utilisateurs                │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│              OPTION B : Container Instances + Managed DB            │
│                                                                     │
│  ┌──────────────────┐    ┌──────────────────────────┐              │
│  │ Azure Container  │    │ Azure Database for        │              │
│  │ Instances (ACI)  │───→│ PostgreSQL Flexible       │              │
│  │ (Odoo + Nginx)   │    │ Server                    │              │
│  └──────────────────┘    └──────────────────────────┘              │
│         ↑                         ↑                                 │
│    Azure File Share          Backups auto                           │
│    (stockage)                Haute dispo                            │
│                                                                     │
│  Coût : ~30-50€/mois                                               │
│  Difficulté : ★★★☆☆                                               │
│  Adapté : PME sérieuse, ~20-50 utilisateurs                       │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                  OPTION C : AKS (Kubernetes)                        │
│                                                                     │
│  ┌──────────────────────────────────────────────────┐              │
│  │            Azure Kubernetes Service (AKS)         │              │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐            │              │
│  │  │ Odoo    │ │ Odoo    │ │ Odoo    │  ← HPA     │              │
│  │  │ Pod 1   │ │ Pod 2   │ │ Pod N   │            │              │
│  │  └─────────┘ └─────────┘ └─────────┘            │              │
│  │       │           │           │                   │              │
│  │  ┌────────────────────────────────────┐          │              │
│  │  │   Ingress Controller (Nginx)       │          │              │
│  │  └────────────────────────────────────┘          │              │
│  └──────────────────────────────────────────────────┘              │
│         ↑                    ↓                                      │
│    Load Balancer     Azure DB Postgres                              │
│                      Azure Blob Storage                             │
│                                                                     │
│  Coût : ~100-200€/mois minimum                                     │
│  Difficulté : ★★★★★                                               │
│  Adapté : Entreprise > 100 utilisateurs, SLA 99.9%                │
└─────────────────────────────────────────────────────────────────────┘
```

### Verdict pour votre cas

| Critère | VM + Docker | ACI + Managed DB | AKS |
|---|---|---|---|
| **Budget étudiant** | ✅ Parfait | ⚠️ Cher | ❌ Trop cher |
| **Apprentissage** | ✅ On apprend tout | ✅ Moyen | ✅ Très formateur |
| **Production-ready** | ⚠️ Limité | ✅ Oui | ✅ Très |
| **Facilité** | ✅ Simple | ✅ Moyen | ❌ Complexe |
| **Scalabilité** | ❌ Verticale | ⚠️ Limitée | ✅ Horizontale |

**→ RECOMMANDATION : Option A (VM + Docker) pour commencer, migrable vers B ou C plus tard.**

---

## 2. Architecture Budget Étudiant

### Schéma détaillé

```
                    ┌─────────────────────────────────────┐
                    │           INTERNET                    │
                    └───────────────┬─────────────────────┘
                                    │
                    ┌───────────────▼─────────────────────┐
                    │    Azure NSG (Network Security Group) │
                    │    Ports autorisés: 22, 80, 443       │
                    └───────────────┬─────────────────────┘
                                    │
            ┌───────────────────────▼───────────────────────┐
            │          Azure VM - Standard_B1s               │
            │          Ubuntu 22.04 LTS                      │
            │          1 vCPU | 1 Go RAM | 30 Go SSD         │
            │          + 2 Go Swap                            │
            │                                                 │
            │  ┌─────────────────────────────────────────┐   │
            │  │         Docker Engine                    │   │
            │  │                                          │   │
            │  │  ┌──────────┐                           │   │
            │  │  │  Nginx   │ ← Port 80/443 (public)   │   │
            │  │  │  64 Mo   │   SSL Let's Encrypt       │   │
            │  │  └────┬─────┘                           │   │
            │  │       │ reverse proxy                    │   │
            │  │  ┌────▼─────┐                           │   │
            │  │  │  Odoo    │ ← Port 8069 (interne)    │   │
            │  │  │  17.0    │   2 workers               │   │
            │  │  │  512 Mo  │   custom_addons montés    │   │
            │  │  └────┬─────┘                           │   │
            │  │       │                                  │   │
            │  │  ┌────▼─────┐                           │   │
            │  │  │ Postgres │ ← Port 5432 (interne)    │   │
            │  │  │  15      │   PAS exposé à internet   │   │
            │  │  │  384 Mo  │                           │   │
            │  │  └──────────┘                           │   │
            │  │                                          │   │
            │  │  Réseau: odoo_net (bridge isolé)        │   │
            │  └─────────────────────────────────────────┘   │
            │                                                 │
            │  Volumes Docker:                                │
            │    📁 odoo_db_data  → /var/lib/postgresql/data  │
            │    📁 odoo_web_data → /var/lib/odoo             │
            │                                                 │
            │  Cron:                                          │
            │    🕐 02:00 → backup.sh (BDD + fichiers)       │
            │                                                 │
            └─────────────────────────────────────────────────┘

    Coût total : 0 € (12 premiers mois avec Azure Free Tier)
    Après 12 mois : ~7-10 €/mois (B1s Pay-as-you-go)
```

### Répartition mémoire optimisée (1 Go RAM + 2 Go Swap)

```
┌────────────────────────────────────────────────────┐
│                  1 Go RAM Total                     │
├────────────────┬───────────────┬───────────────────┤
│  PostgreSQL    │    Odoo       │   Nginx + OS      │
│   384 Mo       │    512 Mo     │    128 Mo         │
│   (shared_buf  │   (2 workers  │   (reverse proxy  │
│    128 Mo)     │    limit_mem  │    + cache)       │
│                │    soft=400Mo)│                    │
├────────────────┴───────────────┴───────────────────┤
│               + 2 Go SWAP (SSD)                     │
│   Sert de filet de sécurité quand RAM saturée       │
└────────────────────────────────────────────────────┘
```

---

## 3. Déploiement étape par étape

### Prérequis sur votre PC

```powershell
# Installer Azure CLI (Windows)
winget install Microsoft.AzureCLI

# Vérifier l'installation
az --version

# Se connecter à Azure
az login
```

### Étape 1 : Créer l'infrastructure Azure (CLI)

```bash
# ============================================================
# Variables (à personnaliser)
# ============================================================
RESOURCE_GROUP="rg-odoo-erp"
LOCATION="francecentral"        # ou "westeurope"
VM_NAME="vm-odoo-erp"
VM_SIZE="Standard_B1s"          # Gratuit 12 mois
ADMIN_USER="azureuser"
VM_IMAGE="Canonical:0001-com-ubuntu-server-jammy:22_04-lts-gen2:latest"

# ============================================================
# 1. Créer le groupe de ressources
# ============================================================
az group create \
    --name $RESOURCE_GROUP \
    --location $LOCATION

# ============================================================
# 2. Créer la VM avec ouverture des ports
# ============================================================
az vm create \
    --resource-group $RESOURCE_GROUP \
    --name $VM_NAME \
    --image $VM_IMAGE \
    --size $VM_SIZE \
    --admin-username $ADMIN_USER \
    --generate-ssh-keys \
    --public-ip-sku Standard \
    --os-disk-size-gb 30

# ============================================================
# 3. Ouvrir les ports nécessaires
# ============================================================
az vm open-port --resource-group $RESOURCE_GROUP --name $VM_NAME --port 80 --priority 1001
az vm open-port --resource-group $RESOURCE_GROUP --name $VM_NAME --port 443 --priority 1002
# Port 22 (SSH) est ouvert par défaut

# ============================================================
# 4. Récupérer l'IP publique
# ============================================================
az vm show \
    --resource-group $RESOURCE_GROUP \
    --name $VM_NAME \
    --show-details \
    --query publicIps \
    --output tsv
```

### Étape 2 : Se connecter et déployer

```powershell
# Depuis votre PC Windows (remplacer par votre IP)
ssh azureuser@<VOTRE_IP_AZURE>
```

```bash
# ============================================================
# Sur la VM Azure (connecté en SSH)
# ============================================================

# 1. Cloner votre projet
sudo git clone https://github.com/belhaid2001-glitch/odoo-erp-commercial.git /opt/odoo-erp-commercial
cd /opt/odoo-erp-commercial

# 2. Lancer le script de déploiement automatique
sudo chmod +x deploy/deploy.sh
sudo ./deploy/deploy.sh

# Le script fait tout automatiquement :
#   ✓ Mise à jour Ubuntu
#   ✓ Installation Docker + Docker Compose
#   ✓ Configuration du Swap (2 Go)
#   ✓ Copie de la config de production
#   ✓ Lancement des containers
```

### Étape 3 : Vérifier que tout fonctionne

```bash
# Vérifier les containers
docker ps
# Vous devez voir : odoo_erp_app, odoo_erp_db, odoo_nginx

# Vérifier la mémoire
free -h
# Total ~1 Go + 2 Go Swap

# Vérifier les logs
docker logs odoo_erp_app --tail 20
# Chercher : "HTTP service (werkzeug) running on 0.0.0.0:8069"

# Test rapide
curl -I http://localhost
# Doit retourner : HTTP/1.1 200 OK
```

### Étape 4 : Accéder via URL

Ouvrir dans votre navigateur :
```
http://<VOTRE_IP_AZURE>
```

**Premier accès = création de la base de données :**
- Master Password : `admin_odoo_2026` (défini dans odoo.prod.conf)
- Database Name : `odoo_erp_commercial`
- Email : votre email
- Password : choisir un mot de passe sécurisé
- Language : Français
- Country : Maroc

### Étape 5 (optionnel) : Domaine + HTTPS

```bash
# Option gratuite : sous-domaine via freedns.afraid.org
# 1. Créer un compte sur https://freedns.afraid.org
# 2. Ajouter un sous-domaine (ex: erp-belha.mooo.com)
# 3. Pointer vers votre IP Azure

# Activer SSL
cd /opt/odoo-erp-commercial
sudo ./deploy/setup-ssl.sh erp-belha.mooo.com
```

---

## 4. Erreurs à éviter

### ❌ Erreur 1 : Utiliser App Service Free Tier
**Pourquoi c'est une erreur :**
- Pas de PostgreSQL, pas de Docker Compose, RAM partagée
- Odoo PLANTE après 60 min CPU/jour
- Les fichiers uploadés sont PERDUS au redémarrage

**Solution :** → VM B1s (gratuit aussi, mais c'est une VRAIE machine)

### ❌ Erreur 2 : Exposer PostgreSQL à Internet
**Pourquoi c'est dangereux :**
```yaml
# MAUVAIS - Ne JAMAIS faire ça en production !
db:
  ports:
    - "5432:5432"  # ← Accessible depuis internet !
```
**Solution :** Ne pas mapper le port, utiliser un réseau Docker interne :
```yaml
# CORRECT - PostgreSQL isolé
db:
  # PAS de "ports:" → accessible uniquement par Odoo via odoo_net
  networks:
    - odoo_net
```

### ❌ Erreur 3 : Mot de passe en dur dans docker-compose.yml
**Pourquoi c'est une erreur :**
Si le code est sur GitHub public, tout le monde voit vos mots de passe.

**Solution :** Utiliser un fichier `.env` :
```bash
# Créer /opt/odoo-erp-commercial/.env
DB_PASSWORD=UnVraiMotD3Pass_Secur1se!
ADMIN_PASSWD=M4sterP@ssw0rd_Prod!
```
```yaml
# docker-compose.prod.yml (référence les variables)
environment:
  - POSTGRES_PASSWORD=${DB_PASSWORD}
```
```bash
# .gitignore → JAMAIS commit le .env
echo ".env" >> .gitignore
```

### ❌ Erreur 4 : Oublier le Swap sur B1s
**Pourquoi :** 1 Go RAM est INSUFFISANT pour Odoo + PostgreSQL sans swap.
Odoo sera killed par l'OOM killer après quelques minutes.

**Solution :** Le script `deploy.sh` active déjà 2 Go de swap. Vérifier :
```bash
sudo swapon --show
# NAME      TYPE SIZE USED PRIO
# /swapfile file   2G  0B   -2
```

### ❌ Erreur 5 : Ne pas configurer les limites mémoire Docker
**Pourquoi :** Sans limites, un container peut prendre TOUTE la RAM.

**Solution :** (déjà dans votre docker-compose.prod.yml)
```yaml
deploy:
  resources:
    limits:
      memory: 512M  # Odoo
      memory: 384M  # PostgreSQL  
      memory: 64M   # Nginx
```

### ❌ Erreur 6 : Ignorer les backups
**Pourquoi :** Si la VM crash, vous perdez TOUT.

**Solution :**
```bash
# Backup automatique (déjà dans deploy/backup.sh)
sudo crontab -e
# Ajouter :
0 2 * * * /opt/odoo-erp-commercial/deploy/backup.sh

# + Copier les backups vers Azure Blob Storage (optionnel mais recommandé)
```

### ❌ Erreur 7 : Laisser le port SSH (22) ouvert à tout le monde
**Solution :** Restreindre SSH à votre IP :
```bash
# Dans Azure Portal → VM → Réseau → NSG
# Modifier la règle SSH :
#   Source : "My IP address" (au lieu de "Any")
```

### ❌ Erreur 8 : workers = 0 (mode thread)
**Pourquoi :** En mode thread, Odoo ne gère pas bien la concurrence.
**Solution :** `workers = 2` (déjà dans votre `odoo.prod.conf`)

---

## 5. Architecture avancée (pour scaler)

### Phase 2 : VM B2s + Azure DB for PostgreSQL

```
    Prix : ~30-40€/mois
    Quand : > 10 utilisateurs ou besoin de fiabilité BDD

┌────────────────────────────┐     ┌──────────────────────────┐
│    Azure VM B2s            │     │ Azure Database for       │
│    2 vCPU | 4 Go RAM       │     │ PostgreSQL Flexible      │
│                             │     │                          │
│  ┌──────────┐ ┌──────────┐ │     │  Burstable B1ms          │
│  │  Nginx   │→│  Odoo    │─┼────→│  1 vCPU | 2 Go RAM      │
│  │          │ │  4 work. │ │     │  32 Go stockage          │
│  └──────────┘ └──────────┘ │     │                          │
│                             │     │  ✅ Backups auto (7j)    │
│  + Azure Files (stockage)  │     │  ✅ Haute disponibilité  │
│  pour les pièces jointes   │     │  ✅ Monitoring intégré   │
└────────────────────────────┘     └──────────────────────────┘
         │                                    │
         └──── Azure VNet (réseau privé) ─────┘
              10.0.0.0/16
              Subnet VM:  10.0.1.0/24
              Subnet DB:  10.0.2.0/24
```

**Migration depuis Phase 1 :**
```bash
# 1. Exporter la BDD
docker exec odoo_erp_db pg_dump -U odoo odoo_erp_commercial > dump.sql

# 2. Créer Azure DB for PostgreSQL (CLI)
az postgres flexible-server create \
    --resource-group rg-odoo-erp \
    --name odoo-pg-server \
    --location francecentral \
    --admin-user odooadmin \
    --admin-password 'Sup3rS3cure!Pass#2026' \
    --sku-name Standard_B1ms \
    --tier Burstable \
    --storage-size 32 \
    --version 15

# 3. Importer
psql "host=odoo-pg-server.postgres.database.azure.com \
      dbname=odoo_erp_commercial user=odooadmin \
      password='Sup3rS3cure!Pass#2026' sslmode=require" < dump.sql

# 4. Modifier docker-compose → pointer vers Azure DB
# HOST=odoo-pg-server.postgres.database.azure.com
# + Supprimer le container PostgreSQL local
```

### Phase 3 : AKS (Kubernetes) pour l'entreprise

```
    Prix : ~100-200€/mois
    Quand : > 50 utilisateurs, SLA requis, multi-instances

┌─────────────────────────────────────────────────────────────┐
│                Azure Kubernetes Service (AKS)                │
│                                                              │
│  ┌─────────────────────────────────────────┐                │
│  │         Ingress Controller               │                │
│  │         (Nginx + cert-manager)           │                │
│  │         SSL automatique Let's Encrypt    │                │
│  └───────────┬─────────────┬───────────────┘                │
│              │             │                                 │
│  ┌───────────▼──┐ ┌───────▼────────┐                       │
│  │  Odoo Pod 1  │ │  Odoo Pod 2    │  ← HPA auto-scale    │
│  │  (Deployment)│ │  (Deployment)  │     min:2 max:5       │
│  │  CPU: 500m   │ │  CPU: 500m     │                       │
│  │  RAM: 1Gi    │ │  RAM: 1Gi      │                       │
│  └──────┬───────┘ └──────┬─────────┘                       │
│         │                │                                   │
│  ┌──────▼────────────────▼─────────┐                       │
│  │    ClusterIP Service            │                       │
│  │    (load balancing interne)     │                       │
│  └──────────────┬──────────────────┘                       │
│                 │                                            │
│  Node Pool: Standard_B2s (2 vCPU, 4 Go RAM) × 2 nœuds     │
└─────────────────┼──────────────────────────────────────────┘
                  │
    ┌─────────────▼──────────────┐  ┌─────────────────────┐
    │ Azure DB for PostgreSQL    │  │ Azure Blob Storage   │
    │ General Purpose D2s        │  │ (filestore Odoo)     │
    │ HA activé (zone-redundant) │  │ Hot tier             │
    └────────────────────────────┘  └─────────────────────┘
```

**Fichiers Kubernetes (pour plus tard) :**
```yaml
# k8s/odoo-deployment.yaml (exemple)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: odoo
spec:
  replicas: 2
  selector:
    matchLabels:
      app: odoo
  template:
    metadata:
      labels:
        app: odoo
    spec:
      containers:
      - name: odoo
        image: odoo:17.0
        ports:
        - containerPort: 8069
        env:
        - name: HOST
          value: "odoo-pg-server.postgres.database.azure.com"
        - name: USER
          valueFrom:
            secretKeyRef:
              name: odoo-db-credentials
              key: username
        - name: PASSWORD
          valueFrom:
            secretKeyRef:
              name: odoo-db-credentials
              key: password
        resources:
          requests:
            cpu: "250m"
            memory: "512Mi"
          limits:
            cpu: "500m"
            memory: "1Gi"
        volumeMounts:
        - name: odoo-data
          mountPath: /var/lib/odoo
        - name: custom-addons
          mountPath: /mnt/extra-addons
      volumes:
      - name: odoo-data
        persistentVolumeClaim:
          claimName: odoo-filestore-pvc
      - name: custom-addons
        configMap:
          name: odoo-custom-addons
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: odoo-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: odoo
  minReplicas: 2
  maxReplicas: 5
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

### Résumé des phases et coûts

```
┌─────────┬────────────────────────┬──────────────┬──────────────────┐
│  Phase  │   Architecture         │  Coût/mois   │  Utilisateurs    │
├─────────┼────────────────────────┼──────────────┼──────────────────┤
│    1    │ VM B1s + Docker        │ 0€ (12 mois) │  1-10            │
│  (now)  │ PG local + Nginx       │ puis ~8€     │                  │
├─────────┼────────────────────────┼──────────────┼──────────────────┤
│    2    │ VM B2s + Azure DB PG   │ ~30-40€      │  10-50           │
│         │ + Azure Files          │              │                  │
├─────────┼────────────────────────┼──────────────┼──────────────────┤
│    3    │ AKS + Azure DB PG HA   │ ~100-200€    │  50-500          │
│         │ + Blob Storage         │              │                  │
│         │ + HPA auto-scale       │              │                  │
└─────────┴────────────────────────┴──────────────┴──────────────────┘
```

---

## Annexe A : Checklist de sécurité

- [ ] Mots de passe dans `.env` (jamais en dur dans le code)
- [ ] `.env` dans `.gitignore`
- [ ] PostgreSQL NON exposé sur internet (pas de port mapping)
- [ ] SSH restreint à votre IP dans le NSG
- [ ] `list_db = False` dans odoo.conf (empêche de lister les BDD)
- [ ] `admin_passwd` changé (pas la valeur par défaut)
- [ ] HTTPS activé (Let's Encrypt)
- [ ] Backups automatiques (cron + backup.sh)
- [ ] Firewall UFW activé sur la VM
- [ ] Mises à jour automatiques Ubuntu (`unattended-upgrades`)

## Annexe B : Commandes de monitoring utiles

```bash
# Utilisation mémoire par container
docker stats --no-stream

# Espace disque
df -h

# Logs Odoo (dernières erreurs)
docker logs odoo_erp_app --tail 50 2>&1 | grep -i error

# Logs PostgreSQL
docker logs odoo_erp_db --tail 50

# Tester la connectivité BDD
docker exec odoo_erp_db pg_isready -U odoo

# Vérifier le swap
swapon --show && free -h

# Performance réseau
curl -o /dev/null -s -w "Time: %{time_total}s\n" http://localhost
```

## Annexe C : Automatiser le déploiement avec Azure CLI

Le script `deploy/azure-deploy.sh` (créé avec ce guide) permet de tout
déployer en une commande. Voir le fichier pour les détails.
