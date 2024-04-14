/** @odoo-module */

import {patch} from "@web/core/utils/patch";
import {ListController} from '@web/views/list/list_controller';
import { ExportDataDialog } from "@web/views/view_dialogs/export_data_dialog";

patch(ListController.prototype, {
    async onExportData() {
        const dialogProps = {
            context: this.props.context,
            defaultExportList: this.defaultExportList,
            download: this.downloadExport.bind(this),
            getExportedFields: this.getExportedFields.bind(this),
            root: this.model.root,
            vks_parent:this,
        };
        this.dialogService.add(ExportDataDialog, dialogProps);
    },

});