/** @odoo-module alias=mana_dashboard.search_tab **/

import { BlockRegistry } from "@mana_dashboard_base/mana_block_registry";
import { SearchItemBase } from "@mana_dashboard_search/search/mana_search_item";
import { icons } from "@mana_dashboard_base/utils/mana_icons";

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
]

function builder(editor, options) {

    const dc = editor.DomComponents;

    editor.BlockManager.add('search_tab', {
        label: _t('Search Tab'),
        category: _t('Search'),
        select: true,
        render: () => {
            return `<div class="d-flex flex-column align-items-center justify-content-center"><div class="chart-icon">${icons.tab_svg}</div><div class='anita-block-label'>Tab</div></div>`
        },
        content: {
            type: 'search_tab',
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

    dc.addType('search_tab', {
        model: SearchItemModel.extend({

            defaults: {
                ...SearchItemModel.prototype.defaults,
                name: _t('Search Tab'),
                droppable: '.search_group',
                operators: operators,
                default_operator: 'ilike',
                search_template: 'mana_dashboard.search_tab',
                classes: SearchItemModel.prototype.defaults.classes.concat(['search_tab']),
                traits: traits,
                attributes: _.extend({}, SearchItemModel.prototype.defaults.attributes, {
                    'operator': '=',
                    'submit_empty': false,
                    'tab_style': 'nav-line',
                    'options': 'key1,val1\nkey2,val2\nkey3,val3'
                }),
                operators: operators
            },

            initialize() {
                SearchItemModel.prototype.initialize.apply(this, arguments);
            },

            reset_search: function () {
                this.resetOperator();
            },

            getSearchInfo() {
                if (this.view) {
                    // get the active tab
                    let active_tab = this.view.el.querySelector('.nav-link.active');
                    if (!active_tab) {
                        return null;
                    }
                    let value = active_tab && active_tab.getAttribute('value');
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
                            type: 'search_tab',
                            logic_type: this.get('attributes').logic_type || 'and',
                            apply_to_params: this.apply_to_params()
                        }
                    }
                }
                return null;
            }
        }, {
            isComponent: (el) => {
                if (el && el.classList && el.classList.contains('search_tab')) {
                    return { type: 'search_tab' };
                }
            }
        }),

        view: SearchItemView.extend({

            events: _.extend({}, SearchItemView.prototype.events, {
                'click .nav-item': 'handleClick',
            }),

            handleClick(event) {
                let target = event.target;
                $(target).tab('show');
                event.preventDefault();
                let value = $(target).attr('value');
                this.model.set('value', value);
                this.trigger_change();
            },

            init() {
                SearchItemView.prototype.init.apply(this, arguments);
                // listend to options
                this.listenTo(this.model, 'change:attributes:options', this.render);
                // listend to operator
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

                // set the current inited tab
                let current_value = this.model.get_current_value();
                let current_tab = this.el.querySelector(`.nav-link[value="${current_value}"]`);
                if (current_tab) {
                    // active the current tab
                    $(current_tab).tab('show');
                } else {
                    // active the first tab
                    let first_tab = this.el.querySelector('.nav-link');
                    if (first_tab) {
                        $(first_tab).tab('show');
                    }
                }
                this.model.set('state_inited', true);
                return this;
            }
        }),
    });
}

BlockRegistry.add('search_tab', builder);
