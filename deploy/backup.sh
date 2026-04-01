#!/bin/bash
# ================================================================
# Backup automatique de la base de données Odoo
# ================================================================
# Ajouter au cron : crontab -e
# 0 2 * * * /opt/odoo-erp-commercial/deploy/backup.sh
# ================================================================

BACKUP_DIR="/opt/odoo-erp-commercial/backups"
DATE=$(date +%Y%m%d_%H%M%S)
KEEP_DAYS=7

mkdir -p $BACKUP_DIR

echo "Backup de la base de données..."
docker exec odoo_erp_db pg_dump -U odoo odoo_erp_commercial | gzip > $BACKUP_DIR/db_$DATE.sql.gz

echo "Backup des fichiers Odoo..."
docker cp odoo_erp_app:/var/lib/odoo/filestore $BACKUP_DIR/filestore_$DATE
tar czf $BACKUP_DIR/filestore_$DATE.tar.gz -C $BACKUP_DIR filestore_$DATE
rm -rf $BACKUP_DIR/filestore_$DATE

# Supprimer les backups de plus de 7 jours
find $BACKUP_DIR -name "*.gz" -mtime +$KEEP_DAYS -delete

echo "Backup terminé : $BACKUP_DIR/db_$DATE.sql.gz"
ls -lh $BACKUP_DIR/*.gz | tail -5
