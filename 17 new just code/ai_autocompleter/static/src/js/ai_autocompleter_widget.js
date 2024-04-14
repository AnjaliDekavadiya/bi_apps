/** @odoo-module **/

import { loadBundle } from "@web/core/assets";
import { Wysiwyg } from "@web_editor/js/wysiwyg/wysiwyg";
export class IADialog extends Wysiwyg {

    /**
     * @override
     */
    _getPowerboxOptions() {
        const options = super._getPowerboxOptions(...arguments);
        const {commands, categories} = options;
        categories.push({ name: _t('Navigation'), priority: 40 });
        commands.push(
            {
            category: _t("IA"),
            name: _t("IA Complete"),
            priority: 110,
            description: _t("Autocompletado por IA."),
            fontawesome: "fa-info-circle",
            callback: async () => {
              const dialog = new AIModal(this, {});
              dialog.on("save", this, (data) => {
                if (data) {
                  console.log(data);
                  console.log("--------------------");
                  dialog.close();
                  this.focus();
                  this.odooEditor.execCommand("insert", parseHTML(data));
                }
              });
              dialog.open();
            },
          },
        );
        return {...options, commands, categories};
    }
}
