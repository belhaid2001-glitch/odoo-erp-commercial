# -*- coding: utf-8 -*-
"""
===========================================================================
  TEST CONTACTS — Tests E2E pour custom_contacts
  Couvre : ResPartner, ContactSegment
===========================================================================
"""
from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install', 'custom_contacts')
class TestResPartnerCustom(TransactionCase):
    """Tests des champs personnalisés sur res.partner."""

    def _create_partner(self, **kwargs):
        vals = {
            'name': 'Contact Test',
            'email': 'contact@test.com',
        }
        vals.update(kwargs)
        return self.env['res.partner'].create(vals)

    # ─── Champs Marocains ────────────────────────────────────────────

    def test_01_moroccan_ids(self):
        """Les identifiants marocains sont stockés."""
        partner = self._create_partner(
            ice='001234567000089',
            rc='RC-12345',
            if_code='IF-67890',
            cnss='1234567890',
        )
        self.assertEqual(partner.ice, '001234567000089')
        self.assertEqual(partner.rc, 'RC-12345')
        self.assertEqual(partner.if_code, 'IF-67890')
        self.assertEqual(partner.cnss, '1234567890')

    # ─── Classification ──────────────────────────────────────────────

    def test_02_contact_type_custom(self):
        """Tous les types de contact personnalisés sont valides."""
        for ctype in ('prospect', 'client', 'supplier', 'partner', 'other'):
            p = self._create_partner(contact_type_custom=ctype, name=f'Contact {ctype}')
            self.assertEqual(p.contact_type_custom, ctype)

    def test_03_contact_priority(self):
        """Les priorités de contact sont valides."""
        for prio in ('low', 'medium', 'high', 'vip'):
            p = self._create_partner(contact_priority=prio, name=f'Contact {prio}')
            self.assertEqual(p.contact_priority, prio)

    def test_04_preferred_contact_method(self):
        """La méthode de contact préférée est stockée."""
        partner = self._create_partner(preferred_contact_method='email')
        self.assertEqual(partner.preferred_contact_method, 'email')

    # ─── Réseaux sociaux ─────────────────────────────────────────────

    def test_05_social_links(self):
        """Les liens réseaux sociaux sont stockés."""
        partner = self._create_partner(
            linkedin='https://linkedin.com/in/test',
            facebook='https://facebook.com/test',
            instagram='@test_insta',
        )
        self.assertEqual(partner.linkedin, 'https://linkedin.com/in/test')
        self.assertEqual(partner.facebook, 'https://facebook.com/test')
        self.assertEqual(partner.instagram, '@test_insta')

    # ─── Données entreprise ──────────────────────────────────────────

    def test_06_company_data(self):
        """Les données d'entreprise sont stockées."""
        from datetime import date
        partner = self._create_partner(
            is_company=True,
            capital=500000.0,
            date_creation_company=date(2020, 1, 15),
        )
        self.assertEqual(partner.capital, 500000.0)
        self.assertEqual(partner.date_creation_company, date(2020, 1, 15))

    # ─── Champs calculés ─────────────────────────────────────────────

    def test_10_computed_sale_totals(self):
        """Les totaux de vente sont calculés (0 si aucune commande)."""
        partner = self._create_partner()
        self.assertEqual(partner.total_sale_amount, 0)
        self.assertEqual(partner.sale_order_count_custom, 0)

    def test_11_computed_purchase_totals(self):
        """Les totaux d'achat sont calculés."""
        partner = self._create_partner()
        self.assertEqual(partner.total_purchase_amount, 0)
        self.assertEqual(partner.purchase_order_count_custom, 0)

    def test_12_first_last_order_dates(self):
        """Les dates de première/dernière commande sont null sans commandes."""
        partner = self._create_partner()
        self.assertFalse(partner.first_order_date)
        self.assertFalse(partner.last_order_date)

    # ─── Actions ─────────────────────────────────────────────────────

    def test_20_action_view_sale_orders(self):
        """action_view_sale_orders retourne une action."""
        partner = self._create_partner()
        result = partner.action_view_sale_orders()
        self.assertEqual(result.get('type'), 'ir.actions.act_window')
        self.assertEqual(result.get('res_model'), 'sale.order')

    def test_21_action_view_purchase_orders(self):
        """action_view_purchase_orders retourne une action."""
        partner = self._create_partner()
        result = partner.action_view_purchase_orders()
        self.assertEqual(result.get('type'), 'ir.actions.act_window')
        self.assertEqual(result.get('res_model'), 'purchase.order')


@tagged('post_install', '-at_install', 'custom_contacts')
class TestContactSegment(TransactionCase):
    """Tests du modèle de segmentation des contacts."""

    def test_30_create_segment(self):
        """On peut créer un segment de contacts."""
        segment = self.env['contact.segment'].create({
            'name': 'Segment Premium',
            'description': 'Clients à fort potentiel',
            'color': 5,
        })
        self.assertTrue(segment.active)
        self.assertEqual(segment.partner_count, 0)

    def test_31_segment_with_partners(self):
        """Un segment avec des partenaires calcule le compteur."""
        partners = self.env['res.partner']
        for i in range(3):
            partners |= self.env['res.partner'].create({'name': f'P{i}'})
        segment = self.env['contact.segment'].create({
            'name': 'Segment avec contacts',
            'partner_ids': [(6, 0, partners.ids)],
        })
        self.assertEqual(segment.partner_count, 3)

    def test_32_partner_segments(self):
        """Un partenaire peut avoir plusieurs segments."""
        s1 = self.env['contact.segment'].create({'name': 'Seg1'})
        s2 = self.env['contact.segment'].create({'name': 'Seg2'})
        partner = self.env['res.partner'].create({
            'name': 'Multi-segment',
            'segment_ids': [(6, 0, [s1.id, s2.id])],
        })
        self.assertEqual(len(partner.segment_ids), 2)

    def test_33_deactivate_segment(self):
        """On peut archiver un segment."""
        segment = self.env['contact.segment'].create({'name': 'À archiver'})
        segment.active = False
        self.assertFalse(segment.active)
