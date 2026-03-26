# Module 2 : Gestion Commerciale - Achats (custom_purchase)

**Version** : 17.0.1.0.0  
**Catégorie** : Purchase  
**Dépendances** : purchase, purchase_stock, account  
**Plateforme** : Odoo 17 Community Edition  

---

## 1. Vue d'ensemble

Module de gestion avancée des achats qui étend le module standard Odoo Purchase avec la gestion des conventions/accords-cadres fournisseurs, un suivi de réception intelligent, un contrôle qualité intégré et le calcul automatique des économies réalisées.

---

## 2. Fonctionnalités détaillées

### 2.1. Gestion avancée des commandes d'achat (purchase.order)

#### Priorisation des commandes
- Champ **Priorité** avec 5 niveaux : Normale, Basse, Moyenne, Haute, Urgente
- Widget étoiles dans le formulaire et la vue liste

#### Référence et classification
- **Référence Fournisseur** : référence communiquée par le fournisseur (avec tracking)
- **Type d'achat** : Standard, Urgent, Marché-cadre, Récurrent (avec tracking)
- **Convention d'achat** : lien vers une convention/accord-cadre existant

#### Lien avec les conventions d'achat
- Sélection d'une convention lors de la création de la commande
- **Application automatique** des conditions de la convention (conditions de paiement, notes spéciales) via `onchange`
- Calcul des **économies réalisées** : pour chaque ligne, comparaison entre le prix standard du produit et le prix négocié dans la convention

#### Suivi de réception intelligent
- **Statut de réception** calculé automatiquement : En attente / Partielle / Complète
- Basé sur l'état réel des transferts (pickings) associés à la commande
- Badge coloré : bleu=en attente, orange=partielle, vert=complète
- Bouton **"Voir les réceptions"** pour accéder directement aux transferts liés

#### Approbation automatique
- Champ calculé **Approbation requise** : activé automatiquement si le montant total dépasse 50 000 (seuil configurable)

#### Conditionnement & Qualité
- Onglet dédié "Conditionnement & Qualité" dans le formulaire
- **Instructions de conditionnement** : notes texte pour le fournisseur
- **Contrôle qualité requis** : case à cocher + **Notes qualité** (visible uniquement si le contrôle est requis)

#### Indicateurs KPI
- **Économies réalisées** : montant total des économies par rapport aux prix standards
- **Statut de réception** : en badge avec couleurs conditionnelles

### 2.2. Conventions d'achat / Accords-cadres (purchase.convention)

#### Modèle complet de convention
- **Référence** auto-générée par séquence
- **Fournisseur** : partenaire avec filtre `supplier_rank > 0`
- **Période** : Date début et Date fin
- **Conditions de paiement** : lien vers account.payment.term
- **Remise globale (%)** : remise négociée s'appliquant à toute la convention
- **Montant minimum / maximum** : bornes de la convention

#### Workflow de convention
- États : Brouillon → Active → Expirée / Annulée
- Boutons d'action : Activer, Expirer, Annuler, Remettre en brouillon
- Barre de statut avec suivi visuel
- Support complet du chatter (messages, activités, followers)

#### Lignes de convention (purchase.convention.line)
- **Produit** : produit concerné par la convention
- **Quantité minimum / maximum** : bornes de quantité
- **Prix négocié** : prix spécial négocié avec le fournisseur
- **Remise (%)** : remise spécifique au produit
- **Unité de mesure** : affichée automatiquement via related

#### Suivi de consommation
- **Nombre de commandes** : compteur des commandes liées à cette convention
- **Total commandé** : montant HT cumulé des commandes confirmées liées
- Bouton **"Voir les commandes"** : accès direct à la liste filtrée des commandes d'achat

#### Expiration automatique (CRON)
- Job planifié `_cron_check_expiration` : vérifie quotidiennement les conventions actives dont la date de fin est dépassée et les passe automatiquement en statut "Expirée"

### 2.3. Tableau de bord Achats

#### Vue liste étendue
- Colonnes ajoutées : Priorité (étoiles), Type d'achat, Convention, Statut de réception (badge)
- Colonnes optionnelles masquables par l'utilisateur

---

## 3. Modèles de données

| Modèle | Description | Type |
|--------|-------------|------|
| `purchase.order` | Extension de la commande d'achat | Héritage (_inherit) |
| `purchase.convention` | Convention / accord-cadre fournisseur | Nouveau modèle |
| `purchase.convention.line` | Ligne de convention (produit + prix négocié) | Nouveau modèle |

---

## 4. Sécurité / Droits d'accès

- `purchase.convention` : accès CRUD complet pour le groupe purchase_user
- `purchase.convention.line` : accès CRUD complet pour le groupe purchase_user

---

## 5. Automatisations

- **CRON d'expiration** : vérification automatique quotidienne des conventions arrivées à terme → passage en état "Expirée"
- **Onchange convention** : application automatique des conditions de paiement et notes lors de la sélection d'une convention
