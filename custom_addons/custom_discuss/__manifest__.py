# -*- coding: utf-8 -*-
{
    'name': 'Gestion Commerciale - Discussion',
    'version': '17.0.1.0.0',
    'category': 'Productivity/Discuss',
    'summary': 'Discussion avancée - messages, groupes, e-mails',
    'description': """
        Module de discussion incluant :
        - Gestion des messages interne et externe
        - Gestion des groupes de discussions
        - Gestion des e-mails entrants et sortants
        - Modèles de messages personnalisés
    """,
    'author': 'ERP Commercial',
    'depends': [
        'mail',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/discuss_views.xml',
        'data/discuss_data.xml',
        'report/discuss_report_custom.xml',
        'views/menu_views.xml',
    ],
    'images': ['static/description/icon.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
