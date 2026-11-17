from collections import defaultdict
from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

from odoo import api, fields, models
from odoo.exceptions import AccessError, ValidationError


class CofrialBIDashboard(models.AbstractModel):
    _name = "cofrial.bi.dashboard"
    _description = "Indicadores BI de Cofrial"

    def _sale_date_domain(self, period, date_from, date_to):
        allowed = (
            "all",
            "last_7_days",
            "last_30_days",
            "current_month",
            "current_year",
            "custom",
        )

        if period not in allowed:
            raise ValidationError("Periodo BI no valido.")

        if period == "all":
            if date_from is not None or date_to is not None:
                raise ValidationError("Fechas inesperadas.")
            return []

        if period != "custom" and (
            date_from is not None or date_to is not None
        ):
            raise ValidationError("Fechas inesperadas.")

        today = fields.Date.context_today(self)

        if period == "last_7_days":
            start = today - timedelta(days=6)
            end = today

        elif period == "last_30_days":
            start = today - timedelta(days=29)
            end = today

        elif period == "current_month":
            start = today.replace(day=1)
            end = today

        elif period == "current_year":
            start = today.replace(month=1, day=1)
            end = today

        else:
            if not isinstance(date_from, str) or not isinstance(date_to, str):
                raise ValidationError(
                    "Debe indicar ambas fechas."
                )

            try:
                start = date.fromisoformat(date_from)
                end = date.fromisoformat(date_to)
            except ValueError:
                raise ValidationError(
                    "Formato de fecha invalido."
                )

            if start > end:
                raise ValidationError(
                    "La fecha inicial supera la final."
                )

        tz = ZoneInfo(self.env.user.tz or "UTC")

        def inicio_utc(dia):
            local = datetime.combine(
                dia, time.min, tzinfo=tz
            )

            utc = local.astimezone(
                timezone.utc
            ).replace(tzinfo=None)

            return fields.Datetime.to_string(utc)

        return [
            ("date_order", ">=", inicio_utc(start)),
            (
                "date_order",
                "<",
                inicio_utc(end + timedelta(days=1)),
            ),
        ]

    @api.model
    def get_dashboard_data(
        self, period="all", date_from=None, date_to=None
    ):
        if not self.env.user.has_group(
            "base.group_system"
        ):
            raise AccessError(
                "No tiene permisos para consultar "
                "el dashboard de Cofrial."
            )

        Sale = self.env["sale.order"]
        CRM = self.env["crm.lead"]
        Reading = self.env["cofrial.iot.reading"]
        Fleet = self.env["fleet.vehicle"]

        date_domain = self._sale_date_domain(
            period, date_from, date_to
        )

        # Solo pedidos confirmados del periodo.
        orders = Sale.search(
            [("state", "in", ["sale", "done"])]
            + date_domain
        )

        sales_monthly = defaultdict(
            lambda: {
                "net": 0.0,
                "total": 0.0,
                "orders": 0,
            }
        )

        sales_daily = defaultdict(
            lambda: {
                "net": 0.0,
                "total": 0.0,
                "orders": 0,
            }
        )

        channels = {
            "web": {
                "orders": 0,
                "net": 0.0,
                "total": 0.0,
            },
            "internal": {
                "orders": 0,
                "net": 0.0,
                "total": 0.0,
            },
        }

        for order in orders:
            channel = (
                "web" if order.website_id
                else "internal"
            )

            channels[channel]["orders"] += 1
            channels[channel]["net"] += (
                order.amount_untaxed
            )
            channels[channel]["total"] += (
                order.amount_total
            )

            if order.date_order:
                local_datetime = fields.Datetime.context_timestamp(
                    order, order.date_order
                )

                month = local_datetime.strftime("%Y-%m")
                day = local_datetime.strftime("%Y-%m-%d")

                sales_monthly[month]["net"] += (
                    order.amount_untaxed
                )
                sales_monthly[month]["total"] += (
                    order.amount_total
                )
                sales_monthly[month]["orders"] += 1

                sales_daily[day]["net"] += (
                    order.amount_untaxed
                )
                sales_daily[day]["total"] += (
                    order.amount_total
                )
                sales_daily[day]["orders"] += 1

        opportunities = CRM.search([
            ("type", "=", "opportunity")
        ])

        return {
            "updated_at": fields.Datetime.to_string(
                fields.Datetime.now()
            ),
            "sales": {
                "period": period,
                "confirmed_orders": len(orders),
                "net": sum(
                    orders.mapped("amount_untaxed")
                ),
                "tax": sum(
                    orders.mapped("amount_tax")
                ),
                "total": sum(
                    orders.mapped("amount_total")
                ),
                "quotations": Sale.search_count(
                    [("state", "in", ["draft", "sent"])]
                    + date_domain
                ),
                "channels": channels,
                "daily": [
                    {
                        "date": day,
                        **values,
                    }
                    for day, values in sorted(
                        sales_daily.items()
                    )
                ],
                "monthly": [
                    {
                        "month": month,
                        **values,
                    }
                    for month, values in sorted(
                        sales_monthly.items()
                    )
                ],
            },
            "crm": {
                "opportunities": len(opportunities),
                "expected_revenue": sum(
                    opportunities.mapped(
                        "expected_revenue"
                    )
                ),
            },
            "iot": {
                "readings": Reading.search_count([]),
                "historical_alerts":
                    Reading.search_count([
                        (
                            "alerta_ruptura_frio",
                            "=",
                            True,
                        )
                    ]),
                "current_alerts":
                    Fleet.search_count([
                        (
                            "iot_current_thermal_alert",
                            "=",
                            True,
                        )
                    ]),
                "monitored_vehicles":
                    Fleet.search_count([
                        ("iot_monitor_enabled", "=", True)
                    ]),
            },
        }
