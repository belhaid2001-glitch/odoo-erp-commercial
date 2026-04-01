# 🚀 Guide de Déploiement Azure - ERP Commercial

## Prérequis
- Un compte Microsoft (Outlook, Hotmail, ou professionnel)
- Une carte bancaire (VISA/Mastercard) — **aucun débit**, juste pour vérification

---

## Étape 1 : Créer un compte Azure gratuit

1. Aller sur **https://azure.microsoft.com/fr-fr/free/**
2. Cliquer **"Commencez gratuitement"**
3. Se connecter avec votre compte Microsoft
4. Remplir : nom, téléphone, carte bancaire
5. **Vous recevez 200$ de crédit + 12 mois de services gratuits**

---

## Étape 2 : Créer une Machine Virtuelle (VM)

1. Dans le portail Azure (https://portal.azure.com) :
   - Chercher **"Machines virtuelles"** → **"Créer"**

2. **Paramètres de base :**
   | Champ | Valeur |
   |-------|--------|
   | Abonnement | Azure subscription 1 |
   | Groupe de ressources | Créer → `erp-commercial-rg` |
   | Nom de la VM | `erp-odoo-vm` |
   | Région | **(Europe) France Central** ou **West Europe** |
   | Image | **Ubuntu Server 22.04 LTS** |
   | Taille | **Standard_B1s** (1 vCPU, 1 Go RAM) — **GRATUIT 12 mois** |
   | Authentification | **Clé SSH** (recommandé) ou mot de passe |
   | Nom d'utilisateur | `azureuser` |

3. **Disques :** Garder par défaut (30 Go SSD)

4. **Réseau :**
   - Ports entrants publics : **Autoriser les ports sélectionnés**
   - Cocher : **HTTP (80), HTTPS (443), SSH (22)**

5. **Vérifier et créer** → **Créer** → Télécharger la clé SSH

---

## Étape 3 : Se connecter à la VM

### Depuis Windows (PowerShell) :

```powershell
# Avec clé SSH :
ssh -i C:\Users\VOTRE_USER\Downloads\erp-odoo-vm_key.pem azureuser@VOTRE_IP_AZURE

# Avec mot de passe :
ssh azureuser@VOTRE_IP_AZURE
```

> **Trouver l'IP :** Azure Portal → Machines virtuelles → erp-odoo-vm → **Adresse IP publique**

---

## Étape 4 : Déployer l'application (1 commande !)

Une fois connecté en SSH :

```bash
# Télécharger et exécuter le script de déploiement
git clone https://github.com/belhaid2001-glitch/odoo-erp-commercial.git /opt/odoo-erp-commercial
cd /opt/odoo-erp-commercial
chmod +x deploy/deploy.sh
sudo ./deploy/deploy.sh
```

**C'est tout !** Après 2-3 minutes, l'application est accessible sur :

```
http://VOTRE_IP_AZURE
```

---

## Étape 5 (optionnel) : Ajouter un nom de domaine + HTTPS

### Option A : Domaine gratuit (freenom / afraid.org)
1. Aller sur https://freedns.afraid.org/
2. Créer un sous-domaine gratuit (ex: `erp-commercial.mooo.com`)
3. Pointer vers votre IP Azure

### Option B : Domaine payant (~10 DH/an)
1. Acheter un domaine `.ma` sur https://www.genious.ma/ ou `.com` sur Namecheap
2. Dans les DNS, ajouter un enregistrement A : `@` → `VOTRE_IP_AZURE`

### Activer HTTPS (certificat gratuit Let's Encrypt) :
```bash
cd /opt/odoo-erp-commercial
sudo chmod +x deploy/setup-ssl.sh
sudo ./deploy/setup-ssl.sh votre-domaine.com
```

---

## Étape 6 : Configurer les backups automatiques

```bash
# Rendre le script exécutable
chmod +x /opt/odoo-erp-commercial/deploy/backup.sh

# Ajouter au cron (backup chaque nuit à 2h)
sudo crontab -e
# Ajouter cette ligne :
0 2 * * * /opt/odoo-erp-commercial/deploy/backup.sh
```

---

## Commandes utiles

```bash
# Voir les logs Odoo
docker logs -f odoo_erp_app

# Redémarrer l'application
cd /opt/odoo-erp-commercial
docker compose -f deploy/docker-compose.prod.yml restart

# Mettre à jour l'application (après un git push)
cd /opt/odoo-erp-commercial
git pull origin main
docker compose -f deploy/docker-compose.prod.yml restart odoo

# Voir l'état des containers
docker ps

# Voir l'utilisation mémoire
free -h
htop
```

---

## Résumé des coûts

| Service | Coût |
|---------|------|
| VM Azure B1s (12 mois) | **0 €** |
| Certificat SSL (Let's Encrypt) | **0 €** |
| Domaine .com (optionnel) | ~10 €/an |
| **Total** | **0 €** (sans domaine) |

---

## En cas de problème

| Problème | Solution |
|----------|----------|
| Odoo très lent | Le swap est activé ? `sudo swapon --show` |
| Page blanche | `docker logs odoo_erp_app` pour voir l'erreur |
| Impossible de se connecter | Vérifier les ports dans Azure → Réseau → NSG |
| Plus de mémoire | `docker stats` pour voir la consommation |
