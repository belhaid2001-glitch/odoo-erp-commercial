# -*- coding: utf-8 -*-
import base64
import csv
import io
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

# Colonnes attendues dans le CSV (ordre exact du template)
EXPECTED_COLUMNS = [
    'nom',
    'type',
    'adresse',
    'ville',
    'telephone',
    'mobile',
    'email',
    'ice',
    'rc',
    'if',
]


class ContactImportWizard(models.TransientModel):
    _name = 'contact.import.wizard'
    _description = 'Assistant d\'import de contacts CSV'

    file_data = fields.Binary(
        string='Fichier CSV',
        required=True,
        help='Fichier CSV (séparateur: point-virgule ;) encodé en UTF-8.',
    )
    file_name = fields.Char(string='Nom du fichier')

    import_count = fields.Integer(string='Contacts importés', readonly=True)
    error_count = fields.Integer(string='Erreurs', readonly=True)
    error_log = fields.Text(string='Détail des erreurs', readonly=True)
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('done', 'Terminé'),
    ], default='draft')

    # =========================================================================
    #   TÉLÉCHARGER LE TEMPLATE
    # =========================================================================
    def action_download_template(self):
        """Télécharge le fichier CSV template pré-rempli avec 2 exemples."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': '/custom_contacts/download_template',
            'target': 'self',
        }

    # =========================================================================
    #   IMPORTER LE FICHIER
    # =========================================================================
    def action_import(self):
        self.ensure_one()
        if not self.file_data:
            raise UserError(_('Veuillez sélectionner un fichier CSV.'))

        # Décoder le fichier
        try:
            raw = base64.b64decode(self.file_data)
            # Essayer UTF-8 d'abord, puis latin-1 (Excel Windows)
            try:
                content = raw.decode('utf-8-sig')
            except UnicodeDecodeError:
                content = raw.decode('latin-1')
        except Exception as e:
            raise UserError(_('Impossible de lire le fichier: %s') % str(e))

        # Détecter le séparateur (point-virgule ou virgule)
        first_line = content.split('\n')[0] if '\n' in content else content
        if ';' in first_line:
            delimiter = ';'
        elif ',' in first_line:
            delimiter = ','
        elif '\t' in first_line:
            delimiter = '\t'
        else:
            delimiter = ';'

        reader = csv.DictReader(io.StringIO(content), delimiter=delimiter)

        # Normaliser les noms de colonnes (minuscules, strip, sans accents basiques)
        if reader.fieldnames:
            clean_fields = []
            for f in reader.fieldnames:
                cleaned = (f or '').strip().lower()
                cleaned = cleaned.replace('é', 'e').replace('è', 'e').replace('ê', 'e')
                cleaned = cleaned.replace('ô', 'o').replace('î', 'i')
                cleaned = cleaned.replace('téléphone', 'telephone')
                cleaned = cleaned.replace('n°', '').replace('°', '')
                clean_fields.append(cleaned)
            reader.fieldnames = clean_fields

        # Pré-charger le mapping villes → (state_id, zip)
        city_map = self._build_city_map()
        morocco = self.env.ref('base.ma', raise_if_not_found=False)

        imported = 0
        errors = []
        line_num = 1  # Header = ligne 0

        for row in reader:
            line_num += 1
            try:
                nom = (row.get('nom') or '').strip()
                if not nom:
                    errors.append(f'Ligne {line_num}: Nom vide — ignorée.')
                    continue

                # Type: société ou particulier
                type_raw = (row.get('type') or '').strip().lower()
                is_company = type_raw in ('société', 'societe', 'entreprise', 's', 'oui', 'yes', '1')

                # Ville → auto-fill region + zip
                ville_raw = (row.get('ville') or '').strip()
                city_info = city_map.get(ville_raw.lower(), {})

                # Téléphone: nettoyer
                phone = self._clean_phone(row.get('telephone') or '')
                mobile = self._clean_phone(row.get('mobile') or '')
                email = (row.get('email') or '').strip()

                # IDs marocains
                ice = (row.get('ice') or '').strip()
                rc = (row.get('rc') or '').strip()
                if_code = (row.get('if') or '').strip()

                vals = {
                    'name': nom,
                    'is_company': is_company,
                    'street': (row.get('adresse') or '').strip() or False,
                    'city': ville_raw or False,
                    'zip': city_info.get('zip') or False,
                    'state_id': city_info.get('state_id') or False,
                    'country_id': morocco.id if morocco else False,
                    'phone': phone or False,
                    'mobile': mobile or False,
                    'email': email or False,
                    'ice': ice or False,
                    'rc': rc or False,
                    'if_code': if_code or False,
                }

                # Vérifier doublon par nom + email (éviter re-import)
                domain = [('name', '=ilike', nom)]
                if email:
                    domain = ['|', ('name', '=ilike', nom), ('email', '=ilike', email)]
                existing = self.env['res.partner'].search(domain, limit=1)
                if existing:
                    errors.append(
                        f'Ligne {line_num}: "{nom}" existe déjà (ID {existing.id}) — ignorée.'
                    )
                    continue

                self.env['res.partner'].create(vals)
                imported += 1

            except Exception as e:
                errors.append(f'Ligne {line_num}: Erreur — {str(e)}')
                _logger.warning('Import contact line %s error: %s', line_num, e)

        error_log = '\n'.join(errors) if errors else 'Aucune erreur !'
        self.write({
            'state': 'done',
            'import_count': imported,
            'error_count': len(errors),
            'error_log': error_log,
        })

        return {
            'type': 'ir.actions.act_window',
            'name': _('Résultat de l\'import'),
            'res_model': 'contact.import.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    # =========================================================================
    #   HELPERS
    # =========================================================================
    def _build_city_map(self):
        """Construit un dict {nom_ville_lower: {state_id, zip}}."""
        cities = self.env['res.city.morocco'].search([])
        result = {}
        for c in cities:
            result[c.name.lower()] = {
                'state_id': c.state_id.id if c.state_id else False,
                'zip': c.zip_code or False,
            }
        return result

    @staticmethod
    def _clean_phone(value):
        """Nettoie un numéro de téléphone."""
        if not value:
            return ''
        clean = value.strip().replace(' ', '').replace('.', '').replace('-', '')
        # Garder le + si présent
        if clean.startswith('+'):
            return clean
        return clean
