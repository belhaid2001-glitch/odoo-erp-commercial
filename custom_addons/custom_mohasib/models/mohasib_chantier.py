# -*- coding: utf-8 -*-
"""
Mohasib — Modèle Chantier BTP
Centre analytique avec budget, dépenses, encaissements et marge.
"""
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class MohasibChantier(models.Model):
    _name = 'mohasib.chantier'
    _description = 'Chantier BTP'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_debut desc'

    # ──────────────────── Identité ────────────────────
    name = fields.Char(
        string='Nom du chantier',
        required=True,
        tracking=True,
    )
    reference = fields.Char(
        string='Référence marché',
        copy=False,
    )
    code = fields.Char(
        string='Code analytique',
        copy=False,
        readonly=True,
    )
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('in_progress', 'En cours'),
        ('suspended', 'Suspendu'),
        ('done', 'Terminé'),
        ('cancelled', 'Annulé'),
    ], string='État', default='draft', tracking=True)

    # ──────────────────── Client & Localisation ────────────────────
    partner_id = fields.Many2one(
        'res.partner',
        string='Client (Maître d\'ouvrage)',
        tracking=True,
    )
    ville = fields.Char(string='Ville')
    adresse = fields.Text(string='Adresse du chantier')

    # ──────────────────── Dates ────────────────────
    date_debut = fields.Date(string='Date début', tracking=True)
    date_fin_prevue = fields.Date(string='Date fin prévue')
    date_fin_reelle = fields.Date(string='Date fin réelle')

    # ──────────────────── Budget ────────────────────
    montant_marche = fields.Float(
        string='Montant du marché (TTC)',
        tracking=True,
        help='Montant total du marché signé avec le client',
    )
    montant_marche_ht = fields.Float(
        string='Montant du marché (HT)',
        compute='_compute_montant_ht',
        store=True,
    )
    taux_tva = fields.Float(
        string='Taux TVA (%)',
        default=20.0,
    )
    budget_main_oeuvre = fields.Float(string='Budget main d\'œuvre')
    budget_materiaux = fields.Float(string='Budget matériaux')
    budget_sous_traitance = fields.Float(string='Budget sous-traitance')
    budget_materiel = fields.Float(string='Budget matériel & location')
    budget_divers = fields.Float(string='Budget frais divers')
    budget_total = fields.Float(
        string='Budget total prévu',
        compute='_compute_budget_total',
        store=True,
    )

    # ──────────────────── Dépenses réelles (Computed) ────────────────────
    depense_main_oeuvre = fields.Float(
        string='Dépensé — Main d\'œuvre',
        compute='_compute_depenses',
        store=True,
    )
    depense_materiaux = fields.Float(
        string='Dépensé — Matériaux',
        compute='_compute_depenses',
        store=True,
    )
    depense_sous_traitance = fields.Float(
        string='Dépensé — Sous-traitance',
        compute='_compute_depenses',
        store=True,
    )
    depense_materiel = fields.Float(
        string='Dépensé — Matériel & location',
        compute='_compute_depenses',
        store=True,
    )
    depense_divers = fields.Float(
        string='Dépensé — Frais divers',
        compute='_compute_depenses',
        store=True,
    )
    depense_totale = fields.Float(
        string='Total dépensé',
        compute='_compute_depenses',
        store=True,
    )
    depense_ids = fields.One2many(
        'mohasib.depense.line',
        'chantier_id',
        string='Lignes de dépenses',
    )

    # ──────────────────── Encaissements ────────────────────
    total_encaisse = fields.Float(
        string='Total encaissé',
        compute='_compute_encaissements',
        store=True,
    )
    reste_a_facturer = fields.Float(
        string='Reste à facturer',
        compute='_compute_encaissements',
        store=True,
    )
    reste_a_encaisser = fields.Float(
        string='Reste à encaisser',
        compute='_compute_encaissements',
        store=True,
    )
    transaction_ids = fields.One2many(
        'mohasib.transaction',
        'chantier_id',
        string='Transactions',
    )

    # ──────────────────── KPI ────────────────────
    taux_avancement = fields.Float(
        string='Taux d\'avancement (%)',
        compute='_compute_kpi',
        store=True,
    )
    marge_brute = fields.Float(
        string='Marge brute estimée (DH)',
        compute='_compute_kpi',
        store=True,
    )
    taux_marge = fields.Float(
        string='Taux de marge (%)',
        compute='_compute_kpi',
        store=True,
    )
    alerte_depassement = fields.Text(
        string='Alertes dépassement',
        compute='_compute_kpi',
    )

    # ──────────────────── Lien comptable ────────────────────
    analytic_account_id = fields.Many2one(
        'account.analytic.account',
        string='Compte analytique',
        help='Compte analytique Odoo lié à ce chantier',
    )
    company_id = fields.Many2one(
        'res.company',
        string='Société',
        default=lambda self: self.env.company,
    )
    currency_id = fields.Many2one(
        related='company_id.currency_id',
    )
    notes = fields.Html(string='Notes')

    # ══════════════════ COMPUTED ══════════════════

    @api.depends('montant_marche', 'taux_tva')
    def _compute_montant_ht(self):
        for rec in self:
            if rec.taux_tva:
                rec.montant_marche_ht = rec.montant_marche / (1 + rec.taux_tva / 100)
            else:
                rec.montant_marche_ht = rec.montant_marche

    @api.depends('budget_main_oeuvre', 'budget_materiaux',
                 'budget_sous_traitance', 'budget_materiel', 'budget_divers')
    def _compute_budget_total(self):
        for rec in self:
            rec.budget_total = (
                rec.budget_main_oeuvre + rec.budget_materiaux +
                rec.budget_sous_traitance + rec.budget_materiel +
                rec.budget_divers
            )

    @api.depends('depense_ids', 'depense_ids.montant', 'depense_ids.categorie')
    def _compute_depenses(self):
        for rec in self:
            lines = rec.depense_ids
            rec.depense_main_oeuvre = sum(
                l.montant for l in lines if l.categorie == 'main_oeuvre')
            rec.depense_materiaux = sum(
                l.montant for l in lines if l.categorie == 'materiaux')
            rec.depense_sous_traitance = sum(
                l.montant for l in lines if l.categorie == 'sous_traitance')
            rec.depense_materiel = sum(
                l.montant for l in lines if l.categorie == 'materiel')
            rec.depense_divers = sum(
                l.montant for l in lines if l.categorie == 'divers')
            rec.depense_totale = sum(l.montant for l in lines)

    @api.depends('transaction_ids', 'transaction_ids.montant',
                 'transaction_ids.type_transaction', 'montant_marche')
    def _compute_encaissements(self):
        for rec in self:
            encaissements = rec.transaction_ids.filtered(
                lambda t: t.type_transaction == 'encaissement' and t.state == 'done'
            )
            facture = rec.transaction_ids.filtered(
                lambda t: t.type_transaction == 'encaissement'
            )
            rec.total_encaisse = sum(e.montant for e in encaissements)
            total_facture = sum(f.montant for f in facture)
            rec.reste_a_facturer = max(0, rec.montant_marche - total_facture)
            rec.reste_a_encaisser = total_facture - rec.total_encaisse

    @api.depends('montant_marche_ht', 'depense_totale',
                 'budget_total', 'budget_main_oeuvre', 'budget_materiaux',
                 'budget_sous_traitance', 'budget_materiel', 'budget_divers',
                 'depense_main_oeuvre', 'depense_materiaux',
                 'depense_sous_traitance', 'depense_materiel', 'depense_divers')
    def _compute_kpi(self):
        for rec in self:
            # Taux d'avancement
            if rec.budget_total > 0:
                rec.taux_avancement = min(100, (rec.depense_totale / rec.budget_total) * 100)
            else:
                rec.taux_avancement = 0

            # Marge brute
            rec.marge_brute = rec.montant_marche_ht - rec.depense_totale
            if rec.montant_marche_ht > 0:
                rec.taux_marge = (rec.marge_brute / rec.montant_marche_ht) * 100
            else:
                rec.taux_marge = 0

            # Alertes dépassement par catégorie
            alertes = []
            checks = [
                ('Main d\'œuvre', rec.depense_main_oeuvre, rec.budget_main_oeuvre),
                ('Matériaux', rec.depense_materiaux, rec.budget_materiaux),
                ('Sous-traitance', rec.depense_sous_traitance, rec.budget_sous_traitance),
                ('Matériel', rec.depense_materiel, rec.budget_materiel),
                ('Divers', rec.depense_divers, rec.budget_divers),
            ]
            for label, depense, budget in checks:
                if budget > 0 and depense > budget:
                    pct = ((depense - budget) / budget) * 100
                    alertes.append(
                        f"⚠️ {label} dépasse le budget de {pct:.0f}% "
                        f"({depense:,.0f} / {budget:,.0f} DH)"
                    )
            rec.alerte_depassement = '\n'.join(alertes) if alertes else ''

    # ══════════════════ ACTIONS ══════════════════

    def action_start(self):
        """Démarrer le chantier — crée le compte analytique"""
        for rec in self:
            if not rec.analytic_account_id:
                plan = self.env['account.analytic.plan'].search([], limit=1)
                analytic = self.env['account.analytic.account'].create({
                    'name': f"CHANTIER - {rec.name}",
                    'plan_id': plan.id if plan else False,
                    'company_id': rec.company_id.id,
                })
                rec.analytic_account_id = analytic.id
            if not rec.code:
                rec.code = self.env['ir.sequence'].next_by_code('mohasib.chantier')
            rec.state = 'in_progress'

    def action_suspend(self):
        self.write({'state': 'suspended'})

    def action_resume(self):
        self.write({'state': 'in_progress'})

    def action_done(self):
        self.write({
            'state': 'done',
            'date_fin_reelle': fields.Date.today(),
        })

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    # ══════════════════ RAPPORT TEXTE ══════════════════

    def get_rapport_simple(self):
        """Génère un rapport texte comme le ferait Mohasib."""
        self.ensure_one()
        r = self
        rapport = (
            f"📊 Chantier {r.name}\n"
            f"   Marché : {r.montant_marche:,.0f} DH TTC\n"
            f"   Dépensé à ce jour : {r.depense_totale:,.0f} DH "
            f"({r.taux_avancement:.0f}%)\n"
            f"   Encaissé : {r.total_encaisse:,.0f} DH\n"
            f"   Marge estimée : {r.taux_marge:.0f}%\n"
        )
        if r.alerte_depassement:
            rapport += f"\n{r.alerte_depassement}"
        return rapport


class MohasibDepenseLine(models.Model):
    """Ligne de dépense unitaire rattachée à un chantier."""
    _name = 'mohasib.depense.line'
    _description = 'Ligne de dépense chantier'
    _order = 'date desc'

    chantier_id = fields.Many2one(
        'mohasib.chantier',
        string='Chantier',
        required=True,
        ondelete='cascade',
    )
    date = fields.Date(
        string='Date',
        default=fields.Date.today,
        required=True,
    )
    categorie = fields.Selection([
        ('main_oeuvre', 'Main d\'œuvre'),
        ('materiaux', 'Matériaux'),
        ('sous_traitance', 'Sous-traitance'),
        ('materiel', 'Matériel & location'),
        ('divers', 'Frais divers'),
    ], string='Catégorie', required=True)
    description = fields.Char(string='Description')
    montant = fields.Float(string='Montant (DH)', required=True)
    transaction_id = fields.Many2one(
        'mohasib.transaction',
        string='Transaction liée',
    )
    move_id = fields.Many2one(
        'account.move',
        string='Écriture comptable',
    )
