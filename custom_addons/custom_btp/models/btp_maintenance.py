# -*- coding: utf-8 -*-
"""
Modèle btp.maintenance — Maintenance des engins BTP
"""

from odoo import models, fields, api


class BtpMaintenance(models.Model):
    _name = 'btp.maintenance'
    _description = 'Maintenance Engin BTP'
    _order = 'date_planifiee desc'
    _inherit = ['mail.thread']

    # ──────────────── Références ────────────────
    engin_id = fields.Many2one('btp.engin', string='Engin', required=True, ondelete='cascade')
    fournisseur_id = fields.Many2one('res.partner', string='Fournisseur / Prestataire')

    # ──────────────── Dates ────────────────
    date_planifiee = fields.Date(string='Date planifiée', required=True)
    date_realisee = fields.Date(string='Date réalisée')

    # ──────────────── Type ────────────────
    type = fields.Selection([
        ('preventif', 'Préventif'),
        ('correctif', 'Correctif'),
    ], string='Type', required=True, default='preventif')

    # ──────────────── Détails ────────────────
    description = fields.Text(string='Description')
    cout_pieces = fields.Float(string='Coût pièces (DH)')
    cout_main_oeuvre = fields.Float(string='Coût main d\'œuvre (DH)')
    cout_total = fields.Float(string='Coût total (DH)', compute='_compute_cout_total', store=True)

    # ──────────────── Calculs ────────────────
    @api.depends('cout_pieces', 'cout_main_oeuvre')
    def _compute_cout_total(self):
        for rec in self:
            rec.cout_total = (rec.cout_pieces or 0) + (rec.cout_main_oeuvre or 0)
