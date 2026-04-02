# -*- coding: utf-8 -*-
"""
Modèle btp.ressource — Gestion des ressources humaines BTP
"""

from odoo import models, fields, api


class BtpRessource(models.Model):
    _name = 'btp.ressource'
    _description = 'Ressource BTP'
    _inherit = ['mail.thread']
    _order = 'name'

    # ──────────────── Identification ────────────────
    name = fields.Char(string='Nom', compute='_compute_name', store=True)
    employee_id = fields.Many2one('hr.employee', string='Employé', required=True)
    partner_id = fields.Many2one('res.partner', related='employee_id.work_contact_id', string='Contact', store=True)

    # ──────────────── Qualification ────────────────
    qualification = fields.Selection([
        ('manoeuvre', 'Manœuvre'),
        ('ouvrier_qualifie', 'Ouvrier qualifié'),
        ('chef_equipe', 'Chef d\'équipe'),
        ('chef_chantier', 'Chef de chantier'),
        ('conducteur_travaux', 'Conducteur de travaux'),
        ('ingenieur', 'Ingénieur'),
        ('topographe', 'Topographe'),
    ], string='Qualification', required=True, tracking=True)

    specialite = fields.Selection([
        ('maconnerie', 'Maçonnerie'),
        ('coffrage', 'Coffrage'),
        ('ferraillage', 'Ferraillage'),
        ('electricite', 'Électricité'),
        ('plomberie', 'Plomberie'),
        ('peinture', 'Peinture'),
        ('etancheite', 'Étanchéité'),
        ('vrd', 'VRD'),
    ], string='Spécialité')

    # ──────────────── Rémunération ────────────────
    taux_journalier = fields.Float(string='Taux journalier (DH)')
    taux_horaire = fields.Float(string='Taux horaire (DH)', default=17.25)  # SMIG BTP 2025

    # ──────────────── Contrat ────────────────
    type_contrat = fields.Selection([
        ('cdi', 'CDI'),
        ('cdd', 'CDD'),
        ('journalier', 'Journalier'),
        ('tacheronnat', 'Tâcheronnat'),
    ], string='Type de contrat', required=True, default='journalier')

    # ──────────────── Documents ────────────────
    numero_cnss = fields.Char(string='N° CNSS')
    numero_cin = fields.Char(string='N° CIN')

    # ──────────────── Affectation ────────────────
    chantier_ids = fields.Many2many('btp.chantier', string='Chantiers affectés')
    active = fields.Boolean(default=True)

    # ──────────────── Relations ────────────────
    pointage_ids = fields.One2many('btp.pointage', 'ressource_id', string='Pointages')

    # ──────────────── Calcul du nom ────────────────
    @api.depends('employee_id', 'employee_id.name')
    def _compute_name(self):
        for rec in self:
            rec.name = rec.employee_id.name if rec.employee_id else ''

    _sql_constraints = [
        ('cin_unique', 'unique(numero_cin)', 'Le numéro CIN doit être unique !'),
        ('taux_horaire_positive', 'CHECK(taux_horaire >= 0)', 'Le taux horaire doit être positif !'),
    ]
