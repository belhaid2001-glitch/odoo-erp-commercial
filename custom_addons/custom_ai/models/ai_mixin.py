# -*- coding: utf-8 -*-
import json
import logging
import urllib.request
import urllib.error
from odoo import models, api, _

_logger = logging.getLogger(__name__)


class AIMixin(models.AbstractModel):
    """Mixin providing AI capabilities to any Odoo model.

    Usage: inherit this mixin in your model and call self.ai_generate() or
    self.ai_analyze() to get AI-powered results.  Works in two modes:
    - builtin: rule-based intelligence (always works, no API key needed)
    - api: calls OpenAI or Ollama for advanced results
    """
    _name = 'ai.mixin'
    _description = 'Mixin IA pour tous les modules'

    # =================================================================
    #  PUBLIC API
    # =================================================================
    @api.model
    def ai_generate(self, prompt, context_data=None, module='general'):
        """Generate text using AI.

        :param prompt: The user prompt / instruction
        :param context_data: dict with contextual information
        :param module: module name for builtin rules
        :returns: dict {'success': bool, 'result': str, 'provider': str}
        """
        provider = self.env['ir.config_parameter'].sudo().get_param(
            'custom_ai.provider', 'builtin')

        if provider == 'builtin':
            return self._ai_builtin_generate(prompt, context_data, module)
        else:
            return self._ai_api_generate(prompt, context_data)

    @api.model
    def ai_analyze(self, data, analysis_type='general', module='general'):
        """Analyze data and return insights.

        :param data: dict with data to analyze
        :param analysis_type: type of analysis (trend, prediction, scoring, etc.)
        :param module: module name for builtin rules
        :returns: dict with analysis results
        """
        provider = self.env['ir.config_parameter'].sudo().get_param(
            'custom_ai.provider', 'builtin')

        if provider == 'builtin':
            return self._ai_builtin_analyze(data, analysis_type, module)
        else:
            prompt = self._build_analysis_prompt(data, analysis_type, module)
            return self._ai_api_generate(prompt, data)

    @api.model
    def ai_suggest(self, record_data, suggestion_type='general', module='general'):
        """Get AI suggestions for a record.

        :param record_data: dict with record information
        :param suggestion_type: type of suggestions needed
        :param module: module name for builtin rules
        :returns: dict with suggestions
        """
        provider = self.env['ir.config_parameter'].sudo().get_param(
            'custom_ai.provider', 'builtin')

        if provider == 'builtin':
            return self._ai_builtin_suggest(record_data, suggestion_type, module)
        else:
            prompt = self._build_suggest_prompt(record_data, suggestion_type, module)
            return self._ai_api_generate(prompt, record_data)

    # =================================================================
    #  API-BASED GENERATION (OpenAI / Ollama)
    # =================================================================
    @api.model
    def _ai_api_generate(self, prompt, context_data=None):
        """Call external AI API."""
        ICP = self.env['ir.config_parameter'].sudo()
        api_key = ICP.get_param('custom_ai.api_key', '')
        api_url = ICP.get_param('custom_ai.api_url', 'https://api.openai.com/v1')
        model = ICP.get_param('custom_ai.model', 'gpt-3.5-turbo')
        temperature = float(ICP.get_param('custom_ai.temperature', '0.7'))

        if not api_key:
            _logger.warning("AI API key not configured, falling back to builtin")
            return self._ai_builtin_generate(prompt, context_data, 'general')

        system_msg = (
            "Tu es un assistant IA intégré dans un ERP Odoo. "
            "Réponds en français de manière concise et professionnelle. "
            "Fournis des suggestions concrètes et actionnables."
        )

        messages = [
            {"role": "system", "content": system_msg},
        ]
        if context_data:
            messages.append({
                "role": "user",
                "content": f"Contexte: {json.dumps(context_data, ensure_ascii=False, default=str)}"
            })
        messages.append({"role": "user", "content": prompt})

        payload = json.dumps({
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": 1000,
        }).encode('utf-8')

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }

        url = f"{api_url.rstrip('/')}/chat/completions"

        try:
            req = urllib.request.Request(url, data=payload, headers=headers, method='POST')
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read().decode('utf-8'))
                text = result['choices'][0]['message']['content'].strip()
                return {'success': True, 'result': text, 'provider': 'api'}
        except urllib.error.HTTPError as e:
            _logger.error("AI API HTTP error: %s", e.read().decode() if e.fp else str(e))
            return {'success': False, 'result': f"Erreur API: {e.code}", 'provider': 'api'}
        except Exception as e:
            _logger.error("AI API error: %s", str(e))
            return {'success': False, 'result': f"Erreur: {str(e)}", 'provider': 'api'}

    # =================================================================
    #  BUILTIN INTELLIGENCE (Rule-based, always works)
    # =================================================================
    @api.model
    def _ai_builtin_generate(self, prompt, context_data=None, module='general'):
        """Rule-based text generation."""
        prompt_lower = (prompt or '').lower()
        ctx = context_data or {}
        result = ''

        # --- SALE module ---
        if module == 'sale' or 'vente' in prompt_lower or 'devis' in prompt_lower:
            name = ctx.get('product_name', ctx.get('name', ''))
            amount = ctx.get('amount_total', 0)
            partner = ctx.get('partner_name', '')
            if 'description' in prompt_lower or 'produit' in prompt_lower:
                result = self._gen_product_description(name)
            elif 'prix' in prompt_lower or 'remise' in prompt_lower or 'discount' in prompt_lower:
                result = self._gen_price_suggestion(ctx)
            elif 'relance' in prompt_lower or 'email' in prompt_lower:
                result = self._gen_sale_followup(ctx)
            else:
                result = (
                    f"📊 Analyse de la commande :\n"
                    f"• Client : {partner}\n"
                    f"• Montant : {amount:,.2f} MAD\n"
                    f"• Recommandation : "
                )
                if amount > 50000:
                    result += "Commande importante - proposer des conditions de paiement avantageuses."
                elif amount > 10000:
                    result += "Commande significative - vérifier la disponibilité stock."
                else:
                    result += "Commande standard - traitement priorité normale."

        # --- CRM module ---
        elif module == 'crm' or 'lead' in prompt_lower or 'prospect' in prompt_lower:
            result = self._gen_crm_analysis(ctx)

        # --- HR module ---
        elif module == 'hr' or 'évaluation' in prompt_lower or 'employé' in prompt_lower:
            result = self._gen_hr_evaluation(ctx)

        # --- Accounting ---
        elif module == 'accounting' or 'facture' in prompt_lower or 'paiement' in prompt_lower:
            result = self._gen_accounting_analysis(ctx)

        # --- Stock ---
        elif module == 'stock' or 'stock' in prompt_lower or 'inventaire' in prompt_lower:
            result = self._gen_stock_analysis(ctx)

        # --- General ---
        else:
            result = (
                "🤖 Analyse IA :\n"
                f"Module : {module}\n"
                "L'assistant IA a analysé les données disponibles.\n"
                "Pour des résultats plus précis, configurez une clé API OpenAI "
                "dans Configuration > IA."
            )

        return {'success': True, 'result': result, 'provider': 'builtin'}

    @api.model
    def _ai_builtin_analyze(self, data, analysis_type, module):
        """Rule-based data analysis."""
        result = {}
        if analysis_type == 'scoring' and module == 'crm':
            result = self._analyze_lead_scoring(data)
        elif analysis_type == 'prediction' and module == 'accounting':
            result = self._analyze_payment_prediction(data)
        elif analysis_type == 'forecast' and module == 'stock':
            result = self._analyze_stock_forecast(data)
        elif analysis_type == 'trend':
            result = self._analyze_trend(data)
        else:
            result = {'score': 50, 'confidence': 'medium',
                      'insight': 'Analyse basique effectuée. Configurez l\'API IA pour des analyses avancées.'}
        return {'success': True, 'result': result, 'provider': 'builtin'}

    @api.model
    def _ai_builtin_suggest(self, record_data, suggestion_type, module):
        """Rule-based suggestions."""
        suggestions = []
        if module == 'sale':
            suggestions = self._suggest_sale(record_data)
        elif module == 'crm':
            suggestions = self._suggest_crm(record_data)
        elif module == 'hr':
            suggestions = self._suggest_hr(record_data)
        elif module == 'purchase':
            suggestions = self._suggest_purchase(record_data)
        else:
            suggestions = [{'type': 'info', 'text': 'Aucune suggestion spécifique disponible.'}]
        return {'success': True, 'result': suggestions, 'provider': 'builtin'}

    # =================================================================
    #  BUILTIN GENERATORS
    # =================================================================
    @api.model
    def _gen_product_description(self, name):
        name = name or 'Produit'
        return (
            f"📝 Description générée pour « {name} » :\n\n"
            f"{name} — Solution professionnelle de qualité supérieure conçue pour "
            f"répondre aux exigences les plus élevées de votre entreprise.\n\n"
            f"✅ Caractéristiques clés :\n"
            f"• Performance et fiabilité garanties\n"
            f"• Conforme aux normes en vigueur\n"
            f"• Support technique inclus\n\n"
            f"💡 Conseil IA : Personnalisez cette description avec les "
            f"spécificités techniques de votre {name.lower()}."
        )

    @api.model
    def _gen_price_suggestion(self, ctx):
        amount = ctx.get('amount_total', 0)
        margin = ctx.get('margin_percent', 0)
        partner = ctx.get('partner_name', 'Client')
        is_returning = ctx.get('is_returning_customer', False)
        result = f"💰 Suggestion de prix pour {partner} :\n\n"
        if is_returning:
            result += "🔄 Client fidèle — remise recommandée : 5-10%\n"
        if amount > 100000:
            result += "📦 Commande volumineuse — remise volume : 3-7%\n"
        if margin and margin < 15:
            result += f"⚠️ Marge actuelle ({margin:.1f}%) faible — éviter des remises supplémentaires\n"
        elif margin and margin > 40:
            result += f"✅ Marge confortable ({margin:.1f}%) — marge de négociation disponible\n"
        result += "\n💡 Conseil : Privilégiez des avantages non-monétaires (livraison gratuite, extension garantie)."
        return result

    @api.model
    def _gen_sale_followup(self, ctx):
        partner = ctx.get('partner_name', 'Client')
        ref = ctx.get('name', 'Devis')
        amount = ctx.get('amount_total', 0)
        return (
            f"📧 Email de relance suggéré :\n\n"
            f"Objet : Suivi de votre devis {ref}\n\n"
            f"Bonjour,\n\n"
            f"Je me permets de revenir vers vous concernant le devis {ref} "
            f"d'un montant de {amount:,.2f} MAD que nous vous avons adressé.\n\n"
            f"Avez-vous eu l'occasion de l'examiner ? Je reste à votre "
            f"entière disposition pour toute question ou ajustement.\n\n"
            f"Cordialement"
        )

    @api.model
    def _gen_crm_analysis(self, ctx):
        name = ctx.get('name', 'Opportunité')
        revenue = ctx.get('expected_revenue', 0)
        prob = ctx.get('probability', 0)
        days = ctx.get('days_since_last_contact', 0)
        quality = ctx.get('lead_quality', 'warm')

        result = f"🎯 Analyse IA du lead « {name} » :\n\n"
        # Scoring
        score = 50
        if revenue > 100000:
            score += 20
            result += "✅ Potentiel élevé (> 100K MAD)\n"
        elif revenue > 20000:
            score += 10
            result += "📊 Potentiel moyen (20-100K MAD)\n"
        if prob > 50:
            score += 15
            result += f"✅ Probabilité favorable ({prob}%)\n"
        if quality == 'hot':
            score += 15
            result += "🔥 Lead chaud — action immédiate recommandée\n"
        if days > 14:
            score -= 10
            result += f"⚠️ {days} jours sans contact — risque de perte\n"
        elif days > 7:
            score -= 5
            result += f"📞 {days} jours sans contact — relance conseillée\n"

        score = max(0, min(100, score))
        result += f"\n📈 Score IA : {score}/100\n"

        # Next action
        result += "\n🎬 Prochaine action recommandée : "
        if days > 14:
            result += "APPEL URGENT - Recontacter le prospect immédiatement"
        elif quality == 'hot':
            result += "Planifier une démo / présentation commerciale"
        elif prob > 70:
            result += "Préparer une proposition commerciale"
        else:
            result += "Envoyer du contenu éducatif / cas client"

        return result

    @api.model
    def _gen_hr_evaluation(self, ctx):
        name = ctx.get('employee_name', 'Collaborateur')
        scores = ctx.get('scores', {})
        global_score = ctx.get('global_score', 0)

        result = f"📋 Synthèse d'évaluation — {name}\n\n"

        if global_score >= 8:
            result += "🌟 Performance excellente — Profil à fort potentiel\n\n"
        elif global_score >= 6:
            result += "✅ Performance satisfaisante — Progression régulière\n\n"
        elif global_score >= 4:
            result += "⚠️ Performance à améliorer — Accompagnement nécessaire\n\n"
        else:
            result += "🔴 Performance insuffisante — Plan d'action urgent\n\n"

        # Strengths & weaknesses
        if scores:
            strengths = [k for k, v in scores.items() if v >= 7]
            weaknesses = [k for k, v in scores.items() if v < 5]
            if strengths:
                result += "💪 Points forts : " + ", ".join(strengths) + "\n"
            if weaknesses:
                result += "📈 Axes d'amélioration : " + ", ".join(weaknesses) + "\n"

        result += f"\n🎯 Objectifs suggérés :\n"
        if global_score < 6:
            result += "• Formation technique ciblée sur les compétences en retrait\n"
            result += "• Mentorat avec un collaborateur senior\n"
            result += "• Point de suivi bi-mensuel\n"
        else:
            result += "• Prendre en charge un projet transversal\n"
            result += "• Mentorer un junior\n"
            result += "• Explorer une certification professionnelle\n"

        return result

    @api.model
    def _gen_accounting_analysis(self, ctx):
        partner = ctx.get('partner_name', 'Client')
        amount = ctx.get('amount_residual', 0)
        days_overdue = ctx.get('days_overdue', 0)
        risk = ctx.get('risk_level', 'low')

        result = f"💳 Analyse IA — Facture {partner}\n\n"
        result += f"• Montant restant : {amount:,.2f} MAD\n"
        result += f"• Retard : {days_overdue} jours\n"
        result += f"• Niveau de risque : {risk}\n\n"

        if days_overdue > 60:
            result += "🔴 Action : Mise en demeure recommandée\n"
            result += "Prédiction : probabilité de paiement < 40%\n"
        elif days_overdue > 30:
            result += "🟠 Action : Relance téléphonique personnalisée\n"
            result += "Prédiction : paiement probable sous 15 jours avec relance\n"
        elif days_overdue > 7:
            result += "🟡 Action : Email de rappel courtois\n"
            result += "Prédiction : paiement probable sous 7 jours\n"
        else:
            result += "🟢 Facture récente — Pas d'action nécessaire\n"

        return result

    @api.model
    def _gen_stock_analysis(self, ctx):
        product = ctx.get('product_name', 'Produit')
        qty = ctx.get('qty_available', 0)
        avg_daily = ctx.get('avg_daily_usage', 0)

        result = f"📦 Analyse Stock IA — {product}\n\n"
        result += f"• Quantité en stock : {qty}\n"

        if avg_daily > 0:
            days_remaining = qty / avg_daily if qty > 0 else 0
            result += f"• Consommation moyenne : {avg_daily:.1f}/jour\n"
            result += f"• Jours de stock restants : {days_remaining:.0f}\n\n"
            if days_remaining < 7:
                result += "🔴 ALERTE : Réapprovisionnement URGENT\n"
                result += f"• Quantité suggérée : {avg_daily * 30:.0f} unités (1 mois)\n"
            elif days_remaining < 14:
                result += "🟠 Attention : Stock bas — Commande recommandée sous 48h\n"
                result += f"• Quantité suggérée : {avg_daily * 30:.0f} unités (1 mois)\n"
            else:
                result += "🟢 Stock suffisant\n"
        else:
            result += "• Pas de données de consommation disponibles\n"
            result += "💡 Conseil : Alimentez l'historique pour de meilleures prédictions\n"

        return result

    # =================================================================
    #  BUILTIN ANALYZERS
    # =================================================================
    @api.model
    def _analyze_lead_scoring(self, data):
        score = 50
        factors = []
        revenue = data.get('expected_revenue', 0)
        prob = data.get('probability', 0)
        days = data.get('days_since_last_contact', 0)
        calls = data.get('call_count', 0)
        meetings = data.get('meeting_count', 0)

        if revenue > 100000: score += 20; factors.append('Potentiel élevé (+20)')
        elif revenue > 20000: score += 10; factors.append('Potentiel moyen (+10)')
        if prob > 70: score += 15; factors.append('Forte probabilité (+15)')
        elif prob > 40: score += 5; factors.append('Probabilité moyenne (+5)')
        if calls >= 3: score += 5; factors.append('Engagement par appels (+5)')
        if meetings >= 1: score += 10; factors.append('Réunion effectuée (+10)')
        if days > 21: score -= 15; factors.append('Inactivité prolongée (-15)')
        elif days > 7: score -= 5; factors.append('Contact récent insuffisant (-5)')

        score = max(0, min(100, score))
        return {'score': score, 'factors': factors,
                'confidence': 'high' if len(factors) >= 4 else 'medium',
                'recommendation': 'Prioriser' if score >= 70 else 'Suivre' if score >= 40 else 'Qualifier'}

    @api.model
    def _analyze_payment_prediction(self, data):
        days_overdue = data.get('days_overdue', 0)
        amount = data.get('amount_residual', 0)
        history_avg = data.get('avg_payment_delay', 0)

        if days_overdue > 90:
            prob = 20
        elif days_overdue > 60:
            prob = 40
        elif days_overdue > 30:
            prob = 60
        elif days_overdue > 0:
            prob = 80
        else:
            prob = 95

        return {
            'payment_probability': prob,
            'estimated_days': max(0, int(history_avg * 1.2)) if history_avg else days_overdue + 15,
            'risk': 'high' if prob < 50 else 'medium' if prob < 80 else 'low',
        }

    @api.model
    def _analyze_stock_forecast(self, data):
        qty = data.get('qty_available', 0)
        avg_daily = data.get('avg_daily_usage', 0)
        lead_time = data.get('lead_time_days', 7)

        days_remaining = (qty / avg_daily) if avg_daily > 0 else 999
        reorder_point = avg_daily * (lead_time + 3)  # safety stock = 3 days
        suggested_qty = avg_daily * 30  # 1 month supply

        return {
            'days_remaining': round(days_remaining),
            'reorder_point': round(reorder_point),
            'suggested_qty': round(suggested_qty),
            'urgency': 'critical' if days_remaining < lead_time else
                       'warning' if days_remaining < lead_time * 2 else 'ok',
        }

    @api.model
    def _analyze_trend(self, data):
        values = data.get('values', [])
        if len(values) < 2:
            return {'trend': 'stable', 'change': 0}
        recent = sum(values[-3:]) / min(3, len(values))
        older = sum(values[:-3]) / max(1, len(values) - 3) if len(values) > 3 else values[0]
        change = ((recent - older) / older * 100) if older else 0
        return {
            'trend': 'up' if change > 5 else 'down' if change < -5 else 'stable',
            'change_percent': round(change, 1),
        }

    # =================================================================
    #  BUILTIN SUGGESTERS
    # =================================================================
    @api.model
    def _suggest_sale(self, data):
        suggestions = []
        amount = data.get('amount_total', 0)
        margin = data.get('margin_percent', 0)
        if amount > 50000:
            suggestions.append({'type': 'success', 'icon': 'fa-handshake-o',
                                'text': 'Proposer un échéancier de paiement pour ce montant important'})
        if margin and margin < 15:
            suggestions.append({'type': 'warning', 'icon': 'fa-exclamation',
                                'text': f'Marge faible ({margin:.1f}%) - Vérifier les prix unitaires'})
        if margin and margin > 40:
            suggestions.append({'type': 'info', 'icon': 'fa-gift',
                                'text': 'Marge confortable - Possibilité d\'offrir un geste commercial'})
        suggestions.append({'type': 'info', 'icon': 'fa-cart-plus',
                            'text': 'Proposer des produits complémentaires pour augmenter le panier'})
        return suggestions

    @api.model
    def _suggest_crm(self, data):
        suggestions = []
        days = data.get('days_since_last_contact', 0)
        quality = data.get('lead_quality', 'warm')
        prob = data.get('probability', 0)
        if days > 14:
            suggestions.append({'type': 'danger', 'icon': 'fa-phone',
                                'text': 'Contact urgent — Plus de 2 semaines sans interaction'})
        if quality == 'hot':
            suggestions.append({'type': 'success', 'icon': 'fa-calendar',
                                'text': 'Lead chaud — Planifier une démo immédiatement'})
        if prob > 70:
            suggestions.append({'type': 'info', 'icon': 'fa-file-text',
                                'text': 'Forte probabilité — Préparer une proposition commerciale'})
        suggestions.append({'type': 'info', 'icon': 'fa-envelope',
                            'text': 'Envoyer un contenu personnalisé (étude de cas, témoignage)'})
        return suggestions

    @api.model
    def _suggest_hr(self, data):
        suggestions = []
        score = data.get('global_score', 0)
        scores = data.get('scores', {})
        if score >= 8:
            suggestions.append({'type': 'success', 'icon': 'fa-trophy',
                                'text': 'Excellent profil — Envisager une promotion ou augmentation'})
        elif score < 5:
            suggestions.append({'type': 'danger', 'icon': 'fa-exclamation-triangle',
                                'text': 'Performance insuffisante — Mettre en place un plan d\'amélioration'})
        for criterion, val in scores.items():
            if val < 4:
                suggestions.append({'type': 'warning', 'icon': 'fa-graduation-cap',
                                    'text': f'Formation recommandée en {criterion}'})
        return suggestions or [{'type': 'info', 'icon': 'fa-check', 'text': 'Aucune action urgente'}]

    @api.model
    def _suggest_purchase(self, data):
        suggestions = []
        amount = data.get('amount_total', 0)
        if amount > 100000:
            suggestions.append({'type': 'info', 'icon': 'fa-percent',
                                'text': 'Négocier une remise volume sur cette commande importante'})
        suggestions.append({'type': 'info', 'icon': 'fa-balance-scale',
                            'text': 'Comparer avec au moins 3 fournisseurs pour les meilleurs tarifs'})
        suggestions.append({'type': 'info', 'icon': 'fa-calendar-check-o',
                            'text': 'Vérifier les délais de livraison du fournisseur'})
        return suggestions

    # =================================================================
    #  PROMPT BUILDERS (for API mode)
    # =================================================================
    @api.model
    def _build_analysis_prompt(self, data, analysis_type, module):
        return (
            f"Analyse de type '{analysis_type}' pour le module '{module}'.\n"
            f"Données : {json.dumps(data, ensure_ascii=False, default=str)}\n"
            f"Fournis une analyse structurée avec un score, des facteurs clés "
            f"et des recommandations concrètes."
        )

    @api.model
    def _build_suggest_prompt(self, record_data, suggestion_type, module):
        return (
            f"Suggestions de type '{suggestion_type}' pour le module '{module}'.\n"
            f"Données de l'enregistrement : {json.dumps(record_data, ensure_ascii=False, default=str)}\n"
            f"Propose 3 à 5 actions concrètes et priorisées."
        )
