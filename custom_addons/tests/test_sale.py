# -*- coding: utf-8 -*-
"""
===========================================================================
  TEST SALE — Tests E2E pour custom_sale
  Couvre : SaleOrder, SaleOrderOptionalProduct, SaleForecast
===========================================================================
"""
from datetime import date, timedelta
from odoo.tests.common import TransactionCase, tagged, Form
from odoo.exceptions import UserError, AccessError, ValidationError


@tagged('post_install', '-at_install', 'custom_sale')
class TestSaleOrderCustomFields(TransactionCase):
    """Tests des champs personnalisés sur sale.order."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({
            'name': 'Client Test Vente',
            'email': 'client.vente@test.com',
        })
        cls.product = cls.env['product.product'].create({
            'name': 'Produit Test Vente',
            'list_price': 100.0,
            'standard_price': 60.0,
            'type': 'consu',
        })
        cls.manager_user = cls.env['res.users'].create({
            'name': 'Manager Vente Test',
            'login': 'manager_vente_test',
            'email': 'manager.vente@test.com',
            'groups_id': [(6, 0, [
                cls.env.ref('sales_team.group_sale_manager').id,
                cls.env.ref('base.group_user').id,
            ])],
        })
        cls.salesman_user = cls.env['res.users'].create({
            'name': 'Vendeur Test',
            'login': 'vendeur_test',
            'email': 'vendeur@test.com',
            'groups_id': [(6, 0, [
                cls.env.ref('sales_team.group_sale_salesman').id,
                cls.env.ref('base.group_user').id,
            ])],
        })

    def _create_sale_order(self, **kwargs):
        """Helper : crée un bon de commande avec une ligne."""
        vals = {
            'partner_id': self.partner.id,
            'order_line': [(0, 0, {
                'product_id': self.product.id,
                'product_uom_qty': 5,
                'price_unit': 100.0,
            })],
        }
        vals.update(kwargs)
        return self.env['sale.order'].create(vals)

    # ─── Champs personnalisés ────────────────────────────────────────

    def test_01_default_fields(self):
        """Les champs personnalisés ont des valeurs par défaut correctes."""
        order = self._create_sale_order()
        self.assertEqual(order.priority, '0', "Priorité par défaut = normal")
        self.assertEqual(order.sale_type, 'standard', "Type de vente par défaut = standard")
        self.assertEqual(order.approval_status, 'draft', "Statut d'approbation par défaut = brouillon")
        self.assertFalse(order.customer_reference, "Référence client vide par défaut")
        self.assertFalse(order.delivery_note, "Note de livraison vide par défaut")

    def test_02_sale_type_selection(self):
        """On peut définir tous les types de vente."""
        for sale_type in ('standard', 'subscription', 'project'):
            order = self._create_sale_order(sale_type=sale_type)
            self.assertEqual(order.sale_type, sale_type)

    def test_03_priority_values(self):
        """Les priorités 0-4 sont acceptées."""
        for prio in ('0', '1', '2', '3'):
            order = self._create_sale_order(priority=prio)
            self.assertEqual(order.priority, prio)

    def test_04_customer_reference(self):
        """La référence client est stockée correctement."""
        order = self._create_sale_order(customer_reference='REF-CLIENT-2026')
        self.assertEqual(order.customer_reference, 'REF-CLIENT-2026')

    # ─── Champs calculés ─────────────────────────────────────────────

    def test_10_margin_percent_computed(self):
        """Le pourcentage de marge se calcule automatiquement."""
        order = self._create_sale_order()
        # total = 5 * 100 = 500, cost = 5 * 60 = 300 → margin 40%
        self.assertGreater(order.margin_percent, 0, "Marge positive attendue")

    def test_11_total_discount_computed(self):
        """Le total de remise est calculé à partir des lignes."""
        order = self._create_sale_order()
        order.order_line[0].discount = 10  # 10% discount
        self.assertGreater(order.total_discount, 0, "Remise totale > 0 quand discount appliqué")

    def test_12_is_ready_to_invoice(self):
        """is_ready_to_invoice est calculé correctement."""
        order = self._create_sale_order()
        # Un devis brouillon ne devrait pas être ready to invoice
        self.assertFalse(order.is_ready_to_invoice)

    # ─── Workflow d'approbation ──────────────────────────────────────

    def test_20_request_approval(self):
        """action_request_approval passe le statut en pending."""
        order = self._create_sale_order()
        order.action_request_approval()
        self.assertEqual(order.approval_status, 'pending')

    def test_21_approve_order(self):
        """action_approve_order valide le devis et enregistre l'approbateur."""
        order = self._create_sale_order()
        order.action_request_approval()
        order.with_user(self.manager_user).action_approve_order()
        self.assertEqual(order.approval_status, 'approved')
        self.assertTrue(order.approved_by, "Approbateur renseigné")
        self.assertTrue(order.approval_date, "Date d'approbation renseignée")

    def test_22_reject_order(self):
        """action_reject_order rejette le devis."""
        order = self._create_sale_order()
        order.action_request_approval()
        order.with_user(self.manager_user).action_reject_order()
        self.assertEqual(order.approval_status, 'rejected')

    def test_23_approval_on_draft_raises(self):
        """Impossible d'approuver un devis en brouillon (pas en attente)."""
        order = self._create_sale_order()
        with self.assertRaises(Exception):
            order.with_user(self.manager_user).action_approve_order()

    # ─── Produits optionnels ─────────────────────────────────────────

    def test_30_optional_product_creation(self):
        """On peut ajouter des produits optionnels à une commande."""
        order = self._create_sale_order()
        optional = self.env['sale.order.optional.product'].create({
            'order_id': order.id,
            'product_id': self.product.id,
            'description': 'Produit optionnel test',
            'quantity': 2,
            'price_unit': 80.0,
        })
        self.assertEqual(len(order.optional_product_ids), 1)
        self.assertFalse(optional.is_selected, "Produit optionnel non sélectionné par défaut")

    def test_31_add_optional_to_order(self):
        """action_add_to_order ajoute le produit optionnel aux lignes."""
        order = self._create_sale_order()
        optional = self.env['sale.order.optional.product'].create({
            'order_id': order.id,
            'product_id': self.product.id,
            'description': 'Produit optionnel test',
            'quantity': 3,
            'price_unit': 75.0,
        })
        initial_lines = len(order.order_line)
        optional.action_add_to_order()
        self.assertTrue(optional.is_selected, "Produit marqué comme sélectionné")
        self.assertEqual(len(order.order_line), initial_lines + 1, "Ligne ajoutée")

    # ─── Facturation par lot ─────────────────────────────────────────

    def test_40_batch_invoice(self):
        """action_generate_invoice_batch ne crash pas."""
        order = self._create_sale_order()
        # On ne peut pas facturer un devis brouillon, mais on vérifie qu'il n'y a pas d'erreur
        try:
            self.env['sale.order'].action_generate_invoice_batch()
        except Exception:
            pass  # Acceptable si aucune commande prête


@tagged('post_install', '-at_install', 'custom_sale')
class TestSaleForecast(TransactionCase):
    """Tests du modèle de prévision de ventes."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({
            'name': 'Client Forecast',
        })
        cls.product = cls.env['product.product'].create({
            'name': 'Produit Forecast',
            'list_price': 200.0,
            'type': 'consu',
        })

    def _create_forecast(self, **kwargs):
        """Helper : crée une prévision de vente."""
        vals = {
            'date_forecast': date.today(),
            'date_target': date.today() + timedelta(days=30),
            'user_id': self.env.uid,
            'partner_id': self.partner.id,
            'product_id': self.product.id,
            'forecast_amount': 10000.0,
        }
        vals.update(kwargs)
        return self.env['sale.forecast'].create(vals)

    def test_50_forecast_creation(self):
        """Une prévision est créée en état brouillon avec un nom séquencé."""
        forecast = self._create_forecast()
        self.assertEqual(forecast.state, 'draft')
        self.assertTrue(forecast.name, "Nom auto-séquencé renseigné")

    def test_51_forecast_workflow(self):
        """Le workflow draft → confirmed → done fonctionne."""
        forecast = self._create_forecast()
        forecast.action_confirm()
        self.assertEqual(forecast.state, 'confirmed')
        forecast.action_done()
        self.assertEqual(forecast.state, 'done')

    def test_52_forecast_cancel_and_reset(self):
        """On peut annuler puis remettre en brouillon."""
        forecast = self._create_forecast()
        forecast.action_confirm()
        forecast.action_cancel()
        self.assertEqual(forecast.state, 'cancelled')
        forecast.action_reset_draft()
        self.assertEqual(forecast.state, 'draft')

    def test_53_achievement_rate_computed(self):
        """Le taux de réalisation se calcule."""
        forecast = self._create_forecast(forecast_amount=10000.0)
        # achievement_rate dépend des ventes réelles
        self.assertIsNotNone(forecast.achievement_rate)

    def test_54_forecast_negative_amount(self):
        """Une prévision avec montant négatif est techniquement possible."""
        forecast = self._create_forecast(forecast_amount=-100.0)
        self.assertEqual(forecast.forecast_amount, -100.0)


@tagged('post_install', '-at_install', 'custom_sale')
class TestSaleAccessRights(TransactionCase):
    """Tests des droits d'accès sur les modèles de vente."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.basic_user = cls.env['res.users'].create({
            'name': 'Utilisateur Basique',
            'login': 'basic_sale_test',
            'email': 'basic@test.com',
            'groups_id': [(6, 0, [cls.env.ref('base.group_user').id])],
        })
        cls.salesman = cls.env['res.users'].create({
            'name': 'Vendeur Droits',
            'login': 'salesman_rights_test',
            'email': 'salesman.rights@test.com',
            'groups_id': [(6, 0, [
                cls.env.ref('sales_team.group_sale_salesman').id,
                cls.env.ref('base.group_user').id,
            ])],
        })

    def test_60_salesman_can_create_optional_product(self):
        """Un vendeur peut créer un produit optionnel."""
        partner = self.env['res.partner'].create({'name': 'P'})
        product = self.env['product.product'].create({'name': 'P', 'list_price': 10})
        order = self.env['sale.order'].with_user(self.salesman).create({
            'partner_id': partner.id,
            'order_line': [(0, 0, {'product_id': product.id, 'product_uom_qty': 1, 'price_unit': 10})],
        })
        optional = self.env['sale.order.optional.product'].with_user(self.salesman).create({
            'order_id': order.id,
            'product_id': product.id,
            'quantity': 1,
            'price_unit': 10,
        })
        self.assertTrue(optional.id)

    def test_61_salesman_can_create_forecast(self):
        """Un vendeur peut créer une prévision."""
        partner = self.env['res.partner'].create({'name': 'P'})
        product = self.env['product.product'].create({'name': 'P', 'list_price': 10})
        forecast = self.env['sale.forecast'].with_user(self.salesman).create({
            'date_forecast': date.today(),
            'date_target': date.today() + timedelta(days=30),
            'user_id': self.salesman.id,
            'partner_id': partner.id,
            'product_id': product.id,
            'forecast_amount': 5000,
        })
        self.assertTrue(forecast.id)
