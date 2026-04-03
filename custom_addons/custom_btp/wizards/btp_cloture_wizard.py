# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError


class BtpClotureWizard(models.TransientModel):
    """Wizard — Clôture de chantier avec vérifications complètes"""
    _name = 'btp.cloture.wizard'
    _description = 'Clôture de Chantier'

    # ── Champs ─────────────────────────────────────────────────
    chantier_id = fields.Many2one(
        'btp.chantier', string='Chantier', required=True,
        default=lambda self: self.env.context.get('active_id'),
    )
    date_cloture = fields.Date('Date de clôture', required=True, default=fields.Date.today)
    
    # Vérifications (computed)
    documents_complets = fields.Boolean('Documents complets', compute='_compute_verifications')
    reserves_levees = fields.Boolean('Réserves levées', compute='_compute_verifications')
    reception_definitive = fields.Boolean('Réception définitive effectuée', compute='_compute_verifications')
    situations_validees = fields.Boolean('Situations toutes validées', compute='_compute_verifications')
    retenue_restituable = fields.Float('Retenue restituable (DH)', compute='_compute_verifications')
    
    notes_verification = fields.Text('Détail des vérifications', compute='_compute_verifications')
    restituer_retenue = fields.Boolean('Restituer la retenue de garantie', default=True)
    forcer_cloture = fields.Boolean(
        'Forcer la clôture malgré les anomalies',
        help="À utiliser uniquement par le directeur en cas de besoin",
    )

    # ── Compute ────────────────────────────────────────────────
    @api.depends('chantier_id')
    def _compute_verifications(self):
        for wiz in self:
            chantier = wiz.chantier_id
            notes = []

            # 1. Documents obligatoires
            docs_obligatoires = chantier.document_ids.filtered(lambda d: d.obligatoire)
            docs_manquants = docs_obligatoires.filtered(lambda d: not d.fichier)
            wiz.documents_complets = len(docs_manquants) == 0
            if docs_manquants:
                notes.append("⚠ Documents manquants : %s" % ', '.join(docs_manquants.mapped('name')))
            else:
                notes.append("✓ Tous les documents obligatoires sont présents")

            # 2. Réserves
            reserves_ouvertes = self.env['btp.reserve'].search([
                ('reception_id.chantier_id', '=', chantier.id),
                ('state', '!=', 'levee'),
            ])
            wiz.reserves_levees = len(reserves_ouvertes) == 0
            if reserves_ouvertes:
                notes.append("⚠ %d réserve(s) non levée(s)" % len(reserves_ouvertes))
            else:
                notes.append("✓ Toutes les réserves sont levées")

            # 3. Réception définitive
            reception_def = self.env['btp.reception'].search([
                ('chantier_id', '=', chantier.id),
                ('type', '=', 'definitive'),
            ], limit=1)
            wiz.reception_definitive = bool(reception_def)
            if not reception_def:
                notes.append("⚠ Aucune réception définitive validée")
            else:
                notes.append("✓ Réception définitive effectuée le %s" % reception_def.date)

            # 4. Situations
            situations_brouillon = self.env['btp.situation'].search([
                ('chantier_id', '=', chantier.id),
                ('state', '=', 'brouillon'),
            ])
            wiz.situations_validees = len(situations_brouillon) == 0
            if situations_brouillon:
                notes.append("⚠ %d situation(s) en brouillon" % len(situations_brouillon))
            else:
                notes.append("✓ Toutes les situations sont validées")

            # 5. Retenue de garantie
            total_retenue = sum(
                self.env['btp.situation'].search([
                    ('chantier_id', '=', chantier.id),
                    ('state', '=', 'valide'),
                ]).mapped('montant_retenue_garantie')
            )
            wiz.retenue_restituable = total_retenue
            notes.append("💰 Retenue de garantie restituable : %.2f DH" % total_retenue)

            wiz.notes_verification = '\n'.join(notes)

    # ── Actions ────────────────────────────────────────────────
    def action_cloturer(self):
        """Clôturer le chantier après vérifications"""
        self.ensure_one()
        chantier = self.chantier_id

        # Vérifications
        erreurs = []
        if not self.documents_complets and not self.forcer_cloture:
            erreurs.append("Documents obligatoires manquants")
        if not self.reserves_levees and not self.forcer_cloture:
            erreurs.append("Réserves non levées")
        if not self.reception_definitive and not self.forcer_cloture:
            erreurs.append("Réception définitive non effectuée")
        if not self.situations_validees and not self.forcer_cloture:
            erreurs.append("Situations en brouillon")

        if erreurs:
            raise UserError(
                "Impossible de clôturer le chantier :\n\n• " +
                "\n• ".join(erreurs) +
                "\n\nCochez 'Forcer la clôture' pour passer outre."
            )

        # Clôture
        chantier.write({
            'state': 'cloture',
            'date_fin_reel': self.date_cloture,
        })

        # Log
        body = "<p><strong>Clôture du chantier</strong></p>"
        body += "<ul>"
        for line in (self.notes_verification or '').split('\n'):
            body += "<li>%s</li>" % line
        if self.restituer_retenue:
            body += "<li>Retenue de garantie de %.2f DH à restituer</li>" % self.retenue_restituable
        if self.forcer_cloture:
            body += "<li><strong>⚠ Clôture forcée par %s</strong></li>" % self.env.user.name
        body += "</ul>"
        chantier.message_post(body=body)

        return {'type': 'ir.actions.act_window_close'}
