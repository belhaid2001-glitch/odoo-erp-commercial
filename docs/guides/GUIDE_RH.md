# 👥 Guide Utilisateur — Module Ressources Humaines

> **Public cible** : Responsable RH, Managers d'équipe, Direction générale
> **Accès** : Menu principal → **Employés** (RH)

---

## 📋 Sommaire

1. [Présentation du module](#1--présentation-du-module)
2. [Gérer les fiches employés](#2--gérer-les-fiches-employés)
3. [Informations spécifiques Maroc](#3--informations-spécifiques-maroc)
4. [Système d'évaluation](#4--système-dévaluation)
5. [Objectifs et suivi de performance](#5--objectifs-et-suivi-de-performance)
6. [Imprimer les rapports PDF](#6--imprimer-les-rapports-pdf)
7. [FAQ & Astuces](#7--faq--astuces)

---

## 1. 📌 Présentation du module

Le module **RH** gère les ressources humaines de l'entreprise :

```
Recrutement → Embauche → Fiche employé → Évaluations → Évolution de carrière
```

**Fonctionnalités clés :**
- **Fiches employés enrichies** avec données marocaines (CIN, CNSS)
- **5 types de contrat** : CDI, CDD, Stagiaire, Freelance, Consultant
- **Système d'évaluation** complet avec 6 critères de notation
- **Objectifs individuels** avec poids et suivi de réalisation
- **Contact d'urgence** avec nom, téléphone et relation
- Calcul automatique de l'**ancienneté**

---

## 2. 📝 Gérer les fiches employés

### Créer un employé

1. **Aller dans** : Employés → Employés
2. Cliquer sur **➕ Nouveau**
3. Remplir les informations principales :

| Champ | Description | Obligatoire |
|-------|-------------|:-----------:|
| **Nom** | Nom complet de l'employé | ✅ |
| **Poste** | Intitulé du poste | ✅ |
| **Département** | Département de rattachement | ✅ |
| **Manager** | Responsable hiérarchique | Non |
| **Type de contrat** | CDI / CDD / Stagiaire / Freelance / Consultant | ✅ |
| **Date d'embauche** | Date de prise de poste | ✅ |
| **Date de fin** | Pour CDD / Stage uniquement | Non |

### Onglet Informations RH (spécifique)

| Champ | Description |
|-------|-------------|
| **CIN** | Carte d'Identité Nationale |
| **N° CNSS** | Numéro d'immatriculation Caisse Nationale de Sécurité Sociale |
| **Groupe sanguin** | A+, A-, B+, B-, AB+, AB-, O+, O- |
| **Contact d'urgence** | Nom, Téléphone, Relation |

### Onglet Compétences & Formation

| Champ | Description |
|-------|-------------|
| **Compétences** | Description des compétences techniques et soft skills |
| **Notes de formation** | Formations suivies, certifications, besoins identifiés |

### Informations calculées automatiquement

| Indicateur | Description |
|-----------|-------------|
| **Ancienneté (années)** | Calculée depuis la date d'embauche |
| **Nb évaluations** | Nombre total d'évaluations (bouton statistique) |
| **Dernière évaluation** | Date de la dernière évaluation |
| **Dernier score** | Score global de la dernière évaluation |

> 💡 **Astuce** : Cliquez sur le bouton statistique **"X Évaluations"** en haut de la fiche pour voir l'historique complet.

---

## 3. 🇲🇦 Informations spécifiques Maroc

Le module est adapté au contexte marocain :

| Champ | Usage |
|-------|-------|
| **CIN** | Obligatoire pour tous les employés marocains |
| **N° CNSS** | Pour la déclaration à la Caisse Nationale de Sécurité Sociale |
| **Groupe sanguin** | Information médicale d'urgence (obligatoire dans certaines entreprises) |
| **Contact d'urgence** | Personne à prévenir en cas d'accident |

> 📌 Ces champs sont dans l'onglet **Informations RH** de la fiche employé.

---

## 4. 📊 Système d'évaluation

### Créer une évaluation

1. **Aller dans** : Employés → Évaluations → Évaluations
2. Cliquer sur **➕ Nouveau**
3. Remplir :

| Champ | Description | Obligatoire |
|-------|-------------|:-----------:|
| **Employé** | L'employé évalué | ✅ |
| **Évaluateur** | Manager ou RH qui évalue | ✅ |
| **Type d'évaluation** | Annuelle / Semestrielle / Trimestrielle / Période d'essai / Spéciale | ✅ |
| **Période évaluée** | Date début → Date fin | ✅ |
| **Date d'évaluation** | Date de l'entretien | ✅ |

### Les 6 critères de notation

Chaque critère est noté de **1 à 5** :

| Critère | Description | Barème |
|---------|-------------|--------|
| ⭐ **Qualité du travail** | Précision, fiabilité, conformité | 1-5 |
| ⚡ **Productivité** | Volume de travail, respect des délais | 1-5 |
| 💡 **Initiative** | Proactivité, propositions d'amélioration | 1-5 |
| 🤝 **Travail d'équipe** | Collaboration, communication, entraide | 1-5 |
| ⏰ **Ponctualité** | Respect des horaires et des deadlines | 1-5 |
| 🗣️ **Communication** | Clarté, écoute, feedback | 1-5 |

### Score global et appréciation

Le **score global** est la **moyenne** des 6 critères.

| Score | Appréciation | Signification |
|-------|-------------|---------------|
| 1.0 - 1.5 | ❌ **Insuffisant** | Performance très en dessous des attentes |
| 1.5 - 2.5 | ⚠️ **À améliorer** | Plusieurs axes d'amélioration importants |
| 2.5 - 3.5 | 🟡 **Satisfaisant** | Performance conforme aux attentes |
| 3.5 - 4.5 | 🟢 **Bon** | Performance au-dessus des attentes |
| 4.5 - 5.0 | ⭐ **Excellent** | Performance exceptionnelle |

### Section commentaires

| Champ | Qui remplit | Description |
|-------|------------|-------------|
| **Points forts** | Évaluateur | Ce que l'employé fait bien |
| **Axes d'amélioration** | Évaluateur | Ce qui doit progresser |
| **Objectifs** | Évaluateur + Employé | Objectifs pour la prochaine période |
| **Commentaires de l'employé** | Employé | Réaction et feedback de l'employé |
| **Commentaires de l'évaluateur** | Évaluateur | Synthèse et recommandations |

### Workflow de l'évaluation

```
📝 Brouillon → 🔄 En cours (entretien) → ✅ Terminée
                                          ↘ ❌ Annulée
```

1. **Brouillon** : L'évaluateur prépare le formulaire
2. **En cours** : L'entretien a lieu, les scores sont renseignés
3. **Terminée** : L'évaluation est finalisée et archivée

---

## 5. 🎯 Objectifs et suivi de performance

### Ajouter des objectifs à une évaluation

1. Ouvrir l'évaluation
2. Aller à la section **Objectifs**
3. Cliquer sur **Ajouter une ligne**
4. Remplir :

| Champ | Description |
|-------|-------------|
| **Objectif** | Nom court de l'objectif |
| **Description** | Détails et critères de réussite |
| **Échéance** | Date limite |
| **Poids (%)** | Importance relative (total devrait = 100%) |
| **Réalisation (%)** | Avancement actuel (0-100%) |
| **Statut** | Non commencé / En cours / Atteint / Non atteint |

### Suivi dans le temps

- Mettez à jour la **Réalisation (%)** à chaque point d'étape
- Changez le **Statut** quand l'objectif est atteint ou non
- Utilisez la vue **Pivot** des évaluations pour une analyse par département

> 💡 **Astuce** : Définissez les objectifs lors de l'évaluation, puis faites un point d'avancement mensuel.

---

## 6. 🖨️ Imprimer les rapports PDF

### Fiche employé

1. Aller dans : Employés → Rapports → **Fiche employé**
2. Cocher les employés
3. Imprimer → **Fiche employé**
4. Le PDF contient :
   - Photo et informations personnelles
   - Type de contrat, département, poste
   - CIN, CNSS, groupe sanguin
   - Contact d'urgence
   - Compétences et formations
   - Ancienneté

### Rapport d'évaluation

1. Aller dans : Employés → Rapports → **Rapport d'évaluation**
2. Cocher les évaluations
3. Imprimer → **Rapport d'évaluation**
4. Le PDF contient :
   - Informations employé et évaluateur
   - Période évaluée
   - Les 6 scores et le score global
   - Appréciation globale
   - Objectifs avec avancement
   - Commentaires des deux parties
   - Zone de signature

---

## 7. 💡 FAQ & Astuces

### Questions fréquentes

**Q : Comment planifier les évaluations annuelles ?**
> Créez les évaluations en **Brouillon** pour tous les employés du département. Programmez les entretiens par calendrier. Passez en **En cours** le jour J.

**Q : L'employé peut-il voir son évaluation ?**
> Par défaut, seuls les RH et managers ont accès. Vous pouvez partager le PDF imprimé lors de l'entretien.

**Q : Comment calculer l'ancienneté ?**
> Elle est automatique depuis la **Date d'embauche**. Aucune action requise.

**Q : Comment gérer un CDD qui devient CDI ?**
> Modifiez le **Type de contrat** sur la fiche employé. L'historique reste dans le chatter.

**Q : Comment suivre les formations ?**
> Utilisez le champ **Notes de formation** sur la fiche employé pour tracker les formations suivies et les besoins.

### Types d'évaluation recommandés

| Type | Fréquence | Pour qui |
|------|-----------|----------|
| **Annuelle** | 1x/an (décembre-janvier) | Tous les employés |
| **Semestrielle** | 2x/an | Managers et postes clés |
| **Trimestrielle** | 4x/an | Commerciaux (objectifs chiffrés) |
| **Période d'essai** | Fin de période d'essai | Nouveaux employés |
| **Spéciale** | Sur demande | Promotion, alerte performance |

---

*Guide RH — ERP Commercial Odoo 17 | Mis à jour le 26/03/2026*
