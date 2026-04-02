# -*- coding: utf-8 -*-
"""
Modèle btp.meteo — Suivi météo chantier (justification retards)
"""

from odoo import models, fields


class BtpMeteo(models.Model):
    _name = 'btp.meteo'
    _description = 'Météo Chantier BTP'
    _order = 'date desc'

    # ──────────────── Références ────────────────
    chantier_id = fields.Many2one('btp.chantier', string='Chantier', required=True, ondelete='cascade')

    # ──────────────── Données ────────────────
    date = fields.Date(string='Date', required=True, default=fields.Date.today)
    intemperie = fields.Boolean(string='Intempérie', default=False)
    description = fields.Text(string='Description')

    # ──────────────── Impact ────────────────
    impact_travaux = fields.Selection([
        ('aucun', 'Aucun impact'),
        ('ralenti', 'Travaux ralentis'),
        ('arret', 'Arrêt des travaux'),
    ], string='Impact sur les travaux', default='aucun')

    # ──────────────── Justificatif ────────────────
    justificatif = fields.Binary(string='Justificatif')
    justificatif_filename = fields.Char(string='Nom fichier')
