# Module 1 : Gestion Commerciale - Vente (custom_sale)

**Version** : 17.0.1.0.0  
**Catégorie** : Sales  
**Dépendances** : sale_management, sale_margin, sale_stock, account, portal  
**Plateforme** : Odoo 17 Community Edition  

---

## 1. Vue d'ensemble

Module de gestion avancée des ventes qui étend le module standard Odoo Sales avec des fonctionnalités de priorisation, un workflow d'approbation, des produits optionnels, des prévisions commerciales et un tableau de bord KPI.

---

## 2. Fonctionnalités détaillées

### 2.1. Gestion avancée des commandes de vente (sale.order)

#### Priorisation des commandes
- Champ **Priorité** avec 5 niveaux : Normale, Basse, Moyenne, Haute, Urgente
- Affichage en widget étoiles dans le formulaire et la liste
- Filtrage rapide des commandes à haute priorité

#### Référence client & Type de vente
- **Référence Client** : champ texte pour stocker la référence communiquée par le client (avec suivi/tracking)
- **Type de vente** : Standard, Abonnement ou Projet (avec suivi)

#### Workflow d'approbation
- **Statut d'approbation** : Brouillon → En attente d'approbation → Approuvé / Rejeté
- Bouton **"Demander approbation"** visible uniquement pour les devis en brouillon
- Boutons **"Approuver"** et **"Rejeter"** réservés aux responsables commerciaux (groupe sale_manager)
- Traçabilité complète : champ **Approuvé par** (utilisateur) et **Date d'approbation**
- Notifications automatiques dans le chatter à chaque étape du workflow
- Affichage du statut en badge coloré dans la vue liste (bleu=en attente, vert=approuvé, rouge=rejeté)

#### Indicateurs de performance
- **Marge (%)** : calcul automatique du pourcentage de marge basé sur le champ `margin` du module sale_margin et le montant HT
- **Remise totale** : somme calculée de toutes les remises appliquées sur les lignes de commande (prix unitaire × quantité × % remise)
- **Prêt à facturer** : booléen calculé automatiquement (commande confirmée + statut facturation = à facturer)

#### Instructions de livraison
- Champ texte **Instructions de livraison** pour des consignes spéciales
- Affichées dans un onglet dédié "Informations complémentaires"

### 2.2. Produits optionnels (sale.order.optional.product)

- Modèle dédié `sale.order.optional.product` lié à la commande (One2many)
- Champs : Produit, Description, Quantité, Prix unitaire, Sélectionné (oui/non)
- **Auto-remplissage** : lors de la sélection d'un produit, la description et le prix se remplissent automatiquement (onchange)
- Bouton **"Ajouter"** sur chaque ligne pour convertir un produit optionnel en ligne de commande réelle
- L'ajout crée automatiquement une ligne `sale.order.line` avec les infos du produit optionnel
- Onglet dédié "Produits optionnels" dans le formulaire de commande avec édition inline

### 2.3. Facturation en lot
- Action **"Facturation en lot"** : sélectionner plusieurs commandes prêtes à facturer et générer toutes les factures en un clic
- Vérification automatique : seules les commandes avec `is_ready_to_invoice = True` sont traitées
- Après génération, ouverture d'une vue liste des factures créées

### 2.4. Prévisions de vente (sale.forecast)

#### Modèle complet de prévision
- **Référence** auto-générée par séquence : PREV/2026/0001
- Champs : Date de prévision, Date cible, Commercial, Équipe commerciale, Client, Produit
- **Montant prévu** : objectif de vente en devise de la société
- **Montant réalisé** : calculé automatiquement à partir des commandes confirmées sur la période (filtré par commercial, client, produit si renseignés)
- **Taux de réalisation (%)** : (réalisé / prévu) × 100, affiché en widget progressbar

#### Workflow de prévision
- États : Brouillon → Confirmée → Terminée / Annulée
- Boutons d'action dans le header avec barre de statut
- Support du chatter (suivi, activités, messages)

#### Vues multiples
- **Liste** : avec couleurs conditionnelles (vert ≥100%, orange 50-100%, rouge <50%)
- **Formulaire** : complet avec notebook Notes
- **Pivot** : lignes par commercial, colonnes par mois, mesures montant prévu/réalisé
- **Graphique** : barres groupées par mois avec montant prévu vs réalisé

### 2.5. Tableau de bord & Recherche avancée

#### Filtres de recherche personnalisés
- **Haute priorité** : filtre les commandes priorité 3 ou 4
- **Prêt à facturer** : commandes prêtes à être facturées
- **En attente d'approbation** : commandes en attente de validation
- **Mois en cours** : commandes du mois courant

#### Regroupements
- Par **Type de vente** (Standard, Abonnement, Projet)
- Par **Statut d'approbation**
- Par **Priorité**

### 2.6. Rapport PDF personnalisé
- Extension du rapport standard de commande de vente
- Ajout des **Instructions de livraison** et de la **Référence client** dans le document PDF imprimé

---

## 3. Modèles de données

| Modèle | Description | Type |
|--------|-------------|------|
| `sale.order` | Extension de la commande de vente | Héritage (_inherit) |
| `sale.order.optional.product` | Produits optionnels d'une commande | Nouveau modèle |
| `sale.forecast` | Prévisions de vente | Nouveau modèle |

---

## 4. Sécurité / Droits d'accès

- `sale.order.optional.product` : accès CRUD complet pour le groupe sale_user
- `sale.forecast` : accès CRUD complet pour le groupe sale_user
- Boutons d'approbation limités au groupe `sales_team.group_sale_manager`

---

## 5. Données de démonstration / Configuration

- Séquence automatique pour les prévisions : `PREV/%(year)s/XXXX`
