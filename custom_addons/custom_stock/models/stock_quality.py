# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class StockQualityCheck(models.Model):
    _name = 'stock.quality.check'
    _description = 'Contrôle qualité stock'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(
        string='Référence',
        default=lambda self: _('Nouveau'),
        readonly=True,
    )

    picking_id = fields.Many2one(
        'stock.picking',
        string='Transfert',
        required=True,
        ondelete='cascade',
    )

    product_id = fields.Many2one(
        'product.product',
        string='Produit',
        required=True,
    )

    quantity = fields.Float(
        string='Quantité à contrôler',
    )

    quantity_checked = fields.Float(
        string='Quantité contrôlée',
    )

    quantity_failed = fields.Float(
        string='Quantité défectueuse',
    )

    check_type = fields.Selection([
        ('visual', 'Visuel'),
        ('dimensional', 'Dimensionnel'),
        ('functional', 'Fonctionnel'),
        ('documentation', 'Documentation'),
    ], string='Type de contrôle', default='visual')

    result = fields.Selection([
        ('pending', 'En attente'),
        ('pass', 'Réussi'),
        ('fail', 'Échoué'),
    ], string='Résultat', default='pending', tracking=True)

    inspector_id = fields.Many2one(
        'res.users',
        string='Inspecteur',
        default=lambda self: self.env.user,
    )

    check_date = fields.Datetime(
        string='Date du contrôle',
    )

    notes = fields.Text(
        string='Observations',
    )

    lot_id = fields.Many2one(
        'stock.lot',
        string='Lot / N° de série',
    )

    team_id = fields.Many2one(
        'stock.quality.team',
        string='Équipe qualité',
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('Nouveau')) == _('Nouveau'):
                vals['name'] = self.env['ir.sequence'].next_by_code('stock.quality.check') or _('Nouveau')
        return super().create(vals_list)

    def action_pass(self):
        """Valider le contrôle"""
        self.write({
            'result': 'pass',
            'check_date': fields.Datetime.now(),
            'quantity_checked': self.quantity,
        })

    def action_fail(self):
        """Marquer comme échoué"""
        self.write({
            'result': 'fail',
            'check_date': fields.Datetime.now(),
        })

    def action_reset(self):
        """Remettre en attente"""
        self.write({
            'result': 'pending',
            'check_date': False,
        })


class StockQualityTeam(models.Model):
    _name = 'stock.quality.team'
    _description = 'Équipe qualité'

    name = fields.Char(string='Nom de l\'équipe', required=True)
    leader_id = fields.Many2one('res.users', string='Responsable')
    member_ids = fields.Many2many('res.users', string='Membres')
    active = fields.Boolean(default=True)
