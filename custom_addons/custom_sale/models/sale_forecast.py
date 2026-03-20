# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import timedelta


class SaleForecast(models.Model):
    _name = 'sale.forecast'
    _description = 'Prévision de vente'
    _order = 'date_forecast desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Référence',
        required=True,
        default=lambda self: _('Nouvelle'),
        readonly=True,
    )

    date_forecast = fields.Date(
        string='Date de prévision',
        required=True,
        default=fields.Date.today,
        tracking=True,
    )

    date_target = fields.Date(
        string='Date cible',
        required=True,
        tracking=True,
    )

    user_id = fields.Many2one(
        'res.users',
        string='Commercial',
        default=lambda self: self.env.user,
        tracking=True,
    )

    team_id = fields.Many2one(
        'crm.team',
        string='Équipe commerciale',
        tracking=True,
    )

    partner_id = fields.Many2one(
        'res.partner',
        string='Client',
    )

    product_id = fields.Many2one(
        'product.product',
        string='Produit',
    )

    forecast_amount = fields.Monetary(
        string='Montant prévu',
        currency_field='currency_id',
        tracking=True,
    )

    actual_amount = fields.Monetary(
        string='Montant réalisé',
        currency_field='currency_id',
        compute='_compute_actual_amount',
        store=True,
    )

    achievement_rate = fields.Float(
        string='Taux de réalisation (%)',
        compute='_compute_achievement_rate',
        store=True,
        digits=(5, 2),
    )

    currency_id = fields.Many2one(
        'res.currency',
        string='Devise',
        default=lambda self: self.env.company.currency_id,
    )

    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('confirmed', 'Confirmée'),
        ('done', 'Terminée'),
        ('cancelled', 'Annulée'),
    ], string='État', default='draft', tracking=True)

    notes = fields.Text(string='Notes')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('Nouvelle')) == _('Nouvelle'):
                vals['name'] = self.env['ir.sequence'].next_by_code('sale.forecast') or _('Nouvelle')
        return super().create(vals_list)

    @api.depends('date_target', 'user_id', 'partner_id', 'product_id')
    def _compute_actual_amount(self):
        for forecast in self:
            domain = [
                ('state', '=', 'sale'),
                ('date_order', '<=', forecast.date_target),
                ('date_order', '>=', forecast.date_forecast),
            ]
            if forecast.user_id:
                domain.append(('user_id', '=', forecast.user_id.id))
            if forecast.partner_id:
                domain.append(('partner_id', '=', forecast.partner_id.id))
            orders = self.env['sale.order'].search(domain)
            if forecast.product_id:
                amount = sum(
                    line.price_subtotal
                    for order in orders
                    for line in order.order_line
                    if line.product_id == forecast.product_id
                )
            else:
                amount = sum(orders.mapped('amount_untaxed'))
            forecast.actual_amount = amount

    @api.depends('forecast_amount', 'actual_amount')
    def _compute_achievement_rate(self):
        for forecast in self:
            if forecast.forecast_amount:
                forecast.achievement_rate = (forecast.actual_amount / forecast.forecast_amount) * 100
            else:
                forecast.achievement_rate = 0.0

    def action_confirm(self):
        self.write({'state': 'confirmed'})

    def action_done(self):
        self.write({'state': 'done'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    def action_reset_draft(self):
        self.write({'state': 'draft'})
