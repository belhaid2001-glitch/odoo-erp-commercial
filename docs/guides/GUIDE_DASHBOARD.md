# 📈 Guide Utilisateur — Module Tableau de Bord

> **Public cible** : Managers, Direction générale, Responsables de département
> **Accès** : Menu principal → **Tableaux de Bord**

---

## 📋 Sommaire

1. [Présentation du module](#1--présentation-du-module)
2. [Vue d'ensemble (Dashboard principal)](#2--vue-densemble)
3. [KPIs en temps réel](#3--kpis-en-temps-réel)
4. [Graphiques et tendances](#4--graphiques-et-tendances)
5. [Système d'alertes](#5--système-dalertes)
6. [Vues détaillées par département](#6--vues-détaillées-par-département)
7. [Configurer les KPIs](#7--configurer-les-kpis)
8. [Imprimer les rapports PDF](#8--imprimer-les-rapports-pdf)
9. [FAQ & Astuces](#9--faq--astuces)

---

## 1. 📌 Présentation du module

Le module **Tableau de Bord** est le cockpit de l'entreprise :

```
Données en temps réel → KPIs → Graphiques → Alertes → Décisions
```

**Fonctionnalités clés :**
- **Vue d'ensemble** style Power BI / cockpit
- **KPIs en temps réel** sur tous les modules (Vente, Achat, Stock, Comptabilité, RH, CRM)
- **4 graphiques** : revenus vs dépenses, ventes par type, opérations stock, pipeline CRM
- **Système d'alertes** automatique (factures en retard, livraisons, leads chauds)
- **Navigation drill-down** : cliquer sur un KPI ouvre la vue détaillée

---

## 2. 🖥️ Vue d'ensemble

### Accéder au dashboard

1. **Aller dans** : Tableaux de Bord → **Vue d'ensemble**
2. Le dashboard se charge avec toutes les données en temps réel

### Organisation de l'écran

Le dashboard est divisé en **sections** :

```
┌─────────────────────────────────────────────────────┐
│  📊 KPIs VENTES        │  📊 KPIs ACHATS           │
│  CA du mois + tendance  │  Total achats + tendance  │
│  Nb commandes           │  Demandes de prix         │
│  Devis en cours         │                           │
│  À facturer             │                           │
├─────────────────────────┼───────────────────────────┤
│  📊 KPIs COMPTABILITÉ  │  📊 KPIs STOCK            │
│  Factures impayées      │  Livraisons en attente    │
│  Factures en retard     │  Réceptions en attente    │
│                         │  Opérations en retard     │
├─────────────────────────┼───────────────────────────┤
│  📊 KPIs CRM           │  📊 KPIs RH               │
│  Pipeline en valeur     │  Nb employés              │
│  Opportunités ouvertes  │                           │
│  Leads chauds           │                           │
├─────────────────────────────────────────────────────┤
│  📈 GRAPHIQUES (revenus, ventes par type, stock,    │
│     pipeline CRM)                                    │
├─────────────────────────────────────────────────────┤
│  ⚠️ ALERTES                                         │
└─────────────────────────────────────────────────────┘
```

---

## 3. 📊 KPIs en temps réel

### KPIs Ventes

| KPI | Description | Comment l'interpréter |
|-----|-------------|----------------------|
| **CA du mois** | Chiffre d'affaires des commandes confirmées ce mois | Comparer avec l'objectif mensuel |
| **Tendance** | Évolution vs mois précédent | ↑ Vert = croissance, ↓ Rouge = baisse |
| **Nombre de commandes** | Commandes confirmées ce mois | Volume d'activité commerciale |
| **Devis en cours** | Devis non encore confirmés | Pipeline court terme |
| **À facturer** | Commandes livrées non facturées | Action requise (facturer) |

### KPIs Achats

| KPI | Description | Comment l'interpréter |
|-----|-------------|----------------------|
| **Total achats** | Montant des achats ce mois | Surveiller les dépenses |
| **Tendance** | Évolution vs mois précédent | Maîtrise des coûts |
| **Demandes de prix** | RFQ en attente de confirmation | Achats en négociation |

### KPIs Comptabilité

| KPI | Description | Comment l'interpréter |
|-----|-------------|----------------------|
| **Factures impayées** | Montant total des factures clients non réglées | Trésorerie attendue |
| **Factures en retard** | Factures dépassant l'échéance | ⚠️ Action urgente |

### KPIs Stock

| KPI | Description | Comment l'interpréter |
|-----|-------------|----------------------|
| **Livraisons en attente** | Bons de livraison non traités | Charge logistique |
| **Réceptions en attente** | Réceptions fournisseur à traiter | Marchandises attendues |
| **Opérations en retard** | Transferts dépassant la date prévue | ⚠️ Urgence logistique |

### KPIs CRM

| KPI | Description | Comment l'interpréter |
|-----|-------------|----------------------|
| **Valeur pipeline** | Montant total pondéré des opportunités | CA potentiel |
| **Opportunités ouvertes** | Nombre de leads actifs | Charge commerciale |
| **Leads chauds** | Leads avec probabilité ≥ 50% | Affaires à conclure rapidement |

---

## 4. 📈 Graphiques et tendances

### 4 graphiques principaux

| Graphique | Type | Ce qu'il montre |
|-----------|------|-----------------|
| **Revenus vs Dépenses** | Barres (6 mois) | Évolution mensuelle du CA et des achats |
| **Ventes par type** | Donut | Répartition Standard / Abonnement / Projet |
| **Opérations Stock** | Barres | Livraisons vs Réceptions vs Internes |
| **Pipeline CRM par étape** | Barres horizontales | Valeur par étape du pipeline |

### Lire les graphiques

**Revenus vs Dépenses** :
- Barres bleues = revenus (ventes)
- Barres rouges = dépenses (achats)
- L'écart = marge brute approximative

**Ventes par type** :
- Si "Standard" domine → activité ponctuelle
- Si "Abonnement" grandit → revenus récurrents (bon signe)

**Pipeline CRM** :
- Plus les premières étapes sont chargées → bon remplissage
- Si "Négociation" est vide → gap futur de conversion

---

## 5. ⚠️ Système d'alertes

Le dashboard affiche des **alertes automatiques** en bas de page :

| Alerte | Déclencheur | Action recommandée |
|--------|------------|-------------------|
| 🔴 **Factures en retard** | Factures clients dépassant l'échéance | Relancer immédiatement |
| 🟠 **Opérations en retard** | Livraisons/réceptions dépassant la date | Traiter en priorité |
| 🟡 **Leads chauds** | Leads avec probabilité ≥ 50% | Pousser la conversion |
| 🔵 **Devis en attente** | Devis non confirmés depuis X jours | Relancer le client |

### Naviguer depuis une alerte

Chaque alerte est **cliquable** :
- Cliquer sur "Factures en retard" → ouvre la liste des factures en retard
- Cliquer sur "Leads chauds" → ouvre la liste des leads chauds
- Cliquer sur "Opérations en retard" → ouvre les transferts en retard

> 💡 C'est le principal intérêt du dashboard : **identifier l'urgent** et **agir immédiatement**.

---

## 6. 📋 Vues détaillées par département

Le menu **Tableaux de Bord** propose des sous-menus par département :

### Ventes
- **Analyse des ventes** : vue pivot/graphique des commandes
- **Devis en cours** : liste des devis non confirmés
- **À facturer** : commandes prêtes à facturer

### Achats
- **Analyse des achats** : vue pivot/graphique des commandes fournisseur

### Stock / Logistique
- **Livraisons en attente** : bons de livraison à traiter
- **Réceptions en attente** : réceptions fournisseur à valider
- **Opérations en retard** : transferts dépassant la date prévue

### Comptabilité
- **Factures clients impayées** : toutes les factures non réglées
- **Factures fournisseurs impayées** : factures à payer

### CRM
- **Pipeline CRM** : vue Kanban du pipeline

### RH
- **Employés** : liste des employés

> 📌 Chaque sous-menu ouvre la vue native d'Odoo avec les filtres appropriés. Vous pouvez naviguer, modifier et agir directement.

---

## 7. ⚙️ Configurer les KPIs

### Accéder à la configuration

1. **Aller dans** : Tableaux de Bord → Configuration → KPI
2. La liste des KPIs s'affiche

### Créer ou modifier un KPI

| Champ | Description |
|-------|-------------|
| **Nom** | Nom affiché du KPI |
| **Catégorie** | Vente / Achat / Stock / Comptabilité / RH / CRM |
| **Séquence** | Ordre d'affichage |
| **Icône** | Icône FontAwesome (ex. fa-shopping-cart) |
| **Description** | Explication du KPI |

> 📌 Les valeurs des KPIs sont calculées **automatiquement** en temps réel. La configuration concerne uniquement l'affichage.

---

## 8. 🖨️ Imprimer les rapports PDF

### Rapport tableau de bord

1. Aller dans le menu Rapports du tableau de bord
2. Sélectionner les données
3. Imprimer le rapport

> 💡 Pour un export plus complet, utilisez les vues **Pivot** de chaque département → **Télécharger en Excel** (icône ↓).

---

## 9. 💡 FAQ & Astuces

### Questions fréquentes

**Q : Les données sont-elles en temps réel ?**
> Oui ! Chaque ouverture du dashboard recalcule tous les KPIs depuis la base de données.

**Q : Puis-je personnaliser les KPIs affichés ?**
> Les KPIs sont configurables dans Configuration → KPI. Le dashboard affiche automatiquement les données calculées.

**Q : Comment exporter les données ?**
> Allez dans la vue détaillée (ex. Ventes → Analyse), passez en vue Pivot, cliquez sur l'icône **Télécharger** pour un export Excel.

**Q : Le dashboard est lent à charger ?**
> C'est normal si la base contient beaucoup de données. Le dashboard interroge tous les modules à la fois. Attendez le chargement complet.

### Routine recommandée

| Quand | Action | Durée |
|-------|--------|-------|
| **Chaque matin** | Consulter le dashboard, traiter les alertes rouges | 5 min |
| **Chaque semaine** | Analyser les tendances, comparer avec les objectifs | 15 min |
| **Chaque mois** | Revue complète avec les managers, export Excel | 30 min |
| **Chaque trimestre** | Analyse approfondie, ajustement des objectifs | 1h |

---

*Guide Tableau de Bord — ERP Commercial Odoo 17 | Mis à jour le 26/03/2026*
