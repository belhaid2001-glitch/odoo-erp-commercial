# -*- coding: utf-8 -*-
"""
Mohasib — Wizard de Saisie Guidée
Interface conversationnelle : le directeur tape en langage naturel,
Mohasib parse et propose une écriture comptable à confirmer.
"""
import json
from odoo import models, fields, api
from odoo.exceptions import UserError


class MohasibSaisieWizard(models.TransientModel):
    _name = 'mohasib.saisie.wizard'
    _description = 'Saisie guidée Mohasib'

    # ──────────────────── Conversation ────────────────────
    conversation_id = fields.Many2one(
        'mohasib.conversation',
        string='Conversation',
    )
    chantier_id = fields.Many2one(
        'mohasib.chantier',
        string='Chantier par défaut',
        help='Si vous ne précisez pas le chantier dans votre phrase, celui-ci sera utilisé.',
    )

    # ──────────────────── Saisie ────────────────────
    user_input = fields.Text(
        string='Votre message',
        help='Décrivez votre opération en langage naturel',
    )

    # ──────────────────── Résultat du parsing ────────────────────
    response_html = fields.Html(
        string='Réponse de Mohasib',
        readonly=True,
    )
    parsed_json = fields.Text(
        string='Données parsées (JSON)',
        readonly=True,
    )

    # ──────────────────── Champs éditables (correction) ────────────────────
    type_transaction = fields.Selection([
        ('achat_materiaux', 'Achat matériaux'),
        ('achat_carburant', 'Achat carburant'),
        ('sous_traitance', 'Sous-traitance'),
        ('salaire', 'Salaire / Avance'),
        ('location_engin', 'Location engin'),
        ('encaissement', 'Encaissement client'),
        ('facture_eau', 'Facture eau'),
        ('facture_electricite', 'Facture électricité'),
        ('frais_divers', 'Frais divers'),
    ], string='Type de transaction')

    montant = fields.Float(string='Montant (DH)')
    article = fields.Char(string='Article / Désignation')
    quantite = fields.Float(string='Quantité')
    prix_unitaire = fields.Float(string='Prix unitaire')
    mode_paiement = fields.Selection([
        ('cash', 'Espèces (Caisse)'),
        ('banque', 'Virement bancaire'),
        ('cheque', 'Chèque'),
        ('credit', 'À crédit'),
    ], string='Mode de paiement', default='cash')

    chantier_parsed_id = fields.Many2one(
        'mohasib.chantier',
        string='Chantier détecté',
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Tiers (fournisseur/client)',
    )
    date_transaction = fields.Date(
        string='Date',
        default=fields.Date.today,
    )

    state = fields.Selection([
        ('input', 'Saisie'),
        ('preview', 'Aperçu'),
        ('done', 'Terminé'),
    ], default='input')

    last_transaction_id = fields.Many2one(
        'mohasib.transaction',
        string='Dernière transaction',
        readonly=True,
    )

    # ──────────────────── Messages historique ────────────────────
    chat_history_html = fields.Html(
        string='Historique',
        readonly=True,
        compute='_compute_chat_history',
    )

    @api.depends('conversation_id', 'conversation_id.chat_message_ids')
    def _compute_chat_history(self):
        for rec in self:
            if not rec.conversation_id:
                rec.chat_history_html = self._get_welcome_html()
                continue
            html_parts = []
            for msg in rec.conversation_id.chat_message_ids.sorted('create_date'):
                if msg.role == 'user':
                    html_parts.append(
                        f'<div class="mohasib-bubble mohasib-user">'
                        f'<strong>🧑 Vous :</strong> {msg.content}'
                        f'</div>'
                    )
                elif msg.role == 'assistant':
                    content = msg.content.replace('\n', '<br/>')
                    html_parts.append(
                        f'<div class="mohasib-bubble mohasib-assistant">'
                        f'<strong>🤖 Mohasib :</strong><br/>{content}'
                        f'</div>'
                    )
            rec.chat_history_html = ''.join(html_parts) or self._get_welcome_html()

    @api.model
    def _get_welcome_html(self):
        return """
        <div class="mohasib-welcome">
            <h3>🤖 Bienvenue, je suis <strong>Mohasib</strong> — محاسب</h3>
            <p>Votre expert-comptable IA spécialisé BTP Maroc.</p>
            <p>Décrivez vos opérations en français ou darija, je m'occupe de la comptabilité :</p>
            <ul>
                <li>💬 "J'ai acheté 200 sacs de ciment à 48 DH pour chantier Hay Riad, payé cash"</li>
                <li>💬 "Reçu 50 000 DH acompte client, chantier Tanger, par virement"</li>
                <li>💬 "Payé maallem Ahmed 15 000 DH travaux plomberie"</li>
                <li>💬 "Location pelleteuse 3 jours × 5 000 DH, chantier Casa"</li>
            </ul>
        </div>
        """

    # ══════════════════ ACTIONS ══════════════════

    def action_send(self):
        """Envoyer le message au moteur NLP."""
        self.ensure_one()
        if not self.user_input:
            raise UserError("Veuillez écrire quelque chose !")

        # Créer la conversation si première fois
        if not self.conversation_id:
            self.conversation_id = self.env['mohasib.conversation'].create({
                'chantier_id': self.chantier_id.id if self.chantier_id else False,
            })

        # Enregistrer le message utilisateur
        self.env['mohasib.message'].create({
            'conversation_id': self.conversation_id.id,
            'role': 'user',
            'content': self.user_input,
        })

        # Parser avec le moteur NLP
        engine = self.env['mohasib.nlp.engine']
        result = engine.parse(
            self.user_input,
            chantier_id=self.chantier_id.id if self.chantier_id else False,
        )

        # Enregistrer la réponse de Mohasib
        self.env['mohasib.message'].create({
            'conversation_id': self.conversation_id.id,
            'role': 'assistant',
            'content': result.get('message', ''),
            'parsed_data': json.dumps(result, ensure_ascii=False, default=str),
        })

        # Remplir les champs éditables
        if result.get('success'):
            self.write({
                'type_transaction': result.get('type_transaction'),
                'montant': result.get('montant', 0),
                'article': result.get('article', ''),
                'quantite': result.get('quantite', 0),
                'prix_unitaire': result.get('prix_unitaire', 0),
                'mode_paiement': result.get('mode_paiement', 'cash'),
                'chantier_parsed_id': result.get('chantier_id') or (
                    self.chantier_id.id if self.chantier_id else False),
                'parsed_json': json.dumps(result, ensure_ascii=False, default=str),
                'response_html': self._format_response_html(result),
                'state': 'preview',
                'user_input': False,  # Vider le champ de saisie
            })
        else:
            self.write({
                'response_html': self._format_response_html(result),
                'state': 'input',
                'user_input': False,
            })

        return self._reopen()

    def action_confirm(self):
        """Confirmer et créer la transaction comptable."""
        self.ensure_one()
        if not self.type_transaction or not self.montant:
            raise UserError("Le type et le montant sont obligatoires.")

        # Créer ou trouver le chantier
        chantier = self.chantier_parsed_id or self.chantier_id
        if not chantier:
            parsed = json.loads(self.parsed_json or '{}')
            chantier_name = parsed.get('chantier_name', '')
            if chantier_name:
                chantier = self.env['mohasib.chantier'].create({
                    'name': chantier_name,
                    'state': 'in_progress',
                })

        # Créer la transaction
        transaction = self.env['mohasib.transaction'].create({
            'type_transaction': self.type_transaction,
            'montant': self.montant,
            'description': self.user_input or '',
            'article': self.article or '',
            'quantite': self.quantite,
            'prix_unitaire': self.prix_unitaire,
            'mode_paiement': self.mode_paiement,
            'chantier_id': chantier.id if chantier else False,
            'partner_id': self.partner_id.id if self.partner_id else False,
            'date': self.date_transaction,
            'conversation_id': self.conversation_id.id if self.conversation_id else False,
            'texte_original': self.user_input or '',
        })

        # Confirmer et comptabiliser automatiquement
        transaction.action_confirm()
        try:
            transaction.action_comptabiliser()
            status_msg = transaction.get_resume_simple()
        except Exception as e:
            status_msg = (
                f"✅ Transaction {transaction.name} créée avec succès !\n"
                f"⚠️ L'écriture comptable sera créée manuellement : {str(e)}"
            )

        # Enregistrer la confirmation
        if self.conversation_id:
            self.env['mohasib.message'].create({
                'conversation_id': self.conversation_id.id,
                'role': 'assistant',
                'content': status_msg,
                'transaction_id': transaction.id,
            })

        # Ajouter lien de téléchargement dans le message
        download_link = (
            f'<br/><br/>'
            f'<a href="/report/pdf/custom_mohasib.report_mohasib_transaction/{transaction.id}" '
            f'target="_blank" class="btn btn-sm btn-primary" '
            f'style="margin-top: 8px;">'
            f'📥 Télécharger la pièce comptable (PDF)</a>'
        )

        self.write({
            'response_html': f'<div class="mohasib-success">{status_msg.replace(chr(10), "<br/>")}{download_link}</div>',
            'state': 'input',
            'user_input': False,
            'type_transaction': False,
            'montant': 0,
            'article': '',
            'quantite': 0,
            'prix_unitaire': 0,
            'last_transaction_id': transaction.id,
        })

        return self._reopen()

    def action_download_piece(self):
        """Télécharger la pièce comptable PDF de la dernière transaction."""
        self.ensure_one()
        if not self.last_transaction_id:
            raise UserError("Aucune transaction à télécharger.")
        return self.env.ref(
            'custom_mohasib.action_report_mohasib_transaction'
        ).report_action(self.last_transaction_id)

    def action_cancel_entry(self):
        """Annuler la saisie en cours et revenir à l'entrée."""
        self.write({
            'state': 'input',
            'user_input': False,
            'type_transaction': False,
            'montant': 0,
        })
        if self.conversation_id:
            self.env['mohasib.message'].create({
                'conversation_id': self.conversation_id.id,
                'role': 'assistant',
                'content': '❌ Saisie annulée. Vous pouvez recommencer.',
            })
        return self._reopen()

    def action_new_conversation(self):
        """Démarrer une nouvelle conversation."""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Mohasib — Nouvelle conversation',
            'res_model': 'mohasib.saisie.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_chantier_id': self.chantier_id.id if self.chantier_id else False,
            },
        }

    # ══════════════════ HELPERS ══════════════════

    def _reopen(self):
        """Réouvrir le wizard en gardant l'état."""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Mohasib — Saisie guidée',
            'res_model': 'mohasib.saisie.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    @api.model
    def _format_response_html(self, result):
        """Formater la réponse en HTML."""
        msg = result.get('message', '')
        # Convertir le markdown simplifié en HTML
        html = msg.replace('\n', '<br/>')
        html = html.replace('**', '<strong>', 1)
        for _ in range(10):
            html = html.replace('**', '</strong>', 1).replace('**', '<strong>', 1)

        confidence = result.get('confidence', 0)
        if confidence >= 0.8:
            badge = '<span class="badge bg-success">Confiance élevée</span>'
        elif confidence >= 0.5:
            badge = '<span class="badge bg-warning">Confiance moyenne</span>'
        else:
            badge = '<span class="badge bg-danger">Confiance faible</span>'

        return f'<div class="mohasib-response">{html}<br/>{badge}</div>'
