/** @odoo-module **/

import {ImportRecords} from "@base_import/import_records/import_records";
import {patch} from "@web/core/utils/patch";

patch(ImportRecords.prototype, {
    importRecords() {
    	const { context, resModel } = this.env.searchModel;
        this.action.doAction({
        	type: 'ir.actions.act_window',
            target: 'current',
            res_model: 'import.data',
            views: [[false, 'form']],
            view_id: 'vks_import_excel.view_import_data_form',
            context: {...context, ...{
                'model_name_tmp': resModel,
                'form_view_ref':false}}
        });
    }
});