# -*- coding: utf-8 -*-
"""
===========================================================================
  TEST CALENDAR — Tests E2E pour custom_calendar
  Couvre : CalendarEvent, CalendarEventType
===========================================================================
"""
from datetime import datetime, timedelta
from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install', 'custom_calendar')
class TestCalendarEventCustom(TransactionCase):
    """Tests des champs et actions personnalisés sur calendar.event."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({'name': 'Contact Calendrier'})

    def _create_event(self, **kwargs):
        vals = {
            'name': 'Rendez-vous Test',
            'start': datetime.now() + timedelta(hours=1),
            'stop': datetime.now() + timedelta(hours=2),
            'partner_ids': [(4, self.partner.id)],
        }
        vals.update(kwargs)
        return self.env['calendar.event'].create(vals)

    # ─── Champs personnalisés ────────────────────────────────────────

    def test_01_event_type_custom(self):
        """Tous les types d'événement custom sont valides."""
        for etype in ('meeting', 'call', 'visit', 'visit_supplier', 'training',
                       'demo', 'interview', 'internal', 'other'):
            ev = self._create_event(event_type_custom=etype, name=f'Event {etype}')
            self.assertEqual(ev.event_type_custom, etype)

    def test_02_priority(self):
        """Les priorités 0-3 sont valides."""
        for p in ('0', '1', '2', '3'):
            ev = self._create_event(priority=p)
            self.assertEqual(ev.priority, p)

    def test_03_meeting_location_type(self):
        """Les types de lieu sont valides."""
        for loc in ('office', 'client', 'remote', 'external'):
            ev = self._create_event(meeting_location_type=loc, name=f'Event {loc}')
            self.assertEqual(ev.meeting_location_type, loc)

    def test_04_meeting_url(self):
        """L'URL de réunion est stockée."""
        ev = self._create_event(
            meeting_location_type='remote',
            meeting_url='https://meet.google.com/abc-defg-hij',
        )
        self.assertEqual(ev.meeting_url, 'https://meet.google.com/abc-defg-hij')

    def test_05_preparation_notes(self):
        """Les notes de préparation sont stockées."""
        ev = self._create_event(preparation_notes='Préparer la démo produit X')
        self.assertEqual(ev.preparation_notes, 'Préparer la démo produit X')

    def test_06_meeting_minutes(self):
        """Le compte-rendu HTML est stocké."""
        ev = self._create_event(meeting_minutes='<p>Discussion sur le projet</p>')
        self.assertIn('Discussion sur le projet', ev.meeting_minutes)

    # ─── Actions de résultat ─────────────────────────────────────────

    def test_10_mark_positive(self):
        """action_mark_positive met le résultat en 'positive'."""
        ev = self._create_event()
        ev.action_mark_positive()
        self.assertEqual(ev.result, 'positive')

    def test_11_mark_negative(self):
        """action_mark_negative met le résultat en 'negative'."""
        ev = self._create_event()
        ev.action_mark_negative()
        self.assertEqual(ev.result, 'negative')

    # ─── Suivi ───────────────────────────────────────────────────────

    def test_15_follow_up(self):
        """action_request_follow_up active le suivi."""
        ev = self._create_event()
        ev.action_request_follow_up()
        self.assertTrue(ev.follow_up_required)

    def test_16_follow_up_notes(self):
        """Les notes de suivi sont stockées."""
        ev = self._create_event(
            follow_up_required=True,
            follow_up_notes='Relancer client la semaine prochaine',
        )
        self.assertEqual(ev.follow_up_notes, 'Relancer client la semaine prochaine')

    # ─── Module lié ──────────────────────────────────────────────────

    def test_20_linked_module(self):
        """Le module lié est stocké."""
        for mod in ('crm', 'sale', 'purchase', 'stock', 'hr', 'project', 'other'):
            ev = self._create_event(linked_module=mod, name=f'Event {mod}')
            self.assertEqual(ev.linked_module, mod)


@tagged('post_install', '-at_install', 'custom_calendar')
class TestCalendarEventTypeCustom(TransactionCase):
    """Tests du modèle type d'événement."""

    def test_30_create_event_type(self):
        """On peut créer un type de rendez-vous."""
        etype = self.env['calendar.event.type.custom'].create({
            'name': 'Visite client',
            'default_duration': 1.5,
            'color': 3,
        })
        self.assertTrue(etype.active)
        self.assertEqual(etype.default_duration, 1.5)

    def test_31_deactivate_event_type(self):
        """On peut archiver un type."""
        etype = self.env['calendar.event.type.custom'].create({'name': 'À archiver'})
        etype.active = False
        self.assertFalse(etype.active)
