# -*- coding: utf-8 -*-
"""
Modèle btp.engin.pointage — Pointage des engins BTP
"""

from odoo import models, fields, api


class BtpEnginPointage(models.Model):
    _name = 'btp.engin.pointage'
    _description = 'Pointage Engin BTP'
    _order = 'date desc'

    # ──────────────── Références ────────────────
    engin_id = fields.Many2one('btp.engin', string='Engin', required=True, ondelete='cascade')
    chantier_id = fields.Many2one('btp.chantier', string='Chantier', required=True)
    operateur_id = fields.Many2one('btp.ressource', string='Opérateur')

    # ──────────────── Données ────────────────
    date = fields.Date(string='Date', required=True, default=fields.Date.today)
    heures_utilisation = fields.Float(string='Heures d\'utilisation')
    gasoil_litres = fields.Float(string='Gasoil (litres)')

    # ──────────────── Coût ────────────────
    cout_total = fields.Float(string='Coût total (DH)', compute='_compute_cout', store=True)

    # ──────────────── Calculs ────────────────
    @api.depends('heures_utilisation', 'gasoil_litres', 'engin_id.cout_heure')
    def _compute_cout(self):
        prix_gasoil = 12.0  # Prix moyen gasoil Maroc DH/L
        for rec in self:
            cout_heures = rec.heures_utilisation * (rec.engin_id.cout_heure or 0)
            cout_gasoil = rec.gasoil_litres * prix_gasoil
            rec.cout_total = cout_heures + cout_gasoil
