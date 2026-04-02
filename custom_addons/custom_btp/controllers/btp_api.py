# -*- coding: utf-8 -*-

import json
import base64
import logging
from datetime import datetime

from odoo import http, fields
from odoo.http import request, Response

_logger = logging.getLogger(__name__)


class BtpApiController(http.Controller):
    """API REST pour le module BTP — Pointage mobile & Dashboard"""

    # ── Helpers ────────────────────────────────────────────────
    def _check_auth(self):
        """Vérifie le token d'authentification dans le header"""
        token = request.httprequest.headers.get('X-BTP-Token')
        if not token:
            return None
        # Rechercher le token dans les paramètres système
        param = request.env['ir.config_parameter'].sudo().get_param('btp.api_token')
        if not param or token != param:
            return None
        return True

    def _json_response(self, data, status=200):
        """Retourne une réponse JSON formatée"""
        return Response(
            json.dumps(data, default=str, ensure_ascii=False),
            content_type='application/json',
            status=status,
        )

    # ── POST /api/btp/pointage ─────────────────────────────────
    @http.route('/api/btp/pointage', type='json', auth='public', methods=['POST'], csrf=False)
    def api_pointage(self, **kwargs):
        """
        Enregistrer un pointage depuis l'application mobile.
        
        Body JSON attendu:
        {
            "employee_id": 1,        // ID ressource BTP
            "chantier_id": 1,        // ID chantier
            "tache_id": 1,           // ID tâche (optionnel)
            "date": "2025-01-15",    // Date (optionnel, défaut: aujourd'hui)
            "heure_debut": 8.0,      // Heure début (float)
            "heure_fin": 17.0,       // Heure fin (float)
            "latitude": 33.5731,     // GPS latitude (optionnel)
            "longitude": -7.5898,    // GPS longitude (optionnel)
            "photo_base64": "...",   // Photo base64 (optionnel)
            "notes": "..."           // Notes (optionnel)
        }
        """
        if not self._check_auth():
            return {'success': False, 'error': 'Authentification invalide'}

        try:
            params = request.jsonrequest
            
            # Validations
            ressource = request.env['btp.ressource'].sudo().browse(params.get('employee_id'))
            if not ressource.exists():
                return {'success': False, 'error': 'Ressource non trouvée'}

            chantier = request.env['btp.chantier'].sudo().browse(params.get('chantier_id'))
            if not chantier.exists():
                return {'success': False, 'error': 'Chantier non trouvé'}

            vals = {
                'ressource_id': ressource.id,
                'chantier_id': chantier.id,
                'date': params.get('date', fields.Date.today()),
                'heure_debut': params.get('heure_debut', 8.0),
                'heure_fin': params.get('heure_fin', 17.0),
            }

            if params.get('tache_id'):
                vals['tache_id'] = params['tache_id']
            if params.get('latitude'):
                vals['latitude'] = params['latitude']
            if params.get('longitude'):
                vals['longitude'] = params['longitude']
            if params.get('notes'):
                vals['notes'] = params['notes']
            if params.get('photo_base64'):
                vals['photo'] = params['photo_base64']

            pointage = request.env['btp.pointage'].sudo().create(vals)

            _logger.info("BTP API: Pointage créé #%s pour ressource %s sur chantier %s",
                         pointage.id, ressource.name, chantier.name)

            return {
                'success': True,
                'pointage_id': pointage.id,
                'montant_journee': pointage.montant_journee,
            }

        except Exception as e:
            _logger.exception("BTP API: Erreur lors de la création du pointage")
            return {'success': False, 'error': str(e)}

    # ── GET /api/btp/chantier/<id>/dashboard ───────────────────
    @http.route('/api/btp/chantier/<int:chantier_id>/dashboard', type='http', auth='public', methods=['GET'], csrf=False)
    def api_dashboard(self, chantier_id, **kwargs):
        """
        Retourne les KPI d'un chantier au format JSON.
        
        Réponse:
        {
            "chantier": {...},
            "kpi": {
                "avancement": 45.5,
                "budget_consomme": 60.2,
                "jours_restants": 120,
                ...
            },
            "lots": [...],
            "alertes": [...]
        }
        """
        if not self._check_auth():
            return self._json_response({'success': False, 'error': 'Authentification invalide'}, 401)

        chantier = request.env['btp.chantier'].sudo().browse(chantier_id)
        if not chantier.exists():
            return self._json_response({'success': False, 'error': 'Chantier non trouvé'}, 404)

        try:
            # Calcul des KPI
            today = fields.Date.today()
            jours_restants = 0
            if chantier.date_fin_prevue:
                delta = chantier.date_fin_prevue - today
                jours_restants = max(0, delta.days)

            budget_total = sum(chantier.lot_ids.mapped('budget_prevu'))
            cout_total = sum(chantier.lot_ids.mapped('cout_reel'))
            taux_budget = (cout_total / budget_total * 100) if budget_total else 0

            # Lots
            lots_data = []
            for lot in chantier.lot_ids:
                lots_data.append({
                    'id': lot.id,
                    'name': lot.name,
                    'budget_prevu': lot.budget_prevu,
                    'cout_reel': lot.cout_reel,
                    'ecart': lot.ecart,
                    'taux_consommation': lot.taux_consommation,
                })

            # Alertes
            alertes = []
            engins_panne = chantier.engin_ids.filtered(lambda e: e.state == 'panne')
            if engins_panne:
                alertes.append({
                    'type': 'danger',
                    'message': "%d engin(s) en panne" % len(engins_panne),
                })

            docs_expires = chantier.document_ids.filtered(lambda d: d.alerte_expiration)
            if docs_expires:
                alertes.append({
                    'type': 'warning',
                    'message': "%d document(s) expirant bientôt" % len(docs_expires),
                })

            if jours_restants == 0 and chantier.state not in ('reception', 'garantie', 'cloture'):
                alertes.append({
                    'type': 'danger',
                    'message': "Délai contractuel dépassé !",
                })

            data = {
                'success': True,
                'chantier': {
                    'id': chantier.id,
                    'name': chantier.name,
                    'reference': chantier.reference,
                    'state': chantier.state,
                    'ville': chantier.ville,
                    'avancement': chantier.avancement_global,
                },
                'kpi': {
                    'avancement': chantier.avancement_global,
                    'budget_total': budget_total,
                    'cout_total': cout_total,
                    'taux_budget': round(taux_budget, 2),
                    'jours_restants': jours_restants,
                    'nb_ressources': len(chantier.ressource_ids),
                    'nb_engins': len(chantier.engin_ids),
                    'nb_lots': len(chantier.lot_ids),
                },
                'lots': lots_data,
                'alertes': alertes,
            }

            return self._json_response(data)

        except Exception as e:
            _logger.exception("BTP API: Erreur dashboard chantier %s", chantier_id)
            return self._json_response({'success': False, 'error': str(e)}, 500)
