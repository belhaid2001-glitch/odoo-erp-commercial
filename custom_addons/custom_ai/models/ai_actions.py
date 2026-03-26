# -*- coding: utf-8 -*-
"""
Adds the action_open_ai_wizard() method to all models that need AI buttons.
Uses monkey-patching via _inherit to inject the method into existing models.
"""
from odoo import models, api


class SaleOrderAI(models.Model):
    _inherit = 'sale.order'

    def action_open_ai_wizard(self):
        return self._open_ai_wizard('sale')


class CrmLeadAI(models.Model):
    _inherit = 'crm.lead'

    def action_open_ai_wizard(self):
        return self._open_ai_wizard('crm')


class PurchaseOrderAI(models.Model):
    _inherit = 'purchase.order'

    def action_open_ai_wizard(self):
        return self._open_ai_wizard('purchase')


class AccountMoveAI(models.Model):
    _inherit = 'account.move'

    def action_open_ai_wizard(self):
        return self._open_ai_wizard('accounting')


class StockPickingAI(models.Model):
    _inherit = 'stock.picking'

    def action_open_ai_wizard(self):
        return self._open_ai_wizard('stock')


class HrEmployeeAI(models.Model):
    _inherit = 'hr.employee'

    def action_open_ai_wizard(self):
        return self._open_ai_wizard('hr')


class ResPartnerAI(models.Model):
    _inherit = 'res.partner'

    def action_open_ai_wizard(self):
        return self._open_ai_wizard('contacts')


class BaseModelAI(models.AbstractModel):
    """Inject _open_ai_wizard into base model so all models can use it."""
    _inherit = 'base'

    def _open_ai_wizard(self, module_name='general'):
        self.ensure_one()
        wizard = self.env['ai.wizard'].create({
            'res_model': self._name,
            'res_id': self.id,
            'module_name': module_name,
        })
        return {
            'type': 'ir.actions.act_window',
            'name': '🤖 Assistant IA',
            'res_model': 'ai.wizard',
            'res_id': wizard.id,
            'view_mode': 'form',
            'target': 'new',
        }
