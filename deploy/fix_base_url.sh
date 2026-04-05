#!/bin/bash
# Fix web.base.url to use HTTPS domain
# Also set up SSL cert renewal cron

DOMAIN="erp-btp-maroc.swedencentral.cloudapp.azure.com"
HTTPS_URL="https://${DOMAIN}"

# Update web.base.url in Odoo database
docker exec odoo_erp_db psql -U odoo -d odoo_erp_commercial -c \
  "UPDATE ir_config_parameter SET value = '${HTTPS_URL}' WHERE key = 'web.base.url';"

docker exec odoo_erp_db psql -U odoo -d odoo_erp_commercial -c \
  "UPDATE ir_config_parameter SET value = 'True' WHERE key = 'web.base.url.freeze';"

# Verify
echo "=== web.base.url ==="
docker exec odoo_erp_db psql -U odoo -d odoo_erp_commercial -t -A -c \
  "SELECT key || ' = ' || value FROM ir_config_parameter WHERE key LIKE 'web.base%';"

# Setup cron for SSL renewal
CRON_CMD="0 3 * * * certbot renew --quiet --deploy-hook 'cp -L /etc/letsencrypt/live/${DOMAIN}/fullchain.pem /opt/odoo-erp-commercial/deploy/certbot/conf/live/${DOMAIN}/ && cp -L /etc/letsencrypt/live/${DOMAIN}/privkey.pem /opt/odoo-erp-commercial/deploy/certbot/conf/live/${DOMAIN}/ && docker restart odoo_nginx'"

# Add to crontab
(crontab -l 2>/dev/null | grep -v certbot; echo "$CRON_CMD") | crontab -
echo "=== Crontab ==="
crontab -l

# Restart Odoo to pick up new base URL
docker restart odoo_erp_app
sleep 5

# Test
echo "=== Test HTTPS ==="
curl -sI "https://${DOMAIN}" 2>&1 | grep -i location
echo "DONE"
