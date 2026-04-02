# -*- coding: utf-8 -*-
"""
Mohasib — Modèle Transaction Comptable
Chaque transaction issue de la saisie NLP génère une écriture comptable.
"""
from odoo import models, fields, api
from odoo.exceptions import UserError


class MohasibTransaction(models.Model):
    _name = 'mohasib.transaction'
    _description = 'Transaction comptable Mohasib'
    _inherit = ['mail.thread']
    _order = 'date desc, id desc'

    name = fields.Char(
        string='Référence',
        readonly=True,
        copy=False,
        default='Nouveau',
    )
    date = fields.Date(
        string='Date',
        default=fields.Date.today,
        required=True,
    )
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('confirmed', 'Confirmé'),
        ('done', 'Comptabilisé'),
        ('cancelled', 'Annulé'),
    ], string='État', default='draft', tracking=True)

    # ──────────────────── Classification ────────────────────
    type_transaction = fields.Selection([
        ('achat_materiaux', 'Achat matériaux'),
        ('achat_carburant', 'Achat carburant'),
        ('sous_traitance', 'Sous-traitance'),
        ('salaire', 'Salaire / Avance ouvrier'),
        ('location_engin', 'Location engin'),
        ('encaissement', 'Encaissement client'),
        ('facture_eau', 'Facture eau'),
        ('facture_electricite', 'Facture électricité'),
        ('frais_divers', 'Frais divers'),
    ], string='Type', required=True, tracking=True)

    categorie_chantier = fields.Selection([
        ('main_oeuvre', 'Main d\'œuvre'),
        ('materiaux', 'Matériaux'),
        ('sous_traitance', 'Sous-traitance'),
        ('materiel', 'Matériel & location'),
        ('divers', 'Frais divers'),
    ], string='Catégorie chantier',
       compute='_compute_categorie_chantier',
       store=True,
    )

    # ──────────────────── Montants ────────────────────
    montant = fields.Float(
        string='Montant TTC (DH)',
        required=True,
        tracking=True,
    )
    montant_ht = fields.Float(
        string='Montant HT (DH)',
        compute='_compute_montants_fiscaux',
        store=True,
    )
    taux_tva = fields.Float(
        string='Taux TVA (%)',
        compute='_compute_taux_tva',
        store=True,
    )
    montant_tva = fields.Float(
        string='TVA (DH)',
        compute='_compute_montants_fiscaux',
        store=True,
    )
    # Retenues BTP
    taux_retenue = fields.Float(
        string='Taux retenue à la source (%)',
        default=0,
    )
    montant_retenue = fields.Float(
        string='Retenue à la source (DH)',
        compute='_compute_montants_fiscaux',
        store=True,
    )
    montant_net = fields.Float(
        string='Net à payer (DH)',
        compute='_compute_montants_fiscaux',
        store=True,
    )

    # ──────────────────── Détails ────────────────────
    description = fields.Text(
        string='Description',
        help='Description en langage naturel de la transaction',
    )
    description_comptable = fields.Text(
        string='Libellé comptable',
    )
    # Détails article (optionnel)
    article = fields.Char(string='Article / Désignation')
    quantite = fields.Float(string='Quantité')
    prix_unitaire = fields.Float(string='Prix unitaire (DH)')

    # ──────────────────── Mode de paiement ────────────────────
    mode_paiement = fields.Selection([
        ('cash', 'Espèces (Caisse)'),
        ('banque', 'Virement bancaire'),
        ('cheque', 'Chèque'),
        ('credit', 'À crédit (fournisseur)'),
    ], string='Mode de paiement', default='cash')

    # ──────────────────── Liens ────────────────────
    chantier_id = fields.Many2one(
        'mohasib.chantier',
        string='Chantier',
        tracking=True,
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Tiers (fournisseur/client)',
    )
    move_id = fields.Many2one(
        'account.move',
        string='Écriture comptable',
        readonly=True,
    )
    conversation_id = fields.Many2one(
        'mohasib.conversation',
        string='Conversation source',
    )
    company_id = fields.Many2one(
        'res.company',
        string='Société',
        default=lambda self: self.env.company,
    )
    currency_id = fields.Many2one(
        related='company_id.currency_id',
    )

    # ──────────────────── Texte NLP original ────────────────────
    texte_original = fields.Text(
        string='Texte original (saisie directeur)',
        help='La phrase exacte que le directeur a tapée',
    )

    # ══════════════════ PCM — MAPPING DES COMPTES ══════════════════

    # Plan Comptable Marocain pour le BTP
    PCM_MAPPING = {
        'achat_materiaux': {
            'debit': '6121',       # Achats de matières premières
            'description': 'achats de matériaux',
            'tva': 20.0,
        },
        'achat_carburant': {
            'debit': '6125',       # Achats non stockés (carburant)
            'description': 'achats de carburant',
            'tva': 10.0,
        },
        'sous_traitance': {
            'debit': '6134',       # Entretien et réparations / Sous-traitance
            'description': 'sous-traitance',
            'tva': 20.0,
            'retenue': 10.0,       # RAS 10% personnes physiques
        },
        'salaire': {
            'debit': '6171',       # Rémunérations du personnel
            'description': 'salaires et avances',
            'tva': 0.0,
        },
        'location_engin': {
            'debit': '6132',       # Locations (matériel)
            'description': 'location d\'engins',
            'tva': 20.0,
            'retenue': 15.0,       # RAS 15% si particulier
        },
        'encaissement': {
            'credit': '7111',      # Ventes de marchandises / Produits
            'description': 'encaissement client',
            'tva': 20.0,
        },
        'facture_eau': {
            'debit': '61251',      # Eau
            'description': 'facture d\'eau',
            'tva': 7.0,
        },
        'facture_electricite': {
            'debit': '61252',      # Électricité
            'description': 'facture d\'électricité',
            'tva': 14.0,
        },
        'frais_divers': {
            'debit': '6185',       # Frais divers
            'description': 'frais divers',
            'tva': 20.0,
        },
    }

    CREDIT_MAPPING = {
        'cash': '5161',            # Caisse
        'banque': '5141',          # Banque
        'cheque': '5141',          # Banque (encaissement chèque)
        'credit': '4411',          # Fournisseurs
    }

    # ══════════════════ COMPUTED ══════════════════

    @api.depends('type_transaction')
    def _compute_taux_tva(self):
        for rec in self:
            mapping = self.PCM_MAPPING.get(rec.type_transaction, {})
            rec.taux_tva = mapping.get('tva', 20.0)

    @api.depends('montant', 'taux_tva', 'taux_retenue')
    def _compute_montants_fiscaux(self):
        for rec in self:
            if rec.taux_tva > 0:
                rec.montant_ht = rec.montant / (1 + rec.taux_tva / 100)
                rec.montant_tva = rec.montant - rec.montant_ht
            else:
                rec.montant_ht = rec.montant
                rec.montant_tva = 0.0
            rec.montant_retenue = rec.montant_ht * (rec.taux_retenue / 100)
            rec.montant_net = rec.montant - rec.montant_retenue

    @api.depends('type_transaction')
    def _compute_categorie_chantier(self):
        mapping = {
            'achat_materiaux': 'materiaux',
            'achat_carburant': 'divers',
            'sous_traitance': 'sous_traitance',
            'salaire': 'main_oeuvre',
            'location_engin': 'materiel',
            'facture_eau': 'divers',
            'facture_electricite': 'divers',
            'frais_divers': 'divers',
        }
        for rec in self:
            rec.categorie_chantier = mapping.get(rec.type_transaction, 'divers')

    # ══════════════════ LIFECYCLE ══════════════════

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'Nouveau') == 'Nouveau':
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'mohasib.transaction') or 'Nouveau'
        return super().create(vals_list)

    # ══════════════════ ACTIONS ══════════════════

    def action_confirm(self):
        """Confirmer la transaction — prête à comptabiliser."""
        self.write({'state': 'confirmed'})

    def action_comptabiliser(self):
        """Créer l'écriture comptable dans le journal Odoo."""
        for rec in self:
            if rec.state != 'confirmed':
                raise UserError("La transaction doit d'abord être confirmée.")
            if rec.move_id:
                raise UserError("Une écriture comptable existe déjà.")

            move = rec._create_account_move()
            rec.write({
                'move_id': move.id,
                'state': 'done',
            })

            # Créer une ligne de dépense dans le chantier
            if rec.chantier_id and rec.type_transaction != 'encaissement':
                self.env['mohasib.depense.line'].create({
                    'chantier_id': rec.chantier_id.id,
                    'date': rec.date,
                    'categorie': rec.categorie_chantier,
                    'description': rec.description_comptable or rec.description,
                    'montant': rec.montant,
                    'transaction_id': rec.id,
                    'move_id': move.id,
                })

    def action_cancel(self):
        for rec in self:
            if rec.move_id and rec.move_id.state == 'posted':
                rec.move_id.button_draft()
                rec.move_id.button_cancel()
            rec.state = 'cancelled'

    # ══════════════════ CRÉATION ÉCRITURE COMPTABLE ══════════════════

    def _create_account_move(self):
        """
        Génère l'écriture comptable PCM complète.

        Exemple pour un achat matériaux 9 600 DH TTC payé cash :
            Débit  6121  Achats matières premières  8 000 DH
            Débit  34552 TVA récupérable            1 600 DH
            Crédit 5161  Caisse                     9 600 DH
        """
        self.ensure_one()
        pcm = self.PCM_MAPPING.get(self.type_transaction, {})
        is_encaissement = self.type_transaction == 'encaissement'

        # Trouver le journal
        journal_type = 'sale' if is_encaissement else 'purchase'
        journal = self.env['account.journal'].search([
            ('type', '=', journal_type),
            ('company_id', '=', self.company_id.id),
        ], limit=1)
        if not journal:
            journal = self.env['account.journal'].search([
                ('type', '=', 'general'),
                ('company_id', '=', self.company_id.id),
            ], limit=1)

        lines = []
        label = self.description_comptable or (
            f"{pcm.get('description', self.type_transaction)} - "
            f"{self.chantier_id.name if self.chantier_id else ''}"
        )

        analytic_id = self.chantier_id.analytic_account_id.id if self.chantier_id else False
        analytic_distribution = {str(analytic_id): 100} if analytic_id else False

        if is_encaissement:
            # ── Encaissement client ──
            # Débit  Banque/Caisse
            # Crédit Produits (chiffre d'affaires)
            credit_account = self.CREDIT_MAPPING.get(self.mode_paiement, '5141')
            lines = [
                (0, 0, {
                    'name': label,
                    'debit': self.montant,
                    'credit': 0,
                    'account_id': self._find_account(
                        self.CREDIT_MAPPING.get(self.mode_paiement, '5141')),
                }),
                (0, 0, {
                    'name': label,
                    'debit': 0,
                    'credit': self.montant_ht,
                    'account_id': self._find_account(pcm.get('credit', '7111')),
                    'analytic_distribution': analytic_distribution,
                }),
            ]
            # TVA collectée
            if self.montant_tva > 0:
                lines.append((0, 0, {
                    'name': f"TVA collectée {self.taux_tva:.0f}%",
                    'debit': 0,
                    'credit': self.montant_tva,
                    'account_id': self._find_account('4455'),  # TVA facturée
                }))
        else:
            # ── Dépense / Achat ──
            # Débit  Charge (6xxx)
            # Débit  TVA récupérable (si applicable)
            # Crédit Caisse/Banque/Fournisseurs
            debit_account_code = pcm.get('debit', '6185')
            lines = [
                (0, 0, {
                    'name': label,
                    'debit': self.montant_ht,
                    'credit': 0,
                    'account_id': self._find_account(debit_account_code),
                    'analytic_distribution': analytic_distribution,
                }),
            ]
            # TVA récupérable
            if self.montant_tva > 0:
                lines.append((0, 0, {
                    'name': f"TVA récupérable {self.taux_tva:.0f}%",
                    'debit': self.montant_tva,
                    'credit': 0,
                    'account_id': self._find_account('34552'),  # TVA récupérable
                }))
            # Retenue à la source
            if self.montant_retenue > 0:
                lines.append((0, 0, {
                    'name': f"Retenue source {self.taux_retenue:.0f}%",
                    'debit': 0,
                    'credit': self.montant_retenue,
                    'account_id': self._find_account('4457'),  # État, retenues
                }))
            # Contrepartie (paiement)
            credit_account_code = self.CREDIT_MAPPING.get(
                self.mode_paiement, '5161')
            lines.append((0, 0, {
                'name': label,
                'debit': 0,
                'credit': self.montant_net,
                'account_id': self._find_account(credit_account_code),
            }))

        move = self.env['account.move'].create({
            'journal_id': journal.id,
            'date': self.date,
            'ref': self.name,
            'line_ids': lines,
        })
        return move

    def _find_account(self, code):
        """Trouver un compte dans le plan comptable par son code."""
        account = self.env['account.account'].search([
            ('code', '=like', code + '%'),
            ('company_id', '=', self.company_id.id),
        ], limit=1)
        if not account:
            # Fallback : chercher le compte le plus proche
            account = self.env['account.account'].search([
                ('code', '=like', code[:3] + '%'),
                ('company_id', '=', self.company_id.id),
            ], limit=1)
        if not account:
            # Dernier fallback : compte divers
            account = self.env['account.account'].search([
                ('company_id', '=', self.company_id.id),
            ], limit=1)
        return account.id

    # ══════════════════ RÉSUMÉ TEXTE ══════════════════

    def get_resume_simple(self):
        """Résumé en langage naturel pour le directeur."""
        self.ensure_one()
        pcm = self.PCM_MAPPING.get(self.type_transaction, {})
        desc = pcm.get('description', self.type_transaction)

        if self.type_transaction == 'encaissement':
            msg = (
                f"✅ J'ai enregistré un encaissement de {self.montant:,.0f} DH "
                f"du client pour le chantier {self.chantier_id.name or '—'}."
            )
        else:
            msg = (
                f"✅ J'ai enregistré {self.montant:,.0f} DH de {desc} "
                f"sur le chantier {self.chantier_id.name or '—'}."
            )
            if self.montant_tva > 0:
                msg += f"\n   TVA récupérable : {self.montant_tva:,.0f} DH ({self.taux_tva:.0f}%)."
            if self.montant_retenue > 0:
                msg += (
                    f"\n   Retenue à la source : {self.montant_retenue:,.0f} DH "
                    f"({self.taux_retenue:.0f}%)."
                )
            paiement_labels = {
                'cash': 'espèces (caisse)',
                'banque': 'virement bancaire',
                'cheque': 'chèque',
                'credit': 'à crédit fournisseur',
            }
            msg += f"\n   Payé par : {paiement_labels.get(self.mode_paiement, self.mode_paiement)}."
        return msg
