# 🏢 ERP Commercial Odoo 17

> **12 modules personnalisés** · **16 rapports PDF** · **202 tests E2E** · **Pipeline CI/CD** · **Docker**

ERP commercial complet basé sur **Odoo 17 Community**, conteneurisé avec Docker. Conçu pour les entreprises marocaines avec des champs spécifiques (ICE, RC, IF, CNSS).

---

## 📦 Modules inclus (12)

| # | Module | Description |
|---|--------|-------------|
| 1 | `custom_sale` | **Vente** — Devis, commandes, priorité, workflow d'approbation, suivi des marges |
| 2 | `custom_purchase` | **Achat** — Commandes fournisseurs, conventions d'achat, contrôle qualité |
| 3 | `custom_stock` | **Stock** — Préparation, livraisons, contrôle qualité, statut de préparation |
| 4 | `custom_accounting` | **Comptabilité** — Factures, gestion de chèques, relances de paiement |
| 5 | `custom_hr` | **RH** — Employés Maroc (CNSS, mutuelle), système d'évaluation |
| 6 | `custom_crm` | **CRM** — Scoring de leads, suivi concurrents, gestion d'activités |
| 7 | `custom_calendar` | **Calendrier** — Types d'événements, PV de réunion, suivi des actions |
| 8 | `custom_contacts` | **Contacts** — Champs Maroc (ICE, RC, IF, CNSS), segmentation |
| 9 | `custom_documents` | **Documents** — GED avec versioning, expiration, catégories |
| 10 | `custom_discuss` | **Discussion** — Templates email personnalisés avec catégories |
| 11 | `custom_dashboard` | **Tableau de bord** — KPIs, catégories, analytique |
| 12 | `custom_ai` | **IA** — Assistance intelligente intégrée |

---

## 📊 Rapports PDF (16)

Chaque module dispose de rapports QWeb PDF accessibles via le menu **📊 Rapports** :
sélectionnez les enregistrements dans la vue liste, puis **Imprimer → PDF**.

- Bons de commande vente & prévisions
- Commandes d'achat & conventions
- Bons de livraison & contrôles qualité stock
- Factures & avoirs comptables
- Fiches employés & évaluations RH
- Fiches leads CRM, contacts, événements calendrier
- Documents, templates discussion, KPIs tableau de bord

---

## 🧪 Tests

- **202 tests E2E** couvrant les 12 modules (0 échecs)
- **Tests Playwright** pour l'interface utilisateur
- **Pipeline CI/CD** via GitHub Actions

```bash
# Lancer les tests
./run_tests.ps1        # Windows
./run_tests.sh         # Linux/Mac
```

---

## 🚀 Installation

### Prérequis
- Docker & Docker Compose

### Démarrage

```bash
git clone https://github.com/belhaid2001-glitch/odoo-erp-commercial.git
cd odoo-erp-commercial
docker-compose up -d
```

Accédez à Odoo sur : **http://localhost:8069**

### Configuration initiale

1. Créez la base de données `odoo_erp_commercial`
2. Login : `admin` / `admin`
3. Allez dans **Apps** et installez les modules `custom_*`

---

## 🏗️ Architecture

```
odoo-erp-commercial/
├── config/                  # Configuration Odoo
├── custom_addons/           # 12 modules personnalisés
│   ├── custom_sale/
│   ├── custom_purchase/
│   ├── custom_stock/
│   ├── custom_accounting/
│   ├── custom_hr/
│   ├── custom_crm/
│   ├── custom_calendar/
│   ├── custom_contacts/
│   ├── custom_documents/
│   ├── custom_discuss/
│   ├── custom_dashboard/
│   ├── custom_ai/
│   └── tests/               # 202 tests E2E
├── docs/                    # Documentation modules
├── .github/workflows/       # CI/CD pipeline
├── docker-compose.yml
└── README.md
```

---

## 🛠️ Stack technique

| Composant | Version |
|-----------|---------|
| Odoo | 17.0 Community |
| Python | 3.10+ |
| PostgreSQL | 15 |
| Docker | Compose v2 |
| Tests | Pytest + Playwright |
| CI/CD | GitHub Actions |

---

## 📚 Documentation

- [Module 1 — Vente](docs/MODULE_1_VENTE.md)
- [Module 2 — Achat](docs/MODULE_2_ACHAT.md)
- [Module 3 — Stock](docs/MODULE_3_STOCK.md)
- [Module 4 — Comptabilité](docs/MODULE_4_COMPTABILITE.md)
- [Module 5 — RH](docs/MODULE_5_RH.md)

---

## 👤 Auteur

**N.BELHAID** — [belhaid2001-glitch](https://github.com/belhaid2001-glitch)

---

*Projet ERP Commercial — Odoo 17 | 2024-2026*
