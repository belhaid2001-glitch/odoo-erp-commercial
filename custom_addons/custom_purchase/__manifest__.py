# -*- coding: utf-8 -*-
{
    'name': 'Gestion Commerciale - Achats',
    'version': '17.0.1.0.0',
    'category': 'Purchase',
    'summary': 'Gestion avancée des achats, réapprovisionnement et conventions',
    'description': """
        Module de gestion des achats incluant :
        - Gestion des achats depuis la demande de prix jusqu'à la facturation
        - Gestion du réapprovisionnement
        - Gestion des conventions d'achats
        - Gestion des unités de mesures
        - Gestion du conditionnement
        - KPI et tableaux de bord
    """,
    'author': 'ERP Commercial',
    'depends': [
        'purchase',
        'purchase_stock',
        'account',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/purchase_order_views.xml',
        'views/purchase_convention_views.xml',
        'views/purchase_dashboard_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
