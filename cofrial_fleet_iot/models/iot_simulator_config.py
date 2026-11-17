from odoo import api, fields, models
from odoo.exceptions import ValidationError


class CofrialIoTSimulatorConfig(models.Model):
    _name = "cofrial.iot.simulator.config"
    _description = "Configuracion del simulador IoT"

    name = fields.Char(
        string="Nombre",
        default="Simulador IoT Cofrial",
        readonly=True,
        required=True,
    )

    enabled = fields.Boolean(
        string="Simulacion habilitada",
        default=True,
    )

    interval_number = fields.Integer(
        string="Ejecutar cada",
        required=True,
        default=5,
    )

    interval_type = fields.Selection(
        [
            ("minutes", "Minutos"),
            ("hours", "Horas"),
        ],
        string="Unidad de tiempo",
        required=True,
        default="minutes",
    )

    @api.constrains("interval_number", "interval_type")
    def _check_interval(self):
        for record in self:
            number = record.interval_number

            if number < 1:
                raise ValidationError(
                    "El intervalo debe ser mayor o igual a 1."
                )

            maximum = (
                1440 if record.interval_type == "minutes"
                else 24
            )

            if number > maximum:
                raise ValidationError(
                    "El intervalo supera el maximo permitido."
                )
