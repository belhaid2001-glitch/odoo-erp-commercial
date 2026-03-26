# Module 3 : Gestion Commerciale - Stock & Inventaire (custom_stock)

**Version** : 17.0.1.0.0  
**Catégorie** : Inventory  
**Dépendances** : stock, product  
**Plateforme** : Odoo 17 Community Edition  

---

## 1. Vue d'ensemble

Module de gestion avancée du stock et de l'inventaire qui étend le module standard Odoo Stock avec un workflow de préparation de commandes, la lecture de codes-barres, un système complet de contrôle qualité, le suivi des expéditions et un rapport de valorisation d'inventaire par vue SQL.

---

## 2. Fonctionnalités détaillées

### 2.1. Gestion avancée des transferts (stock.picking)

#### Priorisation des transferts
- Champ **Priorité personnalisée** avec 5 niveaux : Normale, Basse, Moyenne, Haute, Urgente
- Widget étoiles dans le formulaire et la vue liste

#### Workflow de préparation de commandes
- **Statut de préparation** en 4 étapes :
  - **Non commencée** → Bouton "Commencer préparation"
  - **En cours** → Bouton "Prêt"
  - **Prête** → Bouton "Expédié"
  - **Expédiée** (état final)
- Notification automatique dans le chatter lors du démarrage de la préparation
- Vérification automatique : impossible de marquer comme "Prêt" si le contrôle qualité est requis et non validé
- Badge coloré dans la vue liste (bleu=non commencée, orange=en cours, vert=prête/expédiée)

#### Lecture de codes-barres
- Champ **Code-barre scanné** dans le formulaire
- `onchange` automatique : recherche le produit par code-barre EAN dans la base
- Si trouvé : incrémente automatiquement la quantité de la ligne correspondante
- Si non trouvé : affiche un avertissement avec le code-barre saisi
- Permet un flux de préparation rapide par scan sans souris/clavier

#### Informations d'expédition
- **Numéro de suivi transporteur** (carrier_tracking) avec tracking
- **Instructions de livraison** : notes texte pour le préparateur/livreur
- **Notes de préparation** : zone de texte pour consignes internes
- **Nombre de colis** : champ numérique (défaut : 1)
- **Poids total (kg)** : calculé automatiquement à partir du poids de chaque produit × quantité dans les lignes de mouvement

### 2.2. Contrôle qualité intégré (stock.quality.check)

#### Modèle complet de contrôle qualité
- **Référence** auto-générée par séquence : QC/2026/0001
- **Transfert** : lien vers le picking concerné (One2many)
- **Produit** : produit à contrôler
- **Quantité à contrôler / contrôlée / défectueuse** : suivi quantitatif complet
- **Type de contrôle** : Visuel, Dimensionnel, Fonctionnel, Documentation
- **Résultat** : En attente → Réussi / Échoué (avec tracking)
- **Inspecteur** : utilisateur effectuant le contrôle (par défaut : utilisateur courant)
- **Date du contrôle** : horodatage automatique à la validation
- **Lot / N° de série** : lien vers stock.lot
- **Équipe qualité** : lien vers l'équipe responsable
- **Observations** : notes texte

#### Actions de contrôle
- Bouton **"✓" (Valider)** : marque le contrôle comme réussi, enregistre la date et la quantité
- Bouton **"✗" (Échouer)** : marque le contrôle comme échoué
- Bouton **"Réinitialiser"** : remet en attente
- Édition inline dans un onglet dédié du formulaire de transfert

#### Création automatique
- Bouton **"Créer contrôles qualité"** sur le transfert : génère automatiquement un contrôle pour chaque ligne de mouvement (produit + quantité)
- Active automatiquement le flag `quality_check_required` sur le transfert

#### Statut qualité global
- Champ calculé **Statut qualité** sur le transfert :
  - **Aucun** : pas de contrôles
  - **En attente** : des contrôles non terminés
  - **Réussi** : tous les contrôles passés
  - **Échoué** : au moins un contrôle échoué
- Badge coloré (vert=réussi, rouge=échoué, orange=en attente)

### 2.3. Équipes qualité (stock.quality.team)

- **Nom de l'équipe**
- **Responsable** : res.users
- **Membres** : Many2many vers res.users
- **Actif** : booléen pour archivage

### 2.4. Rapport de valorisation d'inventaire (stock.valuation.report)

#### Vue SQL (rapport BI)
- Modèle avec `_auto = False` : vue PostgreSQL créée par `init()`
- **Sources** : stock_quant × product_product × product_template × ir_property × stock_location
- **Filtre** : uniquement les emplacements internes avec quantité > 0

#### Colonnes du rapport
| Colonne | Description |
|---------|-------------|
| Produit | Nom du produit |
| Catégorie | Catégorie du produit |
| Emplacement | Emplacement de stock |
| Quantité en stock | Quantité disponible |
| Coût unitaire | Prix standard (ir_property) |
| Valeur totale | Quantité × Coût unitaire |
| UdM | Unité de mesure |
| Société | Société propriétaire |

#### Vues disponibles
- Vue **liste** avec colonnes complètes
- Vue **pivot** : lignes par catégorie, colonnes par emplacement, mesures quantité + valeur totale
- Vue **graphique** : barres par catégorie avec valeur totale

#### Menu dédié
- Sous-menu "Rapports > Valorisation d'inventaire" dans le module Inventaire

---

## 3. Modèles de données

| Modèle | Description | Type |
|--------|-------------|------|
| `stock.picking` | Extension des transferts de stock | Héritage (_inherit) |
| `stock.quality.check` | Contrôle qualité unitaire | Nouveau modèle |
| `stock.quality.team` | Équipe qualité | Nouveau modèle |
| `stock.valuation.report` | Rapport de valorisation (vue SQL) | Nouveau modèle (_auto=False) |

---

## 4. Sécurité / Droits d'accès

- `stock.quality.check` : accès CRUD pour stock_user
- `stock.quality.team` : accès CRUD pour stock_user
- `stock.valuation.report` : accès lecture pour stock_user

---

## 5. Données de configuration

- Séquence automatique pour les contrôles qualité : `QC/%(year)s/XXXX`
