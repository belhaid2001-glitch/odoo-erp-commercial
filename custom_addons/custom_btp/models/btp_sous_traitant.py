# -*- coding: utf-8 -*-
"""
Modèle btp.sous.traitant — Sous-traitants BTP Maroc
"""

from odoo import models, fields, api
from datetime import date


class BtpSousTraitant(models.Model):
    _name = 'btp.sous.traitant'
    _description = 'Sous-traitant BTP'
    _inherit = ['mail.thread']
    _order = 'name'

    # ──────────────── Identification ────────────────
    name = fields.Char(string='Nom', compute='_compute_name', store=True)
    partner_id = fields.Many2one('res.partner', string='Partenaire', required=True)

    # ──────────────── Spécialité ────────────────
    specialite = fields.Char(string='Spécialité')

    # ──────────────── Documents légaux marocains ────────────────
    numero_rc = fields.Char(string='N° Registre de Commerce')
    numero_patente = fields.Char(string='N° Patente')
    numero_if = fields.Char(string='N° Identifiant Fiscal')
    numero_ice = fields.Char(string='N° ICE')
    numero_cnss = fields.Char(string='N° CNSS')

    # ──────────────── Validité documents ────────────────
    attestation_fiscale_valide = fields.Date(string='Attestation fiscale valide jusqu\'au')
    assurance_rc_valide = fields.Date(string='Assurance RC valide jusqu\'au')
    agrement = fields.Char(string='Agrément')

    # ──────────────── Affectation ────────────────
    chantier_ids = fields.Many2many('btp.chantier', string='Chantiers')
    montant_contrat = fields.Float(string='Montant contrat (DH)')

    # ──────────────── État ────────────────
    state = fields.Selection([
        ('actif', 'Actif'),
        ('suspendu', 'Suspendu'),
        ('resilie', 'Résilié'),
    ], string='État', default='actif', tracking=True)

    # ──────────────── Conformité ────────────────
    documents_conformes = fields.Boolean(string='Documents conformes', compute='_compute_conformite', store=True)

    # ──────────────── Calculs ────────────────
    @api.depends('partner_id', 'partner_id.name')
    def _compute_name(self):
        for rec in self:
            rec.name = rec.partner_id.name if rec.partner_id else ''

    @api.depends('attestation_fiscale_valide', 'assurance_rc_valide', 'numero_rc',
                 'numero_patente', 'numero_if', 'numero_ice', 'numero_cnss')
    def _compute_conformite(self):
        today = date.today()
        for rec in self:
            conformite = True
            # Vérifier les documents obligatoires
            if not all([rec.numero_rc, rec.numero_patente, rec.numero_if, rec.numero_ice, rec.numero_cnss]):
                conformite = False
            # Vérifier la validité de l'attestation fiscale
            if rec.attestation_fiscale_valide and rec.attestation_fiscale_valide < today:
                conformite = False
            # Vérifier la validité de l'assurance RC
            if rec.assurance_rc_valide and rec.assurance_rc_valide < today:
                conformite = False
            rec.documents_conformes = conformite
