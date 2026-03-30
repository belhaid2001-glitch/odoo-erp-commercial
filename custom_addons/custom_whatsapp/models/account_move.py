# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_send_whatsapp_invoice(self):
        """Ouvrir l'assistant d'envoi WhatsApp pour cette facture"""
        self.ensure_one()
        partner = self.partner_id
        phone = partner.whatsapp_number or partner.mobile or partner.phone
        return {
            'type': 'ir.actions.act_window',
            'name': _('Envoyer WhatsApp - %s') % self.name,
            'res_model': 'whatsapp.send.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_partner_id': partner.id,
                'default_phone': phone or '',
                'default_model_name': 'account.move',
                'default_res_id': self.id,
            },
        }
