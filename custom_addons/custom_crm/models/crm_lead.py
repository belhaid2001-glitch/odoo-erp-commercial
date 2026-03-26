# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    # --- Champs personnalisés ---
    lead_source = fields.Selection([
        ('website', 'Site web'),
        ('phone', 'Téléphone'),
        ('email', 'Email'),
        ('referral', 'Recommandation'),
        ('social', 'Réseaux sociaux'),
        ('event', 'Événement'),
        ('advertising', 'Publicité'),
        ('other', 'Autre'),
    ], string='Source du lead', tracking=True)

    lead_quality = fields.Selection([
        ('cold', 'Froid'),
        ('warm', 'Tiède'),
        ('hot', 'Chaud'),
    ], string='Qualité du lead', tracking=True,
       compute='_compute_lead_quality', store=True, readonly=False)

    estimated_closing_date = fields.Date(
        string='Date de clôture estimée',
        tracking=True,
    )

    competitor_ids = fields.Many2many(
        'crm.competitor',
        string='Concurrents',
    )

    loss_reason_notes = fields.Text(
        string='Notes de perte',
    )

    next_action_description = fields.Text(
        string='Prochaine action',
    )

    next_action_date = fields.Date(
        string='Date prochaine action',
        tracking=True,
    )

    call_count = fields.Integer(
        string='Nombre d\'appels',
        default=0,
    )

    meeting_count_custom = fields.Integer(
        string='Nombre de RDV',
        compute='_compute_meeting_count_custom',
    )

    quote_count = fields.Integer(
        string='Nombre de devis',
        compute='_compute_quote_count',
    )

    conversion_rate = fields.Float(
        string='Probabilité pondérée',
        compute='_compute_conversion_rate',
        digits=(5, 2),
    )

    last_contact_date = fields.Date(
        string='Dernier contact',
        tracking=True,
    )

    days_since_last_contact = fields.Integer(
        string='Jours sans contact',
        compute='_compute_days_since_last_contact',
    )

    internal_notes = fields.Html(
        string='Notes internes CRM',
    )

    # --- Calculs ---
    @api.depends('expected_revenue', 'probability')
    def _compute_conversion_rate(self):
        for lead in self:
            lead.conversion_rate = (lead.expected_revenue or 0) * (lead.probability or 0) / 100

    @api.depends('probability')
    def _compute_lead_quality(self):
        for lead in self:
            if not lead.lead_quality:
                if lead.probability and lead.probability >= 50:
                    lead.lead_quality = 'hot'
                elif lead.probability and lead.probability >= 20:
                    lead.lead_quality = 'warm'
                else:
                    lead.lead_quality = 'cold'

    def _compute_meeting_count_custom(self):
        for lead in self:
            lead.meeting_count_custom = self.env['calendar.event'].search_count([
                ('opportunity_id', '=', lead.id)
            ]) if lead.id else 0

    def _compute_quote_count(self):
        for lead in self:
            lead.quote_count = self.env['sale.order'].search_count([
                ('opportunity_id', '=', lead.id)
            ]) if lead.id else 0

    def _compute_days_since_last_contact(self):
        today = fields.Date.today()
        for lead in self:
            if lead.last_contact_date:
                lead.days_since_last_contact = (today - lead.last_contact_date).days
            else:
                lead.days_since_last_contact = 0

    # --- Actions ---
    def action_log_call(self):
        """Enregistrer un appel"""
        for lead in self:
            lead.call_count += 1
            lead.last_contact_date = fields.Date.today()
            lead.message_post(
                body=_("Appel enregistré par %s (appel n°%d)") % (
                    self.env.user.name, lead.call_count
                ),
                subtype_xmlid='mail.mt_note',
            )

    def action_schedule_meeting(self):
        """Planifier un rendez-vous lié à l'opportunité"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Planifier un RDV'),
            'res_model': 'calendar.event',
            'view_mode': 'form',
            'context': {
                'default_opportunity_id': self.id,
                'default_partner_ids': [(4, self.partner_id.id)] if self.partner_id else [],
                'default_name': _('RDV - %s') % self.name,
            },
        }

    def action_quick_quotation(self):
        """Créer rapidement un devis depuis l'opportunité"""
        self.ensure_one()
        if not self.partner_id:
            raise UserError(_("Veuillez d'abord définir un client pour cette opportunité."))
        return {
            'type': 'ir.actions.act_window',
            'name': _('Nouveau devis'),
            'res_model': 'sale.order',
            'view_mode': 'form',
            'context': {
                'default_partner_id': self.partner_id.id,
                'default_opportunity_id': self.id,
                'default_origin': self.name,
            },
        }

    def action_view_meetings(self):
        """Voir les rendez-vous liés"""
        return {
            'type': 'ir.actions.act_window',
            'name': _('Rendez-vous'),
            'res_model': 'calendar.event',
            'view_mode': 'tree,form,calendar',
            'domain': [('opportunity_id', '=', self.id)],
        }

    def action_view_quotations(self):
        """Voir les devis liés"""
        return {
            'type': 'ir.actions.act_window',
            'name': _('Devis'),
            'res_model': 'sale.order',
            'view_mode': 'tree,form',
            'domain': [('opportunity_id', '=', self.id)],
        }


class CrmCompetitor(models.Model):
    _name = 'crm.competitor'
    _description = 'Concurrent'

    name = fields.Char(string='Nom', required=True)
    website = fields.Char(string='Site web')
    notes = fields.Text(string='Notes')
    strength = fields.Text(string='Points forts')
    weakness = fields.Text(string='Points faibles')
    active = fields.Boolean(default=True)
