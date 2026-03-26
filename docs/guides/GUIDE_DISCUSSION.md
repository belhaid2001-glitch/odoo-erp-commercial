# 💬 Guide Utilisateur — Module Discussion

> **Public cible** : Tous les employés
> **Accès** : Menu principal → **Discussion**

---

## 📋 Sommaire

1. [Présentation du module](#1--présentation-du-module)
2. [Utiliser les modèles de message](#2--utiliser-les-modèles-de-message)
3. [Créer un modèle personnalisé](#3--créer-un-modèle-personnalisé)
4. [Priorité et marquage des messages](#4--priorité-et-marquage-des-messages)
5. [Imprimer les rapports PDF](#5--imprimer-les-rapports-pdf)
6. [FAQ & Astuces](#6--faq--astuces)

---

## 1. 📌 Présentation du module

Le module **Discussion** améliore la communication interne et externe :

```
Modèle de message → Rédaction → Envoi → Suivi
```

**Fonctionnalités clés :**
- **Modèles de message** réutilisables par catégorie
- **6 catégories** : Commercial, Support, Interne, RH, Comptabilité, Autre
- **Priorité des messages** : Basse, Normale, Haute, Urgente
- **Marquage** (flag) des messages importants
- Messages **internes** (visibles uniquement en interne)

---

## 2. 📧 Utiliser les modèles de message

Les modèles sont des **messages pré-rédigés** que vous pouvez réutiliser pour gagner du temps.

### Exemples de modèles par catégorie

| Catégorie | Exemples |
|-----------|----------|
| 🛒 **Commercial** | Bienvenue nouveau client, Confirmation de commande, Relance devis, Remerciement |
| 🔧 **Support** | Accusé de réception ticket, Résolution, Demande d'informations |
| 🔒 **Interne** | Note de service, Rappel procédure, Annonce équipe |
| 👥 **RH** | Bienvenue nouvel employé, Rappel congé, Convocation entretien |
| 💰 **Comptabilité** | Relance facture, Confirmation paiement, Demande de régularisation |
| ❓ **Autre** | Modèles divers |

### Accéder aux modèles

1. **Aller dans** : Discussion → Configuration Discussion → Modèles de message
2. Parcourir la liste triée par **Séquence** (ordre d'affichage)
3. Cliquer sur un modèle pour le lire ou le modifier

---

## 3. ✏️ Créer un modèle personnalisé

### Étape par étape

1. **Aller dans** : Discussion → Configuration Discussion → Modèles de message
2. Cliquer sur **➕ Nouveau**
3. Remplir :

| Champ | Description | Obligatoire |
|-------|-------------|:-----------:|
| **Nom** | Nom descriptif du modèle | ✅ |
| **Catégorie** | Commercial / Support / Interne / RH / Comptabilité / Autre | ✅ |
| **Sujet** | Objet du message/email | ✅ |
| **Contenu** | Corps du message (éditeur HTML riche) | ✅ |
| **Message interne** | ☑ Si le message ne doit être visible qu'en interne | Non |
| **Séquence** | Ordre d'affichage dans la liste | Non |

### Rédiger le contenu

L'éditeur HTML permet de :
- **Mettre en forme** : gras, italique, titres, couleurs
- **Ajouter des listes** : à puces ou numérotées
- **Insérer des tableaux** : pour des informations structurées
- **Ajouter des liens** : URLs cliquables

### Exemple de modèle

**Nom** : Relance devis en attente
**Catégorie** : Commercial
**Sujet** : Votre devis N° [REF] — Relance
**Contenu** :
```
Bonjour,

Nous nous permettons de revenir vers vous concernant notre devis 
N° [REF] du [DATE].

N'hésitez pas à nous contacter pour toute question ou 
pour finaliser votre commande.

Cordialement,
[VOTRE NOM]
Service Commercial
```

> 💡 **Astuce** : Préparez des modèles pour vos cas les plus fréquents. Copiez-collez le contenu dans le chatter d'Odoo quand vous en avez besoin.

---

## 4. 🚩 Priorité et marquage des messages

### Priorité des messages

Chaque message dans Odoo peut avoir une priorité :

| Priorité | Usage |
|----------|-------|
| ⬜ **Basse** | Information non urgente |
| 🔵 **Normale** | Communication courante |
| 🟠 **Haute** | À traiter rapidement |
| 🔴 **Urgente** | Action immédiate requise |

### Marquage (flag)

- Cliquez sur le **drapeau** 🚩 pour marquer un message important
- Les messages marqués sont facilement retrouvables via le filtre **Marqué**

---

## 5. 🖨️ Imprimer les rapports PDF

### Fiche modèle email

1. Aller dans : Discussion → Rapports → **Fiche modèle email**
2. Cocher les modèles
3. Imprimer → **Fiche modèle email**
4. Le PDF contient :
   - Nom et catégorie du modèle
   - Sujet
   - Contenu complet du message
   - Indicateur message interne

> 💡 Ce rapport peut servir de **charte de communication** à distribuer aux équipes.

---

## 6. 💡 FAQ & Astuces

### Questions fréquentes

**Q : Les modèles s'envoient-ils automatiquement ?**
> Non. Les modèles sont des **gabarits** à copier-coller. Ils permettent de standardiser la communication mais l'envoi reste manuel.

**Q : Puis-je utiliser un modèle depuis le chatter d'un devis ?**
> Oui, copiez le contenu du modèle et collez-le dans le chatter de n'importe quel enregistrement (devis, facture, lead, etc.).

**Q : Un message interne est-il visible par le client ?**
> Non. Les messages marqués **interne** sont visibles uniquement par les utilisateurs de l'ERP, pas sur le portail client.

**Q : Comment organiser mes modèles ?**
> Utilisez la **Séquence** pour mettre les modèles les plus utilisés en premier. Classez par **Catégorie** pour retrouver facilement.

### Bonnes pratiques

| Pratique | Bénéfice |
|----------|----------|
| Un modèle par cas d'usage | Cohérence de communication |
| Catégoriser systématiquement | Retrouver facilement |
| Personnaliser avant envoi | Ne pas envoyer un modèle brut |
| Réviser les modèles trimestriellement | Contenu à jour |

---

*Guide Discussion — ERP Commercial Odoo 17 | Mis à jour le 26/03/2026*
