/** @odoo-module alias=mana_dashboard.search_input **/

import { BlockRegistry } from "@mana_dashboard_base/mana_block_registry";
import { icons } from "@mana_dashboard_base/utils/mana_icons";
import { _t } from "@web/core/l10n/translation";
import { SearchItemBase } from "@mana_dashboard_search/search/mana_search_item";

const SearchItemModel = SearchItemBase.SearchItemModel;
const SearchItemView = SearchItemBase.SearchItemView;

let input_id = 0;

let operators = [
    { value: '=', name: '=' },
    { value: '!=', name: '!=' },
    { value: 'ilike', name: 'ilike' },
    { value: 'like', name: 'like' },
    { value: 'not ilike', name: 'not ilike' },
    { value: 'not like', name: 'not like' },
]

function builder(editor, options) {

    const dc = editor.DomComponents;

    editor.BlockManager.add('search_input', {
        label: _t('Search Input'),
        category: _t('Search'),
        select: true,
        render: () => {
            return `<div class="d-flex flex-column align-items-center justify-content-center"><div class="chart-icon">${icons.input_svg}</div><div class='anita-block-label'>Input</div></div>`
        },
        content: {
            type: 'search_input',
        }
    });

    let traits = _.clone(SearchItemModel.prototype.defaults.traits);
    traits = _.reject(traits, function (trait) {
        return trait.name == 'operator';
    });
    // add operator trait
    traits.push({
        type: 'select',
        label: 'Operator',
        name: 'operator',
        options: operators
    });

    dc.addType('search_input', {
        model: SearchItemModel.extend({

            defaults: {
                ...SearchItemModel.prototype.defaults,
                name: _t('Search Input'),
                operators: operators,
                default_operator: 'ilike',
                droppable: '.search_container',
                has_config: false,
                search_template: 'mana_dashboard.search_input',
                classes: SearchItemModel.prototype.defaults.classes.concat(['search_input']),
                traits: traits,
                attributes: _.extend({}, SearchItemModel.prototype.defaults.attributes, {
                    'key': 'input' + input_id++,
                    'operator': 'ilike',
                    'submit_empty': 'false'
                }),
            },

            initialize() {
                SearchItemModel.prototype.initialize.apply(this, arguments);
                this.disable_first_child();
            },

            resetSearch: function () {
                if (this.view) {
                    this.view.el.value = '';
                }
                this.resetOperator();
            },

            getSearchInfo() {
                if (this.view) {
                    let input = this.view.el.querySelector('.o_input');
                    let value = input.value;
                    const attributes = this.get('attributes');
                    let key = attributes && attributes.key;
                    if (!key || key == '') {
                        return null;
                    }
                    let operator = attributes.operator || this.model.get('default_operator');
                    let submit_empty = attributes.submit_empty == 'true' ? true : false;
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
                        apply_to_params: this.apply_to_params(),
                    }
                }
                return null;
            }
        }, {
            isComponent: (el) => {
                if (el && el.classList && el.classList.contains('search_input')) {
                    return { type: 'search_input' };
                }
            }
        }),

        view: SearchItemView.extend({

            events: _.extend({}, SearchItemView.prototype.events, {
                'input input': 'onChange',
            }),

            onChange(event) {
                event.stopPropagation();

                let value = event.target.value;
                this.model.set('value', value);
                this.trigger_change();
            },

            init() {
                SearchItemView.prototype.init.apply(this, arguments);
            },

            removed() {
                SearchItemView.prototype.removed.apply(this, arguments);
            },

            render(...args) {
                SearchItemView.prototype.render.apply(this, args);

                if (this.model.get('components').length == 0) {
                    this.model.updateContent();
                }

                // set the current value
                let current_value = this.model.get_current_value();
                if (current_value) {    
                    this.el.querySelector('.o_input').value = current_value;
                } else {
                    this.el.querySelector('.o_input').value = '';
                }
                this.model.set('state_inited', true);

                // init the operator select2
                this.initSelect2();

                return this;
            }
        }),
    });
}

BlockRegistry.add('search_input', builder);
