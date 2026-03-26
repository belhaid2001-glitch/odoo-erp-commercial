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
            'custom': self.custom_prompt or "Analyse cette situation",
        }
        prompt = prompts.get(self.action_type, self.custom_prompt)
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
            elif any(stripped.startswith(e) for e in ['📊', '📈', '🎯', '📋', '💰', '📧', '📦', '💳']):
                html_lines.append(f'<h4 style="margin:12px 0 6px;color:#2c3e50;">{stripped}</h4>')
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
