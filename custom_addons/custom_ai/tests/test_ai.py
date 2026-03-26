# -*- coding: utf-8 -*-
"""
===========================================================================
  TEST AI — Tests E2E pour custom_ai
  Couvre : AIMixin, AIWizard, AIActions, ResConfigSettings (AI)
===========================================================================
"""
from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install', 'custom_ai')
class TestAIMixin(TransactionCase):
    """Tests du mixin IA (mode builtin / règles métier)."""

    def test_01_ai_generate_sale_description(self):
        """ai_generate produit une description produit pour vente."""
        AIMixin = self.env['ai.mixin']
        result = AIMixin.ai_generate(
            prompt='Génère une description produit',
            context_data={'product_name': 'Bureau ergonomique', 'price': 450},
            module='sale',
        )
        self.assertIsInstance(result, dict)
        self.assertTrue(result.get('success'), "Succ\u00e8s attendu")
        self.assertTrue(len(result.get('result', '')) > 0, "R\u00e9sultat non vide attendu")

    def test_02_ai_generate_crm(self):
        """ai_generate produit un contenu CRM."""
        result = self.env['ai.mixin'].ai_generate(
            prompt='Analyse ce lead',
            context_data={'lead_name': 'Opportunité Delta', 'revenue': 35000},
            module='crm',
        )
        self.assertIsInstance(result, dict)
        self.assertTrue(result.get('success'))

    def test_03_ai_generate_hr(self):
        """ai_generate produit un résumé HR."""
        result = self.env['ai.mixin'].ai_generate(
            prompt='Synthèse évaluation',
            context_data={'employee_name': 'Jean', 'score': 4.2},
            module='hr',
        )
        self.assertIsInstance(result, dict)
        self.assertTrue(result.get('success'))

    def test_04_ai_analyze_lead_scoring(self):
        """ai_analyze effectue un scoring de lead."""
        result = self.env['ai.mixin'].ai_analyze(
            data={'revenue': 50000, 'probability': 70, 'source': 'website'},
            analysis_type='lead_scoring',
            module='crm',
        )
        self.assertIsInstance(result, (str, dict))

    def test_05_ai_analyze_payment_prediction(self):
        """ai_analyze prédit le délai de paiement."""
        result = self.env['ai.mixin'].ai_analyze(
            data={'amount': 10000, 'due_date': '2026-04-01', 'partner': 'Acme'},
            analysis_type='payment_prediction',
            module='accounting',
        )
        self.assertIsInstance(result, (str, dict))

    def test_06_ai_analyze_stock_forecast(self):
        """ai_analyze prédit les besoins stock."""
        result = self.env['ai.mixin'].ai_analyze(
            data={'product_name': 'Widget', 'qty_available': 50, 'avg_daily': 5},
            analysis_type='stock_forecast',
            module='stock',
        )
        self.assertIsInstance(result, (str, dict))

    def test_07_ai_suggest_sale(self):
        """ai_suggest propose des actions pour une vente."""
        result = self.env['ai.mixin'].ai_suggest(
            record_data={'amount_total': 15000, 'state': 'draft', 'partner': 'Client X'},
            suggestion_type='sale',
            module='sale',
        )
        self.assertIsInstance(result, (str, dict, list))

    def test_08_ai_suggest_crm(self):
        """ai_suggest propose des actions CRM."""
        result = self.env['ai.mixin'].ai_suggest(
            record_data={'probability': 40, 'revenue': 20000, 'stage': 'Qualification'},
            suggestion_type='crm',
            module='crm',
        )
        self.assertIsInstance(result, (str, dict, list))

    def test_09_ai_generate_empty_context(self):
        """ai_generate avec contexte vide ne crash pas."""
        result = self.env['ai.mixin'].ai_generate(
            prompt='Test vide',
            context_data={},
            module='sale',
        )
        self.assertIsInstance(result, dict)
        self.assertTrue(result.get('success'))


@tagged('post_install', '-at_install', 'custom_ai')
class TestAIWizard(TransactionCase):
    """Tests du wizard IA."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({
            'name': 'Partenaire Wizard IA',
        })
        cls.product = cls.env['product.product'].create({
            'name': 'Produit Wizard',
            'list_price': 100.0,
            'type': 'consu',
        })

    def _create_wizard(self, res_model='sale.order', res_id=None, **kwargs):
        if not res_id:
            if res_model == 'sale.order':
                order = self.env['sale.order'].create({
                    'partner_id': self.partner.id,
                    'order_line': [(0, 0, {
                        'product_id': self.product.id,
                        'product_uom_qty': 1,
                        'price_unit': 100.0,
                    })],
                })
                res_id = order.id
            elif res_model == 'res.partner':
                res_id = self.partner.id
        vals = {
            'res_model': res_model,
            'res_id': res_id,
            'action_type': 'generate_description',
        }
        vals.update(kwargs)
        return self.env['ai.wizard'].create(vals)

    def test_10_wizard_creation(self):
        """On peut créer un wizard IA."""
        wizard = self._create_wizard()
        self.assertEqual(wizard.res_model, 'sale.order')
        self.assertEqual(wizard.action_type, 'generate_description')
        self.assertFalse(wizard.ai_result)

    def test_11_wizard_action_types(self):
        """Tous les types d'action sont valides."""
        for atype in ('generate_description', 'analyze', 'suggest_price',
                       'suggest_action', 'generate_email', 'evaluate', 'predict', 'custom'):
            wizard = self._create_wizard(action_type=atype)
            self.assertEqual(wizard.action_type, atype)

    def test_12_wizard_generate(self):
        """action_generate produit un résultat HTML."""
        wizard = self._create_wizard()
        wizard.action_generate()
        self.assertTrue(wizard.ai_result, "Résultat IA non vide après génération")

    def test_13_wizard_generate_analysis(self):
        """L'analyse via wizard fonctionne."""
        wizard = self._create_wizard(action_type='analyze')
        wizard.action_generate()
        self.assertTrue(wizard.ai_result)

    def test_14_wizard_suggest_action(self):
        """La suggestion d'action fonctionne."""
        wizard = self._create_wizard(action_type='suggest_action')
        wizard.action_generate()
        self.assertTrue(wizard.ai_result)

    def test_15_wizard_custom_prompt(self):
        """Un prompt custom génère un résultat."""
        wizard = self._create_wizard(
            action_type='custom',
            custom_prompt='Donne-moi 3 idées pour améliorer cette commande',
        )
        wizard.action_generate()
        self.assertTrue(wizard.ai_result)

    def test_16_wizard_apply(self):
        """action_apply ferme le wizard."""
        wizard = self._create_wizard()
        wizard.action_generate()
        result = wizard.action_apply()
        self.assertEqual(result.get('type'), 'ir.actions.act_window_close')

    def test_17_wizard_partner_context(self):
        """Le wizard fonctionne avec res.partner."""
        wizard = self._create_wizard(
            res_model='res.partner',
            res_id=self.partner.id,
            action_type='analyze',
        )
        wizard.action_generate()
        self.assertTrue(wizard.ai_result)


@tagged('post_install', '-at_install', 'custom_ai')
class TestAIActions(TransactionCase):
    """Tests de l'injection des boutons IA dans les modèles."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({
            'name': 'Partner AI Actions',
        })
        cls.product = cls.env['product.product'].create({
            'name': 'Produit AI',
            'list_price': 50.0,
            'type': 'consu',
        })

    def test_20_sale_order_has_ai_action(self):
        """sale.order a la méthode action_open_ai_wizard."""
        order = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'order_line': [(0, 0, {
                'product_id': self.product.id,
                'product_uom_qty': 1,
                'price_unit': 50.0,
            })],
        })
        self.assertTrue(hasattr(order, 'action_open_ai_wizard'))
        result = order.action_open_ai_wizard()
        self.assertEqual(result.get('type'), 'ir.actions.act_window')
        self.assertEqual(result.get('res_model'), 'ai.wizard')

    def test_21_crm_lead_has_ai_action(self):
        """crm.lead a la méthode action_open_ai_wizard."""
        lead = self.env['crm.lead'].create({
            'name': 'Lead AI Test',
            'partner_id': self.partner.id,
        })
        result = lead.action_open_ai_wizard()
        self.assertEqual(result.get('res_model'), 'ai.wizard')

    def test_22_partner_has_ai_action(self):
        """res.partner a la méthode action_open_ai_wizard."""
        result = self.partner.action_open_ai_wizard()
        self.assertEqual(result.get('res_model'), 'ai.wizard')

    def test_23_employee_has_ai_action(self):
        """hr.employee a la méthode action_open_ai_wizard."""
        employee = self.env['hr.employee'].create({'name': 'Employee AI'})
        result = employee.action_open_ai_wizard()
        self.assertEqual(result.get('res_model'), 'ai.wizard')

    def test_24_purchase_has_ai_action(self):
        """purchase.order a la méthode action_open_ai_wizard."""
        po = self.env['purchase.order'].create({
            'partner_id': self.partner.id,
            'order_line': [(0, 0, {
                'product_id': self.product.id,
                'product_qty': 1,
                'price_unit': 50.0,
                'name': 'Ligne test',
            })],
        })
        result = po.action_open_ai_wizard()
        self.assertEqual(result.get('res_model'), 'ai.wizard')


@tagged('post_install', '-at_install', 'custom_ai')
class TestAIConfig(TransactionCase):
    """Tests de la configuration IA dans les paramètres."""

    def test_30_default_ai_provider(self):
        """Le fournisseur IA par défaut est 'builtin'."""
        config = self.env['res.config.settings'].create({})
        self.assertEqual(config.ai_provider, 'builtin')

    def test_31_set_openai_config(self):
        """On peut configurer OpenAI."""
        config = self.env['res.config.settings'].create({
            'ai_provider': 'openai',
            'ai_api_key': 'sk-test123',
            'ai_api_url': 'https://api.openai.com/v1',
            'ai_model': 'gpt-4',
            'ai_temperature': 0.7,
        })
        self.assertEqual(config.ai_provider, 'openai')
        self.assertEqual(config.ai_model, 'gpt-4')

    def test_32_set_ollama_config(self):
        """On peut configurer Ollama."""
        config = self.env['res.config.settings'].create({
            'ai_provider': 'ollama',
            'ai_api_url': 'http://localhost:11434',
            'ai_model': 'llama3',
        })
        self.assertEqual(config.ai_provider, 'ollama')
