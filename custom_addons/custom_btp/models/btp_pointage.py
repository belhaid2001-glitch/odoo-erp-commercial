# -*- coding: utf-8 -*-
"""
Modèle btp.pointage — Pointage des ressources BTP avec géolocalisation
"""

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class BtpPointage(models.Model):
    _name = 'btp.pointage'
    _description = 'Pointage BTP'
    _order = 'date desc, heure_debut'
    _inherit = ['mail.thread']

    # ──────────────── Références ────────────────
    ressource_id = fields.Many2one('btp.ressource', string='Ressource', required=True)
    tache_id = fields.Many2one('btp.tache', string='Tâche')
    chantier_id = fields.Many2one('btp.chantier', string='Chantier', required=True)
    employee_id = fields.Many2one('hr.employee', related='ressource_id.employee_id', store=True)

    # ──────────────── Temps ────────────────
    date = fields.Date(string='Date', required=True, default=fields.Date.today)
    heure_debut = fields.Float(string='Heure début')
    heure_fin = fields.Float(string='Heure fin')
    heures_normales = fields.Float(string='Heures normales', compute='_compute_heures', store=True)
    heures_sup_25 = fields.Float(string='Heures sup +25%', default=0.0)
    heures_sup_50 = fields.Float(string='Heures sup +50%', default=0.0)
    heures_sup_100 = fields.Float(string='Heures sup +100%', default=0.0)

    # ──────────────── Montant ────────────────
    montant_journee = fields.Float(string='Montant journée (DH)', compute='_compute_montant', store=True)

    # ──────────────── Géolocalisation ────────────────
    latitude = fields.Float(string='Latitude', digits=(10, 7))
    longitude = fields.Float(string='Longitude', digits=(10, 7))
    photo_presence = fields.Binary(string='Photo de présence')

    # ──────────────── Validation ────────────────
    valide = fields.Boolean(string='Validé', default=False)
    valide_par = fields.Many2one('res.users', string='Validé par')

    # ──────────────── Calcul heures normales ────────────────
    @api.depends('heure_debut', 'heure_fin')
    def _compute_heures(self):
        for rec in self:
            if rec.heure_debut and rec.heure_fin and rec.heure_fin > rec.heure_debut:
                heures_totales = rec.heure_fin - rec.heure_debut
                # Les 8 premières heures sont normales
                rec.heures_normales = min(heures_totales, 8.0)
            else:
                rec.heures_normales = 0.0

    @api.depends('heures_normales', 'heures_sup_25', 'heures_sup_50', 'heures_sup_100', 'ressource_id.taux_horaire')
    def _compute_montant(self):
        """
        Calcul selon SMIG BTP Maroc :
        - Heures normales : taux horaire
        - Heures sup +25% : taux × 1.25 (après 8h)
        - Heures sup +50% : taux × 1.50 (nuit)
        - Heures sup +100% : taux × 2.00 (jours fériés)
        """
        for rec in self:
            taux = rec.ressource_id.taux_horaire if rec.ressource_id else 17.25  # SMIG BTP 2025
            montant = rec.heures_normales * taux
            montant += rec.heures_sup_25 * taux * 1.25
            montant += rec.heures_sup_50 * taux * 1.50
            montant += rec.heures_sup_100 * taux * 2.00
            rec.montant_journee = montant

    # ──────────────── Actions ────────────────
    def action_valider(self):
        for rec in self:
            rec.write({'valide': True, 'valide_par': self.env.uid})

    def action_invalider(self):
        self.write({'valide': False, 'valide_par': False})

    # ──────────────── Contraintes ────────────────
    @api.constrains('heure_debut', 'heure_fin')
    def _check_heures(self):
        for rec in self:
            if rec.heure_debut and rec.heure_fin:
                if rec.heure_fin <= rec.heure_debut:
                    raise ValidationError("L'heure de fin doit être postérieure à l'heure de début.")
                if rec.heure_debut < 0 or rec.heure_fin > 24:
                    raise ValidationError("Les heures doivent être entre 0 et 24.")
