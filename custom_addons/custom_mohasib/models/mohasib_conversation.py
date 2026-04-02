# -*- coding: utf-8 -*-
"""
Mohasib — Modèle Conversation & Messages
Historique de la conversation entre le directeur et l'agent Mohasib.
"""
from odoo import models, fields, api


class MohasibConversation(models.Model):
    _name = 'mohasib.conversation'
    _description = 'Conversation Mohasib'
    _inherit = ['mail.thread']
    _order = 'create_date desc'

    name = fields.Char(
        string='Titre',
        default=lambda self: f"Conversation du {fields.Date.today()}",
    )
    state = fields.Selection([
        ('active', 'Active'),
        ('closed', 'Clôturée'),
    ], default='active', string='État')

    user_id = fields.Many2one(
        'res.users',
        string='Utilisateur',
        default=lambda self: self.env.user,
    )
    chantier_id = fields.Many2one(
        'mohasib.chantier',
        string='Chantier par défaut',
        help='Chantier utilisé par défaut si non précisé dans la phrase.',
    )

    message_ids = fields.One2many(
        'mohasib.message',
        'conversation_id',
        string='Messages',
    )
    transaction_ids = fields.One2many(
        'mohasib.transaction',
        'conversation_id',
        string='Transactions créées',
    )

    nb_messages = fields.Integer(
        compute='_compute_stats',
        string='Messages',
    )
    nb_transactions = fields.Integer(
        compute='_compute_stats',
        string='Transactions',
    )
    montant_total = fields.Float(
        compute='_compute_stats',
        string='Montant total (DH)',
    )

    company_id = fields.Many2one(
        'res.company',
        default=lambda self: self.env.company,
    )

    @api.depends('message_ids', 'transaction_ids', 'transaction_ids.montant')
    def _compute_stats(self):
        for rec in self:
            rec.nb_messages = len(rec.message_ids)
            rec.nb_transactions = len(rec.transaction_ids)
            rec.montant_total = sum(rec.transaction_ids.mapped('montant'))

    def action_close(self):
        self.write({'state': 'closed'})

    def action_reopen(self):
        self.write({'state': 'active'})


class MohasibMessage(models.Model):
    _name = 'mohasib.message'
    _description = 'Message Mohasib'
    _order = 'create_date asc'

    conversation_id = fields.Many2one(
        'mohasib.conversation',
        string='Conversation',
        required=True,
        ondelete='cascade',
    )
    role = fields.Selection([
        ('user', 'Directeur'),
        ('assistant', 'Mohasib'),
        ('system', 'Système'),
    ], string='Rôle', required=True)

    content = fields.Text(
        string='Message',
        required=True,
    )
    content_html = fields.Html(
        string='Message formaté',
        compute='_compute_content_html',
    )

    # Données structurées extraites (JSON sérialisé)
    parsed_data = fields.Text(
        string='Données extraites (JSON)',
        help='Résultat du parsing NLP en format JSON',
    )

    transaction_id = fields.Many2one(
        'mohasib.transaction',
        string='Transaction créée',
    )

    is_error = fields.Boolean(
        default=False,
        string='Erreur',
    )

    @api.depends('content', 'role')
    def _compute_content_html(self):
        for rec in self:
            if not rec.content:
                rec.content_html = ''
                continue
            # Convertir les retours à la ligne en <br>
            escaped = rec.content.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            html = escaped.replace('\n', '<br/>')
            css_class = 'mohasib-msg-user' if rec.role == 'user' else 'mohasib-msg-assistant'
            rec.content_html = f'<div class="{css_class}">{html}</div>'
