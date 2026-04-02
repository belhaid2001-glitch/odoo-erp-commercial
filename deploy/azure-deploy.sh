#!/bin/bash
# ================================================================
# Script de déploiement complet sur Azure (Infrastructure + App)
# ================================================================
# Usage: chmod +x azure-deploy.sh && ./azure-deploy.sh
# Prérequis: Azure CLI installé (az login effectué)
# ================================================================

set -e

# ============================================================
# CONFIGURATION (modifier selon vos besoins)
# ============================================================
RESOURCE_GROUP="rg-odoo-erp"
LOCATION="francecentral"
VM_NAME="vm-odoo-erp"
VM_SIZE="Standard_B1s"
ADMIN_USER="azureuser"
VM_IMAGE="Canonical:0001-com-ubuntu-server-jammy:22_04-lts-gen2:latest"
GITHUB_REPO="https://github.com/belhaid2001-glitch/odoo-erp-commercial.git"

echo "=========================================="
echo " Déploiement Azure - Odoo ERP Commercial"
echo "=========================================="
echo ""
echo " Région        : $LOCATION"
echo " Taille VM     : $VM_SIZE"
echo " Utilisateur   : $ADMIN_USER"
echo ""

# ============================================================
# 1. Vérifier la connexion Azure
# ============================================================
echo "[1/6] Vérification de la connexion Azure..."
if ! az account show &> /dev/null; then
    echo "Vous n'êtes pas connecté. Lancement de az login..."
    az login
fi
SUBSCRIPTION=$(az account show --query name -o tsv)
echo "  → Abonnement actif : $SUBSCRIPTION"

# ============================================================
# 2. Créer le groupe de ressources
# ============================================================
echo "[2/6] Création du groupe de ressources..."
az group create \
    --name $RESOURCE_GROUP \
    --location $LOCATION \
    --output none
echo "  → Groupe '$RESOURCE_GROUP' créé dans '$LOCATION'"

# ============================================================
# 3. Créer la Machine Virtuelle
# ============================================================
echo "[3/6] Création de la VM (cela peut prendre 2-3 minutes)..."
VM_OUTPUT=$(az vm create \
    --resource-group $RESOURCE_GROUP \
    --name $VM_NAME \
    --image "$VM_IMAGE" \
    --size $VM_SIZE \
    --admin-username $ADMIN_USER \
    --generate-ssh-keys \
    --public-ip-sku Standard \
    --os-disk-size-gb 30 \
    --output json)

PUBLIC_IP=$(echo $VM_OUTPUT | python3 -c "import sys,json; print(json.load(sys.stdin)['publicIpAddress'])" 2>/dev/null || \
    az vm show --resource-group $RESOURCE_GROUP --name $VM_NAME --show-details --query publicIps -o tsv)

echo "  → VM '$VM_NAME' créée"
echo "  → IP publique : $PUBLIC_IP"

# ============================================================
# 4. Ouvrir les ports (HTTP, HTTPS)
# ============================================================
echo "[4/6] Ouverture des ports 80 et 443..."
az vm open-port \
    --resource-group $RESOURCE_GROUP \
    --name $VM_NAME \
    --port 80 \
    --priority 1001 \
    --output none

az vm open-port \
    --resource-group $RESOURCE_GROUP \
    --name $VM_NAME \
    --port 443 \
    --priority 1002 \
    --output none
echo "  → Ports 80 (HTTP) et 443 (HTTPS) ouverts"

# ============================================================
# 5. Déployer l'application sur la VM
# ============================================================
echo "[5/6] Déploiement de l'application sur la VM..."
echo "  → Attente du démarrage SSH (30 secondes)..."
sleep 30

# Exécuter le déploiement via SSH
az vm run-command invoke \
    --resource-group $RESOURCE_GROUP \
    --name $VM_NAME \
    --command-id RunShellScript \
    --scripts "
        # Installer Git
        apt-get update && apt-get install -y git

        # Cloner le projet
        if [ -d /opt/odoo-erp-commercial ]; then
            cd /opt/odoo-erp-commercial && git pull origin main
        else
            git clone $GITHUB_REPO /opt/odoo-erp-commercial
        fi

        # Lancer le déploiement
        cd /opt/odoo-erp-commercial
        chmod +x deploy/deploy.sh
        ./deploy/deploy.sh
    " \
    --output none

echo "  → Application déployée !"

# ============================================================
# 6. Résumé final
# ============================================================
echo ""
echo "=========================================="
echo " DÉPLOIEMENT AZURE TERMINÉ !"
echo "=========================================="
echo ""
echo " Accéder à l'application :"
echo "   http://$PUBLIC_IP"
echo ""
echo " Se connecter en SSH :"
echo "   ssh $ADMIN_USER@$PUBLIC_IP"
echo ""
echo " Premier accès Odoo :"
echo "   Master Password : admin_odoo_2026"
echo "   Database Name   : odoo_erp_commercial"
echo ""
echo " Prochaines étapes :"
echo "   1. Configurer un domaine (optionnel)"
echo "   2. Activer HTTPS : sudo ./deploy/setup-ssl.sh votre-domaine.com"
echo "   3. Configurer les backups : sudo crontab -e"
echo ""
echo "=========================================="
