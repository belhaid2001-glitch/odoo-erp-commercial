# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import date


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    # --- Champs personnalisés ---
    employee_type_custom = fields.Selection([
        ('permanent', 'CDI'),
        ('temporary', 'CDD'),
        ('intern', 'Stagiaire'),
        ('freelance', 'Freelance'),
        ('consultant', 'Consultant'),
    ], string='Type de contrat', tracking=True)

    cin = fields.Char(
        string='CIN',
        help='Carte d\'identité nationale',
        tracking=True,
    )

    cnss_number = fields.Char(
        string='N° CNSS',
        tracking=True,
    )

    emergency_contact_name = fields.Char(
        string='Contact d\'urgence',
    )

    emergency_contact_phone = fields.Char(
        string='Tél. urgence',
    )

    emergency_contact_relation = fields.Char(
        string='Relation',
    )

    hire_date = fields.Date(
        string='Date d\'embauche',
        tracking=True,
    )

    end_date = fields.Date(
        string='Date de fin de contrat',
        tracking=True,
    )

    seniority_years = fields.Float(
        string='Ancienneté (années)',
        compute='_compute_seniority',
        store=True,
    )

    evaluation_ids = fields.One2many(
        'hr.evaluation',
        'employee_id',
        string='Évaluations',
    )

    evaluation_count = fields.Integer(
        string='Nb évaluations',
        compute='_compute_evaluation_count',
    )

    last_evaluation_date = fields.Date(
        string='Dernière évaluation',
        compute='_compute_last_evaluation',
        store=True,
    )

    last_evaluation_score = fields.Float(
        string='Dernier score',
        compute='_compute_last_evaluation',
        store=True,
    )

    skills_description = fields.Text(
        string='Compétences',
    )

    training_notes = fields.Text(
        string='Notes de formation',
    )

    blood_type = fields.Selection([
        ('a+', 'A+'), ('a-', 'A-'),
        ('b+', 'B+'), ('b-', 'B-'),
        ('ab+', 'AB+'), ('ab-', 'AB-'),
        ('o+', 'O+'), ('o-', 'O-'),
    ], string='Groupe sanguin')

    # --- Calculs ---
    @api.depends('hire_date')
    def _compute_seniority(self):
        today = date.today()
        for emp in self:
            if emp.hire_date:
                delta = today - emp.hire_date
                emp.seniority_years = round(delta.days / 365.25, 1)
            else:
                emp.seniority_years = 0.0

    def _compute_evaluation_count(self):
        for emp in self:
            emp.evaluation_count = len(emp.evaluation_ids)

    @api.depends('evaluation_ids.date', 'evaluation_ids.global_score')
    def _compute_last_evaluation(self):
        for emp in self:
            last = emp.evaluation_ids.sorted('date', reverse=True)[:1]
            emp.last_evaluation_date = last.date if last else False
            emp.last_evaluation_score = last.global_score if last else 0.0

    # --- Actions ---
    def action_view_evaluations(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Évaluations de %s') % self.name,
            'res_model': 'hr.evaluation',
            'view_mode': 'tree,form',
            'domain': [('employee_id', '=', self.id)],
            'context': {'default_employee_id': self.id},
        }

    def action_create_evaluation(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Nouvelle évaluation'),
            'res_model': 'hr.evaluation',
            'view_mode': 'form',
            'context': {
                'default_employee_id': self.id,
                'default_evaluator_id': self.env.user.id,
            },
        }
