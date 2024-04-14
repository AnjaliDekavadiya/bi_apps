/** @odoo-module */

import { ListController } from "@web/views/list/list_controller";
import { registry } from '@web/core/registry';
import { listView } from '@web/views/list/list_view';

export class SAMListController extends ListController {

   setup() {
       super.setup();
   }

   openImportRec() {
       this.actionService.doAction({
          type: 'ir.actions.act_window',
          res_model: 'sam.import.document',
          name:'Import',
          view_mode: 'form',
          view_type: 'form',
          views: [[false, 'form']],
      });
   }
}
registry.category("views").add("sam_import_button", {
   ...listView,
   Controller: SAMListController,
   buttonTemplate: "sam_btn_import.ListView.Buttons",
});