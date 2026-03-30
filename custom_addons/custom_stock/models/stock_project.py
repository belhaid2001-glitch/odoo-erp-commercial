# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class StockProject(models.Model):
    _name = 'stock.project'
    _description = 'Projet de stock'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(string='Nom du projet', required=True, tracking=True)
    code = fields.Char(
        string='Code',
        required=True,
        default=lambda self: _('Nouveau'),
        readonly=True,
    )
    description = fields.Text(string='Description')
    responsible_id = fields.Many2one(
        'res.users', string='Responsable',
        default=lambda self: self.env.user, tracking=True,
    )
    partner_id = fields.Many2one('res.partner', string='Client', tracking=True)
    date_start = fields.Date(string='Date de début', default=fields.Date.today)
    date_end = fields.Date(string='Date de fin prévue')
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('active', 'Actif'),
        ('done', 'Terminé'),
        ('cancelled', 'Annulé'),
    ], string='État', default='draft', tracking=True)

    # --- Lignes de stock du projet ---
    line_ids = fields.One2many('stock.project.line', 'project_id', string='Produits du projet')

    # --- Mouvements liés ---
    picking_ids = fields.One2many('stock.picking', 'stock_project_id', string='Opérations de stock')
    picking_count = fields.Integer(compute='_compute_picking_count', string='Opérations')

    # --- KPIs ---
    total_products = fields.Integer(compute='_compute_project_kpis', string='Nb produits', store=True)
    total_value = fields.Float(compute='_compute_project_kpis', string='Valeur totale', store=True)
    completion_rate = fields.Float(compute='_compute_project_kpis', string='Taux avancement (%)', store=True)
    stock_status = fields.Selection([
        ('ok', 'Suffisant'),
        ('warning', 'Attention'),
        ('critical', 'Critique'),
    ], compute='_compute_project_kpis', string='État du stock', store=True)

    color = fields.Integer(string='Couleur')
    notes = fields.Text(string='Notes internes')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('code', _('Nouveau')) == _('Nouveau'):
                vals['code'] = self.env['ir.sequence'].next_by_code('stock.project') or _('Nouveau')
        return super().create(vals_list)

    @api.depends('picking_ids')
    def _compute_picking_count(self):
        for project in self:
            project.picking_count = len(project.picking_ids)

    @api.depends('line_ids', 'line_ids.qty_available', 'line_ids.qty_required',
                 'line_ids.unit_cost')
    def _compute_project_kpis(self):
        for project in self:
            lines = project.line_ids
            project.total_products = len(lines)
            project.total_value = sum(l.qty_available * l.unit_cost for l in lines)

            if lines:
                fulfilled = sum(1 for l in lines if l.qty_available >= l.qty_required)
                project.completion_rate = round(fulfilled / len(lines) * 100, 1)
                shortage = sum(1 for l in lines if l.qty_available < l.qty_required * 0.5)
                if shortage > len(lines) * 0.3:
                    project.stock_status = 'critical'
                elif shortage > 0:
                    project.stock_status = 'warning'
                else:
                    project.stock_status = 'ok'
            else:
                project.completion_rate = 0
                project.stock_status = 'ok'

    # --- Actions ---
    def action_activate(self):
        self.write({'state': 'active'})

    def action_done(self):
        self.write({'state': 'done'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    def action_reset_draft(self):
        self.write({'state': 'draft'})

    def action_view_pickings(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Opérations - %s') % self.name,
            'res_model': 'stock.picking',
            'view_mode': 'tree,form',
            'domain': [('stock_project_id', '=', self.id)],
            'context': {'default_stock_project_id': self.id},
        }

    def action_check_stock(self):
        """Vérifier et mettre à jour les quantités disponibles depuis le stock réel"""
        for project in self:
            for line in project.line_ids:
                line._compute_qty_available()
            project.message_post(
                body=_("Vérification du stock effectuée par %s") % self.env.user.name,
                subtype_xmlid='mail.mt_note',
            )


class StockProjectLine(models.Model):
    _name = 'stock.project.line'
    _description = 'Ligne de stock par projet'

    project_id = fields.Many2one('stock.project', string='Projet', required=True, ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Produit', required=True)
    product_categ_id = fields.Many2one(
        'product.category', related='product_id.categ_id',
        string='Catégorie', store=True,
    )
    qty_required = fields.Float(string='Quantité requise', default=0)
    qty_reserved = fields.Float(string='Quantité réservée', default=0)
    qty_available = fields.Float(
        string='Quantité disponible',
        compute='_compute_qty_available',
        store=True,
    )
    qty_shortage = fields.Float(
        string='Manque',
        compute='_compute_shortage',
        store=True,
    )
    unit_cost = fields.Float(
        string='Coût unitaire',
        related='product_id.standard_price',
        store=True,
    )
    subtotal = fields.Float(
        string='Valeur',
        compute='_compute_subtotal',
        store=True,
    )
    uom_id = fields.Many2one(
        'uom.uom', related='product_id.uom_id',
        string='UdM', store=True,
    )
    status = fields.Selection([
        ('ok', '✅ Suffisant'),
        ('warning', '⚠️ Attention'),
        ('critical', '🔴 Critique'),
    ], compute='_compute_line_status', string='État', store=True)
    notes = fields.Char(string='Notes')

    @api.depends('product_id')
    def _compute_qty_available(self):
        for line in self:
            if line.product_id:
                line.qty_available = line.product_id.qty_available
            else:
                line.qty_available = 0

    @api.depends('qty_required', 'qty_available')
    def _compute_shortage(self):
        for line in self:
            diff = line.qty_required - line.qty_available
            line.qty_shortage = max(0, diff)

    @api.depends('qty_available', 'unit_cost')
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.qty_available * line.unit_cost

    @api.depends('qty_required', 'qty_available')
    def _compute_line_status(self):
        for line in self:
            if line.qty_required <= 0:
                line.status = 'ok'
            elif line.qty_available >= line.qty_required:
                line.status = 'ok'
            elif line.qty_available >= line.qty_required * 0.5:
                line.status = 'warning'
            else:
                line.status = 'critical'
