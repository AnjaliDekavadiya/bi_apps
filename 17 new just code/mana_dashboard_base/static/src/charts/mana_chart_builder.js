/** @odoo-module alias=mana_dashboard.chart_builder default=false **/

import { BlockBase } from "@mana_dashboard_base/mana_block_base";
const BaseModel = BlockBase.BaseModel;
const BaseView = BlockBase.BaseView;

import { ResizeManager } from "@mana_dashboard_base/resize_manager/resize_manager";
const addResizeListener = ResizeManager.addResizeListener;
const removeResizeListener = ResizeManager.removeResizeListener;

import { evaluateExpr } from "@web/core/py_js/py";
import { _t } from "@web/core/l10n/translation";


export const builder = function (chart_info) {

    let ChartModel = BaseModel.extend({

        defaults: {
            ...BaseModel.prototype.defaults,
            classes: ['mana_chart', chart_info.chart_type],
            attributes: {
                'config_id': undefined,
                'chart_type': chart_info.chart_type,
            },
            droppable: false,
            traits: chart_info.traits || [],
            resizable: {
                tl: 0, // Top left
                tc: 1, // Top center
                tr: 0, // Top right
                cl: 0, // Center left
                cr: 0, // Center right
                bl: 0, // Bottom left
                bc: 1, // Bottom center
                br: 0, // Bottom right
            },
            default_option: chart_info.default_option,
            chart_type: chart_info.chart_type,
            default_template: chart_info.default_template,
            template_category: chart_info.template_category,
            template_type: chart_info.template_type,
            search_sensitive: chart_info.search_sensitive,
            enable_drill_down: chart_info.enable_drill_down || false,
            // traits
            traits: [
                {
                    type: 'option_trait',
                    name: 'option_trait',
                    label: _t('Block Settings'),
                    model: 'mana_dashboard.block_settings',
                    form_view_ref: 'mana_dashboard.block_settings_form',
                    context: {},
                    changeProp: 1,
                }
            ]
        },

        /**
         * rewrite this method to get config
         */
        get_default_props() {
            return {
                default_content: this.get('block_settings') || '{}'
            }
        },

        /**
         * initialize the model
         */
        initialize() {
            BaseModel.prototype.initialize.apply(this, arguments);

            this.on('change_date_range', () => {
                this.trigger('change:chart_option');
            });

            this.listenTo(this, 'change:attributes:config_id', this._onChangeConfigId);
            this.listenTo(this, 'change:option_trait', this.on_option_trait_change);
            this.listenTo(this, 'change:block_settings', this.on_block_settings_change);
        },

        /**
         * when the block settings change
         */
        on_block_settings_change() {
            if (this.view) {
                this.view._onOptionChanged();
            }
        },

        _onChangeConfigId() {
            this.set('chart_option', this.get('default_option'));
        },

        on_option_trait_change() {
            let option_trait = this.get('option_trait');
            let disable = option_trait.disable;
            let content = option_trait.content;
            if (disable) {
                content = '{}';
            }
            // replace null to Fasle
            content = content.replace(/null/g, 'false');
            let block_settings = evaluateExpr(content || '{}');
            this.set('block_settings', block_settings);
            this.save_custom_props();
        },

        /**
         * rewrite this method to parse config
         * @param {*} config 
         */
        parse_custom_props(custom_props) {
            custom_props = custom_props || {};
            custom_props = custom_props.replace(/null/g, 'false');
            let tmp_val = evaluateExpr(custom_props || '{}');
            this.set('block_settings', tmp_val, {
                silent: true
            });
        },

        merge() {
            // create a new object
            let target = {}

            // deep merge the object into the target object
            const merger = obj => {
                for (let prop in obj) {
                    if (obj.hasOwnProperty(prop)) {
                        if (typeof obj[prop] != typeof target[prop]) {
                            // if the types are different, skip
                            target[prop] = obj[prop]
                        } else if (Array.isArray(target[prop]) && Array.isArray(obj[prop])) {
                            // if both properties are arrays
                            for (let i = 0; i < obj[prop].length; i++) {
                                if (i >= target[prop].length) {
                                    // if the target array is shorter than the source array
                                    target[prop].push(obj[prop][i])
                                } else {
                                    if (Object.prototype.toString.call(obj[prop][i]) === '[object Object]') {
                                        // if the array item is a nested object
                                        target[prop][i] = this.merge(target[prop][i], obj[prop][i])
                                    } else {
                                        // for regular array item
                                        target[prop][i] = obj[prop][i]
                                    }
                                }
                            }
                        } else {
                            if (Object.prototype.toString.call(obj[prop]) === '[object Object]') {
                                // if the property is a nested object
                                target[prop] = this.merge(target[prop], obj[prop])
                            } else {
                                // for regular property
                                target[prop] = obj[prop]
                            }
                        }
                    }
                }
            }

            // iterate through all objects and
            // deep merge them with target
            for (let i = 0; i < arguments.length; i++) {
                merger(arguments[i])
            }

            return target
        },

        // clone the target object
        _clone(obj) {
            if (Array.isArray(obj)) {
                let arr = [];
                for (let i = 0; i < obj.length; i++) {
                    let item = obj[i];
                    arr.push(this._clone(item));
                }
                return arr;
            } else if (typeof obj === 'object') {
                let new_obj = {};
                for (let key in obj) {
                    let value = obj[key];
                    if (typeof value == 'object' || Array.isArray(value)) {
                        new_obj[key] = this._clone(value);
                    } else if (typeof value == 'function') {
                        // fake function
                        new_obj[key] = 'function(){}'
                    } else {
                        new_obj[key] = value;
                    }
                }
                return new_obj;
            } else if (typeof obj == 'function') {
                // fake function
                return 'function(){}'
            } else {
                return obj;
            }
        },

        get_chart_option() {
            let support_options = [];
            if (this.view && this.view.chart) {
                let chartOption = this.view.chart.getOption();
                if (chartOption) {
                    support_options = Object.keys(chartOption);
                }
            }
            let option = null;
            let extra_option = this.view.getExtraOption();
            let chart_option = this.get('chart_option');
            if (extra_option && chart_option) {
                option = this.merge(this._clone(chart_option), extra_option);
            }
            if (!option) {
                option = chart_option || extra_option;
            }
            option.support_options = support_options;
            return option;
        },

        /**
         * rewrite this method to get config
         */
        get_custom_props() {
            let block_settings = this.get('block_settings') || {};
            return block_settings;
        },

        /**
         * get custom config info
         */
        get_custom_config_infos() {
            return [{
                name: 'option_trait',
                key: 'form_trait_id',
                res_model: 'mana_dashboard.block_settings',
                res_id: this.get('attributes').form_trait_id,
            }];
        },

        /**
         * update script
         * @param {*} scripts 
         */
        _update_script(scripts) {
            // find var option by regex
            let var_option = scripts.match(/\s*var\s+option\s*=\s*/);
            let let_option = scripts.match(/\s*let\s+option\s*=\s*/);
            if (!var_option && !let_option) {
                scripts = 'let option = {};\n' + scripts;
            }
            // find this.set_option or this.setOption
            let set_option = scripts.match(/\s*this.set_option\s*\(/);
            let setOption = scripts.match(/\s*this.setOption\s*\(/);
            if (!set_option && !setOption) {
                scripts = scripts + '\n this.set_option(option);';
            }
            BaseModel.prototype._update_script.apply(this, [scripts]);
        }

    }, {
        isComponent: chart_info.isComponent,
    });

    let ChartView = BaseView.extend({

        init() {
            BaseView.prototype.init.apply(this, arguments);

            // init the chart
            this.chart = null;
            this._onResize = this.onResize.bind(this);

            // old width
            this.old_width = 0;
            this.old_height = 0;

            // listen to the data change event
            this.listenTo(
                this.model, 'change:chart_option', this._onOptionChanged);

            let env = this.get_env();

            // listen to the theme chagned
            this.onDashboardThemeChanged = this._onDashboardThemeChanged.bind(this);
            env.bus.addEventListener(
                'mana_dashboard.dashboard_theme_changed', this.onDashboardThemeChanged);
        },

        initResizeListener() {

            let is_dragging = this.model.get('is_dragging');
            if (is_dragging) {
                return;
            }

            let config_id = this.model.get('attributes').config_id;
            if (!config_id) {
                return;
            }

            // remove the resize event
            removeResizeListener(this.el, this._onResize);

            // deal container resize event
            addResizeListener(this.el, this._onResize);
        },

        /**
         * theme changed
         */
        _onDashboardThemeChanged() {

            if (this.chart) {
                this.chart.dispose();
                this.chart = null;
            }

            setTimeout(() => {
                this.render();
            }, 0);
        },

        _onchange_theme() {
            this._onDashboardThemeChanged();
        },

        /**
         * clear the chart option 
         */
        beforeScriptExecuted() {
            this.model.set('chart_option', null, {
                silent: true
            });
        },

        afterScriptExecuted() {

            if (this.chart) {
                this.chart.resize();
            }

            let config_id = this.model.get('attributes').config_id;
            if (!config_id) {
                return;
            }

            // check editor_ready
            let editor_ready = this.model.get('editor_ready');
            if (!editor_ready) {
                return;
            }

            let loading_config = this.model.get('loading_config');
            if (loading_config) {
                return;
            }

            if (this.model.get('has_script') && this.model.get('script')) {
                let chart_option = this.model.get('chart_option');
                if (!chart_option) {
                    let default_scripts = this.model.get('default_scripts');
                    if (!default_scripts) {
                        this.model.set('chart_option', this.model.get('default_option'));
                    } else {
                        setTimeout(() => {
                            this.model.execute_default_script();
                        }, 0);
                    }
                }
            }
        },

        _onOptionChanged() {
            let chart_option = this.model.get('chart_option');
            if (this.chart && chart_option) {
                this.chart.setOption(chart_option, {
                    notMerge: true
                });
            } else {
                this.renderChart(chart_option);
            }
            let extra_option = JSON.parse(JSON.stringify(this.getExtraOption() || {}));
            // tranverse chart options to eval function
            // function tranverse(obj) {
            //     if (Array.isArray(obj)) {
            //         for (let i = 0; i < obj.length; i++) {
            //             let item = obj[i];
            //             tranverse(item);
            //         }
            //     } else if (typeof obj === 'object') {
            //         for (let key in obj) {
            //             let value = obj[key];
            //             if (typeof value === 'object' || Array.isArray(value)) {
            //                 tranverse(value);
            //             } else {
            //                 if (typeof value === 'string') {
            //                     // check is it is a function or lambda
            //                     if (value.indexOf('function') === 0) {
            //                         obj[key] = eval(value);
            //                     }
            //                 }
            //             }
            //         }
            //     } else {
            //         if (typeof value === 'string') {
            //             if (value.indexOf('function') === 0) {
            //                 obj[key] = eval(value);
            //             }
            //         }
            //     }
            // }
            // tranverse(extra_option);
            this.chart.setOption(extra_option, {
                notMerge: false
            });
        },

        onResize(content) {

            if (!this.chart) {
                return;
            }

            let is_dragging = this.model.get('is_dragging');
            if (is_dragging) {
                return;
            }

            this.resizeChart(content);
        },

        resizeChart(content) {
            if (this.chart) {
                let width = content.contentRect.width;
                let height = content.contentRect.height;
                if (width == this.old_width && height == this.old_height) {
                    return;
                }
                this.old_width = width;
                this.old_height = height;
                this.chart.resize();
            }
        },

        handleClick(e) {
            e.preventDefault();
        },

        renderChart(chart_option) {
            if (!this.chart) {
                let theme = this.model.get('theme');
                if (theme) {
                    let theme_name = this.model.get('theme_name');
                    this.chart = echarts.init(this.el, theme_name);
                } else {
                    // set the global theme
                    let dashboard = this.get_dashboard();
                    if (dashboard) {
                        let global_theme = dashboard.get_theme_name();
                        if (global_theme) {
                            this.chart = echarts.init(this.el, global_theme);
                        }
                    }
                }

                if (!this.chart) {
                    this.chart = echarts.init(this.el);
                }
            }
            chart_option && this.chart.setOption(chart_option, {
                notMerge: true
            });

            // resize listener
            requestAnimationFrame(() => {
                this.initResizeListener();
            });

            // bind the click event
            this.chart.on('click', (params) => {
                let dashboard = this.get_dashboard();
                if (dashboard.is_prevew_widget()) {
                    return;
                }
                if (params.componentType === 'series') {
                    this.onSeriesClick(params);
                }
            });
        },

        /**
         * on click the series
         * @param {*} params 
         */
        onSeriesClick(params) {

            let data_index = params.dataIndex;
            let category = params.name;
            let value = params.value;
            let chart_option = this.model.get('chart_option');

            let data = params.data;

            if (data && typeof data === 'object') {
                if (data.origin_value) {
                    category = data.origin_value;
                }
            } else {
                if (chart_option.get_category_by_index) {
                    category = chart_option.get_category_by_index(data_index);
                } else {
                    let x_axis = chart_option.xAxis;
                    let categroy_data = x_axis && x_axis.data && x_axis.data[data_index];
                    if (categroy_data) {
                        if (typeof categroy_data === 'object' && categroy_data.origin_value) {
                            category = categroy_data.origin_value;
                        }
                    }
                }
            }

            let config = this.model.get('config');
            let drill_down_config = config.drill_down_config;
            if (drill_down_config) {
                let config_id = parseInt(drill_down_config[0]);
                // component type
                this.trigger_up('mana_dashboard.drill_down', {
                    config_id: config_id,
                    category: category,
                    model: this.model,
                    value: value
                });
            } else {
                if (config.linked_config_ids && config.linked_config_ids.length > 0) {
                    // component type
                    this.trigger_up('mana_dashboard.linked_actions', {
                        linked_config_ids: config.linked_config_ids,
                        category: category,
                        model: this.model,
                        value: value
                    });
                } else {
                    // component type
                    this.trigger_up('mana_dashboard.view_chart_data', {
                        category: category,
                        model: this.model,
                        value: value,
                        params: params
                    });
                }
            }
        },

        getExtraOption() {
            let settings = this.model.get('block_settings');
            return settings;
        },

        setOption(option) {
            option.timestamp = new Date().getTime();
            this.model.set('chart_option', option);
        },

        set_option(option) {
            this.setOption(option);
        },

        setChartOption(option) {
            this.setOption(option);
        },

        set_chart_option(option) {
            this.setOption(option);
        },

        getDataSource(index = 0) {
            return this.get_data_source(index);
        },

        setChartOption(option) {
            option.timestamp = new Date().getTime();
            this.model.set('chart_option', option);
        },

        removed() {
            BaseView.prototype.removed.apply(this, arguments);

            let env = this.get_env();
            env.bus.removeEventListener(
                'mana_dashboard.dashboard_theme_changed', this.onDashboardThemeChanged);
            removeResizeListener(this.el, this._onResize);

            if (this.chart) {
                this.chart.dispose();
                this.chart = null;
            }
        },

        render(...args) {
            BaseView.prototype.render.apply(this, args);
            if (this.chart) {
                try {
                    this.chart.dispose();
                } catch (error) {
                    console.error(error);
                }
                this.chart = null;
            }

            // check editor editor_ready
            let editor_ready = this.model.get('editor_ready');
            if (!editor_ready) {
                return this;
            }

            let option = null;
            let config = this.model.get('config');
            if (config && !this.model.get('loading_config')) {
                option = this.model.get('chart_option');
                if (!option) {
                    let dfault_scripts = this.model.get('default_scripts');
                    if (!dfault_scripts) {
                        option = this.model.get('default_option');
                    }
                }
                if (option) {
                    this.model.set('chart_option', option);
                }
            }

            return this;
        }
    });

    return (editor, opts = {}) => {

        let dc = editor.DomComponents;

        /**
         * chart info
         */
        editor.BlockManager.add(chart_info.type, {
            label: chart_info.label,
            category: _t('Charts'),
            select: true,
            render: chart_info.render,
            content: chart_info.content,
        });

        /**
         * add the component
         */
        dc.addType(chart_info.chart_type, {
            model: ChartModel,
            view: ChartView
        });
    }
}
