/** @odoo-module alias=mana_dashboard.search_group **/

import { BlockRegistry } from '@mana_dashboard_base/mana_block_registry';
import { icons } from "@mana_dashboard_base/utils/mana_icons";
import { BlockBase } from "@mana_dashboard_base/mana_block_base";

const BaseModel = BlockBase.BaseModel;
const BaseView = BlockBase.BaseView;

import { _t } from "@web/core/l10n/translation";


let group_name = 1024;

function builder(editor, options) {

    const dc = editor.DomComponents;

    editor.BlockManager.add('search_group', {
        label: _t('Search Group'),
        category: _t('Search'),
        select: true,
        render: () => {
            return `<div class="d-flex flex-column align-items-center justify-content-center"><div class="chart-icon">${icons.search_group_svg}</div><div class='anita-block-label'>Group</div></div>`
        },
        content: {
            type: 'search_group',
        },
    });

    dc.addType('search_group', {
        model: BaseModel.extend({

            defaults: {
                ...BaseModel.prototype.defaults,

                name: _t('Search Group'),
                classes: ['search_group'],

                has_script: false,
                fetch_data: false,
                search_sensitive: false,
                search_item_id: 0,
                is_search: true,
                is_search_group: true,

                // toolbar
                toolbar_config: { 'edit_config': false },

                traits: [
                    {
                        type: 'form_trait',
                        name: 'form_trait',
                        label: 'Form',
                        model: 'mana_dashboard.search_group_traits',
                        form_view_ref: 'mana_dashboard.search_group_traits_form',
                        changeProp: 1,
                    }
                ]
            },

            get_custom_config_infos() {
                return [{
                    name: 'form_trait',
                    key: 'form_trait_id',
                    res_model: 'mana_dashboard.search_group_traits',
                    res_id: this.get('attributes').form_trait_id,
                }];
            },

            initialize() {
                BaseModel.prototype.initialize.apply(this, arguments);
                this.listenTo(this, 'change:form_trait', this.on_form_trait_change);
            },

            on_form_trait_change() {
                this.save_custom_props();
                let form_trait = this.get('form_trait');
                if (form_trait) {
                    let load_last_search = form_trait.load_last_search;
                    if (load_last_search) {
                        this.addAttributes({ load_last_search: '1' });
                    } else {
                        this.addAttributes({ load_last_search: '0' });
                    }
                    let name = form_trait.name;
                    this.addAttributes({ name: name });
                }
            },

            get_search_group_info() {
                if (this.view) {
                    return this.view.get_search_group_info();
                }
                return null;
            },

            /**
             * rewrite this method to parse config
             * @param {*} custom_props 
             */
            parse_custom_props(custom_props) {
                if (custom_props) {
                    custom_props = JSON.parse(custom_props);
                } else {
                    custom_props = {
                        search_immidiate: false,
                        type: 'global',
                        targets: [],
                    };
                }
                // check empty
                if (!custom_props.keys) {
                    custom_props = {
                        name: 'SG' + group_name++,
                        search_immidiate: false,
                        load_last_search: '1',
                        type: 'global',
                        targets: [],
                    };
                    let current_name = this.get('attributes').name;
                    if (!current_name) {
                        this.addAttributes({ name: custom_props.name });
                    } else {
                        custom_props.name = current_name;
                    }
                    this.addAttributes({ load_last_search: '1' });
                }
                this.set('form_trait', custom_props, { silent: true });
            },

            get_search_item_id() {
                let search_item_id = this.get('search_item_id');
                search_item_id += 1;
                this.set('search_item_id', search_item_id);
                return search_item_id;
            },

            /**
             * rewrite this method to get config
             */
            get_custom_props() {
                return this.get('form_trait') || '{}';
            },

            /**
             * get last search info
             */
            _get_last_search_info() {
                let dashboard = this.get_dashboard();
                if (dashboard) {
                    let name = this.get('attributes').name;
                    return dashboard.get_last_group_search_info(name);
                }
                return {};
            },

            /**
             * load last seach by item name
             * @param {*} key 
             */
            get_last_search(key) {
                let last_search_info = this._get_last_search_info();
                if (last_search_info) {
                    return last_search_info.search_infos[key];
                }
                return null;
            },

            /**
             * @returns 
             */
            load_last_search() {
                let load_last_search = this.get('attributes').load_last_search;
                if (load_last_search == '0') {
                    return false;
                } else {
                    return true;
                }
                return false;
            }

        }, {
            isComponent: (el) => {
                if (el && el.classList && el.classList.contains('search_group')) {
                    return { type: 'search_group' };
                }
            }
        }),

        view: BaseView.extend({

            events: {
                'click .search_button': '_onSearchButtonClick',
            },

            init() {
                BaseView.prototype.init.apply(this, arguments);
                this._on_search_item_changed = this._onSearchItemChanged.bind(this);
                this.el.addEventListener(
                    'mana_dashboard.search_item_changed', this._on_search_item_changed);
            },

            /**
             * on search item changed
             * @returns 
             */
            _onSearchItemChanged() {
                let form_trait = this.model.get('form_trait');
                if (!form_trait.keys) {
                    let search_immidiate = false;
                    // check has a search button
                    if (this.$el.find('.search_button').length == 0) {
                        search_immidiate = true;
                    }
                    form_trait = {
                        search_immidiate: search_immidiate,
                    }
                }

                let search_immidiate = form_trait.search_immidiate;
                if (!search_immidiate) {
                    return;
                }

                this._do_search();
            },

            /**
             * rewrite this method to add search button
             */
            get_search_group_info() {
                const search_items = this.$el.find('.search_item');
                let search_infos = {};
                for (let i = 0; i < search_items.length; i++) {
                    const search_item = search_items[i];
                    let search_model = grapesjs.$(search_item).data('model');
                    if (search_model) {
                        let search_info = search_model.getSearchInfo();
                        if (search_info) {
                            let key = search_info.key;
                            if (!key) {
                                continue;
                            }
                            search_infos[key] = search_info;
                        }
                    }
                }

                let form_trait = this.model.get('form_trait');

                return {
                    targets: form_trait && form_trait.targets || [],
                    type: form_trait && form_trait.type || 'global',
                    search_infos: form_trait && search_infos,
                    name: form_trait && form_trait.name || '',
                    is_global: form_trait && form_trait.is_global || false,
                }
            },

            /**
             * search button click
             * @param {*} event 
             * @returns 
             */
            _onSearchButtonClick(event) {
                const $el = $(event.currentTarget);
                if (!this.el.contains($el[0])) {
                    return;
                }
                let model = grapesjs.$(event.target).data('model');
                // check type
                let type = model.get('attributes').type;
                if (type == 'Reset') {
                    this._reset_search();
                }
                this._do_search();
            },

            _reset_search() {
                const search_items = this.$el.find('.search_item');
                for (let i = 0; i < search_items.length; i++) {
                    const search_item = search_items[i];
                    let search_model = grapesjs.$(search_item).data('model');
                    if (search_model) {
                        search_model.resetSearch();
                    }
                }
            },

            _do_search() {
                let dashboard = this.get_dashboard();
                if (dashboard) {
                    dashboard.trigger_up('mana_dashboard.do_search', true);
                }
            }
        })
    });
}

BlockRegistry.add('search_group', builder);
