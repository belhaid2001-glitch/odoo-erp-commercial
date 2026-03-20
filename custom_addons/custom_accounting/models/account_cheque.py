# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AccountCheque(models.Model):
    _name = 'account.cheque'
    _description = 'Gestion des chèques'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc'

    name = fields.Char(
        string='Numéro de chèque',
        required=True,
        tracking=True,
    )

    cheque_type = fields.Selection([
        ('received', 'Reçu'),
        ('issued', 'Émis'),
    ], string='Type', required=True, tracking=True)

    partner_id = fields.Many2one(
        'res.partner',
        string='Partenaire',
        required=True,
        tracking=True,
    )

    amount = fields.Monetary(
        string='Montant',
        required=True,
        currency_field='currency_id',
        tracking=True,
    )

    currency_id = fields.Many2one(
        'res.currency',
        string='Devise',
        default=lambda self: self.env.company.currency_id,
    )

    date = fields.Date(
        string='Date du chèque',
        required=True,
        tracking=True,
    )

    due_date = fields.Date(
        string='Date d\'échéance',
        tracking=True,
    )

    bank_id = fields.Many2one(
        'res.bank',
        string='Banque',
    )

    bank_account = fields.Char(
        string='Compte bancaire',
    )

    move_id = fields.Many2one(
        'account.move',
        string='Pièce comptable',
        ondelete='set null',
    )

    journal_id = fields.Many2one(
        'account.journal',
        string='Journal',
        domain=[('type', 'in', ['bank', 'cash'])],
    )

    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('registered', 'Enregistré'),
        ('deposited', 'Déposé'),
        ('cleared', 'Compensé'),
        ('returned', 'Retourné'),
        ('cancelled', 'Annulé'),
    ], string='État', default='draft', tracking=True)

    memo = fields.Char(string='Mémo')
    notes = fields.Text(string='Notes')

    company_id = fields.Many2one(
        'res.company',
        string='Société',
        default=lambda self: self.env.company,
    )

    # --- Actions ---
    def action_register(self):
        """Enregistrer le chèque"""
        self.write({'state': 'registered'})

    def action_deposit(self):
        """Déposer le chèque"""
        self.write({'state': 'deposited'})

    def action_clear(self):
        """Compenser le chèque"""
        self.write({'state': 'cleared'})

    def action_return(self):
        """Retourner le chèque"""
        self.write({'state': 'returned'})
        for cheque in self:
            cheque.message_post(
                body=_("Chèque %s retourné - Montant : %s %s") % (
                    cheque.name, cheque.amount, cheque.currency_id.symbol
                ),
                subtype_xmlid='mail.mt_note',
            )

    def action_cancel(self):
        """Annuler le chèque"""
        self.write({'state': 'cancelled'})

    def action_reset_draft(self):
        """Remettre en brouillon"""
        self.write({'state': 'draft'})

    def action_print_cheque(self):
        """Imprimer le chèque"""
        return self.env.ref('custom_accounting.action_report_cheque').report_action(self)
