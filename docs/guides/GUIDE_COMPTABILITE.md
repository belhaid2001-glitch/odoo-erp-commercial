# 💰 Guide Utilisateur — Module Comptabilité & Facturation

> **Public cible** : Comptables, Aide-comptables, DAF (Directeur Administratif et Financier)
> **Accès** : Menu principal → **Comptabilité**

---

## 📋 Sommaire

1. [Présentation du module](#1--présentation-du-module)
2. [Gérer les factures clients](#2--gérer-les-factures-clients)
3. [Gérer les factures fournisseurs](#3--gérer-les-factures-fournisseurs)
4. [Système de relance de paiement](#4--système-de-relance-de-paiement)
5. [Gestion des chèques](#5--gestion-des-chèques)
6. [Étiquettes analytiques](#6--étiquettes-analytiques)
7. [Validation des factures](#7--validation-des-factures)
8. [Imprimer les rapports PDF](#8--imprimer-les-rapports-pdf)
9. [FAQ & Astuces](#9--faq--astuces)

---

## 1. 📌 Présentation du module

Le module **Comptabilité** gère la facturation et les paiements :

```
Facture brouillon → Validation → Envoi au client → Relance → Paiement → Lettrage
```

**Fonctionnalités clés :**
- **Suivi des impayés** avec niveau de risque automatique
- **Relances de paiement** manuelles et automatiques (hebdomadaires)
- **Gestion des chèques** reçus et émis avec cycle de vie complet
- **Étiquettes analytiques** personnalisées
- **Validation managériale** des factures
- Calcul automatique des **jours de retard** et du **niveau de risque**

---

## 2. 📄 Gérer les factures clients

### Créer une facture manuellement

1. **Aller dans** : Comptabilité → Clients → Factures
2. Cliquer sur **➕ Nouveau**
3. Remplir :

| Champ | Description | Obligatoire |
|-------|-------------|:-----------:|
| **Client** | Le client facturé | ✅ |
| **Date de facture** | Date d'émission | ✅ |
| **Date d'échéance** | Date limite de paiement | ✅ |
| **Étiquettes analytiques** | Pour le suivi analytique | Non |

4. Ajouter les **Lignes de facture** :
   - Produit, Quantité, Prix unitaire, Taxes
5. Ajouter des **Notes internes** dans l'onglet dédié (visibles uniquement en interne)
6. Cliquer sur **💾 Sauvegarder**

### Depuis une commande de vente

Les factures sont généralement créées **automatiquement** depuis le module Vente :
- Ouvrir la commande confirmée → **Créer une facture**

### Les indicateurs automatiques

| Indicateur | Calcul | Affichage |
|-----------|--------|-----------|
| **Jours de retard** | Date du jour − Date d'échéance | Nombre de jours |
| **Niveau de risque** | Basé sur le retard et le montant | Badge coloré |

#### Niveaux de risque

| Risque | Couleur | Critères |
|--------|---------|----------|
| 🟢 **Faible** | Vert | < 30 jours de retard ET < 50 000 MAD |
| 🟡 **Moyen** | Jaune | 30-59 jours de retard |
| 🟠 **Élevé** | Orange | 60-89 jours OU > 50 000 MAD en retard |
| 🔴 **Critique** | Rouge | ≥ 90 jours OU > 100 000 MAD en retard |

> 📌 Le niveau de risque se met à jour **automatiquement** chaque jour.

---

## 3. 📄 Gérer les factures fournisseurs

1. **Aller dans** : Comptabilité → Fournisseurs → Factures fournisseurs
2. Même principe que les factures clients
3. Les factures fournisseurs sont souvent créées depuis le module **Achat**

---

## 4. ⏰ Système de relance de paiement

### Relance manuelle

1. Ouvrir une facture **en retard** (status : Comptabilisée, date d'échéance dépassée)
2. Cliquer sur le bouton **📧 Envoyer une relance**
3. Le système :
   - Marque la facture comme **Relancée** ✅
   - Enregistre la **Date de relance**
   - Incrémente le **Compteur de relances** (+1)
   - Ajoute un message dans le **Chatter** (historique)

### Relance automatique

Un traitement planifié (cron) s'exécute **chaque semaine** :
- Il identifie toutes les factures comptabilisées et en retard
- Il envoie une relance automatique
- Les mêmes champs sont mis à jour (date, compteur, chatter)

> 💡 **Astuce** : Utilisez le filtre **Relancé** pour voir toutes les factures déjà relancées et le filtre **En retard** pour les impayés.

### Suivi dans la vue liste

La vue liste affiche :
| Colonne | Description |
|---------|-------------|
| **Jours de retard** | Nombre de jours depuis l'échéance |
| **Niveau de risque** | Badge coloré (faible → critique) |
| **Nb relances** | Nombre de relances envoyées |

---

## 5. 💳 Gestion des chèques

### Accéder aux chèques

- **Chèques reçus** : Comptabilité → Chèques → Chèques reçus
- **Chèques émis** : Comptabilité → Chèques → Chèques émis
- **Tous les chèques** : Comptabilité → Chèques → Tous les chèques

### Créer un chèque

1. Cliquer sur **➕ Nouveau**
2. Remplir :

| Champ | Description | Obligatoire |
|-------|-------------|:-----------:|
| **Numéro de chèque** | N° imprimé sur le chèque | ✅ |
| **Type** | Reçu / Émis | ✅ |
| **Partenaire** | Client ou fournisseur | ✅ |
| **Montant** | Montant du chèque | ✅ |
| **Date du chèque** | Date d'émission | ✅ |
| **Date d'échéance** | Date d'encaissement prévue | ✅ |
| **Banque** | Banque émettrice | Non |
| **Compte bancaire** | N° de compte | Non |
| **Journal** | Journal comptable | Non |
| **Pièce comptable** | Facture liée | Non |

### Cycle de vie d'un chèque

```
📝 Brouillon → 📋 Enregistré → 🏦 Déposé → ✅ Encaissé
                                         ↘ ↩️ Retourné
                  ↘ ❌ Annulé
```

| Statut | Action | Description |
|--------|--------|-------------|
| **Brouillon** | Création | Le chèque vient d'être saisi |
| **Enregistré** | Cliquer **Enregistrer** | Le chèque est officiel |
| **Déposé** | Cliquer **Déposer** | Remis à la banque |
| **Encaissé** | Cliquer **Encaisser** | L'argent est sur le compte |
| **Retourné** | Cliquer **Retourner** | Chèque rejeté par la banque |
| **Annulé** | Cliquer **Annuler** | Chèque annulé |

> ⚠️ **Attention** : Un chèque **retourné** nécessite un suivi immédiat avec le client/fournisseur.

---

## 6. 🏷️ Étiquettes analytiques

Les étiquettes analytiques permettent de **catégoriser** les factures pour l'analyse financière.

### Créer une étiquette

1. **Aller dans** : Comptabilité → Analytique → Étiquettes analytiques
2. Ajouter directement dans la liste (édition en ligne) :
   - **Nom** : ex. "Projet Alpha", "Marketing Q1", "Département IT"
   - **Couleur** : choisir une couleur
3. Sauvegarder

### Utiliser les étiquettes

Sur chaque facture, dans l'onglet dédié, sélectionnez une ou plusieurs **Étiquettes analytiques**.

> 💡 **Astuce** : Utilisez les étiquettes pour regrouper vos factures par projet, département ou campagne.

---

## 7. ✅ Validation des factures

### Valider une facture (manager)

1. Ouvrir la facture brouillon
2. Vérifier les montants, les lignes et les conditions
3. Cliquer sur **✅ Valider** (bouton réservé aux responsables)
4. Le système enregistre :
   - **Validé par** : votre nom
   - **Date de validation** : date et heure

> 📌 La validation est différente de la **comptabilisation**. Valider = approbation managériale. Comptabiliser = écriture comptable.

---

## 8. 🖨️ Imprimer les rapports PDF

### Rapport facture personnalisé

1. Aller dans : Comptabilité → Rapports → **Rapport facture personnalisé**
2. Cocher les factures
3. Imprimer → **Rapport facture personnalisé**
4. Le PDF contient :
   - Informations client/fournisseur
   - Niveau de risque et jours de retard
   - Historique des relances
   - Étiquettes analytiques
   - Lignes de facture détaillées

### Impression de chèque

1. Aller dans : Comptabilité → Rapports → **Impression chèque**
2. Cocher les chèques (émis)
3. Imprimer → **Impression de chèque**
4. Le PDF contient :
   - Montant en chiffres et en lettres
   - Bénéficiaire
   - Banque et n° de compte
   - Zone de signature

---

## 9. 💡 FAQ & Astuces

### Questions fréquentes

**Q : Comment voir toutes les factures en retard ?**
> Filtre **En retard** dans la barre de recherche. Vous pouvez aussi regrouper par **Niveau de risque**.

**Q : Les relances automatiques remplacent-elles l'envoi manuel ?**
> Non, les relances automatiques complètent les relances manuelles. Le compteur s'incrémente dans les deux cas.

**Q : Comment annuler une facture comptabilisée ?**
> Créez un **Avoir** (note de crédit) depuis la facture → bouton **Créer un avoir**.

**Q : Un chèque retourné, que faire ?**
> 1. Le statut passe à "Retourné". 2. Contactez le client. 3. Créez un nouveau chèque ou demandez un virement.

### Filtres recommandés

| Filtre | Usage |
|--------|-------|
| **En retard** | Factures impayées dépassant l'échéance |
| **Risque élevé** | Factures à risque financier |
| **Relancé** | Factures ayant reçu au moins une relance |
| **Jours de retard** (regroupement) | Vue par tranches de retard |

---

*Guide Comptabilité — ERP Commercial Odoo 17 | Mis à jour le 26/03/2026*
