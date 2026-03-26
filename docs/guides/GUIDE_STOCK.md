# 🏭 Guide Utilisateur — Module Stock & Inventaire

> **Public cible** : Magasiniers, Préparateurs de commande, Responsable logistique, Équipe qualité
> **Accès** : Menu principal → **Inventaire**

---

## 📋 Sommaire

1. [Présentation du module](#1--présentation-du-module)
2. [Gérer les transferts (livraisons/réceptions)](#2--gérer-les-transferts)
3. [Workflow de préparation](#3--workflow-de-préparation)
4. [Contrôle qualité](#4--contrôle-qualité)
5. [Scanner les codes-barres](#5--scanner-les-codes-barres)
6. [Gérer les équipes qualité](#6--gérer-les-équipes-qualité)
7. [Valorisation de l'inventaire](#7--valorisation-de-linventaire)
8. [Imprimer les rapports PDF](#8--imprimer-les-rapports-pdf)
9. [FAQ & Astuces](#9--faq--astuces)

---

## 1. 📌 Présentation du module

Le module **Stock** gère toute la chaîne logistique :

```
Réception → Contrôle qualité → Stockage → Préparation → Expédition
```

**Fonctionnalités clés :**
- **Statut de préparation** en 4 étapes (Non commencé → En cours → Prêt → Expédié)
- **Contrôle qualité** intégré (visuel, dimensionnel, fonctionnel, documentaire)
- **Scanner de codes-barres** pour accélérer les opérations
- **Équipes qualité** avec responsable et membres
- **Valorisation d'inventaire** en temps réel (vue SQL)
- Suivi des **colis** et **numéros de suivi transporteur**

---

## 2. 📦 Gérer les transferts

### Types de transferts

| Type | Description | Créé automatiquement |
|------|-------------|:--------------------:|
| **Réception** | Marchandises entrantes (fournisseur → entrepôt) | ✅ Depuis commande achat |
| **Livraison** | Marchandises sortantes (entrepôt → client) | ✅ Depuis commande vente |
| **Interne** | Transfert entre emplacements | Manuel |

### Ouvrir un transfert

1. **Aller dans** : Inventaire → Opérations → Transferts
2. Cliquer sur le transfert à traiter
3. Vous voyez :
   - **Informations principales** : origine, destinataire, date prévue
   - **Priorité** : Normal → Urgente
   - **Lignes de produits** : détail de chaque article à transférer

### Traiter un transfert

1. Ouvrir le bon de transfert
2. Pour chaque ligne, renseigner la **Quantité faite**
3. Si tout est conforme, cliquer sur **✅ Valider**
4. Si partiel, confirmer le **reliquat** (backorder)

> 💡 **Astuce** : Ajoutez les **Instructions de livraison** et le **Numéro de suivi transporteur** pour un suivi complet.

---

## 3. 🔄 Workflow de préparation

Le statut de préparation guide le magasinier dans le process :

```
📋 Non commencé → 🔧 En cours → ✅ Prêt → 🚚 Expédié
```

### Étape par étape

| Étape | Action du magasinier | Bouton |
|-------|---------------------|--------|
| **Non commencé** | La commande vient d'arriver | — |
| **Démarrer la préparation** | Commencer à collecter les produits | 🔧 Démarrer |
| **Prêt** | Tous les produits collectés et emballés | ✅ Marquer prêt |
| **Expédié** | Le colis est parti | 🚚 Marquer expédié |

### Informations de préparation

- **Notes de préparation** : instructions spéciales (fragile, lot spécifique, etc.)
- **Nombre de colis** : renseigner le nombre de cartons
- **Poids total (kg)** : calculé automatiquement depuis les lignes de produit

> ⚠️ **Attention** : Le contrôle qualité doit être validé **avant** de passer au statut "Prêt".

---

## 4. 🔍 Contrôle qualité

### Activer le contrôle qualité sur un transfert

1. Ouvrir le bon de transfert
2. Cocher **☑ Contrôle qualité requis**
3. Les contrôles se créent dans l'onglet **Contrôles qualité**

### Réaliser un contrôle

1. Dans l'onglet **Contrôles qualité**, cliquer sur **Ajouter une ligne**
2. Remplir :

| Champ | Description |
|-------|-------------|
| **Produit** | Le produit à contrôler |
| **Type de contrôle** | Visuel / Dimensionnel / Fonctionnel / Documentaire |
| **Quantité à contrôler** | Nombre d'unités |
| **Lot / N° de série** | Si applicable |
| **Inspecteur** | La personne qui fait le contrôle |
| **Équipe qualité** | L'équipe responsable |

3. Effectuer le contrôle physique
4. Renseigner :
   - **Quantité contrôlée** : nombre d'unités vérifiées
   - **Quantité rejetée** : nombre d'unités non conformes
5. Sélectionner le **Résultat** :
   - ✅ **Conforme** (pass)
   - ❌ **Non conforme** (fail)
6. Ajouter des **Observations** si nécessaire

### Statut qualité global du transfert

| Statut | Signification |
|--------|---------------|
| ⚪ **Aucun** | Pas de contrôle qualité |
| 🟡 **En attente** | Contrôles en cours |
| 🟢 **Conforme** | Tous les contrôles OK |
| 🔴 **Non conforme** | Au moins un contrôle échoué |

> 📌 Le statut qualité se calcule **automatiquement** à partir de tous les contrôles du transfert.

---

## 5. 📱 Scanner les codes-barres

Le scan accélère les opérations :

1. Ouvrir un bon de transfert
2. Placer le curseur dans le champ **Code-barre scanné**
3. Scanner le code-barre du produit avec votre douchette
4. Le système :
   - Identifie le produit automatiquement
   - Incrémente la quantité faite (+1)
5. Répéter pour chaque produit scanné

> 💡 **Astuce** : Si le produit n'est pas dans les lignes du transfert, un message d'avertissement s'affiche.

---

## 6. 👥 Gérer les équipes qualité

### Créer une équipe

1. **Aller dans** : Inventaire → Qualité → Équipes qualité
2. Cliquer sur **➕ Nouveau**
3. Remplir :
   - **Nom de l'équipe** : ex. "Équipe CQ Alimentaire"
   - **Responsable** : le chef d'équipe
   - **Membres** : les inspecteurs

### Affecter une équipe à un contrôle

Lors de la création d'un contrôle qualité, sélectionnez l'**Équipe qualité** dans le formulaire de contrôle.

---

## 7. 💰 Valorisation de l'inventaire

La valorisation montre la valeur financière du stock en temps réel.

1. **Aller dans** : Inventaire → Rapports → Valorisation d'inventaire
2. Vous voyez :

| Colonne | Description |
|---------|-------------|
| **Produit** | Nom du produit |
| **Catégorie** | Catégorie du produit |
| **Emplacement** | Lieu de stockage |
| **Quantité** | Stock disponible |
| **Coût unitaire** | Prix d'achat moyen |
| **Valeur totale** | Quantité × Coût unitaire |

3. Utilisez la vue **Pivot** pour regrouper par catégorie ou emplacement
4. La vue **Graphique** affiche un diagramme en barres par catégorie

> 📌 Ces données sont calculées en **temps réel** depuis les mouvements de stock.

---

## 8. 🖨️ Imprimer les rapports PDF

### Rapport bon de livraison

1. Aller dans : Inventaire → Rapports → **Rapport bon de livraison**
2. Cocher les bons à imprimer
3. Imprimer → **Rapport de livraison personnalisé**
4. Le PDF contient :
   - Informations expéditeur / destinataire
   - Statut de préparation et nombre de colis
   - Lignes de produits avec quantités
   - Résultats du contrôle qualité (si applicable)
   - Instructions de livraison et numéro de suivi

### Rapport contrôle qualité

1. Aller dans : Inventaire → Rapports → **Rapport contrôle qualité**
2. Cocher les contrôles
3. Imprimer → **Rapport de contrôle qualité**
4. Le PDF contient :
   - Détails du produit et du lot
   - Type de contrôle et résultat
   - Quantités contrôlées / rejetées
   - Nom de l'inspecteur
   - Zone de signature

---

## 9. 💡 FAQ & Astuces

### Questions fréquentes

**Q : Comment gérer une réception partielle ?**
> Lors de la validation, si toutes les quantités ne sont pas reçues, Odoo propose de créer un **reliquat** (backorder) pour le reste.

**Q : Puis-je forcer la livraison si le CQ a échoué ?**
> Il est déconseillé mais techniquement possible. Le statut qualité sera affiché en **rouge** sur le transfert.

**Q : Comment voir les transferts en retard ?**
> Utilisez le filtre **En retard** dans la barre de recherche.

**Q : Comment trouver un produit par code-barre ?**
> Utilisez le champ **Code-barre scanné** sur le transfert, ou la recherche globale.

### Filtres recommandés

| Filtre | Usage |
|--------|-------|
| **Haute priorité** | Transferts urgents |
| **Qualité en attente** | Transferts avec CQ non finalisé |
| **Qualité échouée** | Transferts avec CQ non conforme |
| **En préparation** | Transferts en cours de picking |

---

*Guide Stock — ERP Commercial Odoo 17 | Mis à jour le 26/03/2026*
