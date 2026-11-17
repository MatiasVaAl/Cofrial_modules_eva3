/** @odoo-module **/

import {
    Component,
    onWillStart,
    onMounted,
    onWillUnmount,
    useState,
} from "@odoo/owl";

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class CofrialBIDashboard extends Component {
    static template = "cofrial_bi.Dashboard";

    setup() {
        this.orm = useService("orm");

        this.state = useState({
            data: null,
            loading: false,
            error: null,
            filterError: null,
            period: "all",
            dateFrom: "",
            dateTo: "",
            appliedPeriod: "all",
            appliedFrom: "",
            appliedTo: "",
            displayPeriod: "all",
            displayFrom: "",
            displayTo: "",
        });

        this.refreshing = false;
        this.timer = null;

        onWillStart(() => this.refresh());

        onMounted(() => {
            this.timer = setInterval(() => {
                if (document.visibilityState === "visible") {
                    this.refresh();
                }
            }, 30000);
        });

        onWillUnmount(() => {
            if (this.timer) {
                clearInterval(this.timer);
            }
        });
    }

    async refresh() {
        if (this.refreshing) {
            return;
        }

        this.refreshing = true;
        this.state.loading = true;

        try {
            const kwargs = {
                period: this.state.appliedPeriod,
            };

            if (this.state.appliedPeriod === "custom") {
                kwargs.date_from = this.state.appliedFrom;
                kwargs.date_to = this.state.appliedTo;
            }

            const data = await this.orm.call(
                "cofrial.bi.dashboard",
                "get_dashboard_data",
                [],
                kwargs
            );

            this.state.data = data;
            this.state.displayPeriod = data.sales.period;
            this.state.displayFrom = this.state.appliedFrom;
            this.state.displayTo = this.state.appliedTo;
            this.state.error = null;
        } catch (error) {
            console.error("Cofrial BI:", error);
            this.state.error =
                "No fue posible actualizar los indicadores.";
        } finally {
            this.state.loading = false;
            this.refreshing = false;
        }
    }

    onPeriodChange(event) {
        this.state.period = event.target.value;
        this.state.filterError = null;
    }

    onDateFromChange(event) {
        this.state.dateFrom = event.target.value;
        this.state.filterError = null;
    }

    onDateToChange(event) {
        this.state.dateTo = event.target.value;
        this.state.filterError = null;
    }

    async applyFilters() {
        if (this.refreshing) {
            return;
        }

        if (this.state.period === "custom") {
            if (!this.state.dateFrom || !this.state.dateTo) {
                this.state.filterError =
                    "Seleccione ambas fechas.";
                return;
            }

            if (this.state.dateFrom > this.state.dateTo) {
                this.state.filterError =
                    "La fecha inicial supera la fecha final.";
                return;
            }
        }

        this.state.filterError = null;
        this.state.appliedPeriod = this.state.period;

        this.state.appliedFrom =
            this.state.period === "custom"
                ? this.state.dateFrom
                : "";

        this.state.appliedTo =
            this.state.period === "custom"
                ? this.state.dateTo
                : "";

        await this.refresh();
    }

    get appliedPeriodLabel() {
        if (this.state.displayPeriod === "custom") {
            return (
                this.state.displayFrom
                + " a "
                + this.state.displayTo
            );
        }

        const labels = {
            all: "Todo el historial",
            last_7_days: "Ultimos 7 dias",
            last_30_days: "Ultimos 30 dias",
            current_month: "Mes actual",
            current_year: "Ano actual",
        };

        return labels[this.state.displayPeriod]
            || "Todo el historial";
    }

    formatCLP(value) {
        return new Intl.NumberFormat("es-CL", {
            style: "currency",
            currency: "CLP",
            maximumFractionDigits: 0,
        }).format(Number(value) || 0);
    }

    get days() {
        return this.state.data?.sales?.daily || [];
    }

    dayBarStyle(value) {
        const max = Math.max(
            1,
            ...this.days.map(
                (item) => Number(item.net) || 0
            )
        );

        const percent = Math.max(
            0,
            Math.min(
                100,
                Math.round(
                    (Number(value) || 0) / max * 100
                )
            )
        );

        return `width: ${percent}%;`;
    }

    get months() {
        return this.state.data?.sales?.monthly || [];
    }

    barStyle(value) {
        const max = Math.max(
            1,
            ...this.months.map((item) => Number(item.net) || 0)
        );

        const percent = Math.max(
            0,
            Math.min(100, Math.round((Number(value) || 0) / max * 100))
        );

        return `width: ${percent}%;`;
    }
}

registry.category("actions").add(
    "cofrial_bi.dashboard",
    CofrialBIDashboard
);
