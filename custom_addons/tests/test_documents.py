# -*- coding: utf-8 -*-
"""
===========================================================================
  TEST DOCUMENTS — Tests E2E pour custom_documents
  Couvre : DocumentFolder, DocumentDocument, DocumentTag
===========================================================================
"""
import base64
from datetime import date, timedelta
from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install', 'custom_documents')
class TestDocumentFolder(TransactionCase):
    """Tests du modèle dossier de documents."""

    def test_01_create_folder(self):
        """On peut créer un dossier."""
        folder = self.env['document.folder'].create({
            'name': 'Dossier Contrats',
            'description': 'Tous les contrats',
        })
        self.assertTrue(folder.active)
        self.assertEqual(folder.document_count, 0)

    def test_02_folder_hierarchy(self):
        """Les dossiers ont une hiérarchie parent/enfant."""
        parent = self.env['document.folder'].create({'name': 'Parent'})
        child = self.env['document.folder'].create({
            'name': 'Enfant',
            'parent_id': parent.id,
        })
        self.assertEqual(child.parent_id.id, parent.id)
        self.assertIn(child.id, parent.child_ids.ids)

    def test_03_folder_document_count(self):
        """Le compteur de documents est incrémenté."""
        folder = self.env['document.folder'].create({'name': 'F'})
        for i in range(3):
            self.env['document.document'].create({
                'name': f'Doc {i}',
                'folder_id': folder.id,
            })
        folder.invalidate_recordset()
        self.assertEqual(folder.document_count, 3)


@tagged('post_install', '-at_install', 'custom_documents')
class TestDocumentDocument(TransactionCase):
    """Tests du modèle document."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.folder = cls.env['document.folder'].create({'name': 'Dossier Test'})
        cls.sample_file = base64.b64encode(b'Contenu fichier test PDF')

    def _create_document(self, **kwargs):
        vals = {
            'name': 'Document Test',
            'folder_id': self.folder.id,
            'document_type': 'contract',
        }
        vals.update(kwargs)
        return self.env['document.document'].create(vals)

    # ─── Création ────────────────────────────────────────────────────

    def test_10_document_creation(self):
        """Un document est créé en brouillon."""
        doc = self._create_document()
        self.assertEqual(doc.state, 'draft')
        self.assertEqual(doc.version, 1)

    def test_11_document_types(self):
        """Tous les types de document sont valides."""
        for dtype in ('contract', 'invoice', 'report', 'policy', 'procedure',
                       'template', 'correspondence', 'certificate', 'other'):
            doc = self._create_document(document_type=dtype, name=f'Doc {dtype}')
            self.assertEqual(doc.document_type, dtype)

    def test_12_document_with_file(self):
        """Un document avec fichier calcule la taille."""
        doc = self._create_document(
            file=self.sample_file,
            file_name='test.pdf',
        )
        self.assertTrue(doc.file)
        self.assertGreater(doc.file_size, 0)

    # ─── Workflow ────────────────────────────────────────────────────

    def test_20_validate_document(self):
        """action_validate passe en 'validated'."""
        doc = self._create_document()
        doc.action_validate()
        self.assertEqual(doc.state, 'validated')

    def test_21_archive_document(self):
        """action_archive passe en 'archived'."""
        doc = self._create_document()
        doc.action_validate()
        doc.action_archive()
        self.assertEqual(doc.state, 'archived')

    def test_22_reset_draft(self):
        """action_reset_draft remet en brouillon."""
        doc = self._create_document()
        doc.action_validate()
        doc.action_reset_draft()
        self.assertEqual(doc.state, 'draft')

    def test_23_new_version(self):
        """action_new_version crée une nouvelle version."""
        doc = self._create_document()
        doc.action_validate()
        result = doc.action_new_version()
        # Devrait créer un nouveau document ou incrémenter la version
        self.assertIsNotNone(result)

    # ─── Expiration ──────────────────────────────────────────────────

    def test_30_expired_document(self):
        """Un document avec date d'expiration passée est marqué expiré."""
        doc = self._create_document(
            expiration_date=date.today() - timedelta(days=1),
        )
        self.assertTrue(doc.is_expired)

    def test_31_not_expired_document(self):
        """Un document avec date future n'est pas expiré."""
        doc = self._create_document(
            expiration_date=date.today() + timedelta(days=30),
        )
        self.assertFalse(doc.is_expired)

    def test_32_no_expiration(self):
        """Sans date d'expiration → pas expiré."""
        doc = self._create_document()
        self.assertFalse(doc.is_expired)

    # ─── Tags ────────────────────────────────────────────────────────

    def test_35_document_tags(self):
        """On peut ajouter des tags à un document."""
        tag1 = self.env['document.tag'].create({'name': 'Confidentiel', 'color': 1})
        tag2 = self.env['document.tag'].create({'name': 'Urgent', 'color': 4})
        doc = self._create_document(tag_ids=[(6, 0, [tag1.id, tag2.id])])
        self.assertEqual(len(doc.tag_ids), 2)

    # ─── Cas négatifs ────────────────────────────────────────────────

    def test_40_document_without_name(self):
        """Impossible de créer un document sans nom."""
        with self.assertRaises(Exception):
            self.env['document.document'].create({
                'folder_id': self.folder.id,
            })


@tagged('post_install', '-at_install', 'custom_documents')
class TestDocumentTag(TransactionCase):
    """Tests du modèle tag de document."""

    def test_50_create_tag(self):
        """On peut créer un tag."""
        tag = self.env['document.tag'].create({'name': 'Important', 'color': 2})
        self.assertTrue(tag.active)

    def test_51_archive_tag(self):
        """On peut archiver un tag."""
        tag = self.env['document.tag'].create({'name': 'Obsolète'})
        tag.active = False
        self.assertFalse(tag.active)
