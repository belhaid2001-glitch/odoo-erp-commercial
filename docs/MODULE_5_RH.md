# Module 5 : Gestion Commerciale - Ressources Humaines (custom_hr)

**Version** : 17.0.1.0.0  
**Catégorie** : Human Resources  
**Dépendances** : hr, hr_contract, hr_holidays, hr_recruitment  
**Plateforme** : Odoo 17 Community Edition  

---

## 1. Vue d'ensemble

Module de gestion avancée des ressources humaines qui étend le module standard Odoo HR avec des informations employé enrichies (CIN, CNSS, groupe sanguin, contact d'urgence), un calcul d'ancienneté automatique, un système complet d'évaluations de performance avec 6 critères de notation, des objectifs SMART et un suivi des compétences et formations.

---

## 2. Fonctionnalités détaillées

### 2.1. Fiche employé enrichie (hr.employee)

#### Informations contractuelles
- **Type de contrat** : CDI, CDD, Stagiaire, Freelance, Consultant (avec tracking)
- **Date d'embauche** : date avec tracking
- **Date de fin de contrat** : pour les CDD et stages
- **Ancienneté (années)** : calculée automatiquement en temps réel = (aujourd'hui - date d'embauche) / 365.25, arrondie à 0.1

#### Identité marocaine
- **CIN** : numéro de Carte d'Identité Nationale (avec tracking)
- **N° CNSS** : numéro d'affiliation à la Caisse Nationale de Sécurité Sociale (avec tracking)
- **Groupe sanguin** : sélection parmi A+, A-, B+, B-, AB+, AB-, O+, O-

#### Contact d'urgence
- **Nom du contact d'urgence**
- **Téléphone d'urgence**
- **Relation** : lien de parenté/relation avec le contact

#### Compétences & Formation
- **Compétences** : zone de texte pour lister les compétences de l'employé
- **Notes de formation** : zone de texte pour formations suivies et certifications
- Onglet dédié "Compétences & Formation" dans le formulaire employé

#### Performance (calculé)
- **Dernière évaluation** : date de la dernière évaluation (calculée)
- **Dernier score** : score global de la dernière évaluation (calculé)
- **Nombre d'évaluations** : compteur total

#### Vues
- **Formulaire** : 2 onglets supplémentaires "Informations RH" et "Compétences & Formation"
- **Bouton statistique** "Évaluations" dans la boîte de boutons avec compteur
- **Vue liste** : colonnes supplémentaires Type de contrat, Date d'embauche, Ancienneté, Dernier score (optionnelles)

#### Actions
- **Voir les évaluations** : ouvre la liste des évaluations de l'employé
- **Nouvelle évaluation** : ouvre le formulaire de création pré-rempli avec l'employé et l'évaluateur courant

### 2.2. Évaluations de performance (hr.evaluation)

#### Modèle complet d'évaluation
- **Référence** auto-générée par séquence : EVAL/2026/0001
- **Employé** : lien requis vers hr.employee
- **Département** et **Poste** : remplis automatiquement via related
- **Évaluateur** : utilisateur (par défaut : utilisateur courant)
- **Date d'évaluation** : date requise (défaut : aujourd'hui)
- **Période** : Date début et Date fin de la période évaluée
- **Type d'évaluation** : Annuelle, Semestrielle, Trimestrielle, Fin de période d'essai, Spéciale

#### Workflow d'évaluation
- États : Brouillon → En cours → Terminée / Annulée
- Boutons d'action : Commencer, Terminer, Annuler, Remettre en brouillon
- Barre de statut avec suivi visuel
- Chatter complet (messages, activités, followers)

#### Système de notation (6 critères)
Chaque critère est noté de 1 à 5 avec des libellés explicites :

| Critère | Catégorie |
|---------|-----------|
| **Qualité du travail** | Performance |
| **Productivité** | Performance |
| **Initiative** | Performance |
| **Travail d'équipe** | Comportement |
| **Ponctualité** | Comportement |
| **Communication** | Comportement |

- Notation par **widget radio** (sélection visuelle)
- Chaque note : 1=Insuffisant, 2=À améliorer, 3=Satisfaisant, 4=Bon, 5=Excellent

#### Score global & Appréciation
- **Score global** : moyenne arithmétique des critères renseignés (0.0 à 5.0)
- **Appréciation globale** : calculée automatiquement :
  - ≥ 4.5 → **Excellent**
  - ≥ 3.5 → **Bon**
  - ≥ 2.5 → **Satisfaisant**
  - ≥ 1.5 → **À améliorer**
  - < 1.5 → **Insuffisant**
- Badge coloré (vert=Bon/Excellent, orange=Satisfaisant, rouge=Insuffisant/À améliorer)

#### Commentaires & Retours
- **Points forts** : zone de texte
- **Points à améliorer** : zone de texte
- **Objectifs prochaine période** : zone de texte
- **Commentaires de l'évaluateur** : zone de texte
- **Commentaires de l'employé** : zone de texte (permet le feedback bidirectionnel)

### 2.3. Objectifs d'évaluation (hr.evaluation.goal)

#### Gestion des objectifs SMART
- **Objectif** : nom/titre de l'objectif (requis)
- **Description** : détail de l'objectif
- **Échéance** : date limite
- **Poids (%)** : pondération de l'objectif (défaut : 100%)
- **Réalisation (%)** : pourcentage d'avancement (widget progressbar)
- **Statut** : Non commencé → En cours → Atteint / Non atteint
- **Notes** : zone de texte

#### Intégration
- Onglet dédié "Objectifs" dans le formulaire d'évaluation
- Édition inline en arborescence
- Badges colorés : vert=Atteint, orange=En cours, rouge=Non atteint, bleu=Non commencé

### 2.4. Vues analytiques

#### Vue liste des évaluations
- Couleurs conditionnelles sur les lignes (vert=Bon/Excellent, orange=Satisfaisant, rouge=mauvais)
- Badge pour l'appréciation globale et l'état
- Colonnes : Référence, Employé, Département, Évaluateur, Date, Type, Score, Appréciation, État

#### Vue Pivot
- Lignes : Département
- Colonnes : Type d'évaluation
- Mesure : Score global
- Permet l'analyse croisée des performances par département et type d'évaluation

#### Vue Graphique
- Type : Barres
- Axe X : Département
- Mesure : Score global moyen
- Visualisation rapide des performances par département

---

## 3. Modèles de données

| Modèle | Description | Type |
|--------|-------------|------|
| `hr.employee` | Extension de la fiche employé | Héritage (_inherit) |
| `hr.evaluation` | Évaluation de performance | Nouveau modèle |
| `hr.evaluation.goal` | Objectif d'évaluation | Nouveau modèle |

---

## 4. Sécurité / Droits d'accès

- `hr.evaluation` : accès CRUD pour hr_user
- `hr.evaluation.goal` : accès CRUD pour hr_user

---

## 5. Données de configuration

- Séquence automatique pour les évaluations : `EVAL/%(year)s/XXXX`

---

## 6. Points clés

- Adapté au contexte marocain (CIN, CNSS)
- Évaluation multi-critères avec scoring automatique
- Objectifs SMART avec suivi de progression
- Feedback bidirectionnel évaluateur/employé
- Analyses pivot et graphiques pour le pilotage RH
