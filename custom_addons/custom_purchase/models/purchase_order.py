# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    # --- Champs personnalisés ---
    priority = fields.Selection([
        ('0', 'Normale'),
        ('1', 'Basse'),
        ('2', 'Moyenne'),
        ('3', 'Haute'),
        ('4', 'Urgente'),
    ], string='Priorité', default='0', tracking=True)

    supplier_reference = fields.Char(
        string='Référence Fournisseur',
        tracking=True,
    )

    convention_id = fields.Many2one(
        'purchase.convention',
        string='Convention d\'achat',
        tracking=True,
    )

    packaging_instructions = fields.Text(
        string='Instructions de conditionnement',
    )

    total_savings = fields.Monetary(
        string='Économies réalisées',
        compute='_compute_total_savings',
        store=True,
        currency_field='currency_id',
    )

    approval_required = fields.Boolean(
        string='Approbation requise',
        compute='_compute_approval_required',
        store=True,
    )

    purchase_type = fields.Selection([
        ('standard', 'Standard'),
        ('urgent', 'Urgent'),
        ('framework', 'Marché-cadre'),
        ('recurring', 'Récurrent'),
    ], string='Type d\'achat', default='standard', tracking=True)

    reception_status = fields.Selection([
        ('pending', 'En attente'),
        ('partial', 'Partielle'),
        ('complete', 'Complète'),
    ], string='Statut réception', compute='_compute_reception_status', store=True)

    quality_check = fields.Boolean(
        string='Contrôle qualité requis',
        default=False,
    )

    quality_notes = fields.Text(
        string='Notes qualité',
    )

    # --- Calculs ---
    @api.depends('order_line.price_unit', 'order_line.product_qty', 'convention_id')
    def _compute_total_savings(self):
        for order in self:
            savings = 0.0
            if order.convention_id:
                for line in order.order_line:
                    standard_price = line.product_id.standard_price if line.product_id else 0
                    if standard_price > line.price_unit:
                        savings += (standard_price - line.price_unit) * line.product_qty
            order.total_savings = savings

    @api.depends('amount_total')
    def _compute_approval_required(self):
        for order in self:
            # Approbation requise au-dessus de 50 000
            order.approval_required = order.amount_total > 50000

    @api.depends('picking_ids.state')
    def _compute_reception_status(self):
        for order in self:
            if not order.picking_ids:
                order.reception_status = 'pending'
            elif all(p.state == 'done' for p in order.picking_ids):
                order.reception_status = 'complete'
            elif any(p.state == 'done' for p in order.picking_ids):
                order.reception_status = 'partial'
            else:
                order.reception_status = 'pending'

    # --- Actions ---
    def action_view_receptions(self):
        """Voir les réceptions associées"""
        return {
            'type': 'ir.actions.act_window',
            'name': _('Réceptions'),
            'res_model': 'stock.picking',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.picking_ids.ids)],
            'context': {'default_partner_id': self.partner_id.id},
        }

    @api.onchange('convention_id')
    def _onchange_convention_id(self):
        """Appliquer les conditions de la convention"""
        if self.convention_id:
            if self.convention_id.payment_term_id:
                self.payment_term_id = self.convention_id.payment_term_id
            if self.convention_id.notes:
                self.notes = self.convention_id.notes
