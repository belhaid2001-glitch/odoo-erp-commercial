# -*- coding: utf-8 -*-
"""
Modèle btp.document — Documents de chantier BTP (obligatoires au Maroc)
"""

from odoo import models, fields, api
from datetime import date, timedelta


class BtpDocument(models.Model):
    _name = 'btp.document'
    _description = 'Document BTP'
    _order = 'date_emission desc'
    _inherit = ['mail.thread']

    # ──────────────── Références ────────────────
    chantier_id = fields.Many2one('btp.chantier', string='Chantier', required=True)
    name = fields.Char(string='Nom du document', required=True)

    # ──────────────── Fichier ────────────────
    fichier = fields.Binary(string='Fichier')
    filename = fields.Char(string='Nom du fichier')

    # ──────────────── Type ────────────────
    type_document = fields.Selection([
        ('permis_construire', 'Permis de construire'),
        ('autorisation_travaux', 'Autorisation de travaux'),
        ('plan_beton_arme', 'Plan béton armé'),
        ('plan_archi', 'Plan architectural'),
        ('os_commencement', 'Ordre de service de commencement'),
        ('os_arret', 'Ordre de service d\'arrêt'),
        ('os_reprise', 'Ordre de service de reprise'),
        ('attestation_assurance', 'Attestation d\'assurance'),
        ('pv_reunion', 'PV de réunion'),
        ('pv_reception', 'PV de réception'),
        ('registre_chantier', 'Registre de chantier'),
        ('plan_hygiene_securite', 'Plan d\'hygiène et sécurité'),
        ('declaration_ouverture_chantier', 'Déclaration d\'ouverture de chantier'),
        ('attestation_cnss', 'Attestation CNSS'),
        ('attestation_fiscale', 'Attestation fiscale'),
        ('caution_bancaire', 'Caution bancaire'),
    ], string='Type de document', required=True)

    # ──────────────── Dates ────────────────
    date_emission = fields.Date(string='Date d\'émission')
    date_expiration = fields.Date(string='Date d\'expiration')
    obligatoire = fields.Boolean(string='Obligatoire', default=False)

    # ──────────────── Alertes ────────────────
    alerte_expiration = fields.Boolean(string='Alerte expiration', compute='_compute_alerte', store=True)

    # ──────────────── Calculs ────────────────
    @api.depends('date_expiration')
    def _compute_alerte(self):
        today = date.today()
        seuil = today + timedelta(days=30)
        for rec in self:
            if rec.date_expiration:
                rec.alerte_expiration = rec.date_expiration <= seuil
            else:
                rec.alerte_expiration = False
