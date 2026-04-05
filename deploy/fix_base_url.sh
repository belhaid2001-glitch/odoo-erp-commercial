#!/bin/bash
# Fix web.base.url to use HTTPS domain
# Also set up SSL cert renewal cron

DOMAIN="erp-btp-maroc.swedencentral.cloudapp.azure.com"
HTTPS_URL="https://${DOMAIN}"

# Write SQL to temp file to avoid quoting issues
cat > /tmp/fix_base_url.sql << 'EOSQL'
UPDATE ir_config_parameter SET value = 'https://erp-btp-maroc.swedencentral.cloudapp.azure.com' WHERE key = 'web.base.url';
INSERT INTO ir_config_parameter (key, value, create_uid, create_date, write_uid, write_date)
  VALUES ('web.base.url.freeze', 'True', 1, now(), 1, now())
  ON CONFLICT (key) DO UPDATE SET value = 'True', write_date = now();
EOSQL

# Copy SQL file into DB container and execute
docker cp /tmp/fix_base_url.sql odoo_erp_db:/tmp/fix_base_url.sql
docker exec odoo_erp_db psql -U odoo -d odoo_erp_commercial -f /tmp/fix_base_url.sql

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
