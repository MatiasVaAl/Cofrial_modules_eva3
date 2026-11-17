from odoo import api, fields, models
from odoo.exceptions import ValidationError


class CofrialIoTReading(models.Model):
    _name = "cofrial.iot.reading"
    _description = "Lectura IoT de camion refrigerado"
    _order = "fecha_lectura desc, id desc"

    name = fields.Char(
        string="Referencia",
        compute="_compute_name",
        store=True,
    )

    vehicle_id = fields.Many2one(
        "fleet.vehicle",
        string="Camion",
        required=True,
        index=True,
        ondelete="restrict",
    )

    company_id = fields.Many2one(
        "res.company",
        related="vehicle_id.company_id",
        store=True,
        index=True,
    )

    fecha_lectura = fields.Datetime(
        string="Fecha de lectura",
        required=True,
        default=fields.Datetime.now,
        index=True,
    )

    temp_monitored = fields.Boolean(
        string="Temperatura monitoreada",
        default=True,
    )

    temp_camara = fields.Float(
        string="Temperatura de camara (C)",
        required=False,
    )

    temp_display = fields.Char(
        string="Temperatura (°C)",
        compute="_compute_temp_display",
    )

    temp_min = fields.Float(
        string="Temperatura minima DEMO",
        default=0.0,
        required=True,
    )

    temp_max = fields.Float(
        string="Temperatura maxima DEMO",
        default=4.0,
        required=True,
    )

    lat = fields.Float(
        string="Latitud",
        digits=(10, 6),
    )

    long = fields.Float(
        string="Longitud",
        digits=(10, 6),
    )

    combustible_pct = fields.Float(
        string="Combustible (%)",
        default=100.0,
        required=True,
    )

    combustible_display = fields.Char(
        string="Combustible (%)",
        compute="_compute_combustible_display",
    )

    origen = fields.Selection(
        [
            ("manual", "Manual"),
            ("simulador", "Simulador"),
        ],
        string="Origen",
        default="manual",
        required=True,
    )

    alerta_ruptura_frio = fields.Boolean(
        string="Alerta termica",
        compute="_compute_alerta",
        store=True,
    )

    @api.depends("combustible_pct")
    def _compute_combustible_display(self):
        for rec in self:
            rec.combustible_display = (
                f"{rec.combustible_pct:.2f} %"
            )

    @api.depends("temp_monitored", "temp_camara")
    def _compute_temp_display(self):
        for rec in self:
            rec.temp_display = (
                f"{rec.temp_camara:.2f} °C"
                if rec.temp_monitored else "—"
            )

    @api.depends("vehicle_id", "fecha_lectura")
    def _compute_name(self):
        for rec in self:
            vehicle = rec.vehicle_id.display_name or "Sin camion"
            stamp = (
                fields.Datetime.to_string(rec.fecha_lectura)
                if rec.fecha_lectura else "Sin fecha"
            )
            rec.name = f"{vehicle} - {stamp}"

    @api.depends(
        "temp_monitored", "temp_camara", "temp_min", "temp_max"
    )
    def _compute_alerta(self):
        for rec in self:
            rec.alerta_ruptura_frio = bool(
                rec.temp_monitored
                and (
                    rec.temp_camara < rec.temp_min
                    or rec.temp_camara > rec.temp_max
                )
            )

    @api.constrains(
        "temp_monitored",
        "temp_min",
        "temp_max",
        "combustible_pct",
        "lat",
        "long",
    )
    def _check_reading(self):
        for rec in self:
            if rec.temp_monitored and rec.temp_min >= rec.temp_max:
                raise ValidationError(
                    "La temperatura minima debe ser menor que la maxima."
                )
            if not 0 <= rec.combustible_pct <= 100:
                raise ValidationError(
                    "El combustible debe estar entre 0 y 100%."
                )
            if not -90 <= rec.lat <= 90:
                raise ValidationError("Latitud fuera de rango.")
            if not -180 <= rec.long <= 180:
                raise ValidationError("Longitud fuera de rango.")
