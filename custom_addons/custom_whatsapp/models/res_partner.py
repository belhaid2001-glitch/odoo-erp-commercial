# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    whatsapp_number = fields.Char(
        string='N° WhatsApp',
        help='Numéro WhatsApp du contact (format international recommandé : +212 6XX XX XX XX)',
    )
    whatsapp_opt_in = fields.Boolean(
        string='WhatsApp autorisé',
        default=True,
        help='Le contact accepte de recevoir des messages WhatsApp',
    )
    whatsapp_message_ids = fields.One2many(
        'whatsapp.message', 'partner_id',
        string='Messages WhatsApp',
    )
    whatsapp_message_count = fields.Integer(
        compute='_compute_whatsapp_count',
        string='Messages WhatsApp',
    )

    def _compute_whatsapp_count(self):
        for partner in self:
            partner.whatsapp_message_count = len(partner.whatsapp_message_ids)

    def action_send_whatsapp(self):
        """Ouvrir l'assistant d'envoi WhatsApp"""
        self.ensure_one()
        phone = self.whatsapp_number or self.mobile or self.phone
        return {
            'type': 'ir.actions.act_window',
            'name': _('Envoyer WhatsApp'),
            'res_model': 'whatsapp.send.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_partner_id': self.id,
                'default_phone': phone or '',
                'default_model_name': 'res.partner',
                'default_res_id': self.id,
            },
        }

    def action_view_whatsapp_messages(self):
        """Voir tous les messages WhatsApp de ce contact"""
        return {
            'type': 'ir.actions.act_window',
            'name': _('Messages WhatsApp - %s') % self.name,
            'res_model': 'whatsapp.message',
            'view_mode': 'tree,form',
            'domain': [('partner_id', '=', self.id)],
        }
