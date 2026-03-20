# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class PurchaseConvention(models.Model):
    _name = 'purchase.convention'
    _description = 'Convention d\'achat'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_start desc'

    name = fields.Char(
        string='Référence',
        required=True,
        default=lambda self: _('Nouvelle'),
        readonly=True,
    )

    partner_id = fields.Many2one(
        'res.partner',
        string='Fournisseur',
        required=True,
        tracking=True,
        domain=[('supplier_rank', '>', 0)],
    )

    date_start = fields.Date(
        string='Date début',
        required=True,
        tracking=True,
    )

    date_end = fields.Date(
        string='Date fin',
        required=True,
        tracking=True,
    )

    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('active', 'Active'),
        ('expired', 'Expirée'),
        ('cancelled', 'Annulée'),
    ], string='État', default='draft', tracking=True)

    payment_term_id = fields.Many2one(
        'account.payment.term',
        string='Conditions de paiement',
    )

    discount = fields.Float(
        string='Remise globale (%)',
        digits=(5, 2),
    )

    min_amount = fields.Monetary(
        string='Montant minimum',
        currency_field='currency_id',
    )

    max_amount = fields.Monetary(
        string='Montant maximum',
        currency_field='currency_id',
    )

    currency_id = fields.Many2one(
        'res.currency',
        string='Devise',
        default=lambda self: self.env.company.currency_id,
    )

    product_ids = fields.Many2many(
        'product.product',
        string='Produits concernés',
    )

    line_ids = fields.One2many(
        'purchase.convention.line',
        'convention_id',
        string='Lignes de convention',
    )

    purchase_count = fields.Integer(
        string='Nombre de commandes',
        compute='_compute_purchase_count',
    )

    total_purchased = fields.Monetary(
        string='Total commandé',
        compute='_compute_total_purchased',
        currency_field='currency_id',
    )

    notes = fields.Text(string='Conditions particulières')

    company_id = fields.Many2one(
        'res.company',
        string='Société',
        default=lambda self: self.env.company,
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('Nouvelle')) == _('Nouvelle'):
                vals['name'] = self.env['ir.sequence'].next_by_code('purchase.convention') or _('Nouvelle')
        return super().create(vals_list)

    def _compute_purchase_count(self):
        for conv in self:
            conv.purchase_count = self.env['purchase.order'].search_count([
                ('convention_id', '=', conv.id)
            ])

    def _compute_total_purchased(self):
        for conv in self:
            orders = self.env['purchase.order'].search([
                ('convention_id', '=', conv.id),
                ('state', 'in', ['purchase', 'done']),
            ])
            conv.total_purchased = sum(orders.mapped('amount_untaxed'))

    def action_activate(self):
        self.write({'state': 'active'})

    def action_expire(self):
        self.write({'state': 'expired'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    def action_reset_draft(self):
        self.write({'state': 'draft'})

    def action_view_purchases(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Commandes d\'achat'),
            'res_model': 'purchase.order',
            'view_mode': 'tree,form',
            'domain': [('convention_id', '=', self.id)],
        }

    @api.model
    def _cron_check_expiration(self):
        """Vérifier et expirer les conventions arrivées à terme"""
        today = fields.Date.today()
        expired = self.search([
            ('state', '=', 'active'),
            ('date_end', '<', today),
        ])
        expired.action_expire()


class PurchaseConventionLine(models.Model):
    _name = 'purchase.convention.line'
    _description = 'Ligne de convention d\'achat'

    convention_id = fields.Many2one(
        'purchase.convention',
        string='Convention',
        required=True,
        ondelete='cascade',
    )

    product_id = fields.Many2one(
        'product.product',
        string='Produit',
        required=True,
    )

    min_qty = fields.Float(
        string='Quantité minimum',
    )

    max_qty = fields.Float(
        string='Quantité maximum',
    )

    negotiated_price = fields.Float(
        string='Prix négocié',
        digits='Product Price',
    )

    discount = fields.Float(
        string='Remise (%)',
        digits=(5, 2),
    )

    uom_id = fields.Many2one(
        'uom.uom',
        string='Unité de mesure',
        related='product_id.uom_id',
        readonly=True,
    )
