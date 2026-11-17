from odoo import fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    cofrial_gemini_api_key = fields.Char(
        string="API Key de Gemini",
        config_parameter="cofrial_crm_ai.gemini_api_key",
        groups="base.group_system",
    )
