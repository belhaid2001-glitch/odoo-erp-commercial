# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime
import urllib.parse


class WhatsappMessage(models.Model):
    _name = 'whatsapp.message'
    _description = 'Message WhatsApp'
    _order = 'send_date desc'
    _inherit = ['mail.thread']

    name = fields.Char(string='Référence', default=lambda self: _('Nouveau'), readonly=True)
    partner_id = fields.Many2one('res.partner', string='Destinataire', required=True)
    phone = fields.Char(string='Numéro WhatsApp', required=True)
    message = fields.Text(string='Message', required=True)
    template_id = fields.Many2one('whatsapp.template', string='Template utilisé')

    # Contexte
    model_name = fields.Char(string='Modèle source')
    res_id = fields.Integer(string='ID enregistrement')
    record_name = fields.Char(string='Nom de l\'enregistrement')

    # Métadonnées
    send_date = fields.Datetime(string='Date d\'envoi', default=fields.Datetime.now)
    user_id = fields.Many2one('res.users', string='Envoyé par', default=lambda self: self.env.user)
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('sent', 'Envoyé'),
        ('failed', 'Échoué'),
    ], string='État', default='draft', tracking=True)
    error_message = fields.Text(string='Erreur')

    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('Nouveau')) == _('Nouveau'):
                vals['name'] = self.env['ir.sequence'].next_by_code('whatsapp.message') or _('Nouveau')
        return super().create(vals_list)

    def _format_phone_for_whatsapp(self, phone):
        """Formater un numéro pour l'API WhatsApp"""
        if not phone:
            return ''
        # Nettoyer
        clean = ''.join(c for c in phone if c.isdigit() or c == '+')
        # Convertir format marocain
        if clean.startswith('0') and len(clean) == 10:
            clean = '+212' + clean[1:]
        elif clean.startswith('212') and not clean.startswith('+'):
            clean = '+' + clean
        # Enlever le + pour l'URL
        return clean.lstrip('+')

    def action_send_whatsapp(self):
        """Ouvrir WhatsApp Web avec le message pré-rempli"""
        self.ensure_one()
        phone = self._format_phone_for_whatsapp(self.phone)
        if not phone:
            self.write({'state': 'failed', 'error_message': 'Numéro de téléphone invalide'})
            return

        encoded_msg = urllib.parse.quote(self.message)
        whatsapp_url = f"https://wa.me/{phone}?text={encoded_msg}"

        self.write({
            'state': 'sent',
            'send_date': fields.Datetime.now(),
        })

        # Logger dans le chatter du partenaire
        if self.partner_id:
            self.partner_id.message_post(
                body=_("📱 Message WhatsApp envoyé :<br/><em>%s</em>") % self.message,
                subtype_xmlid='mail.mt_note',
            )

        return {
            'type': 'ir.actions.act_url',
            'url': whatsapp_url,
            'target': 'new',
        }

    def action_resend(self):
        """Renvoyer le message"""
        self.write({'state': 'draft'})
        return self.action_send_whatsapp()


class WhatsappTemplate(models.Model):
    _name = 'whatsapp.template'
    _description = 'Template de message WhatsApp'
    _order = 'sequence, name'

    name = fields.Char(string='Nom du template', required=True)
    category = fields.Selection([
        ('general', 'Général'),
        ('sale', 'Vente'),
        ('invoice', 'Facturation'),
        ('delivery', 'Livraison'),
        ('reminder', 'Relance'),
        ('greeting', 'Accueil'),
        ('promotion', 'Promotion'),
    ], string='Catégorie', default='general', required=True)
    body = fields.Text(string='Corps du message', required=True,
                       help="Variables disponibles : {partner_name}, {company_name}, {amount}, {reference}, {date}, {salesperson}")
    model_name = fields.Selection([
        ('res.partner', 'Contact'),
        ('sale.order', 'Bon de commande'),
        ('account.move', 'Facture'),
        ('stock.picking', 'Livraison'),
    ], string='Applicable à')
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)

    def render_template(self, record):
        """Rendre le template avec les données de l'enregistrement"""
        body = self.body or ''
        partner = False
        amount = ''
        reference = ''
        date_str = fields.Date.today().strftime('%d/%m/%Y')

        if hasattr(record, 'partner_id') and record.partner_id:
            partner = record.partner_id
        elif record._name == 'res.partner':
            partner = record

        if hasattr(record, 'amount_total'):
            amount = f"{record.amount_total:,.2f}"
        if hasattr(record, 'name'):
            reference = record.name or ''

        salesperson = ''
        if hasattr(record, 'user_id') and record.user_id:
            salesperson = record.user_id.name

        body = body.replace('{partner_name}', partner.name if partner else '')
        body = body.replace('{company_name}', self.env.company.name or '')
        body = body.replace('{amount}', amount)
        body = body.replace('{reference}', reference)
        body = body.replace('{date}', date_str)
        body = body.replace('{salesperson}', salesperson)

        return body
