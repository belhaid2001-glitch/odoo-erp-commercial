# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import json
import logging

_logger = logging.getLogger(__name__)

MONTH_NAMES_FR = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun',
                  'Jul', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc']


class DashboardKpi(models.Model):
    _name = 'dashboard.kpi'
    _description = 'KPI du tableau de bord'

    name = fields.Char(string='Nom du KPI', required=True)
    category = fields.Selection([
        ('sale', 'Ventes'),
        ('purchase', 'Achats'),
        ('stock', 'Stock'),
        ('accounting', 'Comptabilité'),
        ('hr', 'Ressources Humaines'),
        ('crm', 'CRM'),
    ], string='Catégorie', required=True)
    sequence = fields.Integer(string='Séquence', default=10)
    active = fields.Boolean(default=True)
    color = fields.Integer(string='Couleur')
    icon = fields.Char(string='Icône (FontAwesome)', default='fa-bar-chart')
    description = fields.Text(string='Description')

    # ====================================================================
    #  POWER BI-STYLE FULL DASHBOARD DATA
    # ====================================================================
    @api.model
    def get_full_dashboard_data(self):
        """Return all data needed by the OWL dashboard component."""
        today = fields.Date.today()
        first_day_month = today.replace(day=1)
        last_month_start = (first_day_month - timedelta(days=1)).replace(day=1)
        last_month_end = first_day_month - timedelta(days=1)

        kpis = self._dashboard_kpis(today, first_day_month, last_month_start)
        charts = self._dashboard_charts(today, first_day_month)
        alerts = self._dashboard_alerts(today)

        return {
            'kpis': kpis,
            'charts': charts,
            'alerts': alerts,
            'today': today.strftime('%d/%m/%Y'),
            'period_label': 'Données du mois en cours',
        }

    # ---------- KPIs ----------
    @api.model
    def _dashboard_kpis(self, today, first_day_month, last_month_start):
        SO = self.env['sale.order']
        PO = self.env['purchase.order']
        AM = self.env['account.move']
        SP = self.env['stock.picking']
        CL = self.env['crm.lead']

        # --- Sales ---
        sale_this = SO.search([('date_order', '>=', first_day_month),
                               ('state', 'in', ['sale', 'done'])])
        sale_last = SO.search([('date_order', '>=', last_month_start),
                               ('date_order', '<', first_day_month),
                               ('state', 'in', ['sale', 'done'])])
        rev_this = sum(sale_this.mapped('amount_total'))
        rev_last = sum(sale_last.mapped('amount_total'))
        quotations = SO.search_count([('state', '=', 'draft')])
        to_invoice = SO.search_count([('invoice_status', '=', 'to invoice')])

        # --- Purchases ---
        po_this = PO.search([('date_order', '>=', first_day_month),
                             ('state', 'in', ['purchase', 'done'])])
        po_last = PO.search([('date_order', '>=', last_month_start),
                             ('date_order', '<', first_day_month),
                             ('state', 'in', ['purchase', 'done'])])
        pur_this = sum(po_this.mapped('amount_total'))
        pur_last = sum(po_last.mapped('amount_total'))
        rfq = PO.search_count([('state', '=', 'draft')])

        # --- Accounting ---
        unpaid = AM.search([('move_type', '=', 'out_invoice'),
                            ('payment_state', 'in', ['not_paid', 'partial']),
                            ('state', '=', 'posted')])
        unpaid_total = sum(unpaid.mapped('amount_residual'))
        overdue = AM.search_count([('move_type', '=', 'out_invoice'),
                                   ('payment_state', 'in', ['not_paid', 'partial']),
                                   ('state', '=', 'posted'),
                                   ('invoice_date_due', '<', today)])

        # --- Stock ---
        deliveries = SP.search_count([('picking_type_code', '=', 'outgoing'),
                                      ('state', 'in', ['assigned', 'confirmed'])])
        receipts = SP.search_count([('picking_type_code', '=', 'incoming'),
                                    ('state', 'in', ['assigned', 'confirmed'])])
        late = SP.search_count([('state', 'in', ['assigned', 'confirmed']),
                                ('scheduled_date', '<', fields.Datetime.now())])

        # --- CRM ---
        opps = CL.search([('type', '=', 'opportunity'), ('active', '=', True)])
        pipeline_val = sum(opps.mapped('expected_revenue'))
        hot_leads = 0
        try:
            hot_leads = CL.search_count([('lead_quality', '=', 'hot')])
        except Exception:
            pass

        return {
            'revenue_this_month': rev_this,
            'revenue_trend': ((rev_this - rev_last) / rev_last * 100) if rev_last else 0,
            'orders_count': len(sale_this),
            'quotations_count': quotations,
            'to_invoice_count': to_invoice,
            'purchase_total': pur_this,
            'purchase_trend': ((pur_this - pur_last) / pur_last * 100) if pur_last else 0,
            'rfq_count': rfq,
            'unpaid_invoices': unpaid_total,
            'unpaid_count': len(unpaid),
            'overdue_count': overdue,
            'deliveries_pending': deliveries,
            'receipts_pending': receipts,
            'late_pickings': late,
            'pipeline_value': pipeline_val,
            'open_opportunities': len(opps),
            'hot_leads': hot_leads,
        }

    # ---------- Chart Data ----------
    @api.model
    def _dashboard_charts(self, today, first_day_month):
        return {
            'monthly_revenue': self._chart_monthly_revenue(today),
            'sales_by_type': self._chart_sales_by_type(),
            'stock_overview': self._chart_stock_overview(),
            'crm_pipeline': self._chart_crm_pipeline(),
        }

    @api.model
    def _chart_monthly_revenue(self, today):
        """Revenue vs Expenses for the last 6 months."""
        labels, revenue, expenses = [], [], []
        for i in range(5, -1, -1):
            dt = today - relativedelta(months=i)
            m_start = dt.replace(day=1)
            m_end = (m_start + relativedelta(months=1)) - timedelta(days=1)
            labels.append(MONTH_NAMES_FR[m_start.month - 1])
            # Revenue = confirmed customer invoices
            inv = self.env['account.move'].search([
                ('move_type', '=', 'out_invoice'),
                ('state', '=', 'posted'),
                ('invoice_date', '>=', m_start),
                ('invoice_date', '<=', m_end),
            ])
            revenue.append(sum(inv.mapped('amount_total')))
            # Expenses = confirmed vendor bills
            bills = self.env['account.move'].search([
                ('move_type', '=', 'in_invoice'),
                ('state', '=', 'posted'),
                ('invoice_date', '>=', m_start),
                ('invoice_date', '<=', m_end),
            ])
            expenses.append(sum(bills.mapped('amount_total')))
        return {'labels': labels, 'revenue': revenue, 'expenses': expenses}

    @api.model
    def _chart_sales_by_type(self):
        """Sales distribution by type (or by state if sale_type not available)."""
        labels, data = [], []
        try:
            groups = self.env['sale.order'].read_group(
                [('state', 'in', ['sale', 'done'])],
                ['amount_total:sum'],
                ['sale_type'],
            )
            type_labels = dict(self.env['sale.order']._fields.get('sale_type', {}).selection or [])
            for g in groups:
                lbl = type_labels.get(g['sale_type'], g['sale_type'] or 'Non défini')
                labels.append(lbl)
                data.append(g['amount_total'] or 0)
        except Exception:
            # Fallback: by sale state
            for state, label in [('draft', 'Brouillon'), ('sale', 'Confirmé'), ('done', 'Terminé')]:
                count = self.env['sale.order'].search_count([('state', '=', state)])
                if count:
                    labels.append(label)
                    data.append(count)
        if not labels:
            labels, data = ['Aucune donnée'], [0]
        return {'labels': labels, 'data': data}

    @api.model
    def _chart_stock_overview(self):
        """Stock operations overview."""
        SP = self.env['stock.picking']
        items = [
            ('Réceptions', [('picking_type_code', '=', 'incoming'), ('state', 'in', ['assigned', 'confirmed'])]),
            ('Livraisons', [('picking_type_code', '=', 'outgoing'), ('state', 'in', ['assigned', 'confirmed'])]),
            ('En retard', [('state', 'in', ['assigned', 'confirmed']), ('scheduled_date', '<', fields.Datetime.now())]),
            ('Internes', [('picking_type_code', '=', 'internal'), ('state', 'in', ['assigned', 'confirmed'])]),
        ]
        labels = [i[0] for i in items]
        data = [SP.search_count(i[1]) for i in items]
        return {'labels': labels, 'data': data}

    @api.model
    def _chart_crm_pipeline(self):
        """CRM pipeline by stage."""
        labels, data = [], []
        try:
            groups = self.env['crm.lead'].read_group(
                [('type', '=', 'opportunity'), ('active', '=', True)],
                ['expected_revenue:sum'],
                ['stage_id'],
            )
            for g in groups:
                labels.append(g['stage_id'][1] if g['stage_id'] else 'Non défini')
                data.append(g['expected_revenue'] or 0)
        except Exception:
            labels, data = ['Aucune donnée'], [0]
        return {'labels': labels, 'data': data}

    # ---------- Alerts ----------
    @api.model
    def _dashboard_alerts(self, today):
        alerts = []
        alert_id = 0

        # Overdue invoices
        overdue = self.env['account.move'].search_count([
            ('move_type', '=', 'out_invoice'),
            ('payment_state', 'in', ['not_paid', 'partial']),
            ('state', '=', 'posted'),
            ('invoice_date_due', '<', today),
        ])
        if overdue:
            alert_id += 1
            alerts.append({
                'id': alert_id, 'type': 'danger', 'icon': 'fa-exclamation-triangle',
                'title': 'Factures en retard',
                'subtitle': '%d facture(s) au-delà de l\'échéance' % overdue,
                'count': overdue,
                'action': {
                    'type': 'ir.actions.act_window',
                    'name': 'Factures en retard',
                    'res_model': 'account.move',
                    'view_mode': 'list,form',
                    'domain': [('move_type', '=', 'out_invoice'),
                               ('payment_state', 'in', ['not_paid', 'partial']),
                               ('state', '=', 'posted'),
                               ('invoice_date_due', '<', str(today))],
                },
            })

        # Late pickings
        late = self.env['stock.picking'].search_count([
            ('state', 'in', ['assigned', 'confirmed']),
            ('scheduled_date', '<', fields.Datetime.now()),
        ])
        if late:
            alert_id += 1
            alerts.append({
                'id': alert_id, 'type': 'warning', 'icon': 'fa-clock-o',
                'title': 'Opérations en retard',
                'subtitle': '%d opération(s) logistique(s) en retard' % late,
                'count': late,
                'action': {
                    'type': 'ir.actions.act_window',
                    'name': 'Opérations en retard',
                    'res_model': 'stock.picking',
                    'view_mode': 'list,form',
                    'domain': [('state', 'in', ['assigned', 'confirmed']),
                               ('scheduled_date', '<', str(fields.Datetime.now()))],
                },
            })

        # Hot leads
        try:
            hot = self.env['crm.lead'].search_count([('lead_quality', '=', 'hot')])
            if hot:
                alert_id += 1
                alerts.append({
                    'id': alert_id, 'type': 'info', 'icon': 'fa-fire',
                    'title': 'Leads chauds à traiter',
                    'subtitle': '%d lead(s) à fort potentiel' % hot,
                    'count': hot,
                    'action': {
                        'type': 'ir.actions.act_window',
                        'name': 'Leads chauds',
                        'res_model': 'crm.lead',
                        'view_mode': 'list,kanban,form',
                        'domain': [('lead_quality', '=', 'hot')],
                    },
                })
        except Exception:
            pass

        # Quotations waiting
        quotes = self.env['sale.order'].search_count([('state', '=', 'draft')])
        if quotes:
            alert_id += 1
            alerts.append({
                'id': alert_id, 'type': 'info', 'icon': 'fa-file-text-o',
                'title': 'Devis en attente',
                'subtitle': '%d devis à confirmer ou relancer' % quotes,
                'count': quotes,
                'action': {
                    'type': 'ir.actions.act_window',
                    'name': 'Devis en cours',
                    'res_model': 'sale.order',
                    'view_mode': 'list,form',
                    'domain': [('state', '=', 'draft')],
                },
            })

        return alerts


class DashboardMixin(models.AbstractModel):
    _name = 'dashboard.mixin'
    _description = 'Mixin pour les données du tableau de bord'

    @api.model
    def get_dashboard_data(self):
        """Retourne toutes les données consolidées du tableau de bord"""
        today = fields.Date.today()
        first_day_month = today.replace(day=1)
        last_month_start = (first_day_month - timedelta(days=1)).replace(day=1)

        return {
            'sales': self._get_sales_data(today, first_day_month, last_month_start),
            'purchases': self._get_purchase_data(today, first_day_month, last_month_start),
            'stock': self._get_stock_data(),
            'accounting': self._get_accounting_data(today, first_day_month),
            'hr': self._get_hr_data(),
            'crm': self._get_crm_data(today, first_day_month),
        }

    @api.model
    def _get_sales_data(self, today, first_day_month, last_month_start):
        SaleOrder = self.env['sale.order']

        # Commandes ce mois
        orders_this_month = SaleOrder.search([
            ('date_order', '>=', first_day_month),
            ('state', 'in', ['sale', 'done']),
        ])
        # Commandes mois dernier
        orders_last_month = SaleOrder.search([
            ('date_order', '>=', last_month_start),
            ('date_order', '<', first_day_month),
            ('state', 'in', ['sale', 'done']),
        ])
        # Devis en cours
        quotations = SaleOrder.search_count([
            ('state', '=', 'draft'),
        ])
        # À facturer
        to_invoice = SaleOrder.search_count([
            ('invoice_status', '=', 'to invoice'),
        ])

        ca_this_month = sum(orders_this_month.mapped('amount_total'))
        ca_last_month = sum(orders_last_month.mapped('amount_total'))

        return {
            'ca_this_month': ca_this_month,
            'ca_last_month': ca_last_month,
            'orders_count': len(orders_this_month),
            'quotations_count': quotations,
            'to_invoice_count': to_invoice,
            'evolution': ((ca_this_month - ca_last_month) / ca_last_month * 100) if ca_last_month else 0,
        }

    @api.model
    def _get_purchase_data(self, today, first_day_month, last_month_start):
        PurchaseOrder = self.env['purchase.order']

        orders_this_month = PurchaseOrder.search([
            ('date_order', '>=', first_day_month),
            ('state', 'in', ['purchase', 'done']),
        ])
        orders_last_month = PurchaseOrder.search([
            ('date_order', '>=', last_month_start),
            ('date_order', '<', first_day_month),
            ('state', 'in', ['purchase', 'done']),
        ])
        # Demandes de prix en cours
        rfq_count = PurchaseOrder.search_count([
            ('state', '=', 'draft'),
        ])
        # À recevoir (commandes confirmées)
        to_receive = PurchaseOrder.search_count([
            ('state', '=', 'purchase'),
        ])

        total_this_month = sum(orders_this_month.mapped('amount_total'))
        total_last_month = sum(orders_last_month.mapped('amount_total'))

        return {
            'total_this_month': total_this_month,
            'total_last_month': total_last_month,
            'orders_count': len(orders_this_month),
            'rfq_count': rfq_count,
            'to_receive_count': to_receive,
            'evolution': ((total_this_month - total_last_month) / total_last_month * 100) if total_last_month else 0,
        }

    @api.model
    def _get_stock_data(self):
        StockPicking = self.env['stock.picking']

        # Réceptions en attente
        receipts_pending = StockPicking.search_count([
            ('picking_type_code', '=', 'incoming'),
            ('state', 'in', ['assigned', 'confirmed']),
        ])
        # Livraisons en attente
        deliveries_pending = StockPicking.search_count([
            ('picking_type_code', '=', 'outgoing'),
            ('state', 'in', ['assigned', 'confirmed']),
        ])
        # Transferts internes en attente
        internals_pending = StockPicking.search_count([
            ('picking_type_code', '=', 'internal'),
            ('state', 'in', ['assigned', 'confirmed']),
        ])
        # En retard
        late_pickings = StockPicking.search_count([
            ('state', 'in', ['assigned', 'confirmed']),
            ('scheduled_date', '<', fields.Datetime.now()),
        ])

        # Produits en stock (valeur approximative)
        products_in_stock = self.env['product.product'].search_count([
            ('qty_available', '>', 0),
            ('type', '=', 'product'),
        ])

        return {
            'receipts_pending': receipts_pending,
            'deliveries_pending': deliveries_pending,
            'internals_pending': internals_pending,
            'late_pickings': late_pickings,
            'products_in_stock': products_in_stock,
        }

    @api.model
    def _get_accounting_data(self, today, first_day_month):
        AccountMove = self.env['account.move']

        # Factures clients impayées
        unpaid_invoices = AccountMove.search([
            ('move_type', '=', 'out_invoice'),
            ('payment_state', 'in', ['not_paid', 'partial']),
            ('state', '=', 'posted'),
        ])
        unpaid_total = sum(unpaid_invoices.mapped('amount_residual'))

        # Factures fournisseurs impayées
        unpaid_bills = AccountMove.search([
            ('move_type', '=', 'in_invoice'),
            ('payment_state', 'in', ['not_paid', 'partial']),
            ('state', '=', 'posted'),
        ])
        unpaid_bills_total = sum(unpaid_bills.mapped('amount_residual'))

        # Factures en retard
        overdue_invoices = AccountMove.search_count([
            ('move_type', '=', 'out_invoice'),
            ('payment_state', 'in', ['not_paid', 'partial']),
            ('state', '=', 'posted'),
            ('invoice_date_due', '<', today),
        ])

        # CA facturé ce mois
        invoiced_this_month = AccountMove.search([
            ('move_type', '=', 'out_invoice'),
            ('state', '=', 'posted'),
            ('invoice_date', '>=', first_day_month),
        ])
        invoiced_total = sum(invoiced_this_month.mapped('amount_total'))

        return {
            'unpaid_invoices_total': unpaid_total,
            'unpaid_invoices_count': len(unpaid_invoices),
            'unpaid_bills_total': unpaid_bills_total,
            'unpaid_bills_count': len(unpaid_bills),
            'overdue_count': overdue_invoices,
            'invoiced_this_month': invoiced_total,
        }

    @api.model
    def _get_hr_data(self):
        HrEmployee = self.env['hr.employee']

        total_employees = HrEmployee.search_count([])

        # Congés en cours (si le module hr_holidays est installé)
        leaves_today = 0
        if 'hr.leave' in self.env:
            leaves_today = self.env['hr.leave'].search_count([
                ('state', '=', 'validate'),
                ('date_from', '<=', fields.Datetime.now()),
                ('date_to', '>=', fields.Datetime.now()),
            ])

        return {
            'total_employees': total_employees,
            'leaves_today': leaves_today,
        }

    @api.model
    def _get_crm_data(self, today, first_day_month):
        CrmLead = self.env['crm.lead']

        # Opportunités ouvertes
        open_opportunities = CrmLead.search([
            ('type', '=', 'opportunity'),
            ('active', '=', True),
        ])
        pipeline_value = sum(open_opportunities.mapped('expected_revenue'))

        # Nouvelles pistes ce mois
        new_leads = CrmLead.search_count([
            ('create_date', '>=', first_day_month),
        ])

        # Opportunités gagnées ce mois
        won_this_month = CrmLead.search([
            ('stage_id.is_won', '=', True),
            ('date_closed', '>=', first_day_month),
        ])
        won_revenue = sum(won_this_month.mapped('expected_revenue'))

        return {
            'open_opportunities': len(open_opportunities),
            'pipeline_value': pipeline_value,
            'new_leads': new_leads,
            'won_count': len(won_this_month),
            'won_revenue': won_revenue,
        }
