# 📁 Guide Utilisateur — Module Documents

> **Public cible** : Tous les employés, Assistants, Responsables qualité
> **Accès** : Menu principal → **Documents**

---

## 📋 Sommaire

1. [Présentation du module](#1--présentation-du-module)
2. [Naviguer dans les dossiers](#2--naviguer-dans-les-dossiers)
3. [Ajouter un document](#3--ajouter-un-document)
4. [Valider et archiver](#4--valider-et-archiver)
5. [Gérer les versions](#5--gérer-les-versions)
6. [Suivi des expirations](#6--suivi-des-expirations)
7. [Organiser avec les étiquettes](#7--organiser-avec-les-étiquettes)
8. [Imprimer les rapports PDF](#8--imprimer-les-rapports-pdf)
9. [FAQ & Astuces](#9--faq--astuces)

---

## 1. 📌 Présentation du module

Le module **Documents** est une GED (Gestion Électronique de Documents) :

```
Upload → Classification → Validation → Utilisation → Archivage / Expiration
```

**Fonctionnalités clés :**
- **Arborescence de dossiers** (parent/enfant)
- **9 types de documents** : Contrat, Facture, Rapport, Politique, Procédure, Modèle, Correspondance, Certificat, Autre
- **Versioning** : plusieurs versions du même document
- **Expiration** : alerte quand un document expire
- **Étiquettes** pour le classement transversal
- Vue **Kanban** (visuelle) et **Liste** (détaillée)

---

## 2. 📂 Naviguer dans les dossiers

### Structure des dossiers

1. **Aller dans** : Documents → Tous les documents → Dossiers
2. Vous voyez l'arborescence :
   ```
   📁 Contrats
   ├── 📁 Contrats clients
   ├── 📁 Contrats fournisseurs
   📁 RH
   ├── 📁 Fiches de paie
   ├── 📁 Dossiers employés
   📁 Qualité
       ├── 📁 Procédures
       ├── 📁 Certifications
   ```

### Créer un dossier

1. Aller dans : Documents → Tous les documents → Dossiers
2. Cliquer sur **➕ Nouveau**
3. Remplir :
   - **Nom du dossier** : ex. "Contrats 2026"
   - **Dossier parent** : pour créer un sous-dossier
   - **Description** : usage du dossier

---

## 3. 📤 Ajouter un document

### Depuis la vue Kanban (recommandé)

1. **Aller dans** : Documents → Tous les documents → Documents
2. La vue **Kanban** affiche les documents regroupés par dossier
3. Cliquer sur **➕ Nouveau**

### Remplir le formulaire

| Champ | Description | Obligatoire |
|-------|-------------|:-----------:|
| **Nom** | Nom descriptif du document | ✅ |
| **Dossier** | Où ranger le document | ✅ |
| **Fichier** | Télécharger le fichier (PDF, Word, Excel, image...) | ✅ |
| **Type** | Contrat / Facture / Rapport / Politique / Procédure / Modèle / Correspondance / Certificat / Autre | ✅ |
| **Partenaire lié** | Client ou fournisseur concerné | Non |
| **Responsable** | Personne en charge du document | Non |
| **Date d'expiration** | Si le document a une date de validité | Non |
| **Étiquettes** | Tags de classement | Non |
| **Notes** | Informations complémentaires | Non |

> 📌 La **Taille du fichier** est calculée automatiquement après upload.

---

## 4. ✅ Valider et archiver

### Cycle de vie d'un document

```
📝 Brouillon → ✅ Validé → 📦 Archivé
```

| Statut | Signification | Action |
|--------|---------------|--------|
| **Brouillon** | Document en cours de rédaction/vérification | Création |
| **Validé** | Document officiel, peut être utilisé | Cliquer **Valider** |
| **Archivé** | Document obsolète, conservé pour historique | Cliquer **Archiver** |

### Valider un document

1. Ouvrir le document en Brouillon
2. Vérifier le fichier et les métadonnées
3. Cliquer sur **✅ Valider**
4. Le document est maintenant utilisable

### Archiver un document

1. Ouvrir le document Validé
2. Cliquer sur **📦 Archiver**
3. Le document reste consultable mais n'apparaît plus par défaut

> 💡 **Astuce** : Les documents archivés sont masqués par défaut. Utilisez le filtre **Archivé** pour les retrouver.

---

## 5. 🔄 Gérer les versions

Quand un document doit être mis à jour (nouveau contrat, procédure révisée) :

1. Ouvrir le document existant
2. Cliquer sur **📄 Nouvelle version**
3. Un nouveau document est créé avec :
   - Mêmes métadonnées (nom, dossier, type, responsable)
   - **Version +1** (ex. 1 → 2)
   - Champ **Fichier** vide (à remplir avec la nouvelle version)
4. Uploader le nouveau fichier
5. Valider la nouvelle version
6. Archiver l'ancienne version

### Historique des versions

Chaque document affiche son numéro de **Version**. Pour voir toutes les versions :
- Recherche par **Nom** du document → toutes les versions apparaissent
- Triez par **Version** pour voir l'évolution

---

## 6. ⏰ Suivi des expirations

### Documents avec date d'expiration

Certains documents expirent (certificats, contrats, licences, assurances) :

1. Lors de la création, renseigner la **Date d'expiration**
2. Le champ **Expiré** se calcule automatiquement :
   - ✅ Non expiré (date future)
   - ❌ Expiré (date passée)

### Alertes d'expiration

Utilisez les filtres dans la barre de recherche :

| Filtre | Description |
|--------|-------------|
| **Expiré** | Documents dont la date est dépassée |
| **Expire dans 30 jours** | Documents qui vont bientôt expirer |

> ⚠️ **Attention** : Vérifiez régulièrement (ex. chaque début de mois) les documents qui expirent bientôt pour anticiper les renouvellements.

---

## 7. 🏷️ Organiser avec les étiquettes

### Créer des étiquettes

1. **Aller dans** : Documents → Configuration → Étiquettes
2. Ajouter en ligne :
   - **Nom** : ex. "Urgent", "Confidentiel", "ISO 9001", "RGPD"
   - **Couleur** : pour le repérage visuel

### Utiliser les étiquettes

Sur chaque document, ajoutez une ou plusieurs étiquettes dans le champ **Étiquettes**.

### Rechercher par étiquette

Dans la barre de recherche, tapez le nom de l'étiquette pour filtrer les documents correspondants.

> 💡 **Astuce** : Combinez dossiers + étiquettes pour un classement double :
> - Dossier = **emplacement** (où est le document)
> - Étiquette = **nature** (quel type de contenu)

---

## 8. 🖨️ Imprimer les rapports PDF

### Fiche document

1. Aller dans : Documents → Rapports → **Fiche document**
2. Cocher les documents
3. Imprimer → **Fiche document**
4. Le PDF contient :
   - Nom et type du document
   - Dossier de rangement
   - Version et date de création
   - Responsable
   - Date d'expiration et statut
   - Étiquettes
   - Partenaire lié
   - Notes

---

## 9. 💡 FAQ & Astuces

### Questions fréquentes

**Q : Quelle taille maximale pour un fichier ?**
> Dépend de la configuration serveur Odoo (par défaut ~25 Mo). Pour les fichiers volumineux, stockez-les sur un drive et liez l'URL dans les notes.

**Q : Comment retrouver un document rapidement ?**
> Utilisez la barre de recherche : tapez le nom, le type, l'étiquette, ou le partenaire. Les **regroupements** par dossier ou type sont aussi très utiles.

**Q : Puis-je supprimer un document ?**
> Il est préférable d'**archiver** plutôt que de supprimer. L'archivage préserve la traçabilité.

**Q : Qui peut voir les documents ?**
> Par défaut, tous les utilisateurs internes. Pour des restrictions par dossier, configurez les droits d'accès avec l'administrateur.

### Organisation recommandée

```
📁 Commercial
├── 📁 Contrats clients
├── 📁 Conditions générales
├── 📁 Propositions commerciales
📁 Achats
├── 📁 Contrats fournisseurs
├── 📁 Conventions
📁 RH
├── 📁 Dossiers employés
├── 📁 Procédures internes
📁 Qualité
├── 📁 Certifications
├── 📁 Procédures ISO
📁 Juridique
├── 📁 Statuts et PV
├── 📁 Assurances
```

---

*Guide Documents — ERP Commercial Odoo 17 | Mis à jour le 26/03/2026*
