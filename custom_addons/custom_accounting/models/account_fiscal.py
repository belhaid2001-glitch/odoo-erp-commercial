# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import timedelta


class AccountFiscalYear(models.Model):
    _name = 'account.fiscal.year.custom'
    _description = 'Exercice fiscal'
    _order = 'date_from desc'

    name = fields.Char(string='Exercice', required=True)
    date_from = fields.Date(string='Date début', required=True)
    date_to = fields.Date(string='Date fin', required=True)
    state = fields.Selection([
        ('open', 'Ouvert'),
        ('closed', 'Clôturé'),
    ], string='État', default='open', tracking=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company, required=True)
    notes = fields.Text(string='Notes')

    def action_close(self):
        self.write({'state': 'closed'})

    def action_reopen(self):
        self.write({'state': 'open'})


class AccountPaymentTracking(models.Model):
    _name = 'account.payment.tracking'
    _description = 'Suivi des paiements'
    _inherit = ['mail.thread']
    _order = 'date desc'

    name = fields.Char(string='Référence', default=lambda self: _('Nouveau'), readonly=True)
    partner_id = fields.Many2one('res.partner', string='Client / Fournisseur', required=True, tracking=True)
    partner_type = fields.Selection([
        ('customer', 'Client'),
        ('supplier', 'Fournisseur'),
    ], string='Type', required=True, default='customer')
    move_id = fields.Many2one('account.move', string='Facture liée')
    amount = fields.Monetary(string='Montant', required=True, currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    date = fields.Date(string='Date de paiement', required=True, default=fields.Date.today)
    due_date = fields.Date(string='Date d\'échéance')
    payment_method = fields.Selection([
        ('cash', 'Espèces'),
        ('bank_transfer', 'Virement bancaire'),
        ('cheque', 'Chèque'),
        ('card', 'Carte bancaire'),
        ('mobile', 'Paiement mobile'),
        ('lcn', 'Lettre de change'),
        ('billet', 'Billet à ordre'),
    ], string='Mode de paiement', required=True, tracking=True)
    state = fields.Selection([
        ('pending', 'En attente'),
        ('received', 'Reçu'),
        ('validated', 'Validé'),
        ('rejected', 'Rejeté'),
    ], string='État', default='pending', tracking=True)
    journal_id = fields.Many2one('account.journal', string='Journal')
    bank_reference = fields.Char(string='Réf. bancaire')
    notes = fields.Text(string='Notes')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('Nouveau')) == _('Nouveau'):
                vals['name'] = self.env['ir.sequence'].next_by_code('account.payment.tracking') or _('Nouveau')
        return super().create(vals_list)

    def action_receive(self):
        self.write({'state': 'received'})

    def action_validate(self):
        self.write({'state': 'validated'})

    def action_reject(self):
        self.write({'state': 'rejected'})

    def action_reset(self):
        self.write({'state': 'pending'})


class AccountTaxReport(models.Model):
    _name = 'account.tax.report.custom'
    _description = 'Rapport de TVA personnalisé'
    _auto = False
    _order = 'date_month desc, tax_name'

    date_month = fields.Date(string='Mois', readonly=True)
    tax_name = fields.Char(string='Taxe', readonly=True)
    tax_amount = fields.Float(string='Taux (%)', readonly=True)
    base_amount = fields.Float(string='Base HT', readonly=True)
    tax_collected = fields.Float(string='TVA collectée', readonly=True)
    tax_deductible = fields.Float(string='TVA déductible', readonly=True)
    tax_due = fields.Float(string='TVA à payer', readonly=True)

    def init(self):
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW account_tax_report_custom AS (
                SELECT
                    ROW_NUMBER() OVER () as id,
                    DATE_TRUNC('month', am.invoice_date) as date_month,
                    at.name::text as tax_name,
                    at.amount as tax_amount,
                    SUM(CASE WHEN am.move_type IN ('out_invoice', 'out_refund')
                        THEN aml.price_subtotal ELSE 0 END) as base_amount,
                    SUM(CASE WHEN am.move_type IN ('out_invoice', 'out_refund')
                        THEN aml.price_total - aml.price_subtotal ELSE 0 END) as tax_collected,
                    SUM(CASE WHEN am.move_type IN ('in_invoice', 'in_refund')
                        THEN aml.price_total - aml.price_subtotal ELSE 0 END) as tax_deductible,
                    SUM(CASE WHEN am.move_type IN ('out_invoice', 'out_refund')
                        THEN aml.price_total - aml.price_subtotal ELSE 0 END) -
                    SUM(CASE WHEN am.move_type IN ('in_invoice', 'in_refund')
                        THEN aml.price_total - aml.price_subtotal ELSE 0 END) as tax_due
                FROM account_move_line aml
                JOIN account_move am ON am.id = aml.move_id
                LEFT JOIN account_move_line_account_tax_rel atrel ON atrel.account_move_line_id = aml.id
                LEFT JOIN account_tax at ON at.id = atrel.account_tax_id
                WHERE am.state = 'posted'
                AND at.id IS NOT NULL
                GROUP BY DATE_TRUNC('month', am.invoice_date), at.name, at.amount
            )
        """)


class AccountAgedBalance(models.Model):
    _name = 'account.aged.balance.custom'
    _description = 'Balance âgée personnalisée'
    _auto = False
    _order = 'partner_id'

    partner_id = fields.Many2one('res.partner', string='Partenaire', readonly=True)
    total_due = fields.Float(string='Total dû', readonly=True)
    current = fields.Float(string='Non échu', readonly=True)
    period_1 = fields.Float(string='0-30 jours', readonly=True)
    period_2 = fields.Float(string='31-60 jours', readonly=True)
    period_3 = fields.Float(string='61-90 jours', readonly=True)
    period_4 = fields.Float(string='+90 jours', readonly=True)

    def init(self):
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW account_aged_balance_custom AS (
                SELECT
                    ROW_NUMBER() OVER () as id,
                    am.partner_id,
                    SUM(am.amount_residual) as total_due,
                    SUM(CASE WHEN am.invoice_date_due >= CURRENT_DATE
                        THEN am.amount_residual ELSE 0 END) as current,
                    SUM(CASE WHEN CURRENT_DATE - am.invoice_date_due BETWEEN 0 AND 30
                        THEN am.amount_residual ELSE 0 END) as period_1,
                    SUM(CASE WHEN CURRENT_DATE - am.invoice_date_due BETWEEN 31 AND 60
                        THEN am.amount_residual ELSE 0 END) as period_2,
                    SUM(CASE WHEN CURRENT_DATE - am.invoice_date_due BETWEEN 61 AND 90
                        THEN am.amount_residual ELSE 0 END) as period_3,
                    SUM(CASE WHEN CURRENT_DATE - am.invoice_date_due > 90
                        THEN am.amount_residual ELSE 0 END) as period_4
                FROM account_move am
                WHERE am.state = 'posted'
                AND am.move_type = 'out_invoice'
                AND am.payment_state IN ('not_paid', 'partial')
                AND am.partner_id IS NOT NULL
                GROUP BY am.partner_id
                HAVING SUM(am.amount_residual) > 0
            )
        """)
