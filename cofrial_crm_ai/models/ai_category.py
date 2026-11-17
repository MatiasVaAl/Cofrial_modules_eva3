from odoo import fields, models


class CofrialAICategory(models.Model):
    _name = "cofrial.ai.category"
    _description = "Categoria de consulta comercial COFRIAL"
    _order = "name"

    active = fields.Boolean(
        string="Activa",
        default=True,
    )

    name = fields.Char(
        string="Categoria",
        required=True,
        index=True,
    )
