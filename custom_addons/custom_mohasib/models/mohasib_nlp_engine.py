# -*- coding: utf-8 -*-
"""
Mohasib — Moteur NLP (Natural Language Processing)
Parse les phrases en darija/français du directeur et les convertit en données
structurées de transaction comptable.

Fonctionne en 2 modes :
  1. builtin : regex + dictionnaires BTP (toujours dispo, sans API)
  2. api     : appelle l'API IA configurée (OpenAI / Ollama) pour les cas complexes
"""
import json
import logging
import re
import urllib.request
import urllib.error
from odoo import models, api

_logger = logging.getLogger(__name__)


class MohasibNLPEngine(models.AbstractModel):
    _name = 'mohasib.nlp.engine'
    _description = 'Moteur NLP Mohasib'

    # ══════════════════════════════════════════════════════════════
    #  DICTIONNAIRES BTP MAROC
    # ══════════════════════════════════════════════════════════════

    # --- Type de transaction ---
    KEYWORDS_TYPE = {
        'achat_materiaux': [
            'ciment', 'sable', 'gravier', 'fer', 'brique', 'acier', 'bois',
            'peinture', 'carrelage', 'plâtre', 'plomberie', 'tuyau', 'tube',
            'câble', 'fil', 'clou', 'vis', 'colle', 'joint', 'béton',
            'parpaing', 'enduit', 'zinc', 'verre', 'marbre', 'granit',
            'acheté', 'acheter', 'matériaux', 'matériel de construction',
            'sac', 'sacs', 'tonne', 'kg', 'mètre', 'quintal',
            'chrit', 'chrina',  # darija
        ],
        'achat_carburant': [
            'gazoil', 'gazole', 'diesel', 'essence', 'carburant', 'mazout',
            'plein', 'station', 'litre', 'gasoil',
        ],
        'sous_traitance': [
            'sous-traitant', 'sous traitant', 'soustraitant', 'prestataire',
            'maallem', 'maâllem', 'entrepreneur', 'tâcheron',
            'travaux', 'marché', 'prestation',
        ],
        'salaire': [
            'salaire', 'paye', 'paie', 'avance', 'ouvrier', 'main d\'oeuvre',
            'main d\'œuvre', 'journalier', 'kheddam', 'kheddama',
            'pointage', 'rémunération', 'versé à', 'donné à',
        ],
        'location_engin': [
            'location', 'louer', 'loué', 'grue', 'pelleteuse', 'bulldozer',
            'camion', 'bétonnière', 'compacteur', 'chargeuse', 'engin',
            'nacelle', 'échafaudage',
        ],
        'encaissement': [
            'reçu', 'encaissé', 'encaissement', 'acompte', 'paiement client',
            'versement', 'client a payé', 'client a versé',
            'chèque reçu', 'virement reçu', 'khless', 'khlsna',
        ],
        'facture_eau': [
            'eau', 'lydec', 'redal', 'amendis', 'facture eau',
            'radeema', 'onee', 'radeef',
        ],
        'facture_electricite': [
            'électricité', 'electricite', 'courant', 'one', 'steg',
            'facture électricité', 'facture electricite', 'daw',
        ],
        'frais_divers': [
            'frais', 'divers', 'taxi', 'transport', 'repas', 'nourriture',
            'téléphone', 'internet', 'photocopie', 'timbre', 'notaire',
        ],
    }

    # --- Mode de paiement ---
    KEYWORDS_PAIEMENT = {
        'cash': [
            'cash', 'espèce', 'espèces', 'liquide', 'caisse',
            'en main', 'naqd', 'bel flous',
        ],
        'banque': [
            'virement', 'banque', 'bancaire', 'transfert',
        ],
        'cheque': [
            'chèque', 'cheque', 'chik',
        ],
        'credit': [
            'crédit', 'credit', 'à crédit', 'pas encore payé',
            'impayé', 'facture', 'bel crédi',
        ],
    }

    # --- Noms de chantier (patterns) ---
    CHANTIER_PATTERNS = [
        r'(?:chantier|projet|site)\s+(?:de\s+)?([A-Za-zÀ-ÿ\s\-\']+?)(?:\s*,|\s+payé|\s+en|\s+par|\s*$)',
        r'(?:pour|sur|dans)\s+(?:le\s+)?(?:chantier|projet)\s+(?:de\s+)?([A-Za-zÀ-ÿ\s\-\']+?)(?:\s*,|\s+payé|\s+en|\s+par|\s*$)',
        r'(?:pour|sur)\s+([A-Za-zÀ-ÿ\s\-\']+?)(?:\s*,|\s+payé|\s+en|\s+par|\s*$)',
    ]

    # ══════════════════════════════════════════════════════════════
    #  POINT D'ENTRÉE PRINCIPAL
    # ══════════════════════════════════════════════════════════════

    @api.model
    def parse(self, text, chantier_id=None):
        """
        Parse une phrase en langage naturel et retourne des données structurées.

        :param text: ex. "J'ai acheté 200 sacs de ciment à 48 DH pour chantier Hay Riad, payé cash"
        :param chantier_id: ID du chantier par défaut (contexte conversation)
        :returns: dict {
            'success': bool,
            'type_transaction': str,
            'montant': float,
            'description': str,
            'article': str,
            'quantite': float,
            'prix_unitaire': float,
            'mode_paiement': str,
            'chantier_name': str,
            'chantier_id': int or False,
            'confidence': float (0-1),
            'message': str,  # message de confirmation pour le directeur
        }
        """
        if not text or not text.strip():
            return {
                'success': False,
                'message': "Je n'ai pas reçu de texte. "
                           "Décrivez votre opération, par exemple : "
                           "\"Acheté 200 sacs de ciment à 48 DH pour chantier Hay Riad, payé cash\"",
            }

        # Mode 1 : Parser builtin (regex)
        result = self._builtin_parse(text, chantier_id)

        # Si confiance faible et API dispo → Mode 2 : API
        if result.get('confidence', 0) < 0.5:
            api_result = self._api_parse(text, chantier_id)
            if api_result.get('success') and api_result.get('confidence', 0) > result.get('confidence', 0):
                result = api_result

        # Résoudre le chantier par nom
        if result.get('chantier_name') and not result.get('chantier_id'):
            chantier = self.env['mohasib.chantier'].search([
                ('name', 'ilike', result['chantier_name']),
            ], limit=1)
            if chantier:
                result['chantier_id'] = chantier.id
                result['chantier_name'] = chantier.name
            else:
                result['chantier_note'] = (
                    f"⚠️ Chantier '{result['chantier_name']}' non trouvé. "
                    f"Je vais le créer automatiquement si vous confirmez."
                )
        elif chantier_id and not result.get('chantier_id'):
            result['chantier_id'] = chantier_id

        # Générer le message de confirmation
        result['message'] = self._generate_confirmation_message(result)
        return result

    # ══════════════════════════════════════════════════════════════
    #  PARSER BUILTIN (REGEX)
    # ══════════════════════════════════════════════════════════════

    @api.model
    def _builtin_parse(self, text, chantier_id=None):
        text_lower = text.lower().strip()
        confidence = 0.0
        result = {
            'success': False,
            'type_transaction': False,
            'montant': 0.0,
            'description': text,
            'article': '',
            'quantite': 0.0,
            'prix_unitaire': 0.0,
            'mode_paiement': 'cash',
            'chantier_name': '',
            'chantier_id': chantier_id or False,
            'confidence': 0.0,
        }

        # 1. Détecter le TYPE de transaction
        best_type = None
        best_score = 0
        for trans_type, keywords in self.KEYWORDS_TYPE.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            if score > best_score:
                best_score = score
                best_type = trans_type
        if best_type:
            result['type_transaction'] = best_type
            confidence += 0.3

        # 2. Extraire le MONTANT
        montant = self._extract_montant(text_lower)
        if montant > 0:
            result['montant'] = montant
            confidence += 0.3

        # 3. Extraire quantité × prix unitaire
        qty, pu = self._extract_quantite_prix(text_lower)
        if qty > 0 and pu > 0:
            result['quantite'] = qty
            result['prix_unitaire'] = pu
            # Recalculer le montant si pas trouvé directement
            if result['montant'] == 0:
                result['montant'] = qty * pu
                confidence += 0.15

        # 4. Extraire l'article
        result['article'] = self._extract_article(text_lower, best_type)

        # 5. Détecter le MODE DE PAIEMENT
        for mode, keywords in self.KEYWORDS_PAIEMENT.items():
            if any(kw in text_lower for kw in keywords):
                result['mode_paiement'] = mode
                confidence += 0.1
                break

        # 6. Détecter le CHANTIER
        chantier_name = self._extract_chantier(text)
        if chantier_name:
            result['chantier_name'] = chantier_name.strip()
            confidence += 0.1

        # 7. Détecter une DATE
        date_match = re.search(
            r'(\d{1,2})[/\-](\d{1,2})(?:[/\-](\d{2,4}))?', text)
        if date_match:
            result['date_str'] = date_match.group(0)

        result['confidence'] = min(confidence, 1.0)
        result['success'] = confidence >= 0.3
        return result

    # ──────────────── Extraction du montant ────────────────

    @api.model
    def _extract_montant(self, text):
        """Extraire le montant total de la phrase."""
        patterns = [
            # "total 9600 DH", "montant 9 600 DH"
            r'(?:total|montant|somme|pour)\s*[:=]?\s*([\d\s]+(?:[.,]\d+)?)\s*(?:dh|mad|dirham)',
            # "payé 9600 DH", "versé 9 600"
            r'(?:payé|versé|reçu|coûté|coûte|coût)\s*([\d\s]+(?:[.,]\d+)?)\s*(?:dh|mad|dirham)?',
            # "9 600 DH" (montant suivi de devise)
            r'([\d\s]+(?:[.,]\d+)?)\s*(?:dh|mad|dirham)',
            # "à 48 DH" (prix unitaire — pris en dernier recours)
            r'à\s+([\d\s]+(?:[.,]\d+)?)\s*(?:dh|mad|dirham)',
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                val = match.group(1).replace(' ', '').replace(',', '.')
                try:
                    return float(val)
                except ValueError:
                    continue
        # Fallback: plus grand nombre dans la phrase
        numbers = re.findall(r'(\d[\d\s]*(?:[.,]\d+)?)', text)
        if numbers:
            values = []
            for n in numbers:
                clean = n.replace(' ', '').replace(',', '.')
                try:
                    values.append(float(clean))
                except ValueError:
                    pass
            if values:
                return max(values)
        return 0.0

    # ──────────────── Extraction quantité × prix ────────────────

    @api.model
    def _extract_quantite_prix(self, text):
        """Extraire 'N unités à X DH'."""
        patterns = [
            r'(\d+)\s*(?:sacs?|tonnes?|kg|m[èe]tres?|quintaux?|unités?|pièces?|litres?|barres?)\s+'
            r'(?:de\s+)?(?:\w+\s+)?à\s+([\d\s]+(?:[.,]\d+)?)\s*(?:dh|mad)?',
            r'(\d+)\s+\w+\s+à\s+([\d\s]+(?:[.,]\d+)?)\s*(?:dh|mad)?',
            r'(\d+)\s*[x×]\s*([\d\s]+(?:[.,]\d+)?)',
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                qty = float(match.group(1))
                pu = float(match.group(2).replace(' ', '').replace(',', '.'))
                return qty, pu
        return 0.0, 0.0

    # ──────────────── Extraction article ────────────────

    @api.model
    def _extract_article(self, text, trans_type):
        """Extraire le nom de l'article / prestation."""
        if trans_type == 'achat_materiaux':
            for kw in self.KEYWORDS_TYPE['achat_materiaux']:
                if kw in text:
                    return kw.capitalize()
        if trans_type == 'sous_traitance':
            match = re.search(
                r'(?:sous.traitant|maallem|prestataire)\s+([A-Za-zÀ-ÿ]+)', text)
            if match:
                return match.group(1).capitalize()
        if trans_type == 'salaire':
            match = re.search(
                r'(?:ouvrier|kheddam|employé)\s+([A-Za-zÀ-ÿ]+)', text)
            if match:
                return match.group(1).capitalize()
        return ''

    # ──────────────── Extraction chantier ────────────────

    @api.model
    def _extract_chantier(self, text):
        """Extraire le nom du chantier."""
        for pattern in self.CHANTIER_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                name = match.group(1).strip()
                # Nettoyer les stop words
                name = re.sub(
                    r'\b(le|la|les|de|du|des|un|une|pour|sur|dans)\b',
                    '', name, flags=re.IGNORECASE,
                ).strip()
                if len(name) > 2:
                    return name
        return ''

    # ══════════════════════════════════════════════════════════════
    #  PARSER API (OpenAI / Ollama)
    # ══════════════════════════════════════════════════════════════

    @api.model
    def _api_parse(self, text, chantier_id=None):
        """Utilise l'API IA pour parser le texte (fallback)."""
        ICP = self.env['ir.config_parameter'].sudo()
        provider = ICP.get_param('custom_ai.provider', 'builtin')
        api_key = ICP.get_param('custom_ai.api_key', '')
        api_url = ICP.get_param('custom_ai.api_url', 'https://api.openai.com/v1')
        model = ICP.get_param('custom_ai.model', 'gpt-3.5-turbo')

        if provider == 'builtin' or not api_key:
            return {'success': False, 'confidence': 0}

        system_prompt = """Tu es Mohasib, un expert-comptable marocain spécialisé BTP.
Tu reçois une phrase du directeur de chantier et tu dois extraire les données comptables.

RÉPONDS UNIQUEMENT en JSON valide, sans texte avant/après :
{
  "type_transaction": "achat_materiaux|achat_carburant|sous_traitance|salaire|location_engin|encaissement|facture_eau|facture_electricite|frais_divers",
  "montant": 0.0,
  "article": "",
  "quantite": 0.0,
  "prix_unitaire": 0.0,
  "mode_paiement": "cash|banque|cheque|credit",
  "chantier_name": "",
  "description_comptable": ""
}

Règles fiscales marocaines :
- TVA matériaux : 20%
- TVA carburant : 10%
- TVA eau : 7%
- TVA électricité : 14%
- Retenue source sous-traitance : 10%
- Location engins : 15% si particulier
"""

        payload = json.dumps({
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text},
            ],
            "temperature": 0.1,
            "max_tokens": 500,
        }).encode('utf-8')

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }
        url = f"{api_url.rstrip('/')}/chat/completions"

        try:
            req = urllib.request.Request(
                url, data=payload, headers=headers, method='POST')
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read().decode('utf-8'))
                text_resp = result['choices'][0]['message']['content'].strip()
                # Extraire le JSON de la réponse
                json_match = re.search(r'\{[^}]+\}', text_resp, re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group())
                    data['success'] = True
                    data['confidence'] = 0.9
                    data['chantier_id'] = chantier_id or False
                    data['description'] = text
                    return data
        except Exception as e:
            _logger.warning("Mohasib API parse error: %s", str(e))

        return {'success': False, 'confidence': 0}

    # ══════════════════════════════════════════════════════════════
    #  MESSAGE DE CONFIRMATION
    # ══════════════════════════════════════════════════════════════

    @api.model
    def _generate_confirmation_message(self, data):
        """Génère le message de confirmation pour le directeur."""
        if not data.get('success'):
            return (
                "🤔 Désolé, je n'ai pas bien compris. Pouvez-vous reformuler ?\n\n"
                "Exemples :\n"
                "• \"Acheté 200 sacs de ciment à 48 DH pour chantier Hay Riad, payé cash\"\n"
                "• \"Reçu 50 000 DH du client pour chantier Tanger, par virement\"\n"
                "• \"Payé l'ouvrier Ahmed 3 000 DH avance, chantier Casa\"\n"
                "• \"Location pelleteuse 5 000 DH/jour × 3 jours, chantier Marrakech\""
            )

        type_labels = {
            'achat_materiaux': '🧱 Achat matériaux',
            'achat_carburant': '⛽ Achat carburant',
            'sous_traitance': '👷 Sous-traitance',
            'salaire': '💰 Salaire / Avance',
            'location_engin': '🚜 Location engin',
            'encaissement': '💵 Encaissement client',
            'facture_eau': '💧 Facture eau',
            'facture_electricite': '⚡ Facture électricité',
            'frais_divers': '📋 Frais divers',
        }
        paiement_labels = {
            'cash': '💵 Espèces (caisse)',
            'banque': '🏦 Virement bancaire',
            'cheque': '📝 Chèque',
            'credit': '📄 À crédit',
        }

        t = data.get('type_transaction', '')
        msg = f"📊 **{type_labels.get(t, t)}**\n\n"

        if data.get('article'):
            msg += f"📦 Article : {data['article']}\n"
        if data.get('quantite') and data.get('prix_unitaire'):
            msg += f"🔢 Quantité : {data['quantite']:.0f} × {data['prix_unitaire']:,.0f} DH\n"

        msg += f"💰 Montant : **{data.get('montant', 0):,.0f} DH**\n"
        msg += f"💳 Paiement : {paiement_labels.get(data.get('mode_paiement', 'cash'), '—')}\n"

        if data.get('chantier_name'):
            msg += f"🏗️ Chantier : {data['chantier_name']}\n"
        elif data.get('chantier_id'):
            msg += f"🏗️ Chantier : (par défaut)\n"

        if data.get('chantier_note'):
            msg += f"\n{data['chantier_note']}\n"

        msg += "\n✅ **Voulez-vous confirmer cette saisie ?**"
        return msg
