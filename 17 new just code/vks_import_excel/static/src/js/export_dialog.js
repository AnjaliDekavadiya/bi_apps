/** @odoo-module */

import {patch} from "@web/core/utils/patch";
import { ExportDataDialog } from "@web/views/view_dialogs/export_data_dialog";
import {useService} from "@web/core/utils/hooks";
import {Component, onWillStart, useSubEnv, useEffect, useRef} from "@odoo/owl";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { _t } from "@web/core/l10n/translation";

ExportDataDialog.props = {
    close: { type: Function },
    context: { type: Object, optional: true },
    defaultExportList: { type: Array },
    download: { type: Function },
    getExportedFields: { type: Function },
    root: { type: Object },
    vks_parent: { type: Object },
};

patch(ExportDataDialog.prototype, {
    setup() {
        this.orm = useService("orm");
        this.dialogService = useService('dialog');
        this.actionService = useService("action");
        super.setup();
        onWillStart(async () => {
        	this.state.templateId = null;
        });
    },
    
    async on_click_view_export_data() {
    	this.vks_export_data_to_excel('view');
    },
    
    async on_click_edit_export_data() {
    	this.vks_export_data_to_excel('edit');
    },
    
    async onClickExportButton() {
    	super.onClickExportButton();
    	//this.on_click_view_export_data();
    },

    async vks_export_data_to_excel(export_type_selected) {
    	var tmp_export_id = this.state.templateId;
    	if (!tmp_export_id || tmp_export_id == "new_template") {
    		this.dialogService.add(AlertDialog, {
                title: _t('Error'),
                body: _t("Please choose a export template!"),
                confirmLabel: _t('Ok'),
            });
    	}
    	else{
    		var tmp_list_controller = this.props.vks_parent;
        	var tmp_list_view = this.props.root;
        	var tmp_resIds = await tmp_list_controller.getSelectedResIds();
    		var tmp_params  = {'export_type_selected':export_type_selected,
					'export_id':parseInt(tmp_export_id),
					'record_ids_to_export':tmp_resIds,
					'sort_condition':tmp_list_view.orderBy,
					'context': this.props.context
			};
    		var tmp_result = await this.orm.call('ir.exports', 'export_to_excel_from_export_base_form', [], tmp_params);
    		this.actionService.doAction({
                type: 'ir.actions.act_url',
                //target: 'self',
                target: 'download',
                url: tmp_result
            });
    	}
    },
    
    //Ghi de 1 so ham de chac chan neu thay doi lua chon field xuat ra thi bat buoc phai luu template moi cho xuat theo 2 button custom
    vks_make_selected_template_empty() {
    	this.state.templateId = null;
    },
    
    onDraggingEnd(item, target) {
        this.state.exportList.splice(target, 0, this.state.exportList.splice(item, 1)[0]);
        this.vks_make_selected_template_empty();
    },

    onAddItemExportList(fieldId) {
        this.state.exportList.push(this.knownFields[fieldId]);
        this.enterTemplateEdition();
        this.vks_make_selected_template_empty();
    },

    onRemoveItemExportList(fieldId) {
        const item = this.state.exportList.findIndex(({ id }) => id === fieldId);
        this.state.exportList.splice(item, 1);
        this.enterTemplateEdition();
        this.vks_make_selected_template_empty();
    },
    
});