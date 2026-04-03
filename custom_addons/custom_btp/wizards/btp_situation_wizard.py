# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError


class BtpSituationWizard(models.TransientModel):
    """Wizard — Génération d'une nouvelle situation de travaux"""
    _name = 'btp.situation.wizard'
    _description = 'Génération Situation de Travaux'

    # ── Champs ─────────────────────────────────────────────────
    chantier_id = fields.Many2one(
        'btp.chantier', string='Chantier', required=True,
        default=lambda self: self.env.context.get('active_id'),
    )
    date_debut = fields.Date('Début période', required=True)
    date_fin = fields.Date('Fin période', required=True)
    taux_tva = fields.Selection([
        ('20', '20%'),
        ('14', '14%'),
    ], string='Taux TVA', default='20', required=True)
    reprendre_cumuls = fields.Boolean(
        'Reprendre cumuls précédents', default=True,
        help="Pré-remplir les quantités précédentes depuis la dernière situation validée",
    )

    # ── Actions ────────────────────────────────────────────────
    def action_generer(self):
        """Génère une situation avec lignes pré-remplies"""
        self.ensure_one()

        if self.date_debut > self.date_fin:
            raise UserError("La date de début doit être antérieure à la date de fin.")

        chantier = self.chantier_id

        # Récupérer la dernière situation validée pour les cumuls
        derniere_situation = self.env['btp.situation'].search([
            ('chantier_id', '=', chantier.id),
            ('state', '=', 'valide'),
        ], order='numero desc', limit=1)

        cumuls = {}
        if derniere_situation and self.reprendre_cumuls:
            for line in derniere_situation.line_ids:
                key = (line.lot_id.id, line.designation)
                cumuls[key] = {
                    'quantite_precedente': line.quantite_cumule,
                }

        # Créer les lignes depuis les lots du chantier
        lines = []
        for lot in chantier.lot_ids:
            key = (lot.id, lot.name)
            qte_prec = cumuls.get(key, {}).get('quantite_precedente', 0)
            lines.append((0, 0, {
                'lot_id': lot.id,
                'designation': lot.name,
                'unite': 'ENS',
                'quantite_marche': lot.budget_prevu,
                'prix_unitaire': 1,
                'quantite_precedente': qte_prec,
                'quantite_periode': 0,
            }))

        situation = self.env['btp.situation'].create({
            'chantier_id': chantier.id,
            'date_debut_periode': self.date_debut,
            'date_fin_periode': self.date_fin,
            'taux_tva': self.taux_tva,
            'line_ids': lines,
        })

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'btp.situation',
            'res_id': situation.id,
            'view_mode': 'form',
            'target': 'current',
        }
