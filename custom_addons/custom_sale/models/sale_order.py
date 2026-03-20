# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # --- Champs personnalisés ---
    priority = fields.Selection([
        ('0', 'Normale'),
        ('1', 'Basse'),
        ('2', 'Moyenne'),
        ('3', 'Haute'),
        ('4', 'Urgente'),
    ], string='Priorité', default='0', tracking=True)

    customer_reference = fields.Char(
        string='Référence Client',
        help='Référence communiquée par le client',
        tracking=True,
    )

    delivery_note = fields.Text(
        string='Instructions de livraison',
        help='Instructions spéciales pour la livraison',
    )

    margin_percent = fields.Float(
        string='Marge (%)',
        compute='_compute_margin_percent',
        store=True,
        digits=(5, 2),
    )

    total_discount = fields.Monetary(
        string='Remise totale',
        compute='_compute_total_discount',
        store=True,
        currency_field='currency_id',
    )

    is_ready_to_invoice = fields.Boolean(
        string='Prêt à facturer',
        compute='_compute_is_ready_to_invoice',
        store=True,
    )

    sale_type = fields.Selection([
        ('standard', 'Standard'),
        ('subscription', 'Abonnement'),
        ('project', 'Projet'),
    ], string='Type de vente', default='standard', tracking=True)

    approval_status = fields.Selection([
        ('draft', 'Brouillon'),
        ('pending', 'En attente d\'approbation'),
        ('approved', 'Approuvé'),
        ('rejected', 'Rejeté'),
    ], string='Statut d\'approbation', default='draft', tracking=True)

    approved_by = fields.Many2one(
        'res.users',
        string='Approuvé par',
        readonly=True,
    )

    approval_date = fields.Datetime(
        string='Date d\'approbation',
        readonly=True,
    )

    optional_product_ids = fields.One2many(
        'sale.order.optional.product',
        'order_id',
        string='Produits optionnels',
    )

    # --- Calculs ---
    @api.depends('amount_untaxed', 'margin')
    def _compute_margin_percent(self):
        for order in self:
            if order.amount_untaxed:
                order.margin_percent = (order.margin / order.amount_untaxed) * 100
            else:
                order.margin_percent = 0.0

    @api.depends('order_line.discount', 'order_line.price_unit', 'order_line.product_uom_qty')
    def _compute_total_discount(self):
        for order in self:
            total = 0.0
            for line in order.order_line:
                if line.discount:
                    total += (line.price_unit * line.product_uom_qty * line.discount) / 100
            order.total_discount = total

    @api.depends('state', 'invoice_status')
    def _compute_is_ready_to_invoice(self):
        for order in self:
            order.is_ready_to_invoice = (
                order.state == 'sale' and order.invoice_status == 'to invoice'
            )

    # --- Actions ---
    def action_request_approval(self):
        """Demander l'approbation d'un devis"""
        for order in self:
            if order.approval_status != 'draft':
                raise UserError(_("Seuls les devis en brouillon peuvent être soumis pour approbation."))
            order.approval_status = 'pending'
            # Notification
            order.message_post(
                body=_("Demande d'approbation soumise par %s") % self.env.user.name,
                subtype_xmlid='mail.mt_note',
            )

    def action_approve_order(self):
        """Approuver un devis"""
        for order in self:
            order.write({
                'approval_status': 'approved',
                'approved_by': self.env.user.id,
                'approval_date': fields.Datetime.now(),
            })
            order.message_post(
                body=_("Devis approuvé par %s") % self.env.user.name,
                subtype_xmlid='mail.mt_note',
            )

    def action_reject_order(self):
        """Rejeter un devis"""
        for order in self:
            order.write({
                'approval_status': 'rejected',
            })
            order.message_post(
                body=_("Devis rejeté par %s") % self.env.user.name,
                subtype_xmlid='mail.mt_note',
            )

    def action_generate_invoice_batch(self):
        """Facturation en lot des commandes prêtes"""
        orders = self.filtered(lambda o: o.is_ready_to_invoice)
        if not orders:
            raise UserError(_("Aucune commande prête à facturer sélectionnée."))
        invoices = orders._create_invoices()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Factures créées'),
            'res_model': 'account.move',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', invoices.ids)],
        }


class SaleOrderOptionalProduct(models.Model):
    _name = 'sale.order.optional.product'
    _description = 'Produit optionnel de commande'

    order_id = fields.Many2one(
        'sale.order',
        string='Commande',
        required=True,
        ondelete='cascade',
    )

    product_id = fields.Many2one(
        'product.product',
        string='Produit',
        required=True,
    )

    description = fields.Text(string='Description')

    quantity = fields.Float(
        string='Quantité',
        default=1.0,
    )

    price_unit = fields.Float(
        string='Prix unitaire',
        digits='Product Price',
    )

    is_selected = fields.Boolean(
        string='Sélectionné',
        default=False,
    )

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.description = self.product_id.description_sale or self.product_id.name
            self.price_unit = self.product_id.lst_price

    def action_add_to_order(self):
        """Ajouter le produit optionnel à la commande"""
        for rec in self:
            rec.is_selected = True
            self.env['sale.order.line'].create({
                'order_id': rec.order_id.id,
                'product_id': rec.product_id.id,
                'product_uom_qty': rec.quantity,
                'price_unit': rec.price_unit,
                'name': rec.description or rec.product_id.name,
            })
