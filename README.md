# Custom Odoo ERP Commercial Modules

Ce projet contient les modules personnalisés pour l'ERP Odoo Commercial.

## Modules inclus

| Module | Description |
|--------|-------------|
| `custom_sale` | Vente - Gestion des devis, commandes, facturation, portail client |
| `custom_purchase` | Achat - Demandes de prix, réapprovisionnement, conventions |
| `custom_stock` | Stock/Inventaire - Livraisons, codes-barres, lots, qualité |
| `custom_accounting` | Comptabilité/Facturation - Factures, rapprochement, analytique |
| `custom_hr` | Ressources Humaines - Employés, contrats, congés, recrutement |

## Installation

```bash
docker-compose up -d
```

Accédez à Odoo sur : http://localhost:8069

## Configuration initiale

1. Créez la base de données `odoo_erp_commercial`
2. Installez les modules depuis Apps
3. Configurez selon les besoins du client
