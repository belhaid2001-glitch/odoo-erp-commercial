# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class MailTemplateCustom(models.Model):
    _name = 'mail.template.custom'
    _description = 'Modèle de message personnalisé'
    _order = 'sequence, name'

    name = fields.Char(string='Nom du modèle', required=True)
    sequence = fields.Integer(string='Séquence', default=10)
    category = fields.Selection([
        ('commercial', 'Commercial'),
        ('support', 'Support'),
        ('internal', 'Interne'),
        ('hr', 'Ressources humaines'),
        ('accounting', 'Comptabilité'),
        ('other', 'Autre'),
    ], string='Catégorie', default='commercial')

    subject = fields.Char(string='Sujet')
    body = fields.Html(string='Contenu du message')
    is_internal = fields.Boolean(
        string='Message interne',
        default=False,
        help='Si coché, le message ne sera pas envoyé par email',
    )
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        'res.company',
        string='Société',
        default=lambda self: self.env.company,
    )


class MailMessageCustom(models.Model):
    _inherit = 'mail.message'

    message_priority = fields.Selection([
        ('low', 'Basse'),
        ('normal', 'Normale'),
        ('high', 'Haute'),
        ('urgent', 'Urgente'),
    ], string='Priorité message', default='normal')

    is_flagged = fields.Boolean(
        string='Marqué',
        default=False,
    )
