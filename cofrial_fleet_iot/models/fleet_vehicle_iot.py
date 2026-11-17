from odoo import api, fields, models


class FleetVehicleIoT(models.Model):
    _inherit = "fleet.vehicle"

    iot_reading_ids = fields.One2many(
        "cofrial.iot.reading",
        "vehicle_id",
        string="Lecturas IoT",
        readonly=True,
    )

    iot_has_reading = fields.Boolean(
        compute="_compute_iot_dashboard"
    )

    iot_last_has_temp = fields.Boolean(
        compute="_compute_iot_dashboard"
    )

    iot_last_temp = fields.Float(
        compute="_compute_iot_dashboard",
        digits=(8, 2),
    )

    iot_last_fuel = fields.Float(
        compute="_compute_iot_dashboard",
        digits=(8, 2),
    )

    iot_last_alert = fields.Boolean(
        compute="_compute_iot_dashboard"
    )

    iot_current_thermal_alert = fields.Boolean(
        string="Alerta termica actual",
        compute="_compute_iot_current_thermal_alert",
        store=True,
        index=True,
    )

    iot_last_datetime = fields.Datetime(
        compute="_compute_iot_dashboard"
    )

    iot_last_lat = fields.Float(
        compute="_compute_iot_dashboard",
        digits=(10, 6),
    )

    iot_last_long = fields.Float(
        compute="_compute_iot_dashboard",
        digits=(10, 6),
    )

    def _iot_alerta_actual(self, lectura):
        self.ensure_one()

        return bool(
            self.iot_monitor_enabled
            and self.iot_temp_monitor_enabled
            and lectura
            and lectura.temp_monitored
            and (
                lectura.temp_camara < self.iot_temp_min
                or lectura.temp_camara > self.iot_temp_max
            )
        )

    @api.depends(
        "iot_monitor_enabled",
        "iot_temp_monitor_enabled",
        "iot_temp_min",
        "iot_temp_max",
        "iot_reading_ids",
        "iot_reading_ids.fecha_lectura",
        "iot_reading_ids.temp_monitored",
        "iot_reading_ids.temp_camara",
        "iot_reading_ids.combustible_pct",
        "iot_reading_ids.lat",
        "iot_reading_ids.long",
    )
    def _compute_iot_dashboard(self):
        Reading = self.env["cofrial.iot.reading"]

        for vehicle in self:
            last = Reading.search(
                [("vehicle_id", "=", vehicle.id)],
                order="fecha_lectura desc, id desc",
                limit=1,
            )

            vehicle.iot_has_reading = bool(last)

            vehicle.iot_last_has_temp = bool(
                last and last.temp_monitored
            )

            vehicle.iot_last_temp = (
                last.temp_camara if last else 0.0
            )

            vehicle.iot_last_fuel = (
                last.combustible_pct if last else 0.0
            )

            vehicle.iot_last_alert = (
                vehicle._iot_alerta_actual(last)
            )

            vehicle.iot_last_datetime = (
                last.fecha_lectura if last else False
            )

            vehicle.iot_last_lat = (
                last.lat if last else 0.0
            )

            vehicle.iot_last_long = (
                last.long if last else 0.0
            )

    @api.depends(
        "iot_monitor_enabled",
        "iot_temp_monitor_enabled",
        "iot_temp_min",
        "iot_temp_max",
        "iot_reading_ids",
        "iot_reading_ids.fecha_lectura",
        "iot_reading_ids.temp_monitored",
        "iot_reading_ids.temp_camara",
    )
    def _compute_iot_current_thermal_alert(self):
        Reading = self.env["cofrial.iot.reading"]

        for vehicle in self:
            last = Reading.search(
                [("vehicle_id", "=", vehicle.id)],
                order="fecha_lectura desc, id desc",
                limit=1,
            )

            vehicle.iot_current_thermal_alert = (
                vehicle._iot_alerta_actual(last)
            )
