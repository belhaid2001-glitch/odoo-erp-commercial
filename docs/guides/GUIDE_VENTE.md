# 🛒 Guide Utilisateur — Module Vente

> **Public cible** : Commerciaux, Assistants commerciaux, Directeur commercial
> **Accès** : Menu principal → **Ventes**

---

## 📋 Sommaire

1. [Présentation du module](#1--présentation-du-module)
2. [Créer un devis](#2--créer-un-devis)
3. [Gérer les produits optionnels](#3--gérer-les-produits-optionnels)
4. [Workflow d'approbation](#4--workflow-dapprobation)
5. [Confirmer une commande](#5--confirmer-une-commande)
6. [Gérer les prévisions de vente](#6--gérer-les-prévisions-de-vente)
7. [Facturation](#7--facturation)
8. [Imprimer les rapports PDF](#8--imprimer-les-rapports-pdf)
9. [Tableau de bord ventes](#9--tableau-de-bord-ventes)
10. [FAQ & Astuces](#10--faq--astuces)

---

## 1. 📌 Présentation du module

Le module **Vente** gère l'ensemble du cycle commercial :

```
Devis → Approbation → Commande → Livraison → Facturation
```

**Fonctionnalités clés :**
- Gestion des devis et commandes clients
- Système de **priorité** (Normal, Basse, Moyenne, Haute, Urgente)
- **Workflow d'approbation** pour les commandes importantes
- **Produits optionnels** suggérés au client
- Suivi des **marges** et remises
- **Prévisions de vente** par commercial
- **3 types de vente** : Standard, Abonnement, Projet

---

## 2. 📝 Créer un devis

### Étape par étape

1. **Aller dans** : Ventes → Commandes → Devis
2. Cliquer sur **➕ Nouveau**
3. Remplir les champs :

| Champ | Description | Obligatoire |
|-------|-------------|:-----------:|
| **Client** | Sélectionner le client | ✅ |
| **Référence client** | N° de référence du client (bon de commande client) | Non |
| **Type de vente** | Standard / Abonnement / Projet | ✅ |
| **Priorité** | Normal → Urgente | Non |
| **Date d'expiration** | Date limite de validité du devis | Non |

4. **Ajouter les lignes de commande** :
   - Cliquer sur **Ajouter une ligne**
   - Sélectionner le **Produit**
   - Indiquer la **Quantité** et le **Prix unitaire**
   - Le **Sous-total**, la **Marge** et la **Remise** se calculent automatiquement

5. **Instructions de livraison** (onglet **Informations complémentaires**) :
   - Saisir les instructions spéciales pour la livraison

6. Cliquer sur **💾 Sauvegarder**

> 💡 **Astuce** : La marge en % se calcule automatiquement. Surveillez-la pour garantir la rentabilité.

---

## 3. 🎁 Gérer les produits optionnels

Les produits optionnels sont des **suggestions** que le client peut accepter ou refuser.

### Ajouter des produits optionnels

1. Ouvrir un devis
2. Aller à l'onglet **Produits optionnels**
3. Cliquer sur **Ajouter une ligne**
4. Remplir :
   - **Produit** : le produit suggéré
   - **Quantité** et **Prix unitaire**
5. Quand le client accepte, cocher **☑ Sélectionné**

> 📌 Les produits optionnels sélectionnés ne sont **pas** automatiquement ajoutés aux lignes de commande. C'est un outil d'aide à la vente.

---

## 4. ✅ Workflow d'approbation

Le système d'approbation permet au management de valider les commandes importantes.

### Les 4 statuts d'approbation

| Statut | Signification | Couleur |
|--------|---------------|---------|
| **Brouillon** | Pas encore soumis | Gris |
| **En attente** | Soumis, attend l'approbation | Orange |
| **Approuvé** | Validé par un manager | Vert |
| **Rejeté** | Refusé par un manager | Rouge |

### Pour le commercial : Demander l'approbation

1. Ouvrir le devis finalisé
2. Cliquer sur le bouton **📋 Demander approbation**
3. Le statut passe à **⏳ En attente d'approbation**
4. Le manager reçoit une notification

### Pour le manager : Approuver ou Rejeter

1. Aller dans Ventes → filtrer par **En attente d'approbation**
2. Ouvrir la commande
3. Vérifier les détails (montant, marge, conditions)
4. Cliquer sur :
   - **✅ Approuver** → Le commercial peut confirmer la commande
   - **❌ Rejeter** → La commande est bloquée avec un motif

> ⚠️ **Attention** : Seuls les utilisateurs avec les droits **Responsable des ventes** peuvent approuver ou rejeter.

---

## 5. 📋 Confirmer une commande

Une fois le devis approuvé (si approbation requise) :

1. Ouvrir le devis
2. Cliquer sur **✅ Confirmer**
3. Le devis devient une **Commande de vente** (bon de commande)
4. Un **bon de livraison** est automatiquement créé dans le module Stock

> 📌 Le numéro change : `S00001` (devis) → `SO0001` (commande confirmée)

---

## 6. 📈 Gérer les prévisions de vente

Les prévisions permettent de suivre les objectifs commerciaux.

### Créer une prévision

1. **Aller dans** : Ventes → Prévisions → Prévisions de vente
2. Cliquer sur **➕ Nouveau**
3. Remplir :

| Champ | Description |
|-------|-------------|
| **Date de prévision** | Date de création de la prévision |
| **Date cible** | Date objectif de réalisation |
| **Commercial** | Le vendeur responsable |
| **Équipe commerciale** | L'équipe (optionnel) |
| **Client** | Client cible (optionnel) |
| **Produit** | Produit cible (optionnel) |
| **Montant prévu** | Objectif de chiffre d'affaires |

4. Cliquer sur **Confirmer** pour valider la prévision

### Suivre la réalisation

- Le **Montant réalisé** se calcule automatiquement à partir des commandes confirmées
- Le **Taux de réalisation (%)** = Montant réalisé / Montant prévu × 100
- Utilisez la vue **Pivot** ou **Graphique** pour une vision synthétique

### Cycle de vie d'une prévision

```
Brouillon → Confirmée → Terminée
                ↘ Annulée
```

---

## 7. 💰 Facturation

### Facturer une commande

1. Ouvrir la commande confirmée
2. Vérifier que le champ **Prêt à facturer** est à ✅ (calculé automatiquement)
3. Cliquer sur **Créer une facture**
4. Choisir le type : Facture normale / Acompte (%)  / Acompte (montant fixe)
5. La facture est créée dans le module Comptabilité

### Facturation en lot

1. Aller dans la vue liste des commandes
2. Cocher plusieurs commandes **prêtes à facturer**
3. Cliquer sur **Action → Générer les factures en lot**
4. Toutes les factures sont créées en une seule opération

> 💡 **Astuce** : Utilisez le filtre **Prêt à facturer** pour voir toutes les commandes facturables d'un coup.

---

## 8. 🖨️ Imprimer les rapports PDF

### Rapport de commande de vente

1. Aller dans : Ventes → Rapports → **Rapport commande de vente**
2. La liste des commandes s'affiche
3. **Cocher** les commandes à imprimer
4. Cliquer sur **Imprimer** → **Rapport de commande personnalisé**
5. Le PDF contient :
   - Informations du client et référence
   - Priorité et statut d'approbation
   - Lignes de produits avec prix et marges
   - Instructions de livraison
   - Section approbation (si applicable)

### Rapport de prévisions

1. Aller dans : Ventes → Rapports → **Rapport prévisions**
2. Cocher les prévisions
3. Imprimer → **Rapport de prévision de vente**

---

## 9. 📊 Tableau de bord ventes

1. Aller dans : Ventes → **Tableau de bord**
2. Visualisez :
   - **Chiffre d'affaires** par période
   - **Nombre de commandes** confirmées
   - **Top produits** vendus
   - **Performance par commercial**
3. Utilisez les filtres de date et les regroupements pour affiner

---

## 10. 💡 FAQ & Astuces

### Questions fréquentes

**Q : Comment retrouver un devis rapidement ?**
> Utilisez la barre de recherche : tapez le nom du client, le numéro de commande ou la référence client.

**Q : Puis-je modifier une commande confirmée ?**
> Non directement. Vous devez créer un **avoir** ou **annuler** la commande, puis la recréer.

**Q : Comment voir mes marges ?**
> Dans la vue liste, la colonne **Marge (%)** est visible. En vue formulaire, elle apparaît à côté du total.

**Q : Qui peut approuver mes commandes ?**
> Seuls les utilisateurs avec le rôle **Responsable des ventes** dans Configuration → Utilisateurs.

### Raccourcis utiles

| Action | Raccourci |
|--------|-----------|
| Nouveau devis | `Alt + Shift + N` |
| Sauvegarder | `Alt + S` ou `Ctrl + S` |
| Rechercher | `Alt + Q` |
| Vue liste | icône ☰ |
| Vue formulaire | cliquer sur un enregistrement |

### Filtres recommandés

- **Mes devis** : voir uniquement vos devis
- **Haute priorité** : devis urgents à traiter en premier
- **En attente d'approbation** : commandes à valider (pour les managers)
- **Prêt à facturer** : commandes facturables

---

*Guide Vente — ERP Commercial Odoo 17 | Mis à jour le 26/03/2026*
