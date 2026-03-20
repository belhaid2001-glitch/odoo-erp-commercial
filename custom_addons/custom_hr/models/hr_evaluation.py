# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class HrEvaluation(models.Model):
    _name = 'hr.evaluation'
    _description = 'Évaluation employé'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc'

    name = fields.Char(
        string='Référence',
        required=True,
        default=lambda self: _('Nouvelle'),
        readonly=True,
    )

    employee_id = fields.Many2one(
        'hr.employee',
        string='Employé',
        required=True,
        tracking=True,
    )

    department_id = fields.Many2one(
        'hr.department',
        string='Département',
        related='employee_id.department_id',
        store=True,
    )

    job_id = fields.Many2one(
        'hr.job',
        string='Poste',
        related='employee_id.job_id',
        store=True,
    )

    evaluator_id = fields.Many2one(
        'res.users',
        string='Évaluateur',
        default=lambda self: self.env.user,
        required=True,
        tracking=True,
    )

    date = fields.Date(
        string='Date d\'évaluation',
        required=True,
        default=fields.Date.today,
        tracking=True,
    )

    period_start = fields.Date(
        string='Période début',
    )

    period_end = fields.Date(
        string='Période fin',
    )

    evaluation_type = fields.Selection([
        ('annual', 'Annuelle'),
        ('semester', 'Semestrielle'),
        ('quarterly', 'Trimestrielle'),
        ('probation', 'Fin de période d\'essai'),
        ('special', 'Spéciale'),
    ], string='Type d\'évaluation', default='annual', tracking=True)

    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('in_progress', 'En cours'),
        ('done', 'Terminée'),
        ('cancelled', 'Annulée'),
    ], string='État', default='draft', tracking=True)

    # --- Critères d'évaluation ---
    score_quality = fields.Selection([
        ('1', '1 - Insuffisant'),
        ('2', '2 - À améliorer'),
        ('3', '3 - Satisfaisant'),
        ('4', '4 - Bon'),
        ('5', '5 - Excellent'),
    ], string='Qualité du travail', tracking=True)

    score_productivity = fields.Selection([
        ('1', '1 - Insuffisant'),
        ('2', '2 - À améliorer'),
        ('3', '3 - Satisfaisant'),
        ('4', '4 - Bon'),
        ('5', '5 - Excellent'),
    ], string='Productivité', tracking=True)

    score_initiative = fields.Selection([
        ('1', '1 - Insuffisant'),
        ('2', '2 - À améliorer'),
        ('3', '3 - Satisfaisant'),
        ('4', '4 - Bon'),
        ('5', '5 - Excellent'),
    ], string='Initiative', tracking=True)

    score_teamwork = fields.Selection([
        ('1', '1 - Insuffisant'),
        ('2', '2 - À améliorer'),
        ('3', '3 - Satisfaisant'),
        ('4', '4 - Bon'),
        ('5', '5 - Excellent'),
    ], string='Travail d\'équipe', tracking=True)

    score_punctuality = fields.Selection([
        ('1', '1 - Insuffisant'),
        ('2', '2 - À améliorer'),
        ('3', '3 - Satisfaisant'),
        ('4', '4 - Bon'),
        ('5', '5 - Excellent'),
    ], string='Ponctualité', tracking=True)

    score_communication = fields.Selection([
        ('1', '1 - Insuffisant'),
        ('2', '2 - À améliorer'),
        ('3', '3 - Satisfaisant'),
        ('4', '4 - Bon'),
        ('5', '5 - Excellent'),
    ], string='Communication', tracking=True)

    global_score = fields.Float(
        string='Score global',
        compute='_compute_global_score',
        store=True,
        digits=(3, 1),
    )

    global_rating = fields.Selection([
        ('insufficient', 'Insuffisant'),
        ('to_improve', 'À améliorer'),
        ('satisfactory', 'Satisfaisant'),
        ('good', 'Bon'),
        ('excellent', 'Excellent'),
    ], string='Appréciation globale',
        compute='_compute_global_score',
        store=True,
    )

    strengths = fields.Text(string='Points forts')
    improvements = fields.Text(string='Points à améliorer')
    objectives = fields.Text(string='Objectifs pour la prochaine période')
    employee_comments = fields.Text(string='Commentaires de l\'employé')
    evaluator_comments = fields.Text(string='Commentaires de l\'évaluateur')

    goal_ids = fields.One2many(
        'hr.evaluation.goal',
        'evaluation_id',
        string='Objectifs',
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('Nouvelle')) == _('Nouvelle'):
                vals['name'] = self.env['ir.sequence'].next_by_code('hr.evaluation') or _('Nouvelle')
        return super().create(vals_list)

    @api.depends('score_quality', 'score_productivity', 'score_initiative',
                 'score_teamwork', 'score_punctuality', 'score_communication')
    def _compute_global_score(self):
        for ev in self:
            scores = []
            for field_name in ['score_quality', 'score_productivity', 'score_initiative',
                               'score_teamwork', 'score_punctuality', 'score_communication']:
                val = getattr(ev, field_name)
                if val:
                    scores.append(int(val))
            if scores:
                avg = sum(scores) / len(scores)
                ev.global_score = round(avg, 1)
                if avg >= 4.5:
                    ev.global_rating = 'excellent'
                elif avg >= 3.5:
                    ev.global_rating = 'good'
                elif avg >= 2.5:
                    ev.global_rating = 'satisfactory'
                elif avg >= 1.5:
                    ev.global_rating = 'to_improve'
                else:
                    ev.global_rating = 'insufficient'
            else:
                ev.global_score = 0.0
                ev.global_rating = False

    def action_start(self):
        self.write({'state': 'in_progress'})

    def action_done(self):
        self.write({'state': 'done'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    def action_reset_draft(self):
        self.write({'state': 'draft'})


class HrEvaluationGoal(models.Model):
    _name = 'hr.evaluation.goal'
    _description = 'Objectif d\'évaluation'

    evaluation_id = fields.Many2one(
        'hr.evaluation',
        string='Évaluation',
        required=True,
        ondelete='cascade',
    )

    name = fields.Char(
        string='Objectif',
        required=True,
    )

    description = fields.Text(
        string='Description',
    )

    deadline = fields.Date(
        string='Échéance',
    )

    weight = fields.Float(
        string='Poids (%)',
        default=100,
    )

    achievement = fields.Float(
        string='Réalisation (%)',
        default=0,
    )

    status = fields.Selection([
        ('not_started', 'Non commencé'),
        ('in_progress', 'En cours'),
        ('achieved', 'Atteint'),
        ('not_achieved', 'Non atteint'),
    ], string='Statut', default='not_started')

    notes = fields.Text(string='Notes')
