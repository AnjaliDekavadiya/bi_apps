/** @odoo-module alias=mana_dashboard.search_many2many **/

import { BlockRegistry } from "@mana_dashboard_base/mana_block_registry";
import { icons } from "@mana_dashboard_base/utils/mana_icons";
import { SearchItemBase } from "@mana_dashboard_search/search/mana_search_item";
import { mountComponent } from '@web/env';
import { ManaRecordSelector } from "@mana_dashboard_search/many2x_wrapper/mana_record_selector";

const  SearchItemModel = SearchItemBase.SearchItemModel;
const  SearchItemView = SearchItemBase.SearchItemView;

import { _t } from "@web/core/l10n/translation";

let operators = [
    { value: 'in', name: 'in' },
    { value: 'not in', name: 'not in' }
]

function builder(editor, options) {

    const dc = editor.DomComponents;

    editor.BlockManager.add('search_many2many', {
        label: _t('Search Select'),
        category: _t('Search'),
        select: true,
        render: () => {
            return `<div class="d-flex flex-column align-items-center justify-content-center"><div class="chart-icon">${icons.many2many_svg}</div><div class='anita-block-label'>Many2Many</div></div>`
        },
        content: {
            type: 'search_many2many',
        }
    });

    dc.addType('search_many2many', {
        model: SearchItemModel.extend({

            defaults: {
                ...SearchItemModel.prototype.defaults,
                name: _t('Search Many2Many'),
                operators: operators,
                default_operator: 'in',
                search_template: 'mana_dashboard.search_x2x',
                classes: SearchItemModel.prototype.defaults.classes.concat(['search_many2many']),
                traits: SearchItemModel.prototype.defaults.traits.concat([
                    {
                        type: 'select',
                        label: 'Operator',
                        name: 'operator',
                        options: operators
                    },
                    {
                        type: 'many2one_trait',
                        label: 'Model',
                        name: 'res_model',
                        res_model: 'ir.model',
                    },
                    {
                        type: 'text',
                        label: 'Domain',
                        name: 'domain',
                    },
                    {
                        type: 'text',
                        label: 'Context',
                        name: 'context'
                    }
                ]),

                attributes: _.extend({}, SearchItemModel.prototype.defaults.attributes, {
                    'operator': 'ilike',
                    'submit_empty': 'false'
                })
            },

            initialize() {
                SearchItemModel.prototype.initialize.apply(this, arguments);
            },

            resetSearch: function () {
                if (this.view) {
                    this.view.resetSearch();
                }
                this.resetOperator();
            },

            getSearchInfo() {
                if (this.view) {
                    const value = this.get('value') || []
                    const attributes = this.get('attributes');
                    let key = attributes && attributes.key;
                    if (!key || key == '') {
                        return null;
                    }
                    let operator = attributes.operator || this.model.get('default_operator');
                    let submit_empty = attributes.submit_empty == 'true' ? true : false;
                    if (value) {

                        if (!submit_empty && !value.length) {
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
                            type: 'many2many',
                            logic_type: this.get('attributes').logic_type || 'and',
                            apply_to_params: this.apply_to_params()
                        };
                    }
                }
                return null;
            }
        }, {
            isComponent: (el) => {
                if (el && el.classList && el.classList.contains('search_many2many')) {
                    return { type: 'search_many2many' };
                }
            }
        }),

        view: SearchItemView.extend({

            init() {
                SearchItemView.prototype.init.apply(this, arguments);
                this.listenTo(this.model, 'change:type', this.render);
            },

            removed() {
                SearchItemView.prototype.removed.apply(this, arguments);
                if (this.many2many_field) {
                    this.many2many_field.destroy();
                    this.many2many_field = null;
                }
            },

            _reset_components() {
                if (this.man2many_field) {
                    this.man2many_field.destroy();
                    this.man2many_field = null;
                }
                this.model.get('components').reset();
            },

            resetSearch() {
                if (this.many2many_field) {
                    this.many2many_field.set_value([]);
                }
            },

            render(...args) {
                SearchItemView.prototype.render.apply(this, args);

                if (this.many2many_field) {
                    this.many2many_field.destroy();
                    this.many2many_field = null;
                }

                if (this.model.get('components').length == 0) {
                    this.model.updateContent();
                }

                // get the current value    
                let env = this.get_env();
                let res_ids = this.model.get_current_value() || [];
                this.nextTick().then(async () => {
                    let el = this.el.querySelector('.x2x_widget')

                    // check el in the document
                    if (!el || !document.contains(el)) {
                        return;
                    }

                    let res_model = this.model.get('attributes').res_model || 'res.partner';
                    this.many2many_field = await mountComponent(ManaRecordSelector, el, {
                        env: env,
                        translateFn: _t,
                        translatableAttributes: ["data-tooltip"],
                        props: {
                            resModel: this.model.get('attributes').res_model || 'res.partner',
                            resIds: res_ids,
                            context: this.model.get('context') || {},
                            domain: this.model.get('domain') || [],
                            update: (res_ids) => {
                                this.model.set('value', res_ids);
                                this.trigger_change();
                            }
                        }
                    });
                });

                // state inited
                this.model.set('state_inited', true);

                return this;
            }
        }),
    });
}

BlockRegistry.add('search_many2many', builder);
