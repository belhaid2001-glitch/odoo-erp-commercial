# -*- coding: utf-8 -*-
{
    'name': 'Gestion Commerciale - Ressources Humaines',
    'version': '17.0.1.0.0',
    'category': 'Human Resources',
    'summary': 'Gestion RH avancée - employés, contrats, congés, recrutement, évaluations',
    'description': """
        Module de ressources humaines incluant :
        - Gestion des employés et contrats
        - Gestion des congés et absences
        - Gestion du recrutement
        - Gestion des évaluations
    """,
    'author': 'ERP Commercial',
    'depends': [
        'hr',
        'hr_contract',
        'hr_holidays',
        'hr_recruitment',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_employee_views.xml',
        'views/hr_evaluation_views.xml',
        'views/hr_dashboard_views.xml',
        'data/hr_data.xml',
        'report/hr_report_custom.xml',
        'views/menu_views.xml',
    ],
    'images': ['static/description/icon.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
