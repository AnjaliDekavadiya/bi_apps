/** @odoo-module alias=mana_dashboard.search_option **/

import { BlockRegistry } from "@mana_dashboard_base/mana_block_registry";
import { icons } from "@mana_dashboard_base/utils/mana_icons";
import { SearchItemBase } from "@mana_dashboard_search/search/mana_search_item";

const SearchItemModel = SearchItemBase.SearchItemModel;
const SearchItemView = SearchItemBase.SearchItemView;

import { _t } from "@web/core/l10n/translation";

let operators = [
    { value: '=', name: '=' },
    { value: '!=', name: '!=' },
    { value: 'ilike', name: 'ilike' },
    { value: 'like', name: 'like' },
    { value: 'not ilike', name: 'not ilike' },
    { value: 'not like', name: 'not like' },
    { value: 'in', name: 'in' },
]

export function builder(editor, options) {

    const dc = editor.DomComponents;

    editor.BlockManager.add('search_option', {
        label: _t('Search Input'),
        category: _t('Search'),
        select: true,
        render: () => {
            return `<div class="d-flex flex-column align-items-center justify-content-center"><div class="chart-icon">${icons.option_svg}</div><div class='anita-block-label'>Option</div></div>`
        },
        content: {
            type: 'search_option',
        }
    });

    let traits = _.clone(SearchItemModel.prototype.defaults.traits);
    traits = _.reject(traits, function (trait) {
        return trait.name == 'operator';
    });
    
    let extra_traits = [
        {
            type: 'select',
            label: 'Submit Empty',
            name: 'submit_empty',
            options: [
                { value: 'true', name: 'True' },
                { value: 'false', name: 'False' },
            ]
        },
        {
            type: 'checkbox',
            label: 'Multi Select',
            name: 'multi_select',
        },
        {
            type: 'select',
            label: 'Operator',
            name: 'operator',
            options: operators,
        },
        {
            type: 'text',
            name: 'options',
            textarea: true,
            options: 'key1,val1\nkey2,val2\nkey3,val3',
        }
    ];
    traits = traits.concat(extra_traits);

    // add search template
    dc.addType('search_option', {
        model: SearchItemModel.extend({

            defaults: {
                ...SearchItemModel.prototype.defaults,

                name: _t('Search Option'),
                operators: operators,
                default_operator: 'ilike',
                droppable: '.search_container',
                search_template: 'mana_dashboard.search_option',
                classes: SearchItemModel.prototype.defaults.classes.concat(['search_option']),

                traits: traits,
                attributes: _.extend({}, SearchItemModel.prototype.defaults.attributes, {
                    'operator': 'ilike',
                    'submit_empty': false,
                    'multi_select': false,
                    'options': 'key1,val1\nkey2,val2\nkey3,val3',
                }),
                operators: operators,
            },

            initialize() {
                SearchItemModel.prototype.initialize.apply(this, arguments);
                this.disable_first_child();
            },

            reset: function () {
                if (this.view) {
                    this.view.el.value = '';
                }
            },

            getSearchInfo() {
                if (this.view) {
                    const value = this.view.el.value;
                    const attributes = this.get('attributes');
                    let key = attributes && attributes.key;
                    if (!key || key == '') {
                        return null;
                    }
                    let operator = attributes.operator || this.model.get('default_operator');
                    let submit_empty = attributes.submit_empty == 'true' ? true : false;
                    if (value) {
                        if (!submit_empty && (value == '' || value == null)) {
                            return null;
                        }
                        return {
                            key: key,
                            operator: operator,
                            value: value,
                            origin_value: value,
                            type: 'option',
                            logic_type: this.model.get('attributes').logic_type || 'and',
                            apply_to_params: this.apply_to_params()
                        }
                    }
                }
                return null;
            }
        }, {
            isComponent: (el) => {
                if (el && el.classList && el.classList.contains('search_option')) {
                    return { type: 'search_option' };
                }
            }
        }),

        view: SearchItemView.extend({

            events: _.extend({}, SearchItemView.prototype.events, {
                'input': 'onInput',
                'change checkbox': 'onCheckboxChange',
                'change radio': 'onRadioChange',
            }),

            init: function () {
                SearchItemView.prototype.init.apply(this, arguments);
                this.listenTo(
                    this.model, 'change:attributes:multi_select', this.on_multi_select_change);
            },

            on_multi_select_change: function () {
                this._reset_components();
                this.render();
            },

            onCheckboxChange(e) {
                this.trigger_change()
            },

            onRadioChange(e) {
                let value = $(e.target).val();
                this.model.set('value', value);
                this.trigger_change()
            },

            onInput() {
                this.trigger_change();
            },

            render(...args) {
                SearchItemView.prototype.render.apply(this, args);

                if (this.model.get('components').length == 0) {
                    this.model.updateContent();
                }

                // set the default value
                let value = this.model.get_current_value();
                // reset all the selected options
                this.el.querySelectorAll('input').forEach((el) => {
                    el.checked = false;
                });

                // set the current value
                if (value) {
                    this.el.querySelector('[value="' + value + '"]').checked = true;
                }

                // set the state of the select
                this.model.set('state_inited', true);

                return this;
            }
        })
    });
}

BlockRegistry.add('search_option', builder);