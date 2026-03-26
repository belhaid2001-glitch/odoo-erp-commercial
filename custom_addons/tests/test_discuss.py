# -*- coding: utf-8 -*-
"""
===========================================================================
  TEST DISCUSS — Tests E2E pour custom_discuss
  Couvre : MailTemplateCustom, MailMessageCustom
===========================================================================
"""
from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install', 'custom_discuss')
class TestMailTemplateCustom(TransactionCase):
    """Tests du modèle template de message personnalisé."""

    def _create_template(self, **kwargs):
        vals = {
            'name': 'Template Test',
            'category': 'commercial',
            'subject': 'Sujet test',
            'body': '<p>Corps du message</p>',
        }
        vals.update(kwargs)
        return self.env['mail.template.custom'].create(vals)

    def test_01_create_template(self):
        """On peut créer un template personnalisé."""
        tpl = self._create_template()
        self.assertTrue(tpl.active)
        self.assertFalse(tpl.is_internal)

    def test_02_template_categories(self):
        """Toutes les catégories sont valides."""
        for cat in ('commercial', 'support', 'internal', 'hr', 'accounting', 'other'):
            tpl = self._create_template(category=cat, name=f'Template {cat}')
            self.assertEqual(tpl.category, cat)

    def test_03_internal_template(self):
        """Un template interne est marqué comme tel."""
        tpl = self._create_template(is_internal=True)
        self.assertTrue(tpl.is_internal)

    def test_04_template_body_html(self):
        """Le corps HTML est stocké."""
        tpl = self._create_template(body='<h1>Titre</h1><p>Paragraphe</p>')
        self.assertIn('Titre', tpl.body)

    def test_05_template_sequence(self):
        """La séquence d'ordonnancement est stockée."""
        tpl = self._create_template(sequence=5)
        self.assertEqual(tpl.sequence, 5)

    def test_06_archive_template(self):
        """On peut archiver un template."""
        tpl = self._create_template()
        tpl.active = False
        self.assertFalse(tpl.active)

    def test_07_template_without_name(self):
        """Impossible de créer un template sans nom."""
        with self.assertRaises(Exception):
            self.env['mail.template.custom'].create({
                'category': 'commercial',
                'subject': 'Test',
                'body': '<p>Test</p>',
            })


@tagged('post_install', '-at_install', 'custom_discuss')
class TestMailMessageCustom(TransactionCase):
    """Tests des champs personnalisés sur mail.message."""

    def test_10_message_priority(self):
        """La priorité de message est stockée."""
        msg = self.env['mail.message'].create({
            'body': '<p>Message prioritaire</p>',
            'message_type': 'comment',
            'message_priority': 'urgent',
        })
        self.assertEqual(msg.message_priority, 'urgent')

    def test_11_message_priority_values(self):
        """Toutes les priorités sont valides."""
        for prio in ('low', 'normal', 'high', 'urgent'):
            msg = self.env['mail.message'].create({
                'body': f'<p>Message {prio}</p>',
                'message_type': 'comment',
                'message_priority': prio,
            })
            self.assertEqual(msg.message_priority, prio)

    def test_12_message_flagged(self):
        """On peut marquer un message comme flaggé."""
        msg = self.env['mail.message'].create({
            'body': '<p>Message flaggé</p>',
            'message_type': 'comment',
            'is_flagged': True,
        })
        self.assertTrue(msg.is_flagged)
