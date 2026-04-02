# -*- coding: utf-8 -*-
"""
Modèles btp.reunion et btp.decision — Réunions de chantier BTP
"""

from odoo import models, fields, api


class BtpReunion(models.Model):
    _name = 'btp.reunion'
    _description = 'Réunion de chantier BTP'
    _order = 'date desc'
    _inherit = ['mail.thread']

    # ──────────────── Références ────────────────
    chantier_id = fields.Many2one('btp.chantier', string='Chantier', required=True)

    # ──────────────── Détails ────────────────
    name = fields.Char(string='Objet', compute='_compute_name', store=True)
    date = fields.Datetime(string='Date et heure', required=True, default=fields.Datetime.now)
    type = fields.Selection([
        ('chantier', 'Réunion de chantier'),
        ('coordination', 'Réunion de coordination'),
        ('securite', 'Réunion sécurité'),
    ], string='Type', required=True, default='chantier')

    # ──────────────── Contenu ────────────────
    ordre_jour = fields.Html(string='Ordre du jour')
    compte_rendu = fields.Html(string='Compte rendu')

    # ──────────────── Participants ────────────────
    participant_ids = fields.Many2many('res.partner', string='Participants')

    # ──────────────── Décisions ────────────────
    decision_ids = fields.One2many('btp.decision', 'reunion_id', string='Décisions')

    # ──────────────── Calcul du nom ────────────────
    @api.depends('type', 'date', 'chantier_id')
    def _compute_name(self):
        type_labels = dict(self._fields['type'].selection)
        for rec in self:
            type_label = type_labels.get(rec.type, '')
            date_str = rec.date.strftime('%d/%m/%Y') if rec.date else ''
            chantier_name = rec.chantier_id.name or ''
            rec.name = f'{type_label} - {chantier_name} - {date_str}'


class BtpDecision(models.Model):
    _name = 'btp.decision'
    _description = 'Décision de réunion BTP'
    _order = 'date_echeance'

    # ──────────────── Références ────────────────
    reunion_id = fields.Many2one('btp.reunion', string='Réunion', required=True, ondelete='cascade')
    responsable_id = fields.Many2one('res.users', string='Responsable')

    # ──────────────── Détails ────────────────
    description = fields.Text(string='Description', required=True)
    date_echeance = fields.Date(string='Date échéance')

    # ──────────────── État ────────────────
    state = fields.Selection([
        ('en_cours', 'En cours'),
        ('fait', 'Fait'),
        ('retard', 'En retard'),
    ], string='État', default='en_cours')
