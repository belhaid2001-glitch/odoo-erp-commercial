# -*- coding: utf-8 -*-
"""
Modèles btp.reception et btp.reserve — Réceptions et réserves BTP
"""

from odoo import models, fields, api
from dateutil.relativedelta import relativedelta


class BtpReception(models.Model):
    _name = 'btp.reception'
    _description = 'Réception BTP'
    _order = 'date desc'
    _inherit = ['mail.thread']

    # ──────────────── Identification ────────────────
    name = fields.Char(string='Référence', readonly=True, copy=False, default='Nouveau')
    chantier_id = fields.Many2one('btp.chantier', string='Chantier', required=True)

    # ──────────────── Type ────────────────
    type = fields.Selection([
        ('provisoire', 'Réception provisoire'),
        ('definitive', 'Réception définitive'),
    ], string='Type', required=True, tracking=True)

    # ──────────────── Données ────────────────
    date = fields.Date(string='Date de réception', required=True, default=fields.Date.today)
    lieu = fields.Char(string='Lieu')
    pv_file = fields.Binary(string='PV de réception')
    pv_filename = fields.Char(string='Nom fichier PV')
    observations = fields.Text(string='Observations')

    # ──────────────── Réserves ────────────────
    reserve_ids = fields.One2many('btp.reserve', 'reception_id', string='Réserves')

    # ──────────────── Signataires ────────────────
    signataire_ids = fields.Many2many('res.partner', string='Signataires')

    # ──────────────── Garantie ────────────────
    delai_garantie = fields.Integer(string='Délai de garantie (mois)', default=12)
    date_fin_garantie = fields.Date(string='Fin de garantie', compute='_compute_date_fin_garantie', store=True)

    # ──────────────── Calculs ────────────────
    @api.depends('date', 'delai_garantie')
    def _compute_date_fin_garantie(self):
        for rec in self:
            if rec.date and rec.delai_garantie:
                rec.date_fin_garantie = rec.date + relativedelta(months=rec.delai_garantie)
            else:
                rec.date_fin_garantie = False

    # ──────────────── Séquence ────────────────
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'Nouveau') == 'Nouveau':
                vals['name'] = self.env['ir.sequence'].next_by_code('btp.reception') or 'Nouveau'
        return super().create(vals_list)


class BtpReserve(models.Model):
    _name = 'btp.reserve'
    _description = 'Réserve BTP'
    _order = 'date_limite'

    # ──────────────── Références ────────────────
    reception_id = fields.Many2one('btp.reception', string='Réception', required=True, ondelete='cascade')
    responsable_id = fields.Many2one('res.users', string='Responsable')

    # ──────────────── Détails ────────────────
    description = fields.Text(string='Description', required=True)
    date_limite = fields.Date(string='Date limite')

    # ──────────────── État ────────────────
    state = fields.Selection([
        ('ouverte', 'Ouverte'),
        ('levee', 'Levée'),
    ], string='État', default='ouverte')
    date_levee = fields.Date(string='Date de levée')

    # ──────────────── Photos ────────────────
    photo_avant = fields.Binary(string='Photo avant')
    photo_apres = fields.Binary(string='Photo après')

    # ──────────────── Action ────────────────
    def action_lever(self):
        self.write({'state': 'levee', 'date_levee': fields.Date.today()})
