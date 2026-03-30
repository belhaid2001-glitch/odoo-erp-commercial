# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import timedelta
import logging

_logger = logging.getLogger(__name__)


class StockIntelligentReorder(models.Model):
    _name = 'stock.intelligent.reorder'
    _description = 'Règle de réapprovisionnement intelligent'
    _inherit = ['mail.thread']
    _order = 'priority desc, product_id'

    product_id = fields.Many2one('product.product', string='Produit', required=True, tracking=True)
    product_categ_id = fields.Many2one(
        'product.category', related='product_id.categ_id',
        string='Catégorie', store=True,
    )
    warehouse_id = fields.Many2one('stock.warehouse', string='Entrepôt',
                                    default=lambda self: self.env['stock.warehouse'].search([], limit=1))
    location_id = fields.Many2one('stock.location', string='Emplacement')

    # --- Seuils ---
    qty_min = fields.Float(string='Stock minimum', required=True, tracking=True,
                           help="Seuil en dessous duquel une alerte est déclenchée")
    qty_max = fields.Float(string='Stock maximum',
                           help="Quantité cible à atteindre lors du réapprovisionnement")
    qty_available = fields.Float(string='Stock actuel', compute='_compute_qty_available', store=True)
    qty_to_order = fields.Float(string='Quantité à commander', compute='_compute_qty_to_order', store=True)

    # --- Fournisseur ---
    supplier_id = fields.Many2one('res.partner', string='Fournisseur préféré',
                                   domain=[('supplier_rank', '>', 0)])
    lead_time = fields.Integer(string='Délai fournisseur (jours)', default=7)
    last_purchase_price = fields.Float(string='Dernier prix d\'achat')

    # --- Analyse intelligente ---
    avg_daily_consumption = fields.Float(
        string='Consommation moy/jour',
        compute='_compute_consumption_stats', store=True,
        help="Calculée sur les 90 derniers jours",
    )
    days_of_stock = fields.Float(
        string='Jours de stock restant',
        compute='_compute_consumption_stats', store=True,
    )
    estimated_stockout_date = fields.Date(
        string='Date de rupture estimée',
        compute='_compute_consumption_stats', store=True,
    )
    trend = fields.Selection([
        ('up', '↗ En hausse'),
        ('stable', '→ Stable'),
        ('down', '↘ En baisse'),
    ], string='Tendance', compute='_compute_consumption_stats', store=True)

    # --- Priorité & État ---
    priority = fields.Selection([
        ('0', 'Normale'),
        ('1', 'Basse'),
        ('2', 'Moyenne'),
        ('3', 'Haute'),
        ('4', 'Critique'),
    ], string='Priorité', compute='_compute_priority', store=True)
    state = fields.Selection([
        ('ok', '✅ OK'),
        ('warning', '⚠️ Attention'),
        ('critical', '🔴 Critique'),
        ('stockout', '⛔ Rupture'),
    ], string='État', compute='_compute_priority', store=True)
    active = fields.Boolean(default=True)
    notes = fields.Text(string='Notes')

    @api.depends('product_id')
    def _compute_qty_available(self):
        for rule in self:
            rule.qty_available = rule.product_id.qty_available if rule.product_id else 0

    @api.depends('qty_available', 'qty_max')
    def _compute_qty_to_order(self):
        for rule in self:
            if rule.qty_available < rule.qty_min and rule.qty_max:
                rule.qty_to_order = rule.qty_max - rule.qty_available
            elif rule.qty_available < rule.qty_min:
                rule.qty_to_order = rule.qty_min * 2 - rule.qty_available
            else:
                rule.qty_to_order = 0

    @api.depends('product_id', 'qty_available')
    def _compute_consumption_stats(self):
        today = fields.Date.today()
        date_90 = today - timedelta(days=90)
        date_30 = today - timedelta(days=30)

        for rule in self:
            if not rule.product_id:
                rule.avg_daily_consumption = 0
                rule.days_of_stock = 0
                rule.estimated_stockout_date = False
                rule.trend = 'stable'
                continue

            # Consommation sur 90 jours (mouvements sortants)
            moves_90 = self.env['stock.move'].search([
                ('product_id', '=', rule.product_id.id),
                ('state', '=', 'done'),
                ('date', '>=', date_90),
                ('picking_type_id.code', '=', 'outgoing'),
            ])
            total_90 = sum(moves_90.mapped('product_uom_qty'))
            avg_daily = total_90 / 90.0 if total_90 else 0
            rule.avg_daily_consumption = round(avg_daily, 2)

            # Jours de stock restant
            if avg_daily > 0 and rule.qty_available > 0:
                rule.days_of_stock = round(rule.qty_available / avg_daily, 0)
                rule.estimated_stockout_date = today + timedelta(days=int(rule.days_of_stock))
            else:
                rule.days_of_stock = 999 if rule.qty_available > 0 else 0
                rule.estimated_stockout_date = False

            # Tendance (comparer 30 derniers jours vs les 30 précédents)
            moves_30 = self.env['stock.move'].search([
                ('product_id', '=', rule.product_id.id),
                ('state', '=', 'done'),
                ('date', '>=', date_30),
                ('picking_type_id.code', '=', 'outgoing'),
            ])
            total_30 = sum(moves_30.mapped('product_uom_qty'))
            total_prev = total_90 - total_30

            if total_30 > total_prev * 1.2:
                rule.trend = 'up'
            elif total_30 < total_prev * 0.8:
                rule.trend = 'down'
            else:
                rule.trend = 'stable'

    @api.depends('qty_available', 'qty_min', 'days_of_stock', 'lead_time')
    def _compute_priority(self):
        for rule in self:
            if rule.qty_available <= 0:
                rule.state = 'stockout'
                rule.priority = '4'
            elif rule.qty_available < rule.qty_min * 0.5:
                rule.state = 'critical'
                rule.priority = '3'
            elif rule.qty_available < rule.qty_min:
                rule.state = 'warning'
                rule.priority = '2'
            else:
                rule.state = 'ok'
                rule.priority = '0'
            # Ajuster si rupture prévue avant fin délai fournisseur
            if rule.days_of_stock > 0 and rule.days_of_stock <= rule.lead_time:
                if rule.state == 'ok':
                    rule.state = 'warning'
                    rule.priority = '2'

    def action_create_purchase_order(self):
        """Créer un bon de commande fournisseur pour réapprovisionner"""
        self.ensure_one()
        if not self.supplier_id:
            from odoo.exceptions import UserError
            raise UserError(_("Veuillez définir un fournisseur préféré avant de commander."))
        return {
            'type': 'ir.actions.act_window',
            'name': _('Réapprovisionnement - %s') % self.product_id.display_name,
            'res_model': 'purchase.order',
            'view_mode': 'form',
            'context': {
                'default_partner_id': self.supplier_id.id,
                'default_order_line': [(0, 0, {
                    'product_id': self.product_id.id,
                    'product_qty': self.qty_to_order,
                    'price_unit': self.last_purchase_price or self.product_id.standard_price,
                })],
            },
        }

    @api.model
    def _cron_refresh_stock_data(self):
        """Cron : recalculer les statistiques de stock pour toutes les règles"""
        rules = self.search([('active', '=', True)])
        for rule in rules:
            rule._compute_qty_available()
            rule._compute_consumption_stats()
            rule._compute_priority()
        _logger.info("Stock intelligent : %d règles mises à jour", len(rules))
