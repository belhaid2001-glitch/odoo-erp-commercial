# -*- coding: utf-8 -*-
import io
import csv
from odoo import http
from odoo.http import request, content_disposition


class ContactTemplateController(http.Controller):

    @http.route('/custom_contacts/download_template', type='http', auth='user')
    def download_template(self, **kwargs):
        """Télécharge le template CSV avec 2 lignes d'exemple."""
        output = io.StringIO()
        # BOM UTF-8 pour que Excel ouvre correctement les accents
        output.write('\ufeff')

        writer = csv.writer(output, delimiter=';', quoting=csv.QUOTE_MINIMAL)

        # En-têtes
        writer.writerow([
            'Nom',
            'Type',
            'Adresse',
            'Ville',
            'Téléphone',
            'Mobile',
            'Email',
            'ICE',
            'RC',
            'IF',
        ])

        # Exemples
        writer.writerow([
            'TechMaroc SARL',
            'Société',
            '123 Bd Zerktouni',
            'Casablanca',
            '0522123456',
            '',
            'contact@techmaroc.ma',
            '001234567000089',
            '123456',
            '12345678',
        ])
        writer.writerow([
            'Ahmed Bennani',
            'Particulier',
            '45 Rue Hassan II',
            'Rabat',
            '',
            '0661234567',
            'ahmed.bennani@gmail.com',
            '',
            '',
            '',
        ])
        writer.writerow([
            'Salon Beauté Nour',
            'Société',
            '12 Av Mohammed V',
            'Marrakech',
            '0524456789',
            '0700112233',
            'nour.beaute@gmail.com',
            '002345678000012',
            '234567',
            '23456789',
        ])

        content = output.getvalue().encode('utf-8')
        headers = [
            ('Content-Type', 'text/csv; charset=utf-8'),
            ('Content-Disposition', content_disposition('template_import_contacts.csv')),
            ('Content-Length', len(content)),
        ]
        return request.make_response(content, headers=headers)
