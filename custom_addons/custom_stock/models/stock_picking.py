# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    # --- Lien projet ---
    stock_project_id = fields.Many2one(
        'stock.project', string='Projet',
        tracking=True, help='Projet associé à cette opération de stock',
    )

    # --- Champs personnalisés ---
    priority_custom = fields.Selection([
        ('0', 'Normale'),
        ('1', 'Basse'),
        ('2', 'Moyenne'),
        ('3', 'Haute'),
        ('4', 'Urgente'),
    ], string='Priorité', default='0', tracking=True)

    preparation_status = fields.Selection([
        ('not_started', 'Non commencée'),
        ('in_progress', 'En cours'),
        ('ready', 'Prête'),
        ('shipped', 'Expédiée'),
    ], string='Statut préparation', default='not_started', tracking=True)

    barcode_scanned = fields.Char(
        string='Code-barre scanné',
        help='Scanner un code-barre pour trouver le produit',
    )

    preparation_notes = fields.Text(
        string='Notes de préparation',
    )

    weight_total = fields.Float(
        string='Poids total (kg)',
        compute='_compute_weight_total',
        store=True,
    )

    package_count = fields.Integer(
        string='Nombre de colis',
        default=1,
    )

    quality_check_required = fields.Boolean(
        string='Contrôle qualité requis',
        default=False,
    )

    quality_check_ids = fields.One2many(
        'stock.quality.check',
        'picking_id',
        string='Contrôles qualité',
    )

    quality_status = fields.Selection([
        ('none', 'Aucun'),
        ('pending', 'En attente'),
        ('passed', 'Réussi'),
        ('failed', 'Échoué'),
    ], string='Statut qualité',
        compute='_compute_quality_status',
        store=True,
    )

    delivery_instructions = fields.Text(
        string='Instructions de livraison',
    )

    carrier_tracking = fields.Char(
        string='Numéro de suivi',
        tracking=True,
    )

    # --- Calculs ---
    @api.depends('move_line_ids.quantity')
    def _compute_weight_total(self):
        for picking in self:
            total = 0.0
            for line in picking.move_line_ids:
                if line.product_id and line.product_id.weight:
                    total += line.product_id.weight * line.quantity
            picking.weight_total = total

    @api.depends('quality_check_ids.result')
    def _compute_quality_status(self):
        for picking in self:
            checks = picking.quality_check_ids
            if not checks:
                picking.quality_status = 'none'
            elif any(c.result == 'fail' for c in checks):
                picking.quality_status = 'failed'
            elif all(c.result == 'pass' for c in checks):
                picking.quality_status = 'passed'
            else:
                picking.quality_status = 'pending'

    # --- Actions ---
    def action_start_preparation(self):
        """Commencer la préparation"""
        self.write({'preparation_status': 'in_progress'})
        self.message_post(
            body=_("Préparation commencée par %s") % self.env.user.name,
            subtype_xmlid='mail.mt_note',
        )

    def action_mark_ready(self):
        """Marquer comme prêt"""
        for picking in self:
            if picking.quality_check_required and picking.quality_status != 'passed':
                raise UserError(_("Le contrôle qualité doit être validé avant de marquer comme prêt."))
        self.write({'preparation_status': 'ready'})

    def action_mark_shipped(self):
        """Marquer comme expédié"""
        self.write({'preparation_status': 'shipped'})

    @api.onchange('barcode_scanned')
    def _onchange_barcode_scanned(self):
        """Rechercher un produit par code-barre"""
        if self.barcode_scanned:
            product = self.env['product.product'].search([
                ('barcode', '=', self.barcode_scanned)
            ], limit=1)
            if product:
                # Trouver la ligne correspondante et incrémenter
                for line in self.move_line_ids:
                    if line.product_id == product:
                        line.quantity += 1
                        break
                self.barcode_scanned = ''
            else:
                return {
                    'warning': {
                        'title': _('Produit non trouvé'),
                        'message': _('Aucun produit trouvé avec le code-barre : %s') % self.barcode_scanned,
                    }
                }

    def action_create_quality_checks(self):
        """Créer des contrôles qualité pour tous les produits"""
        for picking in self:
            for move in picking.move_ids:
                self.env['stock.quality.check'].create({
                    'picking_id': picking.id,
                    'product_id': move.product_id.id,
                    'quantity': move.product_uom_qty,
                    'team_id': False,
                })
            picking.quality_check_required = True
