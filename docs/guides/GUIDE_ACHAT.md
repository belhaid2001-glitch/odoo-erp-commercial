# 📦 Guide Utilisateur — Module Achat

> **Public cible** : Acheteurs, Responsable achats, Direction des achats
> **Accès** : Menu principal → **Achats**

---

## 📋 Sommaire

1. [Présentation du module](#1--présentation-du-module)
2. [Créer une demande de prix](#2--créer-une-demande-de-prix)
3. [Gérer les conventions d'achat](#3--gérer-les-conventions-dachat)
4. [Confirmer une commande fournisseur](#4--confirmer-une-commande-fournisseur)
5. [Contrôle qualité à la réception](#5--contrôle-qualité-à-la-réception)
6. [Suivi de la réception](#6--suivi-de-la-réception)
7. [Imprimer les rapports PDF](#7--imprimer-les-rapports-pdf)
8. [Tableau de bord achats](#8--tableau-de-bord-achats)
9. [FAQ & Astuces](#9--faq--astuces)

---

## 1. 📌 Présentation du module

Le module **Achat** couvre tout le cycle d'approvisionnement :

```
Demande de prix → Commande fournisseur → Réception → Contrôle qualité → Facturation
```

**Fonctionnalités clés :**
- **4 types d'achat** : Standard, Urgent, Accord-cadre, Récurrent
- **Conventions d'achat** avec prix négociés et remises
- **Contrôle qualité** intégré à chaque commande
- **Approbation automatique** pour les commandes > 50 000 MAD
- Suivi en temps réel du **statut de réception** (En attente / Partielle / Complète)
- Calcul automatique des **économies réalisées**

---

## 2. 📝 Créer une demande de prix

### Étape par étape

1. **Aller dans** : Achats → Commandes → Demandes de prix
2. Cliquer sur **➕ Nouveau**
3. Remplir les informations :

| Champ | Description | Obligatoire |
|-------|-------------|:-----------:|
| **Fournisseur** | Sélectionner le fournisseur | ✅ |
| **Référence fournisseur** | Numéro de référence du fournisseur | Non |
| **Type d'achat** | Standard / Urgent / Accord-cadre / Récurrent | ✅ |
| **Priorité** | Normal → Urgente | Non |
| **Convention d'achat** | Lier à une convention existante (optionnel) | Non |

4. **Ajouter les produits** :
   - Cliquer sur **Ajouter une ligne**
   - Sélectionner le **Produit**, la **Quantité**, le **Prix unitaire**
   - La ligne **Sous-total** se calcule automatiquement

5. **Onglet Conditionnement** :
   - Saisir les **Instructions de conditionnement** spécifiques

6. **Onglet Contrôle Qualité** :
   - Cocher **☑ Contrôle qualité requis** si nécessaire
   - Ajouter des **Notes qualité** pour l'équipe réception

7. Cliquer sur **💾 Sauvegarder**

> 📌 Si une **convention** est sélectionnée, les conditions de paiement sont automatiquement appliquées.

---

## 3. 📜 Gérer les conventions d'achat

Les conventions sont des **accords négociés** avec les fournisseurs (prix, remises, volumes).

### Créer une convention

1. **Aller dans** : Achats → Conventions → Conventions d'achat
2. Cliquer sur **➕ Nouveau**
3. Remplir :

| Champ | Description |
|-------|-------------|
| **Fournisseur** | Le fournisseur concerné |
| **Date de début** | Début de validité |
| **Date de fin** | Fin de validité |
| **Conditions de paiement** | Délais négociés |
| **Remise globale (%)** | Remise applicable à toute commande |
| **Montant minimum / maximum** | Seuils de la convention |
| **Produits concernés** | Liste des produits couverts |

4. Ajouter les **Lignes de convention** (détail par produit) :
   - **Produit**, **Quantité min/max**, **Prix négocié**, **Remise spécifique**

5. Cliquer sur **Activer** pour rendre la convention effective

### Cycle de vie d'une convention

```
Brouillon → Active → Expirée (automatique à la date de fin)
              ↘ Annulée (manuellement)
```

> 💡 **Astuce** : Le bouton statistique en haut du formulaire affiche le **nombre de commandes** et le **total commandé** sous cette convention.

> ⚠️ **Attention** : Les conventions expirées sont automatiquement marquées par un traitement planifié quotidien.

---

## 4. ✅ Confirmer une commande fournisseur

1. Ouvrir la demande de prix validée
2. Cliquer sur **Confirmer la commande**
3. La demande de prix devient une **Commande fournisseur**

### Approbation automatique

| Montant total | Approbation |
|---------------|-------------|
| ≤ 50 000 MAD | **Non requise** — confirmation directe |
| > 50 000 MAD | **Requise** — un badge ⚠️ s'affiche |

> 📌 Le champ **Approbation requise** se calcule automatiquement. Les commandes dépassant 50 000 MAD nécessitent la validation d'un responsable.

---

## 5. 🔍 Contrôle qualité à la réception

Si le contrôle qualité a été activé sur la commande :

1. À la **réception** des marchandises, ouvrir le bon de réception (module Stock)
2. L'information **Contrôle qualité requis** est reportée
3. Vérifier les produits selon les **Notes qualité** spécifiées
4. Documenter les résultats dans le module Stock (voir [Guide Stock](./GUIDE_STOCK.md))

---

## 6. 📊 Suivi de la réception

Le statut de réception est calculé **automatiquement** :

| Statut | Signification |
|--------|---------------|
| 🔴 **En attente** | Aucun produit reçu |
| 🟡 **Partielle** | Certains produits reçus, pas tous |
| 🟢 **Complète** | Tous les produits reçus |

Ce statut est visible dans :
- La vue **liste** des commandes fournisseur
- Le **formulaire** de chaque commande

---

## 7. 🖨️ Imprimer les rapports PDF

### Rapport commande fournisseur

1. Aller dans : Achats → Rapports → **Rapport commande fournisseur**
2. Cocher les commandes à imprimer
3. Imprimer → **Rapport de commande fournisseur**
4. Le PDF contient :
   - Informations fournisseur et références
   - Type d'achat et priorité
   - Lignes de produits avec prix
   - Mention du contrôle qualité
   - Économies réalisées

### Rapport convention d'achat

1. Aller dans : Achats → Rapports → **Rapport convention d'achat**
2. Cocher les conventions
3. Imprimer → **Rapport de convention d'achat**
4. Le PDF contient :
   - Détails du fournisseur
   - Période de validité
   - Remises et conditions négociées
   - Liste des produits et prix

---

## 8. 📊 Tableau de bord achats

1. Aller dans : Achats → **Tableau de bord**
2. Vues disponibles :
   - **Tableau croisé** (Pivot) : analyse par fournisseur, produit, période
   - **Graphique** : visualisation des volumes d'achat
   - **Liste** : détail des commandes

---

## 9. 💡 FAQ & Astuces

### Questions fréquentes

**Q : Comment comparer les prix entre fournisseurs ?**
> Créez plusieurs demandes de prix pour le même produit auprès de différents fournisseurs, puis comparez les totaux.

**Q : Comment savoir si une convention est encore valide ?**
> Dans la liste des conventions, le statut est affiché. Les conventions expirées passent automatiquement en **Expirée**.

**Q : Comment suivre les économies réalisées ?**
> Le champ **Économies réalisées** est calculé automatiquement sur chaque commande et visible dans la vue liste.

**Q : Une commande urgente a-t-elle besoin d'approbation ?**
> Le type (urgent) n'affecte pas l'approbation. Seul le **montant > 50 000 MAD** déclenche l'approbation.

### Filtres recommandés

| Filtre | Usage |
|--------|-------|
| **Haute priorité** | Commandes urgentes |
| **Avec convention** | Commandes liées à une convention |
| **Contrôle qualité** | Commandes nécessitant un CQ |
| **Type : Urgent** | Achats urgents uniquement |

---

*Guide Achat — ERP Commercial Odoo 17 | Mis à jour le 26/03/2026*
