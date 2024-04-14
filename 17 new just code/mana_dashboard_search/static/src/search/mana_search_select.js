/** @odoo-module alias=mana_dashboard.search_select **/

import { BlockRegistry } from "@mana_dashboard_base/mana_block_registry";
import { icons } from "@mana_dashboard_base/utils/mana_icons";
import { SearchItemBase } from "@mana_dashboard_search/search/mana_search_item";

const SearchItemModel = SearchItemBase.SearchItemModel;
const SearchItemView = SearchItemBase.SearchItemView;

import { _t } from "@web/core/l10n/translation";


let operators =  [
    { value: '=', name: '=' },
    { value: '!=', name: '!=' },
    { value: 'ilike', name: 'ilike' },
    { value: 'like', name: 'like' },
    { value: 'not ilike', name: 'not ilike' },
    { value: 'not like', name: 'not like' },
]

function builder(editor, options) {

    const dc = editor.DomComponents;

    editor.BlockManager.add('search_select', {
        label: _t('Search Input'),
        category: _t('Search'),
        select: true,
        render: () => {
            return `<div class="d-flex flex-column align-items-center justify-content-center"><div class="chart-icon">${icons.select_svg}</div><div class='anita-block-label'>Select</div></div>`
        },
        content: {
            type: 'search_select',
        }
    });

    let traits = _.clone(SearchItemModel.prototype.defaults.traits);
    traits = _.reject(traits, function (trait) {
        return trait.name == 'operator';
    });
    
    // add operator trait
    let extra_traits = [
        {
            type: 'select',
            label: 'Operator',
            name: 'operator',
            options: operators
        },
        {
            type: 'text',
            textarea: true,
            label: 'Options',
            name: 'options',
        }
    ]
    traits = traits.concat(extra_traits);

    dc.addType('search_select', {
        model: SearchItemModel.extend({

            defaults: {
                tagName: 'div',
                ...SearchItemModel.prototype.defaults,
                name: _t('Search Select'),
                operators: operators,
                default_operator: 'ilike',
                search_template: 'mana_dashboard.search_select',
                
                classes: SearchItemModel.prototype.defaults.classes.concat(['search_select']),
                traits: traits,
                attributes: _.extend({}, SearchItemModel.prototype.defaults.attributes, {
                    'operator': 'ilike',
                    'submit_empty': 'false',
                    'options': 'key1,val1\nkey2,val2\nkey3,val3',
                }),
            },

            initialize() {
                SearchItemModel.prototype.initialize.apply(this, arguments);
            },

            resetSearch: function () {
                if (this.view) {
                    this.view.el.value = '';
                }
                this.resetOperator();
            },

            getSearchInfo() {
                if (this.view) {
                    const value = this.get('value');
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
                            type: 'search_select',
                            logic_type: 'and',
                            apply_to_params: this.apply_to_params()
                        }
                    }
                }
                return null;
            }
        }, {
            isComponent: (el) => {
                if (el && el.classList && el.classList.contains('search_select')) {
                    return { type: 'search_select' };
                }
            }
        }),

        view: SearchItemView.extend({

            init() {
                SearchItemView.prototype.init.apply(this, arguments);
                
                this.listenTo(this.model, 'change:attributes:options', this.render);
                this.listenTo(this.model, 'change:attributes:operator', this.render);
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
                    // set the select value
                    $(this.$el.find('select')).val(current_value);
                } else {
                    // unselect the select
                    $(this.$el.find('select')).val(null);
                }

                // set the state of the select
                this.model.set('state_inited', true);

                // select2
                $(this.$el.find('select')).select2({
                    width: '100%',
                }).on('change', (e) => {
                    // set the current value
                    this.model.set('value', e.target.value);
                    this.trigger_change();
                });

                return this;
            }
        }),
    });
}

BlockRegistry.add('search_select', builder);
