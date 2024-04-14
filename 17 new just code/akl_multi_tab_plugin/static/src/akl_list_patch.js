/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { ListRenderer } from "@web/views/list/list_renderer";


patch(ListRenderer.prototype, {
    freezeColumnWidths() {
        if (!$(this.tableRef.el).is(":visible")) {
            return;
        }
        super.freezeColumnWidths(this, arguments);
    }
});