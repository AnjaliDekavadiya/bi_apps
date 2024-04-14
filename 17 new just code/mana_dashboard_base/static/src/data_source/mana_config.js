/** @odoo-module alias=mana_dashboard.config **/

import { DataSource } from "@mana_dashboard_base/data_source/mana_data_source";


export class Config {

    constructor(config) {
        this.raw_config = config || {};
        this.multi_data_source = this.raw_config.multi_data_source || undefined;
        this.data_sources = [];
        this._init_data_sources();
    }

    _init_data_sources() {
        let index = 0;
        let data_sources = this.raw_config.data_sources || [];
        data_sources.forEach((data_source) => {
            data_source.index = index++;
            this.data_sources.push(new DataSource(data_source, this));
        });
    }

    get config_id() {
        return this.raw_config.id;
    }

    get_config_id() {
        return this.config_id;
    }

    get_ref_config_id() {
        return this.raw_config.ref_config_id;
    }

    get config_name() {
        return this.raw_config.config_name;
    }

    get_config_name() {
        return this.config_name;
    }

    get title() {
        return this.raw_config.config_name;
    }

    get_title() {
        return this.title;
    }

    has_data_source() {
        return this.data_sources.length > 0;
    }

    get_data_sources() {
        return this.data_sources;
    }

    get_data_source(index = 0) {
        if (index >= this.data_sources.length || index < 0) {
            return null;
        } else {
            return this.data_sources[index];
        }
    }

    get_first_data_source() {
        return this.get_data_source(0);
    }

    get data_source_count() {
        return this.data_sources.length;
    }

    get_data_source_count() {
        return this.data_source_count;
    }

    get first_data_source() {
        if (this.data_sources.length === 0) {
            return null;
        }
        return this.data_sources[0];
    }

    get_first_data_source() {
        return this.first_data_source;
    }

    get styles() {
        return this.get_styles();
    }

    get_styles() {
        return this.raw_config.styles;
    }

    get scripts() {
        return this.raw_config.scripts;
    }

    get_scripts() {
        return this.scripts;
    }

    get default_scripts() {
        return this.raw_config.default_scripts;
    }

    get_default_scripts() {
        return this.default_scripts;
    }

    get template() {
        return this.raw_config.template;
    }

    get_template() {
        return this.template;
    }

    get demo_template() {
        return this.raw_config.demo_template;
    }

    get_demo_template() {
        return this.demo_template;
    }

    get has_multi_data_source() {
        return this.raw_config.multi_data_source === true;
    }

    get_has_multi_data_source() {
        return this.has_multi_data_source;
    }

    get drill_down_config() {
        return this.raw_config.drill_down_config;
    }

    get_drill_down_config() {
        return this.drill_down_config;
    }

    get drill_up_config() {
        return this.raw_config.drill_up_config;
    }

    get_drill_up_config() {
        return this.drill_up_config;
    }

    get is_drill_down() {
        return this.raw_config.drill_down_config !== undefined;
    }

    get_is_drill_down() {
        return this.is_drill_down;
    }

    get linked_config_ids() {
        return this.raw_config.linked_config_ids;
    }

    get_linked_config_ids() {
        return this.linked_config_ids;
    }

    get data_source_type() {
        return this.raw_config.data_source_type;
    }

    get_data_source_type() {
        return this.data_source_type();
    }
}