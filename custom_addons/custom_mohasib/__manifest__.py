# -*- coding: utf-8 -*-
{
    'name': 'Mohasib - Expert Comptable IA BTP Maroc',
    'version': '17.0.1.0.0',
    'category': 'Accounting',
    'summary': 'Agent IA expert-comptable spécialisé BTP Maroc avec saisie en langage naturel',
    'description': """
Mohasib (محاسب) — Assistant Comptable IA pour le BTP Marocain
==============================================================

Agent intelligent qui comprend le langage naturel du directeur BTP
et traduit automatiquement en écritures comptables PCM.

**Module 1 — Saisie guidée en langage naturel**
* "J'ai acheté 200 sacs de ciment à 48 DH pour Hay Riad, payé cash"
  → Écriture 6132/5161 avec affectation analytique chantier

**Module 2 — Suivi par chantier**
* Budget, dépenses, encaissements, marge en temps réel
* "Comment va le chantier Casablanca ?" → Rapport instantané

**Module 3 — Fiscalité marocaine BTP**
* TVA 20%/10%/7%, IS, retenues à la source, CNSS
* Alertes automatiques avant échéances DGI

**Module 4 — Paie des ouvriers BTP**
* SMIG BTP, heures sup, CNSS, AMO, IR barème progressif
* Bulletins de paie et bordereaux CNSS

**Module 5 — Alertes intelligentes**
* Trésorerie, fiscal, chantier, légal, CNSS

**Module 6 — Rapports & états financiers**
* Bilan, CPC, ESG, liasse fiscale DGI

**Module 7 — Gestion documentaire BTP**
* Devis, factures DGI, situations de travaux, retenues
    """,
    'author': 'ERP Commercial',
    'depends': [
        'base',
        'account',
        'analytic',
        'mail',
        'hr',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/mohasib_pcm_data.xml',
        'data/mohasib_sequence_data.xml',
        'views/mohasib_chantier_views.xml',
        'views/mohasib_conversation_views.xml',
        'views/mohasib_transaction_views.xml',
        'wizards/mohasib_saisie_wizard_views.xml',
        'views/menu_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'custom_mohasib/static/src/css/mohasib.css',
        ],
    },
    'images': ['static/description/icon.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
