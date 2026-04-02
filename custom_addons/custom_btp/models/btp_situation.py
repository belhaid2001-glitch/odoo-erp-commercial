# -*- coding: utf-8 -*-
"""
Modèles btp.situation et btp.situation.line — Situations de travaux BTP Maroc
"""

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


class BtpSituation(models.Model):
    _name = 'btp.situation'
    _description = 'Situation de travaux BTP'
    _order = 'numero desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # ──────────────── Identification ────────────────
    numero = fields.Char(string='Numéro', readonly=True, copy=False, default='Nouveau')
    chantier_id = fields.Many2one('btp.chantier', string='Chantier', required=True, tracking=True)
    company_id = fields.Many2one(related='chantier_id.company_id', store=True)
    currency_id = fields.Many2one(related='chantier_id.currency_id', store=True)

    # ──────────────── Période ────────────────
    date_debut_periode = fields.Date(string='Début de période', required=True)
    date_fin_periode = fields.Date(string='Fin de période', required=True)

    # ──────────────── Montants ────────────────
    montant_cumule_precedent = fields.Monetary(string='Montant cumulé précédent', currency_field='currency_id')
    montant_periode = fields.Monetary(string='Montant de la période', compute='_compute_montants', store=True, currency_field='currency_id')
    montant_cumule = fields.Monetary(string='Montant cumulé', compute='_compute_montants', store=True, currency_field='currency_id')

    # ──────────────── Avancement ────────────────
    taux_avancement = fields.Float(string='Taux d\'avancement (%)', compute='_compute_montants', store=True)

    # ──────────────── Retenue / TVA / Net ────────────────
    taux_tva = fields.Selection([
        ('20', '20%'),
        ('14', '14%'),
    ], string='Taux TVA', default='20', required=True)
    montant_retenue_garantie = fields.Monetary(string='Retenue de garantie', compute='_compute_montants', store=True, currency_field='currency_id')
    montant_tva = fields.Monetary(string='Montant TVA', compute='_compute_montants', store=True, currency_field='currency_id')
    montant_net = fields.Monetary(string='Montant net à payer', compute='_compute_montants', store=True, currency_field='currency_id')

    # ──────────────── Facture ────────────────
    move_id = fields.Many2one('account.move', string='Facture comptable', readonly=True)

    # ──────────────── État ────────────────
    state = fields.Selection([
        ('brouillon', 'Brouillon'),
        ('valide', 'Validé'),
        ('facture', 'Facturé'),
        ('paye', 'Payé'),
    ], string='État', default='brouillon', tracking=True)

    # ──────────────── Lignes ────────────────
    line_ids = fields.One2many('btp.situation.line', 'situation_id', string='Lignes de situation')

    # ──────────────── Calculs ────────────────
    @api.depends('line_ids', 'line_ids.montant_periode', 'line_ids.montant_cumule',
                 'montant_cumule_precedent', 'chantier_id.montant_total',
                 'chantier_id.taux_retenue_garantie', 'taux_tva')
    def _compute_montants(self):
        for rec in self:
            rec.montant_periode = sum(rec.line_ids.mapped('montant_periode'))
            rec.montant_cumule = rec.montant_cumule_precedent + rec.montant_periode

            # Taux d'avancement par rapport au montant total du marché
            if rec.chantier_id.montant_total:
                rec.taux_avancement = (rec.montant_cumule / rec.chantier_id.montant_total) * 100
            else:
                rec.taux_avancement = 0.0

            # Retenue de garantie sur le montant de la période
            taux_retenue = float(rec.chantier_id.taux_retenue_garantie or '5') / 100.0
            rec.montant_retenue_garantie = rec.montant_periode * taux_retenue

            # TVA
            taux_tva = float(rec.taux_tva or '20') / 100.0
            montant_ht = rec.montant_periode - rec.montant_retenue_garantie
            rec.montant_tva = montant_ht * taux_tva
            rec.montant_net = montant_ht + rec.montant_tva

    # ──────────────── Séquence ────────────────
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('numero', 'Nouveau') == 'Nouveau':
                vals['numero'] = self.env['ir.sequence'].next_by_code('btp.situation') or 'Nouveau'
        return super().create(vals_list)

    # ──────────────── Actions ────────────────
    def action_valider(self):
        self.write({'state': 'valide'})

    def action_generer_facture(self):
        """Générer une facture fournisseur (account.move) à partir de la situation"""
        self.ensure_one()
        if self.move_id:
            raise UserError("Une facture existe déjà pour cette situation.")
        if self.state != 'valide':
            raise UserError("La situation doit être validée avant de générer une facture.")

        move = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'partner_id': self.chantier_id.maitre_ouvrage_id.id,
            'ref': f'Situation {self.numero} - {self.chantier_id.name}',
            'invoice_date': self.date_fin_periode,
            'invoice_line_ids': [(0, 0, {
                'name': f'Situation {self.numero} - Période du {self.date_debut_periode} au {self.date_fin_periode}',
                'quantity': 1,
                'price_unit': self.montant_periode - self.montant_retenue_garantie,
            })],
        })
        self.write({'move_id': move.id, 'state': 'facture'})
        return {
            'name': 'Facture',
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'res_id': move.id,
            'view_mode': 'form',
        }

    def action_marquer_paye(self):
        self.write({'state': 'paye'})

    def action_remettre_brouillon(self):
        self.write({'state': 'brouillon'})

    # ──────────────── Contraintes ────────────────
    @api.constrains('date_debut_periode', 'date_fin_periode')
    def _check_dates(self):
        for rec in self:
            if rec.date_debut_periode and rec.date_fin_periode:
                if rec.date_fin_periode < rec.date_debut_periode:
                    raise ValidationError("La fin de période doit être postérieure au début.")

    _sql_constraints = [
        ('numero_unique', 'unique(numero)', 'Le numéro de situation doit être unique !'),
    ]


class BtpSituationLine(models.Model):
    _name = 'btp.situation.line'
    _description = 'Ligne de situation BTP'
    _order = 'sequence, id'

    # ──────────────── Références ────────────────
    situation_id = fields.Many2one('btp.situation', string='Situation', required=True, ondelete='cascade')
    lot_id = fields.Many2one('btp.lot', string='Lot')
    sequence = fields.Integer(default=10)

    # ──────────────── Désignation ────────────────
    designation = fields.Char(string='Désignation', required=True)
    unite = fields.Char(string='Unité', default='u')

    # ──────────────── Quantités et prix ────────────────
    quantite_marche = fields.Float(string='Quantité marché')
    prix_unitaire = fields.Float(string='Prix unitaire (DH)')
    quantite_precedente = fields.Float(string='Quantité précédente')
    quantite_periode = fields.Float(string='Quantité période')
    quantite_cumule = fields.Float(string='Quantité cumulée', compute='_compute_quantites', store=True)

    # ──────────────── Montants ────────────────
    montant_periode = fields.Float(string='Montant période', compute='_compute_montants', store=True)
    montant_cumule = fields.Float(string='Montant cumulé', compute='_compute_montants', store=True)

    # ──────────────── Calculs ────────────────
    @api.depends('quantite_precedente', 'quantite_periode')
    def _compute_quantites(self):
        for rec in self:
            rec.quantite_cumule = (rec.quantite_precedente or 0) + (rec.quantite_periode or 0)

    @api.depends('quantite_periode', 'quantite_cumule', 'prix_unitaire')
    def _compute_montants(self):
        for rec in self:
            rec.montant_periode = rec.quantite_periode * rec.prix_unitaire
            rec.montant_cumule = rec.quantite_cumule * rec.prix_unitaire
