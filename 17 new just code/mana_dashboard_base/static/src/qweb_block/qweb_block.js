/** @odoo-module alias=mana_dashboard.qweb_block **/

import { BlockBase } from "@mana_dashboard_base/mana_block_base";
import { renderToString } from "@web/core/utils/render";
import { _t } from "@web/core/l10n/translation";

const BaseModel = BlockBase.BaseModel;
const BaseView = BlockBase.BaseView;


let QWebBlockModel = BaseModel.extend({

    defaults: {
        ...BaseModel.prototype.defaults,

        name: _t('QWeb Block'),
        classes: ['qweb_block'],

        has_template: true,
        render_mode: 'components',
    },

    initialize() {
        BaseModel.prototype.initialize.apply(this, arguments);
    },

    _update_script(scripts) {
        this.set('script', scripts);
    },

}, {
    isComponent: (el) => {
        if (el && el.classList && el.classList.contains('qweb_block')) {
            return {
                type: 'qweb_block',
            };
        }
    }
})

let QWebBlockView = BaseView.extend({

    init() {
        BaseView.prototype.init.apply(this, arguments);
        this.listenTo(this, 'change:loading_config', this._on_loading_change);
    },

    _on_loading_change() {},

    is_data_source_valid() {
        
        let data_sources = this.get_data_sources();
        if (!data_sources) {
            let config = this.get_config();
            let data_source_type = config.data_source_type;
            if (data_source_type == 'none') {
                return true;
            } else {
                return false;
            }
        }

        for (let i = 0; i < data_sources.length; i++) {
            let data_source = data_sources[i];
            if (!data_source || !data_source.is_valid()) {
                return false;
            }
        }

        return true;
    },

    /**
     * render template
     * @param {*} dict_data, data input by your self
     */
    render_template(dict_data, force = false) {

        if (!this.has_template()) {
            return;
        }

        // check is loading
        if (this.model.get('loading_config')) {
            return;
        }

        // check has componets
        if (this.model.components().length > 0 && !force) {
            return;
        }
    
        try {
            let template = this.model.get('template');
            if (template) {

                let qweb_template_id = undefined;
                let demo_mode = false;

                if (!this.is_data_source_valid()) {
                    let demo_template = this.model.get('demo_template');
                    if (demo_template) {
                        qweb_template_id = this.model.get_qweb_demo_template_id();
                    }
                    demo_mode = true;
                }

                if (!qweb_template_id) {
                    qweb_template_id = this.model.get_qweb_template_id();
                }

                // get demo data
                if (demo_mode && !dict_data) {
                    dict_data = this.model.get('demo_data') || {};
                }

                // check if it is a array
                if (Array.isArray(dict_data)) {
                    dict_data = {
                        datas: dict_data
                    }
                }
 
                // check render template in the script
                let html_str = renderToString(qweb_template_id, _.extend({
                    view: this,
                    config: this.model.get('config'),
                }, dict_data || {}));

                html_str = html_str.trim();
                // check html_str starts withc <div class="wrapper">
                if (html_str.startsWith('<div class="mana_wrapper">')) {
                    // trim the start <div class="wrapper">
                    html_str = _.str.ltrim(html_str, '<div class="mana_wrapper">');
                    // trim the end </div>
                    // html_str = _.str.rtrim(html_str, '</div>');
                    if (html_str.endsWith('</div>')) {
                        html_str = html_str.slice(0, -6);
                    }
                }
                
                this.model.components().reset();
                this.model.components().add(html_str);

                // find marquee, spical for marquee
                if (this.$el.find('.marquee').length) {
                    if (this.$el.parents('.mana_marquee').length) {
                        this.marquee();
                    }
                }
            }
        } catch (e) {
            let html_str = `<div class="alert alert-danger">${e.message}</div>`;
            this.$el.html(html_str);
            console.error(e);
        }
    },

    render(...args) {
        BaseView.prototype.render.apply(this, args);
        return this;
    },

    renderChildren() {
        BaseView.prototype.renderChildren.apply(this, arguments);
        this._on_loading_change();
    }
})

export const QWebBlock = {
    QWebBlockModel,
    QWebBlockView
}
