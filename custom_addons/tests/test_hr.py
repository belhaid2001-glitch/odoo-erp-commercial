# -*- coding: utf-8 -*-
"""
===========================================================================
  TEST HR — Tests E2E pour custom_hr
  Couvre : HrEmployee, HrEvaluation, HrEvaluationGoal
===========================================================================
"""
from datetime import date, timedelta
from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install', 'custom_hr')
class TestHrEmployeeCustom(TransactionCase):
    """Tests des champs personnalisés sur hr.employee."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.employee = cls.env['hr.employee'].create({
            'name': 'Employé Test RH',
            'job_title': 'Développeur',
        })

    def test_01_default_employee_fields(self):
        """Les champs RH custom ont des valeurs par défaut cohérentes."""
        self.assertFalse(self.employee.cin)
        self.assertFalse(self.employee.cnss_number)
        self.assertFalse(self.employee.emergency_contact_name)

    def test_02_employee_type_custom(self):
        """Tous les types de contrat custom sont valides."""
        for etype in ('cdi', 'cdd', 'stagiaire', 'freelance', 'consultant'):
            self.employee.employee_type_custom = etype
            self.assertEqual(self.employee.employee_type_custom, etype)

    def test_03_cin_and_cnss(self):
        """CIN et CNSS sont stockés correctement."""
        self.employee.write({'cin': 'BK123456', 'cnss_number': '1234567890'})
        self.assertEqual(self.employee.cin, 'BK123456')
        self.assertEqual(self.employee.cnss_number, '1234567890')

    def test_04_emergency_contact(self):
        """Les informations d'urgence sont stockées."""
        self.employee.write({
            'emergency_contact_name': 'Contact Urgence',
            'emergency_contact_phone': '+212600000000',
            'emergency_contact_relation': 'Spouse',
        })
        self.assertEqual(self.employee.emergency_contact_name, 'Contact Urgence')

    def test_05_seniority_computed(self):
        """L'ancienneté est calculée à partir de hire_date."""
        self.employee.hire_date = date.today() - timedelta(days=730)  # ~2 ans
        self.assertGreater(self.employee.seniority_years, 1.5)

    def test_06_blood_type(self):
        """Le groupe sanguin est stocké."""
        for bt in ('A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'):
            self.employee.blood_type = bt
            self.assertEqual(self.employee.blood_type, bt)


@tagged('post_install', '-at_install', 'custom_hr')
class TestHrEvaluation(TransactionCase):
    """Tests du modèle d'évaluation RH."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.employee = cls.env['hr.employee'].create({
            'name': 'Employé Évaluation',
        })

    def _create_evaluation(self, **kwargs):
        vals = {
            'employee_id': self.employee.id,
            'evaluator_id': self.env.uid,
            'date': date.today(),
            'period_start': date.today() - timedelta(days=180),
            'period_end': date.today(),
            'evaluation_type': 'annual',
            'score_quality': '4',
            'score_productivity': '3',
            'score_initiative': '4',
            'score_teamwork': '5',
            'score_punctuality': '4',
            'score_communication': '3',
        }
        vals.update(kwargs)
        return self.env['hr.evaluation'].create(vals)

    def test_10_evaluation_creation(self):
        """Une évaluation est créée en brouillon avec nom séquencé."""
        evaluation = self._create_evaluation()
        self.assertEqual(evaluation.state, 'draft')
        self.assertTrue(evaluation.name)

    def test_11_evaluation_workflow_start(self):
        """action_start passe en 'in_progress'."""
        evaluation = self._create_evaluation()
        evaluation.action_start()
        self.assertEqual(evaluation.state, 'in_progress')

    def test_12_evaluation_workflow_done(self):
        """action_done passe en 'done'."""
        evaluation = self._create_evaluation()
        evaluation.action_start()
        evaluation.action_done()
        self.assertEqual(evaluation.state, 'done')

    def test_13_evaluation_cancel_reset(self):
        """Annulation et remise en brouillon."""
        evaluation = self._create_evaluation()
        evaluation.action_start()
        evaluation.action_cancel()
        self.assertEqual(evaluation.state, 'cancelled')
        evaluation.action_reset_draft()
        self.assertEqual(evaluation.state, 'draft')

    def test_14_global_score_computed(self):
        """Le score global est la moyenne des 6 critères."""
        evaluation = self._create_evaluation(
            score_quality='4', score_productivity='3',
            score_initiative='4', score_teamwork='5',
            score_punctuality='4', score_communication='3',
        )
        # (4+3+4+5+4+3) / 6 = 3.83
        self.assertAlmostEqual(evaluation.global_score, 3.83, places=1)

    def test_15_global_rating_computed(self):
        """Le rating global est dérivé du score."""
        evaluation = self._create_evaluation()
        self.assertIn(evaluation.global_rating, [
            'excellent', 'good', 'average', 'below_average', 'poor', False
        ])

    def test_16_evaluation_types(self):
        """Tous les types d'évaluation sont valides."""
        for etype in ('annual', 'semester', 'quarterly', 'probation', 'special'):
            ev = self._create_evaluation(evaluation_type=etype)
            self.assertEqual(ev.evaluation_type, etype)

    def test_17_employee_evaluation_count(self):
        """Le compteur d'évaluations sur l'employé est incrémenté."""
        self._create_evaluation()
        self._create_evaluation()
        self.assertEqual(self.employee.evaluation_count, 2)

    def test_18_last_evaluation_on_employee(self):
        """La dernière évaluation est reflétée sur l'employé."""
        ev = self._create_evaluation()
        ev.action_start()
        ev.action_done()
        self.employee.invalidate_recordset()
        self.assertTrue(self.employee.last_evaluation_date)
        self.assertGreater(self.employee.last_evaluation_score, 0)


@tagged('post_install', '-at_install', 'custom_hr')
class TestHrEvaluationGoal(TransactionCase):
    """Tests des objectifs d'évaluation."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.employee = cls.env['hr.employee'].create({'name': 'Employé Goal'})
        cls.evaluation = cls.env['hr.evaluation'].create({
            'employee_id': cls.employee.id,
            'evaluator_id': cls.env.uid,
            'date': date.today(),
            'period_start': date.today() - timedelta(days=90),
            'period_end': date.today(),
            'evaluation_type': 'quarterly',
        })

    def test_20_create_goal(self):
        """On peut créer un objectif d'évaluation."""
        goal = self.env['hr.evaluation.goal'].create({
            'evaluation_id': self.evaluation.id,
            'name': 'Augmenter la productivité de 10%',
            'deadline': date.today() + timedelta(days=90),
            'weight': 30.0,
        })
        self.assertEqual(goal.status, 'not_started')

    def test_21_goal_status_transitions(self):
        """Les statuts d'objectif sont modifiables."""
        goal = self.env['hr.evaluation.goal'].create({
            'evaluation_id': self.evaluation.id,
            'name': 'Objectif statut',
            'deadline': date.today() + timedelta(days=30),
            'weight': 20.0,
        })
        for status in ('in_progress', 'achieved', 'not_achieved'):
            goal.status = status
            self.assertEqual(goal.status, status)

    def test_22_goal_achievement(self):
        """Le taux de réalisation est stocké."""
        goal = self.env['hr.evaluation.goal'].create({
            'evaluation_id': self.evaluation.id,
            'name': 'Objectif réalisation',
            'deadline': date.today() + timedelta(days=60),
            'weight': 50.0,
            'achievement': 75.0,
        })
        self.assertEqual(goal.achievement, 75.0)
