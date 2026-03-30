# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class WhatsappSendWizard(models.TransientModel):
    _name = 'whatsapp.send.wizard'
    _description = 'Assistant d\'envoi WhatsApp'

    partner_id = fields.Many2one('res.partner', string='Destinataire', required=True)
    phone = fields.Char(string='Numéro WhatsApp', required=True)
    template_id = fields.Many2one('whatsapp.template', string='Template')
    message = fields.Text(string='Message', required=True)
    model_name = fields.Char(string='Modèle source')
    res_id = fields.Integer(string='ID enregistrement')

    # Envoi en masse
    is_mass_send = fields.Boolean(string='Envoi en masse', default=False)
    partner_ids = fields.Many2many('res.partner', string='Destinataires')

    @api.onchange('template_id')
    def _onchange_template_id(self):
        """Remplir le message depuis le template"""
        if self.template_id:
            record = False
            if self.model_name and self.res_id:
                try:
                    record = self.env[self.model_name].browse(self.res_id)
                except Exception:
                    record = self.partner_id
            else:
                record = self.partner_id
            if record:
                self.message = self.template_id.render_template(record)
            else:
                self.message = self.template_id.body

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.partner_id:
            self.phone = self.partner_id.whatsapp_number or self.partner_id.mobile or self.partner_id.phone or ''

    def action_send(self):
        """Envoyer le message WhatsApp"""
        self.ensure_one()

        if self.is_mass_send and self.partner_ids:
            # Envoi en masse
            for partner in self.partner_ids:
                phone = partner.whatsapp_number or partner.mobile or partner.phone
                if not phone:
                    continue
                msg = self.message.replace('{partner_name}', partner.name or '')
                self.env['whatsapp.message'].create({
                    'partner_id': partner.id,
                    'phone': phone,
                    'message': msg,
                    'template_id': self.template_id.id if self.template_id else False,
                    'model_name': self.model_name,
                    'res_id': self.res_id,
                    'record_name': partner.name,
                    'state': 'sent',
                })
                partner.message_post(
                    body=_("📱 Message WhatsApp envoyé :<br/><em>%s</em>") % msg,
                    subtype_xmlid='mail.mt_note',
                )
            return {'type': 'ir.actions.act_window_close'}

        # Envoi simple
        msg_record = self.env['whatsapp.message'].create({
            'partner_id': self.partner_id.id,
            'phone': self.phone,
            'message': self.message,
            'template_id': self.template_id.id if self.template_id else False,
            'model_name': self.model_name,
            'res_id': self.res_id,
            'record_name': self.partner_id.name,
        })
        return msg_record.action_send_whatsapp()

    def action_preview(self):
        """Prévisualiser le message"""
        return {
            'type': 'ir.actions.act_window',
            'name': _('Aperçu du message'),
            'res_model': 'whatsapp.send.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }
