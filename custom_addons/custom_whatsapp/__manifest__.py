# -*- coding: utf-8 -*-
{
    'name': 'Gestion Commerciale - WhatsApp',
    'version': '17.0.1.0.0',
    'category': 'Marketing',
    'summary': 'Envoi de messages WhatsApp aux clients et fournisseurs',
    'description': """
Module WhatsApp - ERP Commercial
=================================
* Envoi de messages WhatsApp depuis les fiches contacts, devis, factures
* Templates de messages personnalisables
* Historique des messages envoyés
* Envoi en masse
* Intégration WhatsApp Web API (wa.me)
    """,
    'author': 'ERP Commercial',
    'depends': [
        'base',
        'contacts',
        'mail',
        'sale_management',
        'account',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/whatsapp_data.xml',
        'wizard/whatsapp_send_wizard_views.xml',
        'views/whatsapp_views.xml',
        'views/partner_whatsapp_views.xml',
        'views/menu_views.xml',
    ],
    'images': ['static/description/icon.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
