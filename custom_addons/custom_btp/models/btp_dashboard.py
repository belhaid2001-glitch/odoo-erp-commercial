# -*- coding: utf-8 -*-
"""
Dashboard BTP — Méthode de récupération des KPI pour le tableau de bord OWL.
"""

from odoo import models, api, fields
from datetime import date, timedelta
from collections import defaultdict


class BtpChantierDashboard(models.Model):
    _inherit = 'btp.chantier'

    @api.model
    def get_btp_dashboard_data(self):
        """Retourne toutes les données nécessaires au dashboard BTP."""
        today = date.today()
        Chantier = self.env['btp.chantier']
        Pointage = self.env['btp.pointage']
        Engin = self.env['btp.engin']
        Situation = self.env['btp.situation']
        Approvisionnement = self.env['btp.approvisionnement']
        Document = self.env['btp.document']
        Ressource = self.env['btp.ressource']

        # ── Chantiers par état ──
        all_chantiers = Chantier.search([])
        states_count = defaultdict(int)
        for c in all_chantiers:
            states_count[c.state] += 1

        state_labels = dict(self._fields['state'].selection)

        chantiers_en_cours = Chantier.search([('state', 'in', ('en_cours', 'reprise'))])
        chantiers_retard = chantiers_en_cours.filtered(lambda c: c.retard_jours > 0)
        chantiers_etude = Chantier.search([('state', 'in', ('etude', 'appel_offres', 'attribue', 'ordre_service'))])
        chantiers_termines = Chantier.search([('state', 'in', ('reception_prov', 'levee_reserves', 'reception_def', 'cloture'))])

        # ── Montants ──
        montant_total_contrats = sum(all_chantiers.mapped('montant_total'))
        montant_en_cours = sum(chantiers_en_cours.mapped('montant_total'))
        penalites_total = sum(chantiers_en_cours.mapped('penalite_retard'))
        retenues_total = sum(all_chantiers.mapped('montant_retenue'))

        # ── Avancement moyen ──
        avancement_moyen = 0
        if chantiers_en_cours:
            avancement_moyen = round(sum(chantiers_en_cours.mapped('taux_avancement')) / len(chantiers_en_cours), 1)

        # ── Situations financières ──
        situations_brouillon = Situation.search_count([('state', '=', 'brouillon')])
        situations_valide = Situation.search_count([('state', '=', 'valide')])
        situations_impayees = Situation.search_count([('state', '=', 'facture')])
        montant_situations_impayees = sum(
            Situation.search([('state', '=', 'facture')]).mapped('montant_cumule')
        )

        # ── Pointages du jour ──
        pointages_today = Pointage.search_count([('date', '=', today)])

        # ── Ressources ──
        total_ressources = Ressource.search_count([])

        # ── Engins ──
        engins_total = Engin.search_count([])
        engins_disponibles = Engin.search_count([('state', '=', 'disponible')])
        engins_en_service = Engin.search_count([('state', '=', 'en_service')])
        engins_panne = Engin.search_count([('state', '=', 'en_panne')])

        # ── Approvisionnements urgents ──
        appro_attente = Approvisionnement.search_count([('state', '=', 'demande')])
        appro_urgents = Approvisionnement.search_count([('state', '=', 'demande'), ('urgence', '=', True)])

        # ── Documents expirés ou proches ──
        docs_expires = Document.search_count([
            ('date_expiration', '<=', fields.Date.to_string(today)),
            ('date_expiration', '!=', False),
        ])
        docs_bientot = Document.search_count([
            ('date_expiration', '>', fields.Date.to_string(today)),
            ('date_expiration', '<=', fields.Date.to_string(today + timedelta(days=30))),
        ])

        # ── Chantiers en retard (liste détaillée) ──
        alertes = []
        for c in chantiers_retard:
            alertes.append({
                'id': c.id,
                'name': c.name,
                'reference': c.reference,
                'retard_jours': c.retard_jours,
                'penalite': c.penalite_retard,
                'taux_avancement': c.taux_avancement,
                'responsable': c.responsable_id.name or '',
            })
        alertes.sort(key=lambda x: x['retard_jours'], reverse=True)

        # ── Top chantiers par montant ──
        top_chantiers = []
        for c in chantiers_en_cours.sorted(key=lambda x: x.montant_total, reverse=True)[:8]:
            top_chantiers.append({
                'id': c.id,
                'name': c.name,
                'reference': c.reference,
                'montant_total': c.montant_total,
                'taux_avancement': c.taux_avancement,
                'retard_jours': c.retard_jours,
                'state': c.state,
                'responsable': c.responsable_id.name or '',
                'ville': c.ville or '',
            })

        # ── Répartition par ville ──
        villes = defaultdict(int)
        for c in chantiers_en_cours:
            villes[c.ville or 'Non définie'] += 1
        villes_data = [{'ville': k, 'count': v} for k, v in sorted(villes.items(), key=lambda x: x[1], reverse=True)]

        # ── Répartition par type de marché ──
        types_marche = defaultdict(int)
        for c in all_chantiers:
            types_marche[c.type_marche] += 1
        type_labels = {'prive': 'Privé', 'public': 'Public', 'bon_commande': 'Bon de commande'}

        # ── Avancement par chantier (pour graphique) ──
        chart_avancements = []
        for c in chantiers_en_cours.sorted(key=lambda x: x.taux_avancement, reverse=True)[:10]:
            chart_avancements.append({
                'name': c.name[:25] + ('...' if len(c.name) > 25 else ''),
                'avancement': c.taux_avancement,
                'retard': c.retard_jours,
            })

        return {
            'today': today.strftime('%d/%m/%Y'),
            'kpis': {
                'total_chantiers': len(all_chantiers),
                'chantiers_en_cours': len(chantiers_en_cours),
                'chantiers_retard': len(chantiers_retard),
                'chantiers_etude': len(chantiers_etude),
                'chantiers_termines': len(chantiers_termines),
                'avancement_moyen': avancement_moyen,
                'montant_total_contrats': montant_total_contrats,
                'montant_en_cours': montant_en_cours,
                'penalites_total': penalites_total,
                'retenues_total': retenues_total,
                'pointages_today': pointages_today,
                'total_ressources': total_ressources,
                'engins_total': engins_total,
                'engins_disponibles': engins_disponibles,
                'engins_en_service': engins_en_service,
                'engins_panne': engins_panne,
                'appro_attente': appro_attente,
                'appro_urgents': appro_urgents,
                'situations_brouillon': situations_brouillon,
                'situations_valide': situations_valide,
                'situations_impayees': situations_impayees,
                'montant_situations_impayees': montant_situations_impayees,
                'docs_expires': docs_expires,
                'docs_bientot': docs_bientot,
            },
            'alertes': alertes[:10],
            'top_chantiers': top_chantiers,
            'villes_data': villes_data,
            'types_marche': [
                {'type': type_labels.get(k, k), 'count': v}
                for k, v in types_marche.items()
            ],
            'chart_avancements': chart_avancements,
            'states_chart': [
                {'state': state_labels.get(k, k), 'count': v}
                for k, v in states_count.items()
            ],
        }
