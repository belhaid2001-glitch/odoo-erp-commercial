# Module custom_btp — Gestion Complète des Chantiers BTP Maroc

## Description

Module Odoo 17 pour la gestion complète des chantiers BTP (Bâtiment et Travaux Publics) adapté au contexte réglementaire et fiscal marocain.

## Fonctionnalités

### 1. Gestion des Chantiers
- Cycle de vie complet : Étude → Préparation → En cours → Réception → Garantie → Clôture
- Suivi budgétaire par lot en temps réel
- Tâches hiérarchiques avec dépendances
- Calcul automatique de l'avancement global
- Révision des prix (formule BT)

### 2. Ressources Humaines Chantier  
- Registre du personnel (obligatoire — Inspection du Travail)
- Pointage journalier avec géolocalisation
- Calcul automatique heures supplémentaires selon Code du Travail marocain
- Taux SMIG : 17.25 DH/h (mise à jour sept 2024)

### 3. Engins & Maintenance
- Suivi du parc engins avec état et consommation
- Alertes assurance et visite technique (30 jours avant expiration)
- Maintenance préventive et corrective

### 4. Financier
- Situations de travaux avec cumuls progressifs
- TVA marocaine (20% / 14%)
- Retenue de garantie
- Pénalités de retard
- Génération automatique de factures Odoo

### 5. Sous-traitance
- Gestion des sous-traitants avec documents légaux
- Vérification conformité (RC, Patente, IF, ICE, CNSS)

### 6. Réceptions
- PV de réception provisoire et définitive
- Gestion des réserves avec suivi de levée

### 7. Documents
- 16 types de documents BTP marocains
- Alertes d'expiration automatiques

### 8. Rapports PDF
- Situation de travaux (format standard marocain)
- Attachement / Décompte quantitatif
- PV de réception
- Registre du personnel chantier
- Fiche de pointage hebdomadaire
- Bordereau CNSS (format DUE)

### 9. API REST
- `POST /api/btp/pointage` — Enregistrement depuis application mobile
- `GET /api/btp/chantier/<id>/dashboard` — KPI chantier en JSON

### 10. Wizards
- Génération de situation de travaux (avec reprise cumuls)
- Export CNSS format DUE (fichier texte à positions fixes)
- Clôture chantier (vérifications automatiques)

## Groupes de sécurité

| Groupe | Description |
|--------|-------------|
| Compagnon | Accès limité aux pointages |
| Chef de Chantier | Gestion complète du chantier assigné |
| Directeur BTP | Accès complet à tous les chantiers |

## Installation

1. Copier le dossier `custom_btp` dans le répertoire `custom_addons`
2. Mettre à jour la liste des modules : `Apps → Mettre à jour la liste des applications`
3. Installer le module : chercher "BTP Chantiers"

## Dépendances

- `base`, `project`, `hr`, `purchase`, `account`, `maintenance`, `mail`

## Configuration API

Pour activer l'API REST, définir le paramètre système :
- Clé : `btp.api_token`
- Valeur : votre token d'authentification

## Auteur

**ERP Commercial** — Module développé pour la gestion BTP au Maroc.

## Licence

LGPL-3
