# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class ContactSegment(models.Model):
    _name = 'contact.segment'
    _description = 'Segment de contact'
    _order = 'name'

    name = fields.Char(string='Nom du segment', required=True)
    description = fields.Text(string='Description')
    color = fields.Integer(string='Couleur')
    partner_ids = fields.Many2many(
        'res.partner',
        'partner_segment_rel',
        'segment_id',
        'partner_id',
        string='Contacts',
    )
    partner_count = fields.Integer(
        string='Nombre de contacts',
        compute='_compute_partner_count',
    )
    active = fields.Boolean(default=True)

    def _compute_partner_count(self):
        for segment in self:
            segment.partner_count = len(segment.partner_ids)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # --- Informations complémentaires ---
    ice = fields.Char(string='ICE', help='Identifiant Commun de l\'Entreprise')
    rc = fields.Char(string='RC', help='Registre du Commerce')
    if_code = fields.Char(string='IF', help='Identifiant Fiscal')
    cnss = fields.Char(string='CNSS')
    capital = fields.Float(string='Capital social')
    date_creation_company = fields.Date(string='Date de création entreprise')

    # --- Classification ---
    contact_type_custom = fields.Selection([
        ('prospect', 'Prospect'),
        ('client', 'Client'),
        ('supplier', 'Fournisseur'),
        ('partner', 'Partenaire'),
        ('other', 'Autre'),
    ], string='Type de relation', default='other', tracking=True)

    contact_priority = fields.Selection([
        ('low', 'Faible'),
        ('medium', 'Moyen'),
        ('high', 'Élevé'),
        ('vip', 'VIP'),
    ], string='Priorité', default='medium')

    segment_ids = fields.Many2many(
        'contact.segment',
        'partner_segment_rel',
        'partner_id',
        'segment_id',
        string='Segments',
    )

    # --- Communication ---
    preferred_contact_method = fields.Selection([
        ('email', 'E-mail'),
        ('phone', 'Téléphone'),
        ('whatsapp', 'WhatsApp'),
        ('visit', 'Visite'),
        ('mail', 'Courrier'),
    ], string='Moyen de contact préféré', default='email')

    linkedin = fields.Char(string='LinkedIn')
    facebook = fields.Char(string='Facebook')
    instagram = fields.Char(string='Instagram')

    # --- Adresses supplémentaires ---
    delivery_address_ids = fields.One2many(
        'res.partner',
        'parent_id',
        string='Adresses de livraison',
        domain=[('type', '=', 'delivery')],
    )
    invoice_address_ids = fields.One2many(
        'res.partner',
        'parent_id',
        string='Adresses de facturation',
        domain=[('type', '=', 'invoice')],
    )

    # --- Statistiques ---
    total_sale_amount = fields.Monetary(
        string='CA Total Ventes',
        compute='_compute_sale_stats',
        currency_field='currency_id',
    )
    sale_order_count_custom = fields.Integer(
        string='Nombre de commandes',
        compute='_compute_sale_stats',
    )
    total_purchase_amount = fields.Monetary(
        string='Total Achats',
        compute='_compute_purchase_stats',
        currency_field='currency_id',
    )
    purchase_order_count_custom = fields.Integer(
        string='Nombre de commandes fournisseur',
        compute='_compute_purchase_stats',
    )

    first_order_date = fields.Date(
        string='Première commande',
        compute='_compute_sale_stats',
    )
    last_order_date = fields.Date(
        string='Dernière commande',
        compute='_compute_sale_stats',
    )

    # --- Notes internes ---
    internal_notes = fields.Html(string='Notes internes')

    # --- Calculs ---
    def _compute_sale_stats(self):
        for partner in self:
            orders = self.env['sale.order'].search([
                ('partner_id', '=', partner.id),
                ('state', 'in', ['sale', 'done']),
            ])
            partner.total_sale_amount = sum(orders.mapped('amount_total'))
            partner.sale_order_count_custom = len(orders)
            if orders:
                dates = orders.mapped('date_order')
                partner.first_order_date = min(dates).date() if dates else False
                partner.last_order_date = max(dates).date() if dates else False
            else:
                partner.first_order_date = False
                partner.last_order_date = False

    def _compute_purchase_stats(self):
        for partner in self:
            orders = self.env['purchase.order'].search([
                ('partner_id', '=', partner.id),
                ('state', 'in', ['purchase', 'done']),
            ])
            partner.total_purchase_amount = sum(orders.mapped('amount_total'))
            partner.purchase_order_count_custom = len(orders)

    # --- Actions ---
    def action_view_sale_orders(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Commandes de vente'),
            'res_model': 'sale.order',
            'view_mode': 'tree,form',
            'domain': [('partner_id', '=', self.id)],
            'context': {'default_partner_id': self.id},
        }

    def action_view_purchase_orders(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Commandes d\'achat'),
            'res_model': 'purchase.order',
            'view_mode': 'tree,form',
            'domain': [('partner_id', '=', self.id)],
            'context': {'default_partner_id': self.id},
        }
