# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ResCityMorocco(models.Model):
    _name = 'res.city.morocco'
    _description = 'Ville du Maroc'
    _order = 'name'
    _rec_name = 'display_name'

    name = fields.Char(string='Ville', required=True)
    zip_code = fields.Char(string='Code postal')
    state_id = fields.Many2one(
        'res.country.state',
        string='Région/Province',
        domain="[('country_id.code', '=', 'MA')]",
    )
    country_id = fields.Many2one(
        'res.country',
        string='Pays',
        default=lambda self: self.env.ref('base.ma', raise_if_not_found=False),
    )
    display_name = fields.Char(
        string='Nom complet',
        compute='_compute_display_name',
        store=True,
    )

    @api.depends('name', 'zip_code', 'state_id')
    def _compute_display_name(self):
        for city in self:
            parts = [city.name or '']
            if city.zip_code:
                parts.append(f'({city.zip_code})')
            if city.state_id:
                parts.append(f'- {city.state_id.name}')
            city.display_name = ' '.join(parts)
