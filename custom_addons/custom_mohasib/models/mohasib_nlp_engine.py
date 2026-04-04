# -*- coding: utf-8 -*-
"""
Mohasib — Moteur NLP (Natural Language Processing)
Parse les phrases en darija/français du directeur et les convertit en données
structurées de transaction comptable.

Fonctionne en 3 modes :
  1. conseil    : détecte les questions fiscales/comptables → répond en expert
  2. builtin    : regex + dictionnaires BTP (toujours dispo, sans API)
  3. api        : appelle l'API IA configurée (OpenAI / Ollama) pour les cas complexes
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

        text_lower = text.lower().strip()

        # ── Mode 0 : Détection de QUESTION → Conseil fiscal/comptable ──
        conseil_result = self._detect_question(text, text_lower)
        if conseil_result:
            return conseil_result

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
    #  DÉTECTION DE QUESTIONS → MODE CONSEIL
    # ══════════════════════════════════════════════════════════════

    @api.model
    def _detect_question(self, text, text_lower):
        """Détecte si le texte est une question fiscale/comptable.
        Retourne un dict 'conseil' ou None si c'est une transaction."""

        # Marqueurs de question
        is_question = any(kw in text_lower for kw in [
            '?', 'comment', 'pourquoi', 'est-ce', 'est ce', 'quand',
            'quel ', 'quelle', 'quels', 'quelles', 'combien',
            'explique', "c'est quoi", 'différence', 'difference',
            'obligation', 'dois-je', 'faut-il', 'peut-on', 'doit-on',
        ])

        # Marqueurs de transaction (opération concrète)
        is_transaction = any(kw in text_lower for kw in [
            'acheté', 'acheter', 'reçu', 'payé', 'versé', 'loué',
            'encaissé', 'dh', 'mad', 'dirham', 'sacs', 'sac',
            'tonne', 'kg', 'litre', 'jour',
            'chrit', 'khless', 'khlsna',
        ])

        # Si c'est clairement une transaction → laisser le parser builtin
        if is_transaction and not is_question:
            return None

        # Si c'est une question ou un sujet fiscal → conseil
        if is_question or self._is_fiscal_topic(text_lower):
            return self._generate_conseil(text_lower)

        return None

    @api.model
    def _is_fiscal_topic(self, text_lower):
        """Détecte si le texte porte sur un sujet fiscal/comptable."""
        fiscal_keywords = [
            'tva', 'impôt', 'impot', 'is ', 'ir ', 'taxe',
            'fiscal', 'retenue', 'pcm', 'plan comptable',
            'cnss', 'amo', 'cimr', 'cotisation',
            'déduction', 'deduction', 'exonération', 'exoneration',
            'barème', 'bareme', 'déclaration', 'declaration',
            'comptabilisation', 'amortissement', 'provision',
            'bilan', 'résultat', 'resultat',
            'garantie décennale', 'garantie decennale',
            'caution bancaire', 'caution provisoire', 'caution définitive',
            'retenue de garantie', 'pénalité', 'penalite',
        ]
        return any(kw in text_lower for kw in fiscal_keywords)

    @api.model
    def _generate_conseil(self, text_lower):
        """Génère un conseil fiscal/comptable en mode expert BTP Maroc."""
        result = {
            'success': True,
            'is_conseil': True,
            'confidence': 1.0,
        }

        # ── TVA ──
        if 'tva' in text_lower:
            result['message'] = (
                "📋 **TVA dans le secteur BTP au Maroc**\n\n"
                "**Taux applicables :**\n"
                "• 20% — Travaux de construction (taux normal)\n"
                "• 14% — Travaux immobiliers logement social\n"
                "• 10% — Certaines opérations de promotion immobilière\n"
                "• 7% — Eau (factures ONEE/régie)\n"
                "• Exonéré — Export de services BTP\n\n"
                "**Règles BTP :**\n"
                "• Les décomptes provisoires et définitifs sont soumis à la TVA\n"
                "• La retenue de garantie (10%) est soumise à la TVA\n"
                "• Les avances sur marchés sont soumises à la TVA\n"
                "• Marchés publics : autoliquidation par le maître d'ouvrage\n\n"
                "⚠️ **Fait générateur** : encaissement (régime de droit commun) ou débit (sur option)\n\n"
                "✅ Appliquez 20% sur vos décomptes sauf cas spécifiques."
            )

        # ── IS ──
        elif any(kw in text_lower for kw in ['is ', 'impôt sur les sociétés', 'impot sur les societes']):
            result['message'] = (
                "📋 **Impôt sur les Sociétés (IS) — Entreprise BTP**\n\n"
                "**Barème progressif :**\n"
                "• Bénéfice ≤ 300 000 MAD → **10%**\n"
                "• 300 001 à 1 000 000 MAD → **20%**\n"
                "• 1 000 001 à 100 000 000 MAD → **31%**\n"
                "• > 100 000 000 MAD → **35%**\n\n"
                "**Particularités BTP :**\n"
                "• Cotisation minimale : 0,50% du CA (min 3 000 MAD)\n"
                "• Provisions pour risques chantier : déductibles si justifiées\n"
                "• Provisions pour garantie décennale : déductibles\n"
                "• Pénalités de retard subies : NON déductibles fiscalement\n\n"
                "✅ Planifiez vos acomptes IS trimestriellement."
            )

        # ── IR / Salaires ──
        elif any(kw in text_lower for kw in ['ir ', 'salaire', 'paie', 'revenu', 'cnss', 'amo']):
            result['message'] = (
                "📋 **IR sur salaires — Personnel BTP au Maroc**\n\n"
                "**Barème annuel IR :**\n"
                "• 0 à 30 000 MAD → Exonéré\n"
                "• 30 001 à 50 000 → 10%\n"
                "• 50 001 à 60 000 → 20%\n"
                "• 60 001 à 80 000 → 30%\n"
                "• 80 001 à 180 000 → 34%\n"
                "• > 180 000 → 38%\n\n"
                "**Cotisations sociales :**\n"
                "• CNSS patronale : 26,60% (dont AMO)\n"
                "• CNSS salariale : 6,74%\n"
                "• CIMR (retraite complémentaire) : variable\n\n"
                "**Spécificités BTP :**\n"
                "• Indemnités de déplacement chantier : exonérées (justifiées)\n"
                "• Prime de panier : exonérée jusqu'à 20 MAD/jour\n"
                "• Indemnité d'outillage : exonérée si justifiée\n"
                "• Heures supplémentaires : +25% (jour), +50% (nuit/weekend)\n\n"
                "✅ Gérez séparément les indemnités exonérées pour optimiser la charge."
            )

        # ── Retenue à la source ──
        elif any(kw in text_lower for kw in ['retenue à la source', 'retenue a la source', 'ras']):
            result['message'] = (
                "📋 **Retenue à la Source (RAS) — BTP Maroc**\n\n"
                "**Taux :**\n"
                "• 10% sur honoraires et prestations\n"
                "• 10% rémunération des non-résidents (marchés publics)\n"
                "• 15% sur revenus fonciers\n\n"
                "**Application BTP :**\n"
                "• Sous-traitance : vérifiez si le sous-traitant est assujetti\n"
                "• Location d'engins : RAS 15% si le loueur est personne physique\n"
                "• Bureau d'études : RAS 10%\n\n"
                "✅ Pratiquez la RAS et déclarez trimestriellement."
            )

        # ── Retenue de garantie ──
        elif any(kw in text_lower for kw in ['retenue de garantie', 'garantie']):
            result['message'] = (
                "📋 **Retenue de Garantie — Marchés BTP**\n\n"
                "• **Taux** : généralement 10% de chaque décompte\n"
                "• **But** : garantir la bonne exécution et levée des réserves\n"
                "• **Durée** : jusqu'à la réception définitive (1 an après provisoire)\n"
                "• **Substitution** : peut être remplacée par caution bancaire\n\n"
                "**Comptabilisation (PCM) :**\n"
                "• Facturation → compte 3424 « Clients, retenues de garantie »\n"
                "• Libération → 5141 (banque) au débit, 3424 au crédit\n\n"
                "⚠️ La retenue est soumise à la TVA au moment de la facturation, pas de la libération.\n\n"
                "✅ Suivez chaque retenue par chantier."
            )

        # ── Caution ──
        elif 'caution' in text_lower:
            result['message'] = (
                "📋 **Cautions Bancaires BTP — Maroc**\n\n"
                "**Types de cautions :**\n"
                "• Caution provisoire : 1,5% du montant estimé du marché\n"
                "• Caution définitive : 3% du montant du marché\n"
                "• Caution de retenue de garantie : 10% (substitution)\n"
                "• Caution d'avance : 100% du montant de l'avance\n\n"
                "**Comptabilisation (PCM) :**\n"
                "• Frais de dossier : 6147 (services bancaires)\n"
                "• Commissions : 6147 débit, 5141 crédit\n"
                "• Hors bilan : engagement donné (classe 0)\n\n"
                "✅ Provisionnez les commissions et suivez les échéances."
            )

        # ── PCM ──
        elif 'pcm' in text_lower or 'plan comptable' in text_lower or 'compte' in text_lower:
            result['message'] = (
                "📋 **Plan Comptable Marocain (PCM) — Comptes BTP**\n\n"
                "**Classe 3 — Actif circulant :**\n"
                "• 3421 : Clients\n"
                "• 3424 : Clients, retenues de garantie\n"
                "• 34552 : TVA récupérable\n\n"
                "**Classe 4 — Passif circulant :**\n"
                "• 4411 : Fournisseurs\n"
                "• 4455 : TVA facturée\n"
                "• 4457 : Retenues à la source\n\n"
                "**Classe 5 — Trésorerie :**\n"
                "• 5141 : Banque\n"
                "• 5161 : Caisse\n\n"
                "**Classe 6 — Charges :**\n"
                "• 6121 : Achats matières premières (ciment, acier...)\n"
                "• 6125 : Achats non stockés (carburant)\n"
                "• 6132 : Locations matériel\n"
                "• 6134 : Sous-traitance\n"
                "• 6171 : Salaires personnel chantier\n\n"
                "**Classe 7 — Produits :**\n"
                "• 7111 : Travaux facturés\n\n"
                "✅ Utilisez des sous-comptes analytiques par chantier."
            )

        # ── Pénalité de retard ──
        elif any(kw in text_lower for kw in ['pénalité', 'penalite', 'retard']):
            result['message'] = (
                "📋 **Pénalités de retard — Marchés BTP**\n\n"
                "• **Taux** : 1‰ (un pour mille) du montant du marché par jour de retard\n"
                "• **Plafond** : généralement 10% du montant du marché\n"
                "• **Application** : automatique sauf ordre d'arrêt/prolongation\n\n"
                "**Comptabilisation :**\n"
                "• Débit 6585 (créances devenues irrécouvrables) ou 6195\n"
                "• Crédit 4411 ou 3421\n\n"
                "⚠️ Les pénalités subies ne sont PAS déductibles fiscalement.\n\n"
                "✅ Documentez les causes du retard (ordres de service)."
            )

        # ── Amortissement ──
        elif 'amortissement' in text_lower:
            result['message'] = (
                "📋 **Amortissements — Matériel BTP**\n\n"
                "**Durées fiscales courantes :**\n"
                "• Bâtiments de chantier : 20 ans (5%)\n"
                "• Matériel de transport : 5 ans (20%)\n"
                "• Engins BTP (pelleteuse, grue) : 5-10 ans (10-20%)\n"
                "• Outillage : 5 ans (20%)\n"
                "• Mobilier de bureau : 10 ans (10%)\n"
                "• Matériel informatique : 5 ans (20%)\n\n"
                "**Méthodes :**\n"
                "• Linéaire (droit commun)\n"
                "• Dégressif (option, coefficient fiscal)\n\n"
                "✅ Vérifiez la conformité avec les taux fiscaux admis."
            )

        # ── Décompte / Situation ──
        elif any(kw in text_lower for kw in ['décompte', 'decompte']):
            result['message'] = (
                "📋 **Décomptes et Situations — BTP**\n\n"
                "**Types :**\n"
                "• Décompte provisoire : facturation mensuelle des travaux réalisés\n"
                "• Décompte définitif : solde final après réception\n"
                "• DGD (Décompte Général Définitif) : arrêt des comptes\n\n"
                "**Éléments d'un décompte :**\n"
                "• Montant brut HT des travaux\n"
                "• − Retenue de garantie (10%)\n"
                "• − Avance remboursée (prorata)\n"
                "• + TVA (20%)\n"
                "• − Retenue à la source (si applicable)\n"
                "• = **Net à payer**\n\n"
                "✅ Chaque situation doit être rattachée au chantier et validée."
            )

        # ── Question générique ──
        else:
            result['message'] = (
                "🏗️ **Mohasib — Expert-Comptable BTP Maroc**\n\n"
                "Je peux vous aider sur :\n\n"
                "**💬 Questions fiscales :**\n"
                "• \"C'est quoi la TVA BTP ?\" → Conseil avec taux et règles\n"
                "• \"Comment calculer l'IS ?\" → Barème et particularités BTP\n"
                "• \"Quelles sont les retenues à la source ?\" → Taux et obligations\n"
                "• \"Explique la retenue de garantie\" → Comptabilisation PCM\n\n"
                "**📝 Saisie d'opérations :**\n"
                "• \"Acheté 200 sacs ciment à 48 DH, chantier Hay Riad\"\n"
                "• \"Reçu 50 000 DH acompte client, par virement\"\n"
                "• \"Payé maallem Ahmed 15 000 DH plomberie\"\n"
                "• \"Location pelleteuse 3 jours × 5 000 DH\"\n\n"
                "Posez votre question ou décrivez votre opération ! 👆"
            )

        return result

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
