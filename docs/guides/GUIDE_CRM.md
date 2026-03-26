# 📊 Guide Utilisateur — Module CRM

> **Public cible** : Commerciaux, Responsable commercial, Marketing
> **Accès** : Menu principal → **CRM**

---

## 📋 Sommaire

1. [Présentation du module](#1--présentation-du-module)
2. [Gérer les leads et opportunités](#2--gérer-les-leads-et-opportunités)
3. [Pipeline commercial (vue Kanban)](#3--pipeline-commercial)
4. [Logger un appel](#4--logger-un-appel)
5. [Planifier un rendez-vous](#5--planifier-un-rendez-vous)
6. [Créer un devis rapide](#6--créer-un-devis-rapide)
7. [Suivi des concurrents](#7--suivi-des-concurrents)
8. [Imprimer les rapports PDF](#8--imprimer-les-rapports-pdf)
9. [FAQ & Astuces](#9--faq--astuces)

---

## 1. 📌 Présentation du module

Le module **CRM** gère le cycle de prospection et de conversion :

```
Lead entrant → Qualification → Proposition → Négociation → Gagné / Perdu
```

**Fonctionnalités clés :**
- **Qualité du lead** automatique (Froid / Tiède / Chaud)
- **8 sources de leads** : Site web, Téléphone, Email, Recommandation, Réseaux sociaux, Événement, Publicité, Autre
- **Suivi d'activité** : appels, réunions, devis
- **Gestion des concurrents** avec analyse forces/faiblesses
- **Création rapide de devis** depuis une opportunité
- Calcul automatique de la **probabilité pondérée**

---

## 2. 📝 Gérer les leads et opportunités

### Créer un lead

1. **Aller dans** : CRM → Pipeline (ou CRM → Leads)
2. Cliquer sur **➕ Nouveau**
3. Remplir :

| Champ | Description | Obligatoire |
|-------|-------------|:-----------:|
| **Nom de l'opportunité** | Ex. "Équipement Bureau - Société ABC" | ✅ |
| **Contact** | Le prospect/client | ✅ |
| **Revenu attendu** | Montant potentiel de la vente | Non |
| **Probabilité (%)** | Chance de conclure (0-100%) | Non |
| **Source du lead** | Comment le lead est arrivé | ✅ |
| **Date de clôture estimée** | Date prévue pour conclure | Non |
| **Commercial** | Vendeur assigné | Auto (vous) |

### Onglet Suivi commercial

| Champ | Description |
|-------|-------------|
| **Prochaine action** | Description de l'action suivante |
| **Date prochaine action** | Deadline pour cette action |
| **Dernier contact** | Date du dernier échange (auto) |
| **Jours sans contact** | Alerte si trop de temps sans news (auto) |
| **Concurrents** | Concurrents sur cette affaire |
| **Notes de perte** | Si perdue : raison détaillée |

### Qualité du lead (automatique)

| Qualité | Critère | Couleur |
|---------|---------|---------|
| ❄️ **Froid** | Probabilité < 20% | Bleu |
| 🌤️ **Tiède** | Probabilité 20-49% | Jaune |
| 🔥 **Chaud** | Probabilité ≥ 50% | Rouge |

> 📌 La qualité se calcule automatiquement mais peut être **modifiée manuellement** si besoin.

---

## 3. 🏗️ Pipeline commercial

### La vue Kanban

La vue **Pipeline** (Kanban) est la vue principale du CRM :

```
📥 Nouveau → 📋 Qualifié → 💬 Proposition → 🤝 Négociation → 🏆 Gagné
```

- **Glisser-déposer** les cartes d'une colonne à l'autre
- Chaque carte affiche : nom, client, montant, qualité (badge coloré)
- Les colonnes représentent les **étapes du pipeline**

### Actions depuis le Kanban

| Action | Comment |
|--------|---------|
| **Déplacer** | Glisser-déposer vers la colonne suivante |
| **Gagner** | Faire glisser vers "Gagné" ou bouton vert dans le formulaire |
| **Perdre** | Cliquer sur ✖ et renseigner la raison |
| **Ouvrir** | Cliquer sur la carte pour voir le détail |

---

## 4. 📞 Logger un appel

1. Ouvrir le lead
2. Cliquer sur le bouton **📞 Logger un appel**
3. Le système :
   - Incrémente le **Compteur d'appels** (+1)
   - Met à jour le **Dernier contact** à aujourd'hui
   - Ajoute une ligne dans le **Chatter** : "Appel commercial enregistré le..."

> 💡 **Astuce** : Loggez chaque appel même rapide. Ça alimente les statistiques et le suivi dans le temps.

---

## 5. 📅 Planifier un rendez-vous

1. Ouvrir le lead
2. Cliquer sur le bouton **📅 Planifier un RDV**
3. Le formulaire de **Calendrier** s'ouvre, pré-rempli avec :
   - Le nom de l'opportunité
   - Le contact du client
4. Compléter : date, heure, lieu, participants
5. Sauvegarder

Le compteur **RDV** s'incrémente sur la fiche lead.

> 📌 Cliquez sur le bouton statistique **"X RDV"** pour voir tous les rendez-vous liés à cette opportunité.

---

## 6. 💲 Créer un devis rapide

1. Ouvrir le lead
2. Cliquer sur le bouton **📋 Créer un devis**
3. Un **devis de vente** est créé automatiquement avec :
   - Le **Client** pré-rempli depuis le lead
   - La **Référence** liée à l'opportunité
4. Compléter les lignes de produits dans le module Vente

> ⚠️ **Attention** : Le lead doit avoir un **Contact** (res.partner) renseigné. Sinon, une erreur s'affiche.

Le compteur **Devis** sur le lead s'incrémente automatiquement.

### Conversion probability → montant

La **Probabilité pondérée** est calculée :
```
Conversion = Revenu attendu × Probabilité / 100
```
Exemple : 100 000 MAD × 70% = **70 000 MAD** de CA pondéré

---

## 7. 🏢 Suivi des concurrents

### Créer un concurrent

1. **Aller dans** : CRM → Configuration CRM → Concurrents
2. Cliquer sur **➕ Nouveau**
3. Remplir :

| Champ | Description |
|-------|-------------|
| **Nom** | Nom du concurrent |
| **Site web** | URL du site |
| **Points forts** | Ce qu'ils font mieux |
| **Points faibles** | Nos avantages face à eux |
| **Notes** | Informations complémentaires |

### Associer un concurrent à une opportunité

1. Ouvrir le lead
2. Dans l'onglet **Suivi commercial**
3. Ajouter les concurrents dans le champ **Concurrents**

> 💡 **Astuce** : Documentez les forces/faiblesses pour aider les commerciaux à préparer leurs arguments.

---

## 8. 🖨️ Imprimer les rapports PDF

### Fiche opportunité

1. Aller dans : CRM → Rapports → **Fiche opportunité**
2. Cocher les leads/opportunités
3. Imprimer → **Fiche opportunité**
4. Le PDF contient :
   - Informations du lead et du contact
   - Source et qualité
   - Montant et probabilité
   - Nombre d'appels, RDV, devis
   - Concurrents identifiés
   - Prochaine action planifiée
   - Notes internes CRM

---

## 9. 💡 FAQ & Astuces

### Questions fréquentes

**Q : Quelle est la différence entre un lead et une opportunité ?**
> Dans Odoo 17, les leads et opportunités sont le même objet (`crm.lead`). L'étape dans le pipeline détermine s'il est "Lead" ou "Opportunité qualifiée".

**Q : Comment retrouver les leads sans action depuis longtemps ?**
> Utilisez la colonne **Jours sans contact** en vue liste, ou triez par cette colonne pour voir les leads les plus anciens.

**Q : Comment marquer un lead comme perdu ?**
> Cliquez sur le bouton **Perdu** dans le formulaire. Renseignez la **raison de perte** et les **Notes de perte** pour l'analyse.

**Q : Comment renvoyer un lead perdu ?**
> Ouvrir le lead perdu → cliquer sur **Restaurer**. Il revient dans le pipeline.

### Bonnes pratiques CRM

| Action | Fréquence | Pourquoi |
|--------|-----------|----------|
| Logger chaque appel | À chaque appel | Traçabilité et statistiques |
| Mettre à jour la probabilité | Après chaque interaction | Forecast plus précis |
| Renseigner la prochaine action | Toujours | Ne jamais laisser un lead sans suite |
| Documenter la perte | Chaque perte | Améliorer le taux de conversion |

---

*Guide CRM — ERP Commercial Odoo 17 | Mis à jour le 26/03/2026*
