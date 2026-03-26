# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    ai_provider = fields.Selection([
        ('builtin', 'Intelligence intégrée (sans API)'),
        ('openai', 'OpenAI (ChatGPT)'),
        ('ollama', 'Ollama (Local)'),
    ], string="Fournisseur IA",
        config_parameter='custom_ai.provider',
        default='builtin')

    ai_api_key = fields.Char(
        string="Clé API",
        config_parameter='custom_ai.api_key',
        help="Clé API OpenAI (commence par sk-...)")

    ai_api_url = fields.Char(
        string="URL API",
        config_parameter='custom_ai.api_url',
        default='https://api.openai.com/v1',
        help="URL de l'API. Pour Ollama local: http://localhost:11434/v1")

    ai_model = fields.Char(
        string="Modèle IA",
        config_parameter='custom_ai.model',
        default='gpt-3.5-turbo',
        help="Modèle à utiliser (gpt-3.5-turbo, gpt-4, llama2, etc.)")

    ai_temperature = fields.Float(
        string="Température",
        config_parameter='custom_ai.temperature',
        default=0.7,
        help="Créativité des réponses (0=précis, 1=créatif)")
