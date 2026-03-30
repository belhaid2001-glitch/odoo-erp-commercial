# -*- coding: utf-8 -*-
{
    'name': 'Tableaux de Bord',
    'version': '17.0.1.0.0',
    'category': 'Reporting',
    'summary': 'Centralisation des rapports et KPI dans une interface unifiée',
    'description': """
Tableaux de Bord - ERP Commercial
===================================
* Vue centralisée de tous les KPI de l'entreprise
* Indicateurs Ventes, Achats, Stock, Comptabilité, RH
* Rapports consolidés
* Graphiques et statistiques en temps réel
    """,
    'author': 'ERP Commercial',
    'depends': [
        'base',
        'sale_management',
        'purchase',
        'stock',
        'account',
        'hr',
        'crm',
        'mail',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/currency_mad_data.xml',
        'views/dashboard_views.xml',
        'views/hide_standard_menus.xml',
        'report/dashboard_report_custom.xml',
        'views/menu_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'custom_dashboard/static/src/css/dashboard.css',
            'custom_dashboard/static/src/xml/dashboard_templates.xml',
            'custom_dashboard/static/src/js/dashboard_action.js',
        ],
    },
    'images': ['static/description/icon.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
