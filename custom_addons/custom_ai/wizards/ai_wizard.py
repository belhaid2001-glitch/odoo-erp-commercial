# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class AIWizard(models.TransientModel):
    _name = 'ai.wizard'
    _description = 'Assistant IA'

    # Context fields
    res_model = fields.Char(string='Modèle source', required=True)
    res_id = fields.Integer(string='ID enregistrement')
    module_name = fields.Char(string='Module')

    # Input
    action_type = fields.Selection([
        ('generate_description', '📝 Générer une description'),
        ('analyze', '📊 Analyser les données'),
        ('suggest_price', '💰 Suggestion de prix/remise'),
        ('suggest_action', '🎯 Prochaine action recommandée'),
        ('generate_email', '📧 Générer un email'),
        ('evaluate', '📋 Synthèse d\'évaluation'),
        ('predict', '🔮 Prédiction'),
        ('btp_conseil', '🏗️ Mohasib — Conseil fiscal/comptable'),
        ('btp_saisie', '📒 Mohasib — Écriture comptable PCM'),
        ('btp_analyse', '📊 Mohasib — Analyse financière chantier'),
        ('custom', '✏️ Requête personnalisée'),
    ], string='Action IA', required=True, default='analyze')

    custom_prompt = fields.Text(string='Requête personnalisée',
                                help="Décrivez ce que vous souhaitez que l'IA fasse")

    # Output
    ai_result = fields.Html(string='Résultat IA', readonly=True)
    ai_provider = fields.Char(string='Source', readonly=True)

    @api.onchange('action_type')
    def _onchange_action_type(self):
        if self.action_type == 'custom':
            self.custom_prompt = ''
        elif self.action_type in ('btp_conseil', 'btp_saisie'):
            self.custom_prompt = ''

    def action_generate(self):
        """Execute the AI action and display results."""
        self.ensure_one()
        mixin = self.env['ai.mixin']

        # Gather context data from the source record
        ctx = self._get_record_context()

        # Build prompt based on action type
        prompts = {
            'generate_description': f"Génère une description commerciale pour : {ctx.get('name', '')}",
            'analyze': f"Analyse complète de cet enregistrement",
            'suggest_price': f"Suggestion de prix et remise pour cette commande",
            'suggest_action': f"Quelle est la prochaine action recommandée ?",
            'generate_email': f"Génère un email de relance professionnel",
            'evaluate': f"Génère une synthèse d'évaluation",
            'predict': f"Fais une prédiction basée sur les données disponibles",
            'btp_conseil': self.custom_prompt or "Comment fonctionne la TVA BTP au Maroc ?",
            'btp_saisie': self.custom_prompt or "Comptabilise la situation de travaux",
            'btp_analyse': f"Analyse financière complète du chantier {ctx.get('name', '')}",
            'custom': self.custom_prompt or "Analyse cette situation",
        }
        prompt = prompts.get(self.action_type, self.custom_prompt)
        # Force module to 'btp' for Mohasib action types
        if self.action_type in ('btp_conseil', 'btp_saisie', 'btp_analyse'):
            module = 'btp'
        else:
            module = self.module_name or 'general'

        # Call AI
        result = mixin.ai_generate(prompt, ctx, module)

        # Format result as HTML
        text = result.get('result', 'Aucun résultat')
        html_result = self._format_result_html(text, result.get('provider', 'builtin'))

        self.write({
            'ai_result': html_result,
            'ai_provider': result.get('provider', 'builtin'),
        })

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'ai.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
            'name': '🤖 Résultat IA',
        }

    def _get_record_context(self):
        """Extract context data from the source record."""
        ctx = {}
        if not self.res_model or not self.res_id:
            return ctx

        try:
            record = self.env[self.res_model].browse(self.res_id)
            if not record.exists():
                return ctx

            # Common fields
            for f in ['name', 'display_name']:
                if hasattr(record, f):
                    ctx[f] = getattr(record, f) or ''

            # Sale order fields
            if self.res_model == 'sale.order':
                ctx.update({
                    'partner_name': record.partner_id.name if record.partner_id else '',
                    'amount_total': record.amount_total or 0,
                    'state': record.state or '',
                })
                if hasattr(record, 'margin_percent'):
                    ctx['margin_percent'] = record.margin_percent or 0
                if hasattr(record, 'sale_type'):
                    ctx['sale_type'] = record.sale_type or ''
                # Check if returning customer
                prev_orders = self.env['sale.order'].search_count([
                    ('partner_id', '=', record.partner_id.id),
                    ('state', 'in', ['sale', 'done']),
                    ('id', '!=', record.id),
                ])
                ctx['is_returning_customer'] = prev_orders > 0

            # CRM lead fields
            elif self.res_model == 'crm.lead':
                ctx.update({
                    'expected_revenue': record.expected_revenue or 0,
                    'probability': record.probability or 0,
                })
                if hasattr(record, 'lead_quality'):
                    ctx['lead_quality'] = record.lead_quality or 'warm'
                if hasattr(record, 'days_since_last_contact'):
                    ctx['days_since_last_contact'] = record.days_since_last_contact or 0
                if hasattr(record, 'call_count'):
                    ctx['call_count'] = record.call_count or 0

            # HR evaluation fields
            elif self.res_model == 'hr.evaluation':
                if hasattr(record, 'employee_id'):
                    ctx['employee_name'] = record.employee_id.name or ''
                if hasattr(record, 'global_score'):
                    ctx['global_score'] = record.global_score or 0
                scores = {}
                for f in ['quality_score', 'productivity_score', 'initiative_score',
                           'teamwork_score', 'punctuality_score', 'communication_score']:
                    if hasattr(record, f):
                        label = f.replace('_score', '').capitalize()
                        scores[label] = getattr(record, f) or 0
                ctx['scores'] = scores

            # Account move fields
            elif self.res_model == 'account.move':
                ctx.update({
                    'partner_name': record.partner_id.name if record.partner_id else '',
                    'amount_residual': record.amount_residual or 0,
                })
                if hasattr(record, 'days_overdue'):
                    ctx['days_overdue'] = record.days_overdue or 0
                if hasattr(record, 'risk_level'):
                    ctx['risk_level'] = record.risk_level or 'low'

            # Purchase order fields
            elif self.res_model == 'purchase.order':
                ctx.update({
                    'partner_name': record.partner_id.name if record.partner_id else '',
                    'amount_total': record.amount_total or 0,
                    'state': record.state or '',
                })

            # BTP Chantier fields
            elif self.res_model == 'btp.chantier':
                ctx.update({
                    'chantier_name': record.name or '',
                    'reference': record.reference or '',
                    'montant_total': record.montant_total or 0,
                    'montant_contrat': record.montant_contrat or 0,
                    'montant_avenant': record.montant_avenant or 0,
                    'taux_avancement': record.taux_avancement or 0,
                    'retard_jours': record.retard_jours or 0,
                    'penalite_retard': record.penalite_retard or 0,
                    'state': record.state or '',
                    'type_marche': record.type_marche or '',
                    'taux_retenue_garantie': record.taux_retenue_garantie or '',
                    'montant_retenue': record.montant_retenue or 0,
                    'caution_provisoire': record.caution_provisoire or 0,
                    'caution_definitive': record.caution_definitive or 0,
                    'partner_name': record.maitre_ouvrage_id.name if record.maitre_ouvrage_id else '',
                    'client': record.maitre_ouvrage_id.name if record.maitre_ouvrage_id else '',
                    'ville': record.ville or '',
                    'situation_count': record.situation_count or 0,
                })

            # BTP Situation fields
            elif self.res_model == 'btp.situation':
                ctx.update({
                    'amount_total': getattr(record, 'montant_ht', 0) or 0,
                    'montant': getattr(record, 'montant_ht', 0) or 0,
                    'state': record.state if hasattr(record, 'state') else '',
                    'partner_name': record.chantier_id.maitre_ouvrage_id.name if hasattr(record, 'chantier_id') and record.chantier_id and record.chantier_id.maitre_ouvrage_id else '',
                    'chantier_name': record.chantier_id.name if hasattr(record, 'chantier_id') and record.chantier_id else '',
                })

            # BTP Approvisionnement fields
            elif self.res_model == 'btp.approvisionnement':
                ctx.update({
                    'amount_total': getattr(record, 'cout_total', 0) or 0,
                    'montant': getattr(record, 'cout_total', 0) or 0,
                    'state': record.state if hasattr(record, 'state') else '',
                    'partner_name': record.fournisseur_id.name if hasattr(record, 'fournisseur_id') and record.fournisseur_id else '',
                    'chantier_name': record.chantier_id.name if hasattr(record, 'chantier_id') and record.chantier_id else '',
                })

        except Exception:
            pass
        return ctx

    def _format_result_html(self, text, provider):
        """Convert plain text AI result to styled HTML."""
        # Escape HTML
        text = (text or '').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        # Convert markdown-like formatting
        lines = text.split('\n')
        html_lines = []
        for line in lines:
            stripped = line.strip()
            if not stripped:
                html_lines.append('<br/>')
            elif stripped.startswith('•') or stripped.startswith('-'):
                html_lines.append(f'<li style="margin-left:20px;">{stripped[1:].strip()}</li>')
            elif stripped.startswith('🔴') or stripped.startswith('⚠️'):
                html_lines.append(
                    f'<div style="padding:8px 12px;background:#fff5f5;border-left:4px solid #e74a3b;'
                    f'margin:4px 0;border-radius:4px;">{stripped}</div>')
            elif stripped.startswith('🟢') or stripped.startswith('✅'):
                html_lines.append(
                    f'<div style="padding:8px 12px;background:#f0fff4;border-left:4px solid #1cc88a;'
                    f'margin:4px 0;border-radius:4px;">{stripped}</div>')
            elif stripped.startswith('🟠') or stripped.startswith('🟡'):
                html_lines.append(
                    f'<div style="padding:8px 12px;background:#fffbeb;border-left:4px solid #f6c23e;'
                    f'margin:4px 0;border-radius:4px;">{stripped}</div>')
            elif any(stripped.startswith(e) for e in ['📊', '📈', '🎯', '📋', '💰', '📧', '📦', '💳', '📄', '📌']):
                html_lines.append(f'<h4 style="margin:12px 0 6px;color:#2c3e50;">{stripped}</h4>')
            elif stripped.startswith('🏗️'):
                html_lines.append(
                    f'<div style="padding:10px 14px;background:linear-gradient(135deg,#1e3a5f,#2c5f8a);'
                    f'color:white;border-radius:6px;margin:8px 0;font-weight:bold;font-size:14px;">'
                    f'{stripped}</div>')
            elif stripped.startswith('┌') or stripped.startswith('├') or stripped.startswith('└') or stripped.startswith('│'):
                html_lines.append(f'<pre style="margin:0;padding:0 4px;font-size:11px;'
                                  f'line-height:1.6;background:#f8f9fc;font-family:Consolas,monospace;">'
                                  f'{stripped}</pre>')
            else:
                html_lines.append(f'<p style="margin:2px 0;">{stripped}</p>')

        provider_label = '🤖 Intelligence intégrée' if provider == 'builtin' else '🌐 API IA'
        badge_color = '#36b9cc' if provider == 'builtin' else '#4e73df'

        return (
            f'<div style="font-family:Segoe UI,sans-serif;padding:16px;background:#f8f9fc;'
            f'border-radius:8px;">'
            f'<div style="display:inline-block;padding:2px 10px;background:{badge_color};'
            f'color:white;border-radius:12px;font-size:11px;margin-bottom:12px;">'
            f'{provider_label}</div>'
            f'<div style="margin-top:8px;">{"".join(html_lines)}</div>'
            f'</div>'
        )

    def action_apply(self):
        """Apply the AI suggestion to the source record (placeholder for extensions)."""
        self.ensure_one()
        return {'type': 'ir.actions.act_window_close'}
