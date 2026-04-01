#!/bin/bash
# ================================================================
# Configuration SSL avec Let's Encrypt (certificat gratuit)
# ================================================================
# Usage: sudo ./setup-ssl.sh votre-domaine.com
# ================================================================

if [ -z "$1" ]; then
    echo "Usage: sudo ./setup-ssl.sh votre-domaine.com"
    exit 1
fi

DOMAIN=$1
EMAIL="admin@$DOMAIN"
PROJECT_DIR="/opt/odoo-erp-commercial"

echo "Configuration SSL pour $DOMAIN..."

# 1. Obtenir le certificat
docker run --rm \
    -v $PROJECT_DIR/deploy/certbot/conf:/etc/letsencrypt \
    -v $PROJECT_DIR/deploy/certbot/www:/var/www/certbot \
    -p 80:80 \
    certbot/certbot certonly \
    --standalone \
    --non-interactive \
    --agree-tos \
    --email $EMAIL \
    -d $DOMAIN

# 2. Mettre à jour la config Nginx
cd $PROJECT_DIR
sed -i "s/VOTRE_DOMAINE.com/$DOMAIN/g" deploy/nginx.conf
sed -i 's/# listen 443 ssl;/listen 443 ssl;/' deploy/nginx.conf
sed -i 's/# ssl_certificate /ssl_certificate /' deploy/nginx.conf
sed -i 's/# ssl_certificate_key /ssl_certificate_key /' deploy/nginx.conf
sed -i 's/server_name _;/server_name '"$DOMAIN"';/' deploy/nginx.conf

# 3. Activer la redirection HTTP → HTTPS
sed -i '/# server {/,/# }/s/# //' deploy/nginx.conf

# 4. Redémarrer
docker compose -f deploy/docker-compose.prod.yml restart nginx

echo ""
echo "SSL activé ! Votre ERP est maintenant accessible sur :"
echo "  https://$DOMAIN"
echo ""
echo "Le certificat se renouvelle automatiquement."
