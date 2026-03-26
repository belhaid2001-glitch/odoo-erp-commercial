# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class CalendarEvent(models.Model):
    _inherit = 'calendar.event'

    # --- Champs personnalisés ---
    event_type_custom = fields.Selection([
        ('meeting', 'Réunion'),
        ('call', 'Appel téléphonique'),
        ('visit', 'Visite client'),
        ('visit_supplier', 'Visite fournisseur'),
        ('training', 'Formation'),
        ('demo', 'Démonstration'),
        ('interview', 'Entretien'),
        ('internal', 'Réunion interne'),
        ('other', 'Autre'),
    ], string='Type de RDV', default='meeting', tracking=True)

    priority = fields.Selection([
        ('0', 'Normale'),
        ('1', 'Basse'),
        ('2', 'Moyenne'),
        ('3', 'Haute'),
    ], string='Priorité', default='0')

    linked_module = fields.Selection([
        ('crm', 'CRM'),
        ('sale', 'Vente'),
        ('purchase', 'Achat'),
        ('stock', 'Inventaire'),
        ('hr', 'RH'),
        ('project', 'Projet'),
        ('other', 'Autre'),
    ], string='Module lié',
       compute='_compute_linked_module', store=True, readonly=False)

    meeting_location_type = fields.Selection([
        ('office', 'Bureau'),
        ('client', 'Chez le client'),
        ('remote', 'À distance'),
        ('external', 'Lieu externe'),
    ], string='Type de lieu', default='office')

    meeting_url = fields.Char(
        string='Lien visioconférence',
        help='Lien Zoom, Teams, Google Meet...',
    )

    preparation_notes = fields.Text(
        string='Notes de préparation',
    )

    meeting_minutes = fields.Html(
        string='Compte-rendu',
    )

    result = fields.Selection([
        ('pending', 'En attente'),
        ('positive', 'Positif'),
        ('neutral', 'Neutre'),
        ('negative', 'Négatif'),
    ], string='Résultat', default='pending')

    follow_up_required = fields.Boolean(
        string='Suivi requis',
        default=False,
    )

    follow_up_date = fields.Date(
        string='Date de suivi',
    )

    follow_up_notes = fields.Text(
        string='Notes de suivi',
    )

    # --- Calculs ---
    @api.depends('opportunity_id')
    def _compute_linked_module(self):
        for event in self:
            if not event.linked_module:
                if event.opportunity_id:
                    event.linked_module = 'crm'
                else:
                    event.linked_module = False

    # --- Actions ---
    def action_mark_positive(self):
        self.write({'result': 'positive'})

    def action_mark_negative(self):
        self.write({'result': 'negative'})

    def action_request_follow_up(self):
        """Demander un suivi"""
        for event in self:
            event.follow_up_required = True
            event.message_post(
                body=_("Suivi requis pour le RDV '%s'") % event.name,
                subtype_xmlid='mail.mt_note',
            )


class CalendarEventType(models.Model):
    _name = 'calendar.event.type.custom'
    _description = 'Type de rendez-vous personnalisé'

    name = fields.Char(string='Nom', required=True)
    color = fields.Integer(string='Couleur')
    default_duration = fields.Float(string='Durée par défaut (h)', default=1.0)
    description = fields.Text(string='Description')
    active = fields.Boolean(default=True)
