# 📇 Guide Utilisateur — Module Contacts

> **Public cible** : Commerciaux, Administration, Service client
> **Accès** : Menu principal → **Contacts**

---

## 📋 Sommaire

1. [Présentation du module](#1--présentation-du-module)
2. [Créer et enrichir un contact](#2--créer-et-enrichir-un-contact)
3. [Informations légales Maroc](#3--informations-légales-maroc)
4. [Classification et segmentation](#4--classification-et-segmentation)
5. [Gérer les adresses multiples](#5--gérer-les-adresses-multiples)
6. [Statistiques commerciales](#6--statistiques-commerciales)
7. [Imprimer les rapports PDF](#7--imprimer-les-rapports-pdf)
8. [FAQ & Astuces](#8--faq--astuces)

---

## 1. 📌 Présentation du module

Le module **Contacts** est le répertoire central de l'ERP :

```
Prospect → Client / Fournisseur / Partenaire
```

**Fonctionnalités clés :**
- **Champs légaux marocains** : ICE, RC, IF, CNSS
- **5 types de relation** : Prospect, Client, Fournisseur, Partenaire, Autre
- **Segmentation** multi-tags pour le marketing
- **Adresses multiples** (livraison et facturation)
- **Statistiques commerciales** auto-calculées (CA, nombre de commandes)
- **Réseaux sociaux** : LinkedIn, Facebook, Instagram

---

## 2. 📝 Créer et enrichir un contact

### Créer un nouveau contact

1. **Aller dans** : Contacts
2. Cliquer sur **➕ Nouveau**
3. Choisir : **Personne** ou **Société**
4. Remplir les informations de base :

| Champ | Description | Obligatoire |
|-------|-------------|:-----------:|
| **Nom** | Nom complet ou raison sociale | ✅ |
| **Adresse** | Adresse complète | Non |
| **Téléphone / Mobile** | Numéros de contact | Non |
| **Email** | Adresse email | Non |
| **Site web** | URL du site | Non |

### Réseaux sociaux

| Champ | Exemple |
|-------|---------|
| **LinkedIn** | https://linkedin.com/in/nom |
| **Facebook** | https://facebook.com/entreprise |
| **Instagram** | @nom_entreprise |

### Moyen de contact préféré

Sélectionnez comment le client préfère être contacté :
- 📧 Email
- 📞 Téléphone
- 💬 WhatsApp
- 🏢 Visite
- 📮 Courrier postal

---

## 3. 🇲🇦 Informations légales Maroc

Pour les **sociétés marocaines**, remplissez l'onglet dédié :

| Champ | Description | Format |
|-------|-------------|--------|
| **ICE** | Identifiant Commun de l'Entreprise | 15 chiffres |
| **RC** | Registre du Commerce | Variable |
| **IF** | Identifiant Fiscal | Variable |
| **CNSS** | Caisse Nationale de Sécurité Sociale | Variable |
| **Capital social** | Capital de l'entreprise en MAD | Montant |
| **Date de création** | Date de création de la société | Date |

> 📌 Ces informations sont essentielles pour :
> - La facturation légale
> - Les déclarations fiscales
> - Les conventions d'achat
> - Les contrats commerciaux

> 💡 **Astuce** : L'ICE est obligatoire sur toutes les factures au Maroc. Renseignez-le systématiquement.

---

## 4. 🏷️ Classification et segmentation

### Type de relation

Classifiez chaque contact :

| Type | Usage |
|------|-------|
| 🔍 **Prospect** | Potentiel client, pas encore de commande |
| 🛒 **Client** | A déjà passé au moins une commande |
| 📦 **Fournisseur** | On lui achète des produits/services |
| 🤝 **Partenaire** | Relation de partenariat |
| ❓ **Autre** | Presse, administration, divers |

### Priorité

| Priorité | Signification |
|----------|---------------|
| ⬜ **Basse** | Contact secondaire |
| 🟡 **Moyenne** | Contact normal |
| 🟠 **Haute** | Contact important |
| 🔴 **VIP** | Client stratégique, traitement prioritaire |

### Segments

Les segments permettent de **regrouper** les contacts pour des actions commerciales ou marketing :

1. **Créer un segment** : Contacts → Configuration → Segments
   - Nom : ex. "Grand compte", "Retail", "Export", "Zone Nord"
   - Couleur : pour le repérage visuel
2. **Affecter des segments** : sur la fiche contact, champ **Segments** (multi-sélection)

> 💡 **Astuce** : Un contact peut appartenir à **plusieurs segments**. Ex. : "Grand compte" + "Zone Nord" + "Industrie"

---

## 5. 📍 Gérer les adresses multiples

Un client peut avoir **plusieurs adresses** :

### Adresses de livraison

1. Ouvrir la fiche du contact (société)
2. Onglet **Contacts & Adresses** (standard Odoo)
3. Ou voir les **Adresses de livraison** spécifiques

### Adresses de facturation

De même pour les adresses de facturation.

> 📌 Lors de la création d'un devis ou d'une facture, Odoo propose automatiquement les adresses de livraison et facturation du contact.

---

## 6. 📊 Statistiques commerciales

Les statistiques se calculent **automatiquement** et sont visibles sur la fiche contact :

### Boutons statistiques (en haut du formulaire)

| Bouton | Description |
|--------|-------------|
| **X Commandes vente** | Nombre de commandes client (cliquer pour voir le détail) |
| **X Commandes achat** | Nombre de commandes fournisseur |

### Onglet Statistiques

| Indicateur | Description |
|-----------|-------------|
| **CA Total Ventes** | Chiffre d'affaires total (toutes commandes vente) |
| **Nb commandes vente** | Nombre total de bons de commande |
| **Total Achats** | Volume total des achats (si fournisseur) |
| **Nb commandes achat** | Nombre de commandes fournisseur |
| **Première commande** | Date de la toute première commande |
| **Dernière commande** | Date de la commande la plus récente |

> 💡 **Astuce** : Ces statistiques aident à identifier :
> - Les **meilleurs clients** (plus gros CA)
> - Les **clients dormants** (dernière commande ancienne)
> - Les **fournisseurs principaux** (plus gros volumes)

---

## 7. 🖨️ Imprimer les rapports PDF

### Fiche contact

1. Aller dans : Contacts → Rapports → **Fiche contact**
2. Cocher les contacts
3. Imprimer → **Fiche contact**
4. Le PDF contient :
   - Informations de base (nom, adresse, téléphone, email)
   - Informations légales (ICE, RC, IF, CNSS)
   - Type de relation et priorité
   - Segments
   - Statistiques commerciales
   - Réseaux sociaux
   - Notes internes

---

## 8. 💡 FAQ & Astuces

### Questions fréquentes

**Q : Comment fusionner deux fiches contact en double ?**
> Sélectionnez les deux contacts dans la vue liste → Action → Fusionner. Gardez la fiche la plus complète.

**Q : Comment voir tous les clients VIP ?**
> Utilisez le filtre **VIP** dans la barre de recherche, ou filtrez par **Priorité = VIP**.

**Q : Comment trouver les prospects à relancer ?**
> Filtrez par **Type = Prospect** et triez par **Dernière commande** (vide = jamais commandé).

**Q : Le champ ICE est-il obligatoire ?**
> Non dans le système, mais il est **légalement obligatoire** au Maroc pour toute entreprise. Renseignez-le systématiquement.

### Filtres recommandés

| Filtre | Usage |
|--------|-------|
| **Prospects** | Contacts à convertir en clients |
| **Clients** | Base client existante |
| **Fournisseurs** | Répertoire fournisseurs |
| **VIP** | Contacts prioritaires |
| **Partenaires** | Réseau de partenaires |

---

*Guide Contacts — ERP Commercial Odoo 17 | Mis à jour le 26/03/2026*
