# -*- coding: utf-8 -*-
{
    'name': 'Mohasib - Expert Comptable IA BTP Maroc',
    'version': '17.0.1.0.0',
    'category': 'Accounting',
    'summary': 'Agent IA expert-comptable spécialisé BTP Maroc avec saisie en langage naturel',
    'description': """
Mohasib - Assistant Comptable IA pour le BTP Marocain

Agent intelligent qui comprend le langage naturel du directeur BTP
et traduit automatiquement en ecritures comptables PCM.

Module 1 - Saisie guidee en langage naturel: le directeur tape
une phrase et Mohasib cree l'ecriture comptable correspondante.

Module 2 - Suivi par chantier: budget, depenses, encaissements.

Module 3 - Fiscalite marocaine BTP: TVA, IS, retenues a la source.

Module 4 - Paie des ouvriers BTP: SMIG, CNSS, AMO, IR.

Module 5 - Alertes intelligentes.

Module 6 - Rapports et etats financiers.

Module 7 - Gestion documentaire BTP.
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
