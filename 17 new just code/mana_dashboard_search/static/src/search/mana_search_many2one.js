/** @odoo-module alias=mana_dashboard.search_many2one **/

import { BlockRegistry } from "@mana_dashboard_base/mana_block_registry";
import { icons } from "@mana_dashboard_base/utils/mana_icons";
import { SearchItemBase } from "@mana_dashboard_search/search/mana_search_item";
import { mountComponent } from '@web/env';
import { ManaX2manyWrapper } from "@mana_dashboard_base/many2x_wrapper/mana_many2x_wrapper";

const SearchItemModel = SearchItemBase.SearchItemModel;
const SearchItemView = SearchItemBase.SearchItemView;

import { _t } from "@web/core/l10n/translation";


let operators = [
    { value: '=', name: '=' },
    { value: '!=', name: '!=' },
    { value: 'child_of', name: 'child_of' },
    { value: 'parent_of', name: 'parent_of' }
]

function builder(editor, options) {

    const dc = editor.DomComponents;

    editor.BlockManager.add('search_many2one', {
        label: _t('Search Select'),
        category: _t('Search'),
        select: true,
        render: () => {
            return `<div class="d-flex flex-column align-items-center justify-content-center"><div class="chart-icon">${icons.many2one_svg}</div><div class='anita-block-label'>Many2One</div></div>`
        },
        content: {
            type: 'search_many2one',
        }
    });

    dc.addType('search_many2one', {
        model: SearchItemModel.extend({

            defaults: {
                tagName: 'div',
                ...SearchItemModel.prototype.defaults,
                name: _t('Search Many2One'),
                operators: operators,
                default_operator: 'ilike',
                has_config: false,
                search_template: 'mana_dashboard.search_x2x',
                classes: SearchItemModel.prototype.defaults.classes.concat(['search_many2one']),
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
                    'operator': '=',
                    'submit_empty': 'false',
                }),
            },

            initialize() {
                SearchItemModel.prototype.initialize.apply(this, arguments);
            },

            reset: function () {
                if (this.view) {
                    this.view.el.value = '';
                }
                this.resetOperator();
            },

            getValue() {
                return this.get('value');
            },

            getSearchInfo() {
                if (this.view) {
                    const value = this.getValue();
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

                        let apply_to_params = true;
                        if (attributes.apply_to_params == 'false') {
                            apply_to_params = false;
                        }

                        return {
                            key: key,
                            operator: operator,
                            value: value && value.id,
                            origin_value: value,
                            type: 'many2one',
                            logic_type: this.get('attributes').logic_type || 'and',
                            apply_to_params: this.apply_to_params()
                        };
                    }
                }
                return null;
            }
        }, {
            isComponent: (el) => {
                if (el && el.classList && el.classList.contains('search_many2one')) {
                    return { type: 'search_many2one' };
                }
            }
        }),

        view: SearchItemView.extend({

            init() {
                SearchItemView.prototype.init.apply(this, arguments);
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

            render(...args) {
                SearchItemView.prototype.render.apply(this, args);
                
                if (this.model.get('components').length == 0) {
                    this.model.updateContent();
                }

                // select2
                $(this.$el.find('select')).select2({});

                if (this.many2one_field) {
                    this.many2one_field.destroy();
                    this.many2one_field = null;
                }

                // get the current value    
                let env = this.get_env();
                let current_value = this.model.get_current_value();
                this.nextTick().then(async () => {
                    let el = this.el.querySelector('.x2x_widget')
                    // check el in the document
                    if (!el || !document.contains(el)) {
                        return;
                    }

                    let res_model = this.model.get('attributes').res_model || 'res.partner';
                    if (current_value) {
                        let record = await env.services.orm.read(res_model, [current_value], ['display_name']);
                        current_value = record[0].display_name;
                    }
                    
                    this.many2one_field = await mountComponent(ManaX2manyWrapper, el, {
                        env: env,
                        translateFn: _t,
                        translatableAttributes: ["data-tooltip"],
                        props: {
                            resModel: this.model.get('attributes').res_model || 'res.partner',
                            context: this.model.get('context') || {},
                            value: {
                                id: this.model.get('value'),
                                display_name: current_value || "",
                            },
                            isToMany: false,
                            domain: this.model.get('domain') || [],
                            onSelect: (selection) => {
                                let res_id = selection && selection[0] && selection[0].id;
                                this.model.set('value', res_id);
                                this.trigger_change();
                            }
                        }
                    });
                });

                this.model.set('state_inited', true);
                return this;
            },
            
            removed() {
                SearchItemView.prototype.removed.apply(this, arguments);
                if (this.many2one_field) {
                    this.many2one_field.destroy();
                    this.many2one_field = null;
                }
            }
        }),
    });
}

BlockRegistry.add('search_many2one', builder);
