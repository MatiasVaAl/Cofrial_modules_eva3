from odoo import api, fields, models
from odoo.exceptions import ValidationError


class FleetVehicleMonitoring(models.Model):
    _inherit = "fleet.vehicle"

    iot_monitor_enabled = fields.Boolean(
        string="Monitorear flota",
        default=False,
        index=True,
    )

    iot_temp_monitor_enabled = fields.Boolean(
        string="Monitorear temperatura",
        default=False,
        index=True,
    )

    iot_temp_min = fields.Float(
        string="Temperatura minima (°C)",
        default=0.0,
    )

    iot_temp_max = fields.Float(
        string="Temperatura maxima (°C)",
        default=4.0,
    )

    @api.onchange("iot_monitor_enabled")
    def _onchange_monitoring(self):
        for vehicle in self:
            if not vehicle.iot_monitor_enabled:
                vehicle.iot_temp_monitor_enabled = False

    def write(self, vals):
        if vals.get("iot_monitor_enabled") is False:
            vals = {
                **vals,
                "iot_temp_monitor_enabled": False,
            }

        return super().write(vals)

    @api.constrains(
        "iot_monitor_enabled",
        "iot_temp_monitor_enabled",
        "iot_temp_min",
        "iot_temp_max",
    )
    def _check_monitoring(self):
        for vehicle in self:
            if (
                vehicle.iot_temp_monitor_enabled
                and not vehicle.iot_monitor_enabled
            ):
                raise ValidationError(
                    "Para monitorear temperatura debe "
                    "activar primero Monitorear flota."
                )

            if (
                vehicle.iot_temp_monitor_enabled
                and vehicle.iot_temp_min >= vehicle.iot_temp_max
            ):
                raise ValidationError(
                    "La temperatura minima debe ser "
                    "menor que la maxima."
                )
