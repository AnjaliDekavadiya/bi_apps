/** @odoo-module alias=mana_dashboard.search_item_base **/

import { BlockRegistry } from "@mana_dashboard_base/mana_block_registry";
import { icons } from "@mana_dashboard_base/utils/mana_icons";
import { _t } from "@web/core/l10n/translation";
import { evaluateExpr } from "@web/core/py_js/py";
import { session } from "@web/session";
import { BlockBase } from "@mana_dashboard_base/mana_block_base";
import { renderToString } from "@web/core/utils/render";

const BaseModel = BlockBase.BaseModel;
const BaseView = BlockBase.BaseView;

let search_id = 0;

let operators = [
    { value: '=', name: '=' },
    { value: '!=', name: '!=' },
    { value: 'ilike', name: 'ilike' },
    { value: 'like', name: 'like' },
    { value: 'not ilike', name: 'not ilike' },
    { value: 'not like', name: 'not like' },
]

let SearchItemModel = BaseModel.extend({

    defaults: {
        ...BaseModel.prototype.defaults,

        name: _t('Search Item'),
        default_operator: '=',
        draggable: '.search_group',
        has_config: true,
        disable_first_child: false,
        search_template: 'mana_dashboard.search_item',
        search_sensitive: false,
        disable_first_child: true,
        classes: ['search_item'],
        state_inited: false,
        is_search: true,
        toolbar_config: {
            edit_config: false,
        },
        traits: [
            {
                type: 'text',
                name: 'key',
                label: 'key',
            },
            {
                type: 'text',
                name: 'label',
                label: 'label',
            },
            {
                type: 'select',
                label: 'Show Label',
                name: 'show_label',
                options: [
                    { value: 'true', name: 'true' },
                    { value: 'false', name: 'false' },
                ]
            },
            {
                type: 'select',
                label: 'Show Operator',
                name: 'show_operator',
                options: [
                    { value: 'true', name: 'true' },
                    { value: 'false', name: 'false' },
                ]
            },
            {
                type: 'select',
                label: 'OR & AND',
                name: 'logic',
                options: [
                    { value: 'or', name: 'OR' },
                    { value: 'and', name: 'AND' },
                ]
            },
            {
                type: 'select',
                label: 'Immediately',
                name: 'search_immediately',
                options: [
                    { value: 'true', name: 'true' },
                    { value: 'false', name: 'false' },
                ]
            },
            {
                type: 'select',
                label: 'Operator',
                name: 'operator',
                options: operators
            },
            {
                type: 'text',
                label: 'Default Value',
                name: 'default_value',
            },
            {
                type: 'select',
                label: 'Apply To Params',
                name: 'apply_to_params',
                options: [
                    { value: 'true', name: 'true' },
                    { value: 'false', name: 'false' },
                ]
            }
        ],

        attributes: {
            'key': '',
            'label': 'label',
            'show_label': 'true',
            'show_operator': 'false',
            'search_immediately': 'false',
            'logic': 'and',
            'operator': '=',
            'apply_to_params': 'true'
        }
    },

    initialize() {
        BaseModel.prototype.initialize.apply(this, arguments);

        let current_value = this.get_current_value();
        this.set('value', current_value, { silent: true });
        
        // set the default value
        if (this.get('disable_first_child')) {
            this.disable_first_child();
        }
    },

    resetSearch: function () {
        // find all the input
        let inputs = this.$el.find('.search_widget input');
        // reset all the input
        inputs.val('');
        // find all the select
        let selects = this.$el.find('.search_widget select');
        // reset all the select
        selects.val('')
    },

    apply_to_params: function () {
        let apply_to_params = this.get('attributes').apply_to_params;
        if (apply_to_params === 'true') {
            return true;
        }
        return false;
    },

    /**
     * reset Operator
     */
    resetOperator: function () {
        let show_operator = this.get('show_operator');
        if (show_operator) {
            this.$el.find('select').val(this.get('default_operator'));
        }
    },

    get_default_value: function () {
        let value = undefined;
        // eval last search value
        let default_value = this.get('attributes').default_value || '';
        // trim the default value
        default_value = default_value.trim();

        // check if it is like ${{}} or not
        if (default_value.startsWith('${{') && default_value.endsWith('}}')) {
            default_value = default_value.slice(3, -2);
            let system_variables = this.getSystemVariables();
            let value = default_value;
            let user_context = session.user_context;
            let _context = _.extend({}, user_context, system_variables);
            let result = evaluateExpr(value, _context); 
            value = result;
        } else {
            value = default_value;
        }

        return value;
    },

    /**
     * get the current value
     * @returns 
     */
    get_current_value: function (origin = false) {

        let key = this.get('attributes').key;
        if (!key) {
            return undefined;
        }

        let search_group = this.get_parent_group();
        if (!search_group) {
            return undefined;
        }

        // get the current value, just get from the state
        let state_inited = this.get('state_inited');
        if (state_inited) {
            return this.get('value');
        }

        // get from the last search
        let value = undefined;
        let load_last_search = search_group.load_last_search();
        if (load_last_search) {
            let last_search = search_group.get_last_search(key);
            if (last_search) {
                if (last_search.type != "datetime_range") {
                    if (origin) {
                        value = last_search.value;
                    } else {
                        value = last_search.origin_value;
                    }
                } else {
                    value = last_search;
                }
            }
        } else {
            value = this.get_default_value();
        }

        return value;
    },

    get_parent_group: function () {
        let parent = this.parent();
        while (parent) {
            if (parent.get('is_search_group')) {
                return parent;
            }
            parent = parent.parent();
        }
        return undefined;
    },

    /**
     * update content 
     */
    updateContent: function () {

        let template = this.get('search_template');
        let operators = this.get('operators');

        // get the current value
        let current_vaule = this.get_current_value();
        let html_str = renderToString(template, {
            show_label: this.get('attributes').show_label,
            show_operator: this.get('attributes').show_operator,
            label: this.get('attributes').label || 'Search Input',
            name: this.get('attributes').name || 'search_input_' + search_id++,
            operators: operators,
            cur_operator: this.get('attributes').operator || this.get('default_operator'),
            options: this.getOptions(),
            multi_select: this.get('attributes').multi_select,
            current_value: current_vaule,
            _t: _t,
        });
        this.append(html_str);

        // disable first child
        if (this.get('disable_first_child')) {
            this.disable_first_child();
        }
    },

    getOptions() {
        let options = this.get('attributes').options;

        if (options) {
            // split by \n
            options = options.split('\n');
            // split by ,
            options = options.map((option) => {
                let [key, value] = option.split(',');
                if (!value) {
                    value = key;
                }
                return { key: key, value: value };
            });
        } else {
            options = [];
        }

        return options;
    },

    getSystemVariables() {
        let dashboard = this.get_dashboard();
        if (dashboard) {
            return dashboard.getSystemVariables();
        }
        return {};
    },

    getSearchInfo() {
        if (this.view) {
            let value = this.get('value')
            const attributes = this.get('attributes');
            let key = attributes && attributes.key;
            if (!key || key == '') {
                return null;
            }
            let operator = attributes.operator || this.model.get('default_operator');
            let submit_empty = attributes.submit_empty ? true : false;
            if (!submit_empty && (value == '' || value == null)) {
                return null;
            }

            let apply_to_params = true;
            if (attributes.apply_to_params == 'false') {
                apply_to_params = false;
            }

            return {
                key: key,
                operator: operator,
                value: value,
                origin_value: value,
                type: 'char',
                logic_type: this.get('attributes').logic_type || 'and',
                apply_to_params: apply_to_params,
            }
        }
        return null;
    }
}, {
    isComponent: (el) => {
        if (el && el.classList && el.classList.contains('search_item')) {
            return { type: 'search_item' };
        }
    }
})

let SearchItemView = BaseView.extend({

    events: {},

    init() {
        BaseView.prototype.init.apply(this, arguments);

        // listen to the show operator change
        this.listenTo(this.model, 'change:attributes:show_operator', this.on_show_operator_change);
        // listen to the show label change
        this.listenTo(this.model, 'change:attributes:show_label', this.on_show_label_change);
        // listen to the label change
        this.listenTo(this.model, 'change:attributes:label', this.on_label_change);
        // change options
        this.listenTo(this.model, 'change:attributes:options', this.on_options_change);
        // change logic
        this.listenTo(this.model, 'change:attributes:logic', this.on_logic_change);
    },

    on_logic_change() {
        this._reset_components();
        this.render();
    },

    on_label_change() {
        this._reset_components();
        this.render();
    },

    on_show_operator_change() {
        this._reset_components();
        this.render();
    },

    _reset_components() {
        this.model.get('components').reset();
    },

    on_show_label_change() {
        let show_label = this.model.get('attributes').show_label;
        this._reset_components();
        this.render();
    },

    on_options_change() {
        this._reset_components();
        this.render();
    },

    trigger_change() {
        this.el.dispatchEvent(new CustomEvent('mana_dashboard.search_item_changed', {
            bubbles: true,
            detail: {
                model: this.model,
            }
        }));
    },

    removed() {
        BaseView.prototype.removed.apply(this, arguments);
    },

    initSelect2() {
        $(this.$el.find('select')).select2({}).on('change', (event) => {
            this.model.addAttributes({ operator: event.target.value });
            this.trigger_change();
        });
    },

    render(...args) {
        BaseView.prototype.render.apply(this, args);
        return this;
    }
})

export const SearchItemBase = {
    SearchItemModel,
    SearchItemView
}
