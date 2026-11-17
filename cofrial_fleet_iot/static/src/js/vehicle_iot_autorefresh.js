/** @odoo-module **/

import { KanbanController } from "@web/views/kanban/kanban_controller";
import { kanbanView } from "@web/views/kanban/kanban_view";
import { registry } from "@web/core/registry";
import { onMounted, onWillUnmount } from "@odoo/owl";

const REFRESH_INTERVAL = 30000;

export class CofrialIoTKanbanController extends KanbanController {
    setup() {
        super.setup();

        let timer = null;
        let active = false;
        let refreshing = false;

        onMounted(() => {
            active = true;

            timer = setInterval(async () => {
                if (
                    !active ||
                    refreshing ||
                    document.visibilityState === "hidden"
                ) {
                    return;
                }

                refreshing = true;

                try {
                    await this.model.load();
                } catch (error) {
                    console.warn(
                        "Cofrial IoT: error al actualizar dashboard",
                        error
                    );
                } finally {
                    refreshing = false;
                }
            }, REFRESH_INTERVAL);
        });

        onWillUnmount(() => {
            active = false;

            if (timer !== null) {
                clearInterval(timer);
                timer = null;
            }
        });
    }
}

registry.category("views").add("cofrial_iot_autorefresh", {
    ...kanbanView,
    Controller: CofrialIoTKanbanController,
});
