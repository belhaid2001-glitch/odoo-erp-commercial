# -*- coding: utf-8 -*-
{
    'name': 'Gestion Commerciale - Vente',
    'version': '17.0.1.0.0',
    'category': 'Sales',
    'summary': 'Gestion avancée des ventes, devis, commandes et facturation',
    'description': """
        Module de gestion commerciale des ventes incluant :
        - Gestion des devis et commandes clients
        - Suivi des commandes à facturer
        - Gestion des modèles de devis
        - Accès portail clients pour suivi factures et commandes
        - Gestion des listes de prix avancées
        - Gestion des produits optionnels
        - Gestion des prévisions
        - Tableaux de bord et KPI
    """,
    'author': 'ERP Commercial',
    'website': '',
    'depends': [
        'sale_management',
        'sale_margin',
        'sale_stock',
        'account',
        'portal',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/sale_order_views.xml',
        'views/sale_dashboard_views.xml',
        'views/sale_forecast_views.xml',
        'data/sale_template_data.xml',
        'report/sale_report_templates.xml',
        'report/sale_report_custom.xml',
        'views/menu_views.xml',
    ],
    'images': ['static/description/icon.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
