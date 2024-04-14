/** @odoo-module alias=mana_dashboard.gauge_chart **/

import { BlockRegistry } from "@mana_dashboard_base/mana_block_registry";

import { icons } from "@mana_dashboard_base/utils/mana_icons";
import { date_utils } from "@mana_dashboard/utils/mana_date_util";
import { SearchItemBase } from "@mana_dashboard_search/search/mana_search_item";

const SearchItemModel = SearchItemBase.SearchItemModel;
const SearchItemView = SearchItemBase.SearchItemView;

import { _t } from "@web/core/l10n/translation";


function builder(editor, options) {

    const dc = editor.DomComponents;

    editor.BlockManager.add('time_range', {
        label: _t('Time Range'),
        category: _t('Search'),
        select: true,
        render: () => {
            return `<div class="d-flex flex-column align-items-center justify-content-center"><div class="chart-icon">${icons.time_range_svg}</div><div class='anita-block-label'>Time Range</div></div>`
        },
        content: {
            type: 'time_range',
        },
    });

    let traits = _.clone(SearchItemModel.prototype.defaults.traits);

    dc.addType('time_range', {
        model: SearchItemModel.extend({

            defaults: {
                ...SearchItemModel.prototype.defaults,
                name: _t('Time Range'),
                search_template: 'mana_dashboard.data_range',
                classes: SearchItemModel.prototype.defaults.classes.concat(['time_range']),
                traits: traits,
                attributes: _.extend({}, SearchItemModel.prototype.defaults.attributes, {
                    'operator': 'ilike',
                    'show_operator': false,
                    'submit_empty': false,
                    'show_label': false,
                }),
            },

            initialize() {
                SearchItemModel.prototype.initialize.apply(this, arguments);
            },

            resetSearch: function () {
                if (this.view) {
                    this.view.resetSearch();
                }
                this.model.set('value', false, { silent: true });
            },

            /**
             * get range info
             * @returns 
             */
            getSearchInfo() {
                if (this.view) {
                    const attributes = this.get('attributes');
                    let key = attributes && attributes.key || 'global_datetime_range'
                    let range_info = this.get('value')
                    if (!range_info) {
                        return null;
                    }
                    return {
                        key: key,
                        type: 'datetime_range',
                        start: range_info.start,
                        end: range_info.end,
                        range_type: range_info.range_type,
                        apply_to_params: this.apply_to_params()
                    }
                }
                return null;
            }
        }, {
            isComponent: (el) => {
                if (el && el.classList && el.classList.contains('time_range')) {
                    return { type: 'time_range' };
                }
            }
        }),

        view: SearchItemView.extend({

            on_picker_change(start, end, range_type) {

                this.model.set('value', {
                    start: start.format('YYYY-MM-DD HH:mm:ss'),
                    end: end.format('YYYY-MM-DD HH:mm:ss'),
                    range_type: range_type,
                }, { silent: true });

                this.trigger_change();
            },

            resetSearch() {
                this.model.set('value', null, { silent: true });
                $(this.el).find('input').val('');
            },

            init_datatimepicker() {

                let option = {
                    alwaysShowCalendars: true,
                    ranges: date_utils.date_ranges
                }

                // set current value
                let current_value = this.model.get_current_value();
                // check current value is a object
                if (typeof current_value === 'object') {
                    option.startDate = moment(current_value.start);
                    option.endDate = moment(current_value.end);
                    if (current_value.range_type) {
                        option.range_type = current_value.range_type;
                    }
                } else {
                    option.startDate = current_value;
                    option.endDate = current_value;
                    option.range_type = 'custom';
                }

                $(this.el).find('input').daterangepicker(
                    option, this.on_picker_change.bind(this));
            },

            render(...args) {
                SearchItemView.prototype.render.apply(this, args);

                if (this.model.get('components').length == 0) {
                    this.model.updateContent();
                }
                this.init_datatimepicker();
                this.model.set('state_inited', true);

                return this;
            }
        })
    });
}

BlockRegistry.add('time_range', builder);
