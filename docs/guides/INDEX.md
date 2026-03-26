# 📖 Guide Utilisateur — ERP Commercial Odoo 17

> **Documentation métier** à destination des utilisateurs finaux (employés, managers, direction).
> Chaque guide décrit pas à pas comment utiliser le module au quotidien.

---

## 📚 Table des matières

| # | Module | Guide | Public cible |
|---|--------|-------|-------------|
| 1 | 🛒 **Vente** | [Guide Vente](./GUIDE_VENTE.md) | Commerciaux, Directeur commercial |
| 2 | 📦 **Achat** | [Guide Achat](./GUIDE_ACHAT.md) | Acheteurs, Responsable achats |
| 3 | 🏭 **Stock & Inventaire** | [Guide Stock](./GUIDE_STOCK.md) | Magasiniers, Responsable logistique |
| 4 | 💰 **Comptabilité** | [Guide Comptabilité](./GUIDE_COMPTABILITE.md) | Comptables, DAF |
| 5 | 👥 **Ressources Humaines** | [Guide RH](./GUIDE_RH.md) | RH, Managers, Direction |
| 6 | 📊 **CRM** | [Guide CRM](./GUIDE_CRM.md) | Commerciaux, Marketing |
| 7 | 📅 **Calendrier** | [Guide Calendrier](./GUIDE_CALENDRIER.md) | Tous les employés |
| 8 | 📇 **Contacts** | [Guide Contacts](./GUIDE_CONTACTS.md) | Commercial, Administration |
| 9 | 📁 **Documents** | [Guide Documents](./GUIDE_DOCUMENTS.md) | Tous les employés |
| 10 | 💬 **Discussion** | [Guide Discussion](./GUIDE_DISCUSSION.md) | Tous les employés |
| 11 | 📈 **Tableau de bord** | [Guide Tableau de bord](./GUIDE_DASHBOARD.md) | Managers, Direction |
| 12 | 🤖 **Intelligence Artificielle** | [Guide IA](./GUIDE_IA.md) | Tous les employés |

---

## 🚀 Premiers pas

### Se connecter
1. Ouvrir le navigateur et aller sur **http://localhost:8069**
2. Entrer votre **identifiant** et **mot de passe**
3. Vous arrivez sur la page d'accueil avec les applications installées

### Navigation générale
- **Barre de menu** (haut) : accès aux applications principales
- **Recherche** (barre de recherche) : filtres, regroupements, favoris
- **Vues** : Liste, Formulaire, Kanban, Calendrier, Pivot, Graphique
- **Chatter** (bas des formulaires) : historique, notes, messages

### Conventions de ce guide
| Icône | Signification |
|-------|---------------|
| 📌 | Point important à retenir |
| ⚠️ | Attention — action irréversible ou critique |
| 💡 | Astuce pour gagner du temps |
| ✅ | Validation ou étape obligatoire |

---

## 🖨️ Imprimer les rapports PDF

Chaque module propose des **rapports PDF** imprimables :

1. Aller dans le menu **📊 Rapports** du module
2. La vue **liste** s'ouvre avec les enregistrements
3. **Cocher** les enregistrements souhaités
4. Cliquer sur **Imprimer** → choisir le rapport
5. Le PDF se télécharge automatiquement

---

## 📄 Convertir ces guides en PDF

### Option 1 : Depuis le navigateur (la plus simple)
1. Ouvrir le guide sur GitHub
2. `Ctrl + P` → Imprimer → **Enregistrer en PDF**

### Option 2 : Avec Pandoc (meilleure qualité)
```bash
# Installer pandoc
# Windows: winget install JohnMacFarlane.Pandoc
# Mac: brew install pandoc

# Convertir un guide
pandoc GUIDE_VENTE.md -o Guide_Vente.pdf --pdf-engine=xelatex

# Convertir tous les guides d'un coup
for file in GUIDE_*.md; do pandoc "$file" -o "${file%.md}.pdf" --pdf-engine=xelatex; done
```

### Option 3 : Extension VS Code
Installer l'extension **Markdown PDF** (`yzane.markdown-pdf`), clic droit → "Markdown PDF: Export (pdf)"

---

*Documentation créée le 26/03/2026 — ERP Commercial Odoo 17*
