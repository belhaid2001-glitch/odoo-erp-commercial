# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class StockValuationReport(models.Model):
    _name = 'stock.valuation.report'
    _description = 'Rapport de valorisation d\'inventaire'
    _auto = False
    _order = 'product_id'

    product_id = fields.Many2one('product.product', string='Produit', readonly=True)
    product_categ_id = fields.Many2one('product.category', string='Catégorie', readonly=True)
    location_id = fields.Many2one('stock.location', string='Emplacement', readonly=True)
    quantity = fields.Float(string='Quantité en stock', readonly=True)
    unit_cost = fields.Float(string='Coût unitaire', readonly=True)
    total_value = fields.Float(string='Valeur totale', readonly=True)
    uom_id = fields.Many2one('uom.uom', string='UdM', readonly=True)
    company_id = fields.Many2one('res.company', string='Société', readonly=True)

    def init(self):
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW stock_valuation_report AS (
                SELECT
                    ROW_NUMBER() OVER () as id,
                    sq.product_id,
                    pt.categ_id as product_categ_id,
                    sq.location_id,
                    sq.quantity,
                    COALESCE(ip.value_float, 0) as unit_cost,
                    sq.quantity * COALESCE(ip.value_float, 0) as total_value,
                    pt.uom_id,
                    sq.company_id
                FROM stock_quant sq
                JOIN product_product pp ON pp.id = sq.product_id
                JOIN product_template pt ON pt.id = pp.product_tmpl_id
                LEFT JOIN ir_property ip ON (
                    ip.name = 'standard_price'
                    AND ip.res_id = CONCAT('product.product,', pp.id)
                    AND ip.company_id = sq.company_id
                )
                JOIN stock_location sl ON sl.id = sq.location_id
                WHERE sl.usage = 'internal'
                AND sq.quantity > 0
            )
        """)
