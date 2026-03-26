# 📅 Guide Utilisateur — Module Calendrier

> **Public cible** : Tous les employés (commerciaux, managers, assistants)
> **Accès** : Menu principal → **Calendrier**

---

## 📋 Sommaire

1. [Présentation du module](#1--présentation-du-module)
2. [Créer un événement](#2--créer-un-événement)
3. [Types de rendez-vous](#3--types-de-rendez-vous)
4. [Rédiger un compte-rendu](#4--rédiger-un-compte-rendu)
5. [Suivi post-réunion](#5--suivi-post-réunion)
6. [Imprimer les rapports PDF](#6--imprimer-les-rapports-pdf)
7. [FAQ & Astuces](#7--faq--astuces)

---

## 1. 📌 Présentation du module

Le module **Calendrier** centralise tous les rendez-vous et réunions :

```
Planifier → Préparer → Réunion → Compte-rendu → Suivi
```

**Fonctionnalités clés :**
- **9 types de RDV** (réunion, appel, visite client, formation, démo, etc.)
- **4 types de lieu** (bureau, chez le client, visioconférence, externe)
- **Compte-rendu** (PV de réunion) intégré
- **Suivi post-réunion** avec date de relance
- Lien automatique avec le module **CRM**
- **Priorité** et **résultat** de chaque réunion

---

## 2. 📝 Créer un événement

### Étape par étape

1. **Aller dans** : Calendrier
2. Cliquer sur un créneau dans le calendrier ou **➕ Nouveau**
3. Remplir :

| Champ | Description | Obligatoire |
|-------|-------------|:-----------:|
| **Résumé** (nom) | Objet de la réunion | ✅ |
| **Date de début** | Date et heure | ✅ |
| **Date de fin** | Date et heure | ✅ |
| **Type de RDV** | Voir section suivante | Non |
| **Priorité** | Normal / Basse / Haute / Urgente | Non |
| **Participants** | Employés et/ou contacts externes | Non |
| **Type de lieu** | Bureau / Chez le client / Visio / Externe | Non |
| **Lien visioconférence** | URL Teams, Zoom, Google Meet... | Non |

4. **Onglet Préparation** :
   - Saisir les **Notes de préparation** : ordre du jour, documents à apporter

5. Cliquer sur **💾 Sauvegarder**

---

## 3. 📋 Types de rendez-vous

| Type | Usage habituel |
|------|---------------|
| 📋 **Réunion** | Réunion interne d'équipe |
| 📞 **Appel** | Appel téléphonique planifié |
| 🏢 **Visite client** | Déplacement chez un client |
| 🏭 **Visite fournisseur** | Déplacement chez un fournisseur |
| 📚 **Formation** | Session de formation |
| 💻 **Démonstration** | Démo produit/service |
| 🤝 **Entretien** | Entretien RH (recrutement, évaluation) |
| 🔒 **Interne** | Point rapide, stand-up, retrospective |
| ❓ **Autre** | Tout autre type |

### Configurer les types

1. **Aller dans** : Calendrier → Configuration → Types de rendez-vous
2. Créer ou modifier :
   - **Nom** du type
   - **Couleur** pour le repérage visuel
   - **Durée par défaut** (en heures)
   - **Description** du type

---

## 4. 📝 Rédiger un compte-rendu

Après la réunion :

1. Ouvrir l'événement
2. Aller à l'onglet **Compte-rendu**
3. Rédiger le **PV de réunion** (éditeur HTML riche) :
   - Participants présents
   - Points discutés
   - Décisions prises
   - Actions à mener

> 💡 **Astuce** : Rédigez le compte-rendu **le jour même** pendant que tout est frais. Utilisez des listes à puces pour structurer.

---

## 5. 🔄 Suivi post-réunion

### Marquer le résultat

Après la réunion, renseignez le **Résultat** :

| Résultat | Signification |
|----------|---------------|
| ⏳ **En attente** | Pas encore déterminé |
| ✅ **Positif** | La réunion a atteint ses objectifs |
| ➖ **Neutre** | RAS, suivi normal |
| ❌ **Négatif** | Objectifs non atteints, problème |

### Programmer un suivi

Si des actions sont nécessaires après la réunion :

1. Cocher **☑ Suivi requis**
2. Renseigner la **Date de suivi** (deadline)
3. Ajouter les **Notes de suivi** : actions à mener, responsables

> 📌 Utilisez le filtre **Suivi requis** dans la vue liste pour retrouver toutes les réunions nécessitant un suivi.

---

## 6. 🖨️ Imprimer les rapports PDF

### Rapport de réunion

1. Aller dans : Calendrier → Rapports → **Rapport de réunion**
2. Cocher les événements
3. Imprimer → **Rapport de réunion**
4. Le PDF contient :
   - Date, heure, lieu
   - Type de RDV et priorité
   - Participants
   - Notes de préparation
   - Compte-rendu complet
   - Résultat et suivi
   - Actions à mener

> 💡 Ce rapport peut servir de **PV officiel** à envoyer aux participants après la réunion.

---

## 7. 💡 FAQ & Astuces

### Questions fréquentes

**Q : Comment synchroniser avec Google Calendar ou Outlook ?**
> Odoo 17 propose des modules de synchronisation natifs. Consultez l'administrateur pour l'activation.

**Q : Comment voir les réunions de toute l'équipe ?**
> Dans la vue Calendrier, utilisez le filtre des participants pour afficher plusieurs collaborateurs.

**Q : Les événements CRM apparaissent-ils ici ?**
> Oui ! Les RDV planifiés depuis le CRM (bouton "Planifier un RDV") apparaissent dans le calendrier avec le **Module lié : CRM** automatiquement détecté.

**Q : Comment retrouver les réunions sans compte-rendu ?**
> En vue liste, triez par réunions récentes et vérifiez la colonne Résultat (si "En attente", le CR n'est probablement pas fait).

### Bonnes pratiques

| Action | Pourquoi |
|--------|----------|
| Renseigner les **notes de préparation** avant la réunion | Arriver préparé |
| Rédiger le **compte-rendu** le jour même | Mémoire fidèle |
| Toujours renseigner le **résultat** | Suivi et statistiques |
| Utiliser le **suivi** pour les actions | Ne rien oublier |

---

*Guide Calendrier — ERP Commercial Odoo 17 | Mis à jour le 26/03/2026*
