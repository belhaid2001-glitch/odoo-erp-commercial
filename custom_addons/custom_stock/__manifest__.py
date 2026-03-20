# -*- coding: utf-8 -*-
{
    'name': 'Gestion Commerciale - Stock & Inventaire',
    'version': '17.0.1.0.0',
    'category': 'Inventory',
    'summary': 'Gestion avancée du stock, inventaire, lots et contrôle qualité',
    'description': """
        Module de gestion du stock et inventaire incluant :
        - Gestion des livraisons et réceptions
        - Gestion des transferts internes
        - Gestion de règles de stock (Stock min et max)
        - Automatisation des alimentations de stock
        - Gestion de préparation
        - Gestion de contrôle qualité
        - Gestion d'inventaire en temps réel
        - Gestion des lots et N de série
        - Gestion des stratégies de rangement
        - Gestion des codes à barre
        - Valorisation de l'inventaire
        - Tableaux de bord et KPI
    """,
    'author': 'ERP Commercial',
    'depends': [
        'stock',
        'product',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/stock_picking_views.xml',
        'views/stock_quality_views.xml',
        'views/stock_dashboard_views.xml',
        'views/stock_valuation_views.xml',
        'views/menu_views.xml',
        'data/stock_data.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
