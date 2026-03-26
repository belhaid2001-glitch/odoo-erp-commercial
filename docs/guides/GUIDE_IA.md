# 🤖 Guide Utilisateur — Module Intelligence Artificielle

> **Public cible** : Tous les employés utilisant l'ERP
> **Accès** : Bouton **🤖 Assistant IA** sur chaque formulaire, ou Configuration → Intelligence Artificielle

---

## 📋 Sommaire

1. [Présentation du module](#1--présentation-du-module)
2. [Utiliser l'assistant IA](#2--utiliser-lassistant-ia)
3. [Actions IA par module](#3--actions-ia-par-module)
4. [Configurer le fournisseur IA](#4--configurer-le-fournisseur-ia)
5. [Mode intégré vs API externe](#5--mode-intégré-vs-api-externe)
6. [FAQ & Astuces](#6--faq--astuces)

---

## 1. 📌 Présentation du module

Le module **IA** ajoute de l'intelligence artificielle à chaque module de l'ERP :

```
Enregistrement (devis, lead, facture...) → 🤖 Assistant IA → Suggestion / Analyse → Appliquer
```

**Fonctionnalités clés :**
- **Bouton IA** intégré dans 7 modules (Vente, CRM, Achat, Comptabilité, Stock, RH, Contacts)
- **8 types d'actions IA** : description, prix, analyse, scoring, email, prédiction, suggestions, requête libre
- **2 modes** : Intégré (règles, toujours disponible) ou API (OpenAI / Ollama, plus avancé)
- **Wizard popup** pour interagir avec l'IA

---

## 2. 🧙 Utiliser l'assistant IA

### Lancer l'assistant

1. Ouvrir n'importe quel enregistrement supporté :
   - Un **devis** (Vente)
   - Un **lead** (CRM)
   - Une **commande fournisseur** (Achat)
   - Une **facture** (Comptabilité)
   - Un **bon de transfert** (Stock)
   - Un **employé** (RH)
   - Un **contact** (Contacts)

2. Cliquer sur le bouton **🤖 Assistant IA** (en haut du formulaire)

3. Le **Wizard IA** s'ouvre en popup

### Utiliser le wizard

| Étape | Action |
|-------|--------|
| 1 | Sélectionner le **Type d'action** (ex. "Générer une description produit") |
| 2 | Optionnel : saisir une **Requête personnalisée** pour affiner |
| 3 | Cliquer sur **🤖 Générer** |
| 4 | Lire le **Résultat IA** affiché |
| 5 | Cliquer sur **✅ Appliquer** pour utiliser la suggestion, ou **Fermer** pour ignorer |

> 📌 Le résultat s'affiche dans le wizard. Vous pouvez le copier, le modifier ou l'appliquer directement.

---

## 3. 📦 Actions IA par module

### 🛒 Vente (sale.order)

| Action | Ce que l'IA fait |
|--------|------------------|
| **Générer description produit** | Crée une description commerciale attractive pour les lignes de commande |
| **Suggestion de prix** | Analyse l'historique des ventes et suggère un prix/remise optimal |
| **Email de suivi** | Rédige un email de suivi commercial personnalisé |

**Exemple concret :**
> Vous avez un devis pour 50 chaises de bureau. L'IA génère :
> *"Lot de 50 chaises ergonomiques modèle ProConfort — finition tissu noir, accoudoirs réglables, garantie 5 ans. Idéal pour l'aménagement de vos espaces de travail."*

### 📊 CRM (crm.lead)

| Action | Ce que l'IA fait |
|--------|------------------|
| **Analyse du lead** | Évalue la qualité du lead et recommande le traitement |
| **Scoring multi-facteurs** | Calcule un score basé sur : montant, probabilité, ancienneté, activité |
| **Prochaine action** | Suggère la prochaine étape commerciale à effectuer |

**Exemple concret :**
> Pour un lead "Équipement Bureau - SociétéABC" avec 80% probabilité et 200K MAD :
> *"Score : 85/100 — Lead CHAUD. Recommandation : planifier une démo sur site dans les 48h. Le montant et la probabilité élevée justifient un traitement prioritaire."*

### 📦 Achat (purchase.order)

| Action | Ce que l'IA fait |
|--------|------------------|
| **Négociation volume** | Conseils pour négocier les prix sur des volumes importants |
| **Comparaison fournisseurs** | Analyse les commandes passées pour comparer les fournisseurs |

### 💰 Comptabilité (account.move)

| Action | Ce que l'IA fait |
|--------|------------------|
| **Prédiction de paiement** | Estime quand le client va payer (basé sur l'historique) |
| **Analyse de risque** | Évalue le risque d'impayé |
| **Générer relance** | Rédige un email de relance professionnel et adapté |

**Exemple concret :**
> Pour une facture de 45 000 MAD en retard de 35 jours :
> *"Risque MOYEN. Historique client : paiement moyen à 42 jours. Recommandation : relance téléphonique suivie d'un email formel. Proposition de plan de paiement si nécessaire."*

### 🏭 Stock (stock.picking)

| Action | Ce que l'IA fait |
|--------|------------------|
| **Analyse de réapprovisionnement** | Calcule le stock restant en jours et les quantités à commander |
| **Suggestions de commande** | Recommande les produits à réapprovisionner |

### 👥 RH (hr.employee)

| Action | Ce que l'IA fait |
|--------|------------------|
| **Synthèse d'évaluation** | Génère une synthèse des évaluations de l'employé |
| **Suggestions de formation** | Recommande des formations basées sur le profil |

### 📇 Contacts (res.partner)

| Action | Ce que l'IA fait |
|--------|------------------|
| **Analyse du contact** | Synthèse du profil client/fournisseur avec historique commercial |

---

## 4. ⚙️ Configurer le fournisseur IA

### Accéder aux paramètres

1. **Aller dans** : Configuration → Paramètres → Intelligence Artificielle
2. Ou directement : la section IA dans les paramètres généraux

### Options de configuration

| Paramètre | Description | Valeur par défaut |
|-----------|-------------|:--:|
| **Fournisseur IA** | Intégré / OpenAI / Ollama | Intégré |
| **Clé API** | Clé d'accès OpenAI (si applicable) | — |
| **URL API** | Adresse du serveur (Ollama) | — |
| **Modèle IA** | Nom du modèle (ex. gpt-4, llama3) | — |
| **Température** | Créativité des réponses (0 = précis, 1 = créatif) | 0.7 |

---

## 5. 🔄 Mode intégré vs API externe

### Mode Intégré (par défaut)

| Avantage | Inconvénient |
|----------|-------------|
| ✅ Toujours disponible | ❌ Réponses basiques (règles) |
| ✅ Pas de coût additionnel | ❌ Pas de NLP avancé |
| ✅ Rapide | ❌ Pas de personnalisation fine |
| ✅ Fonctionne hors ligne | |

Le mode intégré utilise des **règles métier** codées en Python :
- Scoring basé sur des formules
- Descriptions basées sur des templates
- Analyses basées sur des calculs statistiques

### Mode API (OpenAI / Ollama)

| Avantage | Inconvénient |
|----------|-------------|
| ✅ Réponses très naturelles | ❌ Coût par requête (OpenAI) |
| ✅ Compréhension du contexte | ❌ Nécessite une connexion internet |
| ✅ Personnalisation via prompt | ❌ Configuration requise |
| ✅ Multi-langues natif | ❌ Temps de réponse variable |

**OpenAI** : Utilise GPT-4 ou GPT-3.5 via l'API payante d'OpenAI.
**Ollama** : Utilise des modèles open-source (Llama, Mistral...) en local.

### Recommandation

| Taille d'entreprise | Recommandation |
|---------------------|---------------|
| **TPE (< 10 employés)** | Mode intégré (gratuit, suffisant) |
| **PME (10-100 employés)** | OpenAI GPT-3.5 (bon rapport qualité/prix) |
| **Grande entreprise** | Ollama en local (données privées, pas de coût récurrent) |

---

## 6. 💡 FAQ & Astuces

### Questions fréquentes

**Q : L'IA peut-elle modifier mes données automatiquement ?**
> Non. L'IA **propose** des suggestions. Vous cliquez sur **Appliquer** pour valider, ou **Fermer** pour ignorer. Rien n'est modifié sans votre accord.

**Q : Les données sont-elles envoyées à l'extérieur ?**
> En mode **Intégré** : non, tout reste en local. En mode **OpenAI** : oui, les données du contexte sont envoyées à l'API. En mode **Ollama** : non, si le serveur est en local.

**Q : L'assistant IA ne s'affiche pas sur mon formulaire ?**
> Le bouton IA est disponible sur : devis, leads, commandes fournisseur, factures, transferts stock, fiches employés, contacts. Si vous ne le voyez pas, vérifiez vos droits d'accès.

**Q : La requête personnalisée sert à quoi ?**
> Elle permet de guider l'IA avec un contexte spécifique. Ex. : "Rédige l'email en anglais" ou "Focus sur les délais de livraison".

**Q : Puis-je utiliser l'IA sans clé API ?**
> Oui ! Le mode **Intégré** fonctionne sans aucune configuration. Il utilise des règles métier pour générer des réponses.

### Bonnes pratiques

| Pratique | Pourquoi |
|----------|----------|
| Commencer par le mode Intégré | Tester sans coût |
| Toujours vérifier les suggestions | L'IA peut se tromper |
| Utiliser la requête personnalisée | Meilleurs résultats |
| Ne pas partager la clé API | Sécurité |

---

*Guide IA — ERP Commercial Odoo 17 | Mis à jour le 26/03/2026*
