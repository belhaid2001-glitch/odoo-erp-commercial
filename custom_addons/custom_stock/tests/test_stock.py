# -*- coding: utf-8 -*-
"""
===========================================================================
  TEST STOCK — Tests E2E pour custom_stock
  Couvre : StockPicking, StockQualityCheck, StockQualityTeam, StockValuationReport
===========================================================================
"""
from odoo.tests.common import TransactionCase, tagged
from odoo.exceptions import UserError


@tagged('post_install', '-at_install', 'custom_stock')
class TestStockPickingCustom(TransactionCase):
    """Tests des champs et workflow de préparation sur stock.picking."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({'name': 'Client Stock Test'})
        cls.product = cls.env['product.product'].create({
            'name': 'Produit Stock Test',
            'type': 'product',
            'list_price': 50.0,
            'standard_price': 30.0,
        })
        cls.warehouse = cls.env['stock.warehouse'].search([], limit=1)
        cls.picking_type_out = cls.warehouse.out_type_id
        # Locations de secours si les valeurs par défaut sont vides
        cls.stock_location = cls.warehouse.lot_stock_id
        cls.customer_location = cls.env.ref('stock.stock_location_customers')

    def _create_picking(self, **kwargs):
        src = self.picking_type_out.default_location_src_id or self.stock_location
        dest = self.picking_type_out.default_location_dest_id or self.customer_location
        vals = {
            'partner_id': self.partner.id,
            'picking_type_id': self.picking_type_out.id,
            'location_id': src.id,
            'location_dest_id': dest.id,
            'move_ids': [(0, 0, {
                'name': 'Move Test',
                'product_id': self.product.id,
                'product_uom_qty': 5,
                'location_id': src.id,
                'location_dest_id': dest.id,
            })],
        }
        vals.update(kwargs)
        return self.env['stock.picking'].create(vals)

    # ─── Champs par défaut ───────────────────────────────────────────

    def test_01_default_preparation_status(self):
        """Le statut de préparation est 'not_started' par défaut."""
        picking = self._create_picking()
        self.assertEqual(picking.preparation_status, 'not_started')

    def test_02_default_quality_fields(self):
        """Les champs qualité sont vides par défaut."""
        picking = self._create_picking()
        self.assertFalse(picking.quality_check_required)
        self.assertEqual(picking.quality_status, 'none')

    # ─── Workflow de préparation ─────────────────────────────────────

    def test_10_start_preparation(self):
        """action_start_preparation passe en 'in_progress'."""
        picking = self._create_picking()
        picking.action_start_preparation()
        self.assertEqual(picking.preparation_status, 'in_progress')

    def test_11_mark_ready(self):
        """action_mark_ready passe en 'ready'."""
        picking = self._create_picking()
        picking.action_start_preparation()
        picking.action_mark_ready()
        self.assertEqual(picking.preparation_status, 'ready')

    def test_12_mark_shipped(self):
        """action_mark_shipped passe en 'shipped'."""
        picking = self._create_picking()
        picking.action_start_preparation()
        picking.action_mark_ready()
        picking.action_mark_shipped()
        self.assertEqual(picking.preparation_status, 'shipped')

    # ─── Contrôle qualité ────────────────────────────────────────────

    def test_20_create_quality_checks(self):
        """action_create_quality_checks crée des contrôles pour chaque produit."""
        picking = self._create_picking()
        picking.action_create_quality_checks()
        self.assertTrue(len(picking.quality_check_ids) > 0)
        self.assertEqual(picking.quality_check_required, True)

    def test_21_quality_pass(self):
        """action_pass valide un contrôle qualité."""
        picking = self._create_picking()
        picking.action_create_quality_checks()
        qc = picking.quality_check_ids[0]
        qc.action_pass()
        self.assertEqual(qc.result, 'pass')

    def test_22_quality_fail(self):
        """action_fail met un contrôle en échec."""
        picking = self._create_picking()
        picking.action_create_quality_checks()
        qc = picking.quality_check_ids[0]
        qc.action_fail()
        self.assertEqual(qc.result, 'fail')

    def test_23_quality_reset(self):
        """action_reset remet un contrôle en pending."""
        picking = self._create_picking()
        picking.action_create_quality_checks()
        qc = picking.quality_check_ids[0]
        qc.action_pass()
        qc.action_reset()
        self.assertEqual(qc.result, 'pending')

    def test_24_quality_status_computed(self):
        """Le quality_status picking est calculé à partir des contrôles."""
        picking = self._create_picking()
        picking.action_create_quality_checks()
        # Tous pending → pending
        self.assertEqual(picking.quality_status, 'pending')
        # Tous pass → passed
        for qc in picking.quality_check_ids:
            qc.action_pass()
        picking.invalidate_recordset()
        self.assertEqual(picking.quality_status, 'passed')

    # ─── Poids et colis ──────────────────────────────────────────────

    def test_30_weight_total_computed(self):
        """Le poids total est calculé."""
        picking = self._create_picking()
        self.assertIsNotNone(picking.weight_total)

    def test_31_package_count(self):
        """Le nombre de colis peut être défini."""
        picking = self._create_picking(package_count=3)
        self.assertEqual(picking.package_count, 3)

    # ─── Champs texte ────────────────────────────────────────────────

    def test_35_delivery_instructions(self):
        """Les instructions de livraison sont stockées."""
        picking = self._create_picking(delivery_instructions="Fragile - Manipuler avec soin")
        self.assertEqual(picking.delivery_instructions, "Fragile - Manipuler avec soin")

    def test_36_carrier_tracking(self):
        """Le numéro de suivi transporteur est stocké."""
        picking = self._create_picking(carrier_tracking="TR-2026-00123")
        self.assertEqual(picking.carrier_tracking, "TR-2026-00123")


@tagged('post_install', '-at_install', 'custom_stock')
class TestStockQualityTeam(TransactionCase):
    """Tests du modèle équipe qualité."""

    def test_40_create_quality_team(self):
        """On peut créer une équipe qualité."""
        user = self.env['res.users'].search([], limit=1)
        team = self.env['stock.quality.team'].create({
            'name': 'Équipe Qualité A',
            'leader_id': user.id,
            'member_ids': [(6, 0, [user.id])],
        })
        self.assertTrue(team.active)
        self.assertEqual(team.name, 'Équipe Qualité A')

    def test_41_deactivate_team(self):
        """On peut désactiver une équipe."""
        user = self.env['res.users'].search([], limit=1)
        team = self.env['stock.quality.team'].create({
            'name': 'Équipe à désactiver',
            'leader_id': user.id,
        })
        team.active = False
        self.assertFalse(team.active)


@tagged('post_install', '-at_install', 'custom_stock')
class TestStockValuationReport(TransactionCase):
    """Tests du rapport de valorisation (vue SQL)."""

    def test_50_valuation_report_readable(self):
        """Le rapport de valorisation est lisible sans erreur."""
        records = self.env['stock.valuation.report'].search([], limit=10)
        # Peut être vide, mais la requête ne doit pas planter
        self.assertIsNotNone(records)
