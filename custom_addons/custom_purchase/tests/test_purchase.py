# -*- coding: utf-8 -*-
"""
===========================================================================
  TEST PURCHASE — Tests E2E pour custom_purchase
  Couvre : PurchaseOrder, PurchaseConvention, PurchaseConventionLine
===========================================================================
"""
from datetime import date, timedelta
from odoo.tests.common import TransactionCase, tagged
from odoo.exceptions import UserError


@tagged('post_install', '-at_install', 'custom_purchase')
class TestPurchaseOrderCustom(TransactionCase):
    """Tests des champs et méthodes personnalisés sur purchase.order."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.supplier = cls.env['res.partner'].create({
            'name': 'Fournisseur Test Achat',
            'email': 'fournisseur@test.com',
            'supplier_rank': 1,
        })
        cls.product = cls.env['product.product'].create({
            'name': 'Produit Test Achat',
            'list_price': 50.0,
            'standard_price': 30.0,
            'type': 'consu',
        })

    def _create_purchase_order(self, **kwargs):
        vals = {
            'partner_id': self.supplier.id,
            'order_line': [(0, 0, {
                'product_id': self.product.id,
                'product_qty': 10,
                'price_unit': 50.0,
                'name': 'Ligne test',
            })],
        }
        vals.update(kwargs)
        return self.env['purchase.order'].create(vals)

    # ─── Champs personnalisés ────────────────────────────────────────

    def test_01_default_purchase_fields(self):
        """Les champs custom ont les valeurs par défaut."""
        po = self._create_purchase_order()
        self.assertEqual(po.purchase_type, 'standard')
        self.assertFalse(po.quality_check)
        self.assertFalse(po.supplier_reference)

    def test_02_purchase_types(self):
        """Tous les types d'achat sont valides."""
        for ptype in ('standard', 'urgent', 'framework', 'recurring'):
            po = self._create_purchase_order(purchase_type=ptype)
            self.assertEqual(po.purchase_type, ptype)

    def test_03_priority_extended(self):
        """La priorité étendue fonctionne."""
        po = self._create_purchase_order(priority='2')
        self.assertEqual(po.priority, '2')

    # ─── Champs calculés ─────────────────────────────────────────────

    def test_10_total_savings_computed(self):
        """Les économies totales sont calculées."""
        po = self._create_purchase_order()
        self.assertIsNotNone(po.total_savings)

    def test_11_approval_required_above_threshold(self):
        """L'approbation est requise au-dessus de 50k."""
        po = self._create_purchase_order()
        po.order_line[0].write({'product_qty': 1100, 'price_unit': 50.0})
        # 1100 * 50 = 55000 → approval_required should be True
        self.assertTrue(po.approval_required)

    def test_12_approval_not_required_below_threshold(self):
        """Pas d'approbation requise en dessous de 50k."""
        po = self._create_purchase_order()
        # 10 * 50 = 500 → pas de seuil
        self.assertFalse(po.approval_required)

    def test_13_reception_status_pending(self):
        """Le statut de réception est 'pending' pour un nouveau PO."""
        po = self._create_purchase_order()
        self.assertEqual(po.reception_status, 'pending')

    # ─── Quality ─────────────────────────────────────────────────────

    def test_20_quality_check_toggle(self):
        """On peut activer le contrôle qualité."""
        po = self._create_purchase_order(quality_check=True)
        self.assertTrue(po.quality_check)

    def test_21_quality_notes(self):
        """Les notes qualité sont stockées."""
        po = self._create_purchase_order(quality_check=True, quality_notes="Vérifier dimensions")
        self.assertEqual(po.quality_notes, "Vérifier dimensions")


@tagged('post_install', '-at_install', 'custom_purchase')
class TestPurchaseConvention(TransactionCase):
    """Tests du modèle convention fournisseur."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.supplier = cls.env['res.partner'].create({
            'name': 'Fournisseur Convention',
            'supplier_rank': 1,
        })
        cls.product = cls.env['product.product'].create({
            'name': 'Produit Convention',
            'list_price': 100.0,
            'type': 'consu',
        })

    def _create_convention(self, **kwargs):
        vals = {
            'partner_id': self.supplier.id,
            'date_start': date.today(),
            'date_end': date.today() + timedelta(days=365),
            'discount': 10.0,
            'min_amount': 1000.0,
            'max_amount': 100000.0,
        }
        vals.update(kwargs)
        return self.env['purchase.convention'].create(vals)

    def test_30_convention_creation(self):
        """Une convention est créée en brouillon avec nom séquencé."""
        conv = self._create_convention()
        self.assertEqual(conv.state, 'draft')
        self.assertTrue(conv.name)

    def test_31_convention_activate(self):
        """On peut activer une convention."""
        conv = self._create_convention()
        conv.action_activate()
        self.assertEqual(conv.state, 'active')

    def test_32_convention_expire(self):
        """On peut expirer une convention active."""
        conv = self._create_convention()
        conv.action_activate()
        conv.action_expire()
        self.assertEqual(conv.state, 'expired')

    def test_33_convention_cancel(self):
        """On peut annuler une convention."""
        conv = self._create_convention()
        conv.action_cancel()
        self.assertEqual(conv.state, 'cancelled')

    def test_34_convention_reset_draft(self):
        """On peut remettre en brouillon une convention annulée."""
        conv = self._create_convention()
        conv.action_cancel()
        conv.action_reset_draft()
        self.assertEqual(conv.state, 'draft')

    def test_35_convention_lines(self):
        """On peut ajouter des lignes de convention."""
        conv = self._create_convention()
        self.env['purchase.convention.line'].create({
            'convention_id': conv.id,
            'product_id': self.product.id,
            'min_qty': 10,
            'max_qty': 1000,
            'negotiated_price': 85.0,
            'discount': 15.0,
        })
        self.assertEqual(len(conv.line_ids), 1)

    def test_36_convention_purchase_count(self):
        """Le compteur d'achats est calculé."""
        conv = self._create_convention()
        self.assertEqual(conv.purchase_count, 0)

    def test_37_convention_expired_dates(self):
        """Convention avec dates passées."""
        conv = self._create_convention(
            date_start=date.today() - timedelta(days=400),
            date_end=date.today() - timedelta(days=30),
        )
        conv.action_activate()
        # Le cron devrait l'expirer
        self.env['purchase.convention']._cron_check_expiration()
        conv.invalidate_recordset()
        self.assertEqual(conv.state, 'expired')

    # ─── Cas négatifs ────────────────────────────────────────────────

    def test_40_convention_without_partner(self):
        """Impossible de créer une convention sans partenaire."""
        with self.assertRaises(Exception):
            self.env['purchase.convention'].create({
                'date_start': date.today(),
                'date_end': date.today() + timedelta(days=30),
            })

    def test_41_convention_line_without_product(self):
        """Impossible de créer une ligne de convention sans produit."""
        conv = self._create_convention()
        with self.assertRaises(Exception):
            self.env['purchase.convention.line'].create({
                'convention_id': conv.id,
                'min_qty': 1,
                'negotiated_price': 50,
            })
