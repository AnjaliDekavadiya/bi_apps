/** @odoo-module alias=xxxx_module **/

import { ActionContainer } from "@web/webclient/actions/action_container";
import { patch } from "@web/core/utils/patch";
import { AklMultiTab } from "./components/multi_tab/akl_multi_tab";

import {
    xml,
    useState
} from "@odoo/owl";


import { useService } from "@web/core/utils/hooks";

patch(ActionContainer.prototype, {
    
    setup() {
        super.setup(arguments);
        
        this.action_infos = useState([]);
        this.action_service = useService("action");

        // add the action to the actions stack
        this.env.bus.addEventListener("ACTION_MANAGER:UPDATE", ({ detail: info }) => {

            for (var i = 0; i < this.action_infos.length; i++) {
                var action_info = this.action_infos[i];
                if (action_info == info) {
                    continue;
                }
                action_info.active = false;
            }

            // init the active state
            info.active = true;

            // get old action info
            let old_action_info = this.get_action_info(info);
            if (old_action_info) {
                // update old action info
                var index = this.action_infos.indexOf(old_action_info);
                this.action_infos.splice(index, 1, info);
            } else {
                this.action_infos.push(info);
            }

            //  set current action info
            this._set_current_action_stack(info);
        });

        this.env.bus.addEventListener("AKL_MULTI_PLUGIN:REMOVE", (action_info) => {
            var index = this.action_infos.indexOf(action_info);
            this.action_infos.splice(index, 1);
            this.render();
        });
    },

    get_action_info(action_info, options) {
        var action = action_info.componentProps.action || action_info.action;
        while (action.ref_action) {
            action = action.ref_action;
            if (action == action.ref_action) {
                break;
            }
        }

        let context = JSON.parse(JSON.stringify(action.context || {}))
        if (!context.params) {
            context.params = {}
        } else {
            delete context.params['action']
            delete context.params['cids']
            delete context.params['model']
            delete context.params['view_type']
            delete context.params['menu_id']
        }

        for(var key in context) {
            // check start with search_default_
            if (key.indexOf('search_default_') != -1) {
                delete context[key]
            }
        }

        var old_action_info = this.action_infos.find((action_info) => {
            var tmp_action = action_info.componentProps.action || action_info.action;
            while (tmp_action.ref_action) {
                tmp_action = tmp_action.ref_action;
                if (tmp_action == tmp_action.ref_action) {
                    break;
                }
            }
            // clone context to prevent it
            var tmp_context = tmp_action.context || {};
            if (!tmp_context.params) {
                tmp_context.params = {}
            } else {
                delete tmp_context.params['action']
                delete tmp_context.params['cids']
                delete tmp_context.params['model']
                delete tmp_context.params['view_type']
                delete tmp_context.params['menu_id']
            }

            for(var key in tmp_context) {
                // check start with search_default_
                if (key.indexOf('search_default_') != -1) {
                    delete tmp_context[key]
                }
            }

            if (tmp_action.id == action.id
                && tmp_action.name == action.name
                && tmp_action.res_model == tmp_action.res_model
                && tmp_action.xml_id == action.xml_id
                && tmp_action.view_mode == action.view_mode
                && tmp_action.binding_model_id == action.binding_model_id
                && tmp_action.binding_type == action.binding_type
                && tmp_action.binding_view_types == action.binding_view_types
                && tmp_action.res_id == action.res_id
                && JSON.stringify(tmp_action.domain || {}) == JSON.stringify(action.domain || {})
                && JSON.stringify(tmp_context || {}) == JSON.stringify(context)) {
                return true
            } else {
                return false
            }
        })
        
        return old_action_info
    },

    _get_action(action_info) {
        var action = action_info.componentProps.action || action_info.action;
        while (action.ref_action) {
            action = action.ref_action;
            if (action == action.ref_action) {
                break;
            }
        }
        return action;
    },

    _get_action_jsId(action_info) {
        var action = this._get_action(action_info);
        return action.jsId;
    },

    _set_current_action_stack(action_info) {
        // get jsId
        var jsId = this._get_action_jsId(action_info);
        // call service function to set current action stack
        this.action_service.setCurrentAction(jsId);
    },

    _on_active_action(action_info) {
        this._set_current_action_stack(action_info);
        // deactive all
        for (let i = 0; i < this.action_infos.length; i++) {
            var tmp_action_info = this.action_infos[i];
            tmp_action_info.active = false;
        }
        action_info.active = true;
        this.action_service.setChangingTab(true);
    },

    removeActionStacks(action_info) {
        // remove the action from service
        var actionJsIds = []
        if (action_info.ref_action) {
            var ref_action = action_info.ref_action;
            while (ref_action.ref_action) {
                ref_action = ref_action.ref_action;
                if (ref_action == ref_action.ref_action) {
                    break;
                }
            }
            actionJsIds.push(ref_action.jsId)
        } else {
            if (action_info.componentProps.action) {
                actionJsIds.push(action_info.componentProps.action.jsId)
            } else if (action_info.action) {
                actionJsIds.push(action_info.action.jsId)
            }
        }
        this.action_service.removeStacks(actionJsIds)
    },

    _on_close_action(action_info) {

        action_info = this.get_action_info(action_info);
        let index = this.action_infos.indexOf(action_info);
        this.action_infos.splice(index, 1);
        
        // remove the action stack
        this.removeActionStacks(action_info);
        
        index = index - 1;
        if (index < 0) {
            index = 0;
        }
        
        // if there has no active item, maybe it not click the current item
        var bFind = false;
        for (var i = 0; i < this.action_infos.length; i++) {
            var tmp_action_info = this.action_infos[i];
            if (tmp_action_info.active) {
                bFind = true;
                break;
            }
        }
        if (!bFind && this.action_infos.length > 0) {
            this.action_infos[index].active = true;
            this._on_active_action(this.action_infos[index]);
        }
        // prevent widget reload
        this.action_service.setChangingTab(true);
    },

    _close_other_action(action_info) {
        action_info = this.get_action_info(action_info);
        let action_infos = [];
        for (var i = 0; i < this.action_infos.length; i++) {
            var tmp_action_info = this.action_infos[i];
            if(tmp_action_info != action_info) {
                action_infos.push(tmp_action_info);
            }
        }
        for (let i = 0; i < action_infos.length; i++) {
            let tmp_action_info = action_infos[i];
            let index = this.action_infos.indexOf(tmp_action_info);
            this.action_infos.splice(index, 1);
            this.removeActionStacks(tmp_action_info);
        }
    },

    _on_close_cur_action() {
        for (let i = 0; i < this.action_infos.length; i++) {
            let tmp_action_info = this.action_infos[i];
            if (tmp_action_info.active) {
                this._on_close_action(tmp_action_info)
            }
        }
    },

    _on_close_all_action() {
        this.action_infos.splice(0, this.action_infos.length);
        this.action_service.removeAllStacks();
    }
});

ActionContainer.components = {
    ...ActionContainer.components,
    AklMultiTab
};

// change the template
ActionContainer.template = xml`
    <t t-name="web.ActionContainer">
        <div class="o_action_manager">
            <AklMultiTab 
                action_infos="this.action_infos"
                active_action.bind="this._on_active_action"
                close_action.bind="this._on_close_action"
                close_cur_action.bind="this._on_close_cur_action"
                close_other_action.bind="this._close_other_action"
                close_all_action.bind="this._on_close_all_action"
            />
            <div t-foreach="action_infos||[]" t-as="action_info" t-key="action_info.id" class="akl_action_wrapper akl_tab_page_container" t-att-class="action_info.active ? '' : 'd-none'">
                <t t-component="action_info.Component" className="'o_action'" t-props="action_info.componentProps" />
            </div>
        </div>
    </t>`;
