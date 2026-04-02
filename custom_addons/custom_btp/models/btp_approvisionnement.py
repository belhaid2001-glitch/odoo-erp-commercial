# -*- coding: utf-8 -*-
"""
Modèle btp.approvisionnement — Approvisionnement chantier BTP
"""

from odoo import models, fields, api
from odoo.exceptions import UserError


class BtpApprovisionnement(models.Model):
    _name = 'btp.approvisionnement'
    _description = 'Approvisionnement BTP'
    _order = 'date_besoin desc'
    _inherit = ['mail.thread']

    # ──────────────── Références ────────────────
    chantier_id = fields.Many2one('btp.chantier', string='Chantier', required=True)
    lot_id = fields.Many2one('btp.lot', string='Lot')
    product_id = fields.Many2one('product.product', string='Article', required=True)
    purchase_order_id = fields.Many2one('purchase.order', string='Bon de commande')

    # ──────────────── Quantités ────────────────
    quantite_demandee = fields.Float(string='Quantité demandée', required=True)
    quantite_livree = fields.Float(string='Quantité livrée', default=0.0)

    # ──────────────── Dates ────────────────
    date_besoin = fields.Date(string='Date du besoin', required=True)
    date_commande = fields.Date(string='Date commande')
    date_livraison_prevue = fields.Date(string='Date livraison prévue')
    date_livraison_reelle = fields.Date(string='Date livraison réelle')

    # ──────────────── État ────────────────
    state = fields.Selection([
        ('demande', 'Demande'),
        ('commande', 'Commandé'),
        ('partiel', 'Livraison partielle'),
        ('livre', 'Livré'),
    ], string='État', default='demande', tracking=True)

    urgence = fields.Boolean(string='Urgent', default=False)

    # ──────────────── Devise ────────────────
    company_id = fields.Many2one(related='chantier_id.company_id', store=True)
    currency_id = fields.Many2one(related='chantier_id.currency_id', store=True)

    # ──────────────── Action : Créer commande fournisseur ────────────────
    def action_creer_commande(self):
        """Créer un bon de commande fournisseur à partir de l'approvisionnement"""
        self.ensure_one()
        if self.purchase_order_id:
            raise UserError("Un bon de commande existe déjà pour cet approvisionnement.")

        # Chercher un fournisseur par défaut du produit
        supplier = self.product_id.seller_ids[:1]
        if not supplier:
            raise UserError("Aucun fournisseur défini pour ce produit. Veuillez en configurer un.")

        po = self.env['purchase.order'].create({
            'partner_id': supplier.partner_id.id,
            'origin': f'BTP/{self.chantier_id.reference}',
            'order_line': [(0, 0, {
                'product_id': self.product_id.id,
                'product_qty': self.quantite_demandee,
                'name': self.product_id.display_name,
                'price_unit': supplier.price or 0.0,
                'date_planned': self.date_besoin,
            })],
        })
        self.write({
            'purchase_order_id': po.id,
            'state': 'commande',
            'date_commande': fields.Date.today(),
        })
        return {
            'name': 'Bon de commande',
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.order',
            'res_id': po.id,
            'view_mode': 'form',
        }

    @api.onchange('quantite_livree')
    def _onchange_quantite_livree(self):
        if self.quantite_livree >= self.quantite_demandee:
            self.state = 'livre'
        elif self.quantite_livree > 0:
            self.state = 'partiel'
