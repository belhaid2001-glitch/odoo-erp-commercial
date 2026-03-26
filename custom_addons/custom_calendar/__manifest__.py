# -*- coding: utf-8 -*-
{
    'name': 'Gestion Commerciale - Calendrier',
    'version': '17.0.1.0.0',
    'category': 'Productivity/Calendar',
    'summary': 'Calendrier avancé - rendez-vous, synchronisation planning',
    'description': """
        Module de calendrier incluant :
        - Planification des rendez-vous
        - Synchronisation du planning avec les autres modules (Inventaire, CRM, Projet...)
        - Gestion des types de rendez-vous
        - Rappels et notifications
    """,
    'author': 'ERP Commercial',
    'depends': [
        'calendar',
        'crm',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/calendar_data.xml',
        'views/calendar_event_views.xml',
        'report/calendar_report_custom.xml',
        'views/menu_views.xml',
    ],
    'images': ['static/description/icon.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
