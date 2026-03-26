# -*- coding: utf-8 -*-
{
    'name': 'Intelligence Artificielle ERP',
    'version': '17.0.1.0.0',
    'category': 'Extra Tools',
    'summary': 'Assistant IA intégré à tous les modules - suggestions, analyses et automatisations intelligentes',
    'description': """
Intelligence Artificielle ERP
==============================
* Assistant IA intégré dans chaque module
* Suggestions intelligentes (prix, descriptions, actions)
* Analyse prédictive (paiement, stock, CRM)
* Génération automatique de texte (évaluations, relances)
* Fonctionne en mode autonome (règles) ou avec API OpenAI/Ollama
    """,
    'author': 'ERP Commercial',
    'depends': [
        'base',
        'mail',
        'sale_management',
        'purchase',
        'stock',
        'account',
        'hr',
        'crm',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/ai_config_views.xml',
        'views/ai_wizard_views.xml',
        'views/ai_buttons_views.xml',
    ],
    'images': ['static/description/icon.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
