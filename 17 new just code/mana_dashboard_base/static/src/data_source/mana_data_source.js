/** @odoo-module alias=mana_dashboard.data_source **/

import { Record } from "@mana_dashboard_base/data_source/mana_record";

export class DataSource {

    constructor(data_source, config) {

        this.raw_data_source = data_source;
        this.datas = data_source.datas;
        this.data_source_info = data_source.data_source_info;
        this.get_previous_data = this.data_source_info.get_previous_data;
        this.previous_datas = data_source.previous_datas || [];
        this.selections = data_source.selections || {}
        this.result_type = this.data_source_info.result_type;
        this.data_source_type = this.data_source_info.data_source_type_name;
        this.records = [];
        this.index = data_source.index;
        this.config = config;

        // init valid 
        this._valid = this.data_source_info.is_valid;

        // init raw field cache
        this._init_raw_fields_cache();
        this.hidden_fields = this.get_hidden_fields();

        // init data records
        if (!this.is_custom()) {
            this.init_data_records();
        }

        // init previous data source
        if (this.get_previous_data) {
            this._init_previous_data_source();
        }
    }

    get_previous_data_source() {
        return this.previous_data_source;
    }

    is_valid() {
        return this._valid;
    }

    get valid() {
        return this._valid;
    }

    /**
     * init data source
     * @returns 
     */
    init_data_records() {
        // check if it is a array
        if (!this.datas || !Array.isArray(this.datas)) {
            this.records = [];
            // need set valid ???
            if (this.data_source_type != 'none') {
                this._valid = false;
            }
            return;
        }
        let records = [];
        for (let i = 0; i < this.datas.length; i++) {
            let data = this.datas[i];
            let record = new Record(data);
            records.push(record);
        }
        this.records = records;
    }

    /**
     * init previous data
     */
    _init_previous_data_source() {
        let data_source = _.cloneDeep(this.raw_data_source);
        data_source.datas = this.previous_datas;
        delete data_source.previous_datas;
        this.previous_data_source = new DataSource(data_source, this.config);
    }

    /**
     * inti raw fields cache
     * @returns 
     */
    _init_raw_fields_cache() {
        this._raw_field_cache = {};
        if (!this.data_source_info.raw_fields) {
            return;
        }
        for (let i = 0; i < this.data_source_info.raw_fields.length; i++) {
            let raw_field = this.data_source_info.raw_fields[i];
            this._raw_field_cache[raw_field.name] = raw_field;
        }
    }

    is_custom() {
        return this.result_type != 'Standard';
    }

    get_model() {
        return this.data_source_info.model;
    }

    get_domain() {
        return this.data_source_info.domain;
    }

    get_context() {
        return this.data_source_info.context;
    }

    get_ids() {
        let ids = [];
        for (let i = 0; i < this.records.length; i++) {
            let record = this.records[i];
            ids.push(record.id);
        }
        return ids;
    }

    get_model_action() {
        if (this.is_get_data_from_model()) {
            return {
                type: 'ir.actions.act_window',
                name: this.data_source_info.name,
                res_model: this.data_source_info.model,
                views: [[false, 'list'], [false, 'form']],
                domain: [['id', 'in', this.get_ids()]]
            }
        }
    }

    is_get_data_from_model() {
        if (this.data_source_info.data_source_type_name == 'model') {
            return true;
        }
        return false;
    }

    is_get_data_from_sql() {
        if (this.data_source_info.data_source_type_name == 'sql') {
            return true;
        }
        return false;
    }

    get raw_datas() {
        return this.datas;
    }

    get_raw_datas() {
        return this.datas;
    }

    get_raw_data_source() {
        return this.raw_data_source;
    }

    get_records() {
        return this.records;
    }

    get_record(index) {
        return this.records[index];
    }

    get_record_by_col_value(col_name, col_value) {
        for (let i = 0; i < this.records.length; i++) {
            let record = this.records[i];
            let value = record.get_value(col_name);
            if (value == col_value) {
                return record;
            }
        }
        return null;
    }

    get_records_count() {
        return this.records.length;
    }

    get_raw_fields() {
        if (!this.data_source_info.raw_fields) {
            return [];
        }
        this._raw_field_cache = {};
        for (let i = 0; i < this.data_source_info.raw_fields.length; i++) {
            let raw_field = this.data_source_info.raw_fields[i];
            raw_field.title = raw_field.alias || raw_field.name;
            raw_field.field = raw_field.name;
            this._raw_field_cache[raw_field.name] = raw_field;
        }
        return this.data_source_info.raw_fields;
    }

    get_raw_field(name) {
        return this._raw_field_cache[name];
    }

    get_table_columns() {
        let columns = [];
        let raw_fields = this.get_raw_fields();
        for (let i = 0; i < raw_fields.length; i++) {
            let raw_field = raw_fields[i];
            if (raw_field.hidden) {
                continue;
            }
            let column = {
                title: raw_field.alias || raw_field.name,
                field: raw_field.name
            }
            columns.push(column);
        }
        return columns;
    }

    get_data_source_type() {
        return this.data_source_info.data_source_type_name;
    }

    get_data_source_info() {
        return this.data_source_info;
    }

    fields_as_category() {
        return this.data_source_info.fields_as_category;
    }

    has_previous_data() {
        return this.get_previous_data;
    }

    has_group_by() {
        if (this.is_get_data_from_model()) {
            return this.data_source_info.group_by_infos && this.data_source_info.group_by_infos.length > 0;
        } else {
            // raw fields
            let raw_fields = this.get_raw_fields();
            for (let i = 0; i < raw_fields.length; i++) {
                let raw_field = raw_fields[i];
                if (raw_field.group_by) {
                    return true;
                }
            }
        }
        return false;
    }

    has_multi_group_by() {
        if (this.is_get_data_from_model()) {
            return this.data_source_info.group_by_infos && this.data_source_info.group_by_infos.length > 1;
        } else {
            // raw fields
            let raw_fields = this.get_raw_fields();
            let group_by_count = 0;
            for (let i = 0; i < raw_fields.length; i++) {
                let raw_field = raw_fields[i];
                if (raw_field.group_by) {
                    group_by_count++;
                }
            }
            return group_by_count > 1;
        }
    }

    has_domain_field() {
        // check __domain in raw fields
        let raw_fields = this.get_raw_fields();
        for (let i = 0; i < raw_fields.length; i++) {
            let raw_field = raw_fields[i];
            if (raw_field.name == '__domain') {
                return true;
            }
        }
        return false;
    }

    get_first_group_by() {
        if (this.data_source_info.group_by_infos) {
            return this.data_source_info.group_by_infos[0];
        }
        return null;
    }

    has_order_by() {
        if (this.data_source_info.order_by_infos) {
            return true;
        }
        return false;
    }

    has_multi_order_by() {
        if (this.data_source_info.order_by_infos && this.data_source_info.order_by_infos.length > 1) {
            return true;
        }
        return false;
    }

    get_fields_info() {
        if (!this.data_source_info.model_fields) {
            return [];
        }
        return this.data_source_info.model_fields;
    }

    get_group_by_infos() {
        if (!this.data_source_info.group_by_infos) {
            return [];
        }
        return this.data_source_info.group_by_infos;
    }

    get_title() {
        return this.data_source_info.name;
    }

    get_max_value(column_name) {
        let max_value = 0;
        for (let i = 0; i < this.records.length; i++) {
            let record = this.records[i];
            let value = record.get_value(column_name);
            if (value > max_value) {
                max_value = value;
            }
        }
        return max_value;
    }

    get_display_name(column_name_or_names) {
        return this.get_alias(column_name_or_names);
    }

    get_alias(column_name_or_names) {
        if (!column_name_or_names) {
            return;
        }
        if (Array.isArray(column_name_or_names)) {
            return this.convert_to_alias(column_name_or_names);
        } else {
            let raw_field = this.get_raw_field(column_name_or_names);
            if (raw_field) {
                if (raw_field.alias) {
                    return raw_field.alias;
                }
            }
            return column_name_or_names;
        }
    }

    /**
     * use for column names
     * @param {*} column_names 
     * @returns 
     */
    convert_to_alias(column_names) {
        let alias_column_names = [];
        for (let i = 0; i < column_names.length; i++) {
            let column_name = column_names[i];
            let raw_field = this.get_raw_field(column_name);
            if (raw_field) {
                if (raw_field.alias) {
                    alias_column_names.push(raw_field.alias);
                } else {
                    alias_column_names.push(column_name);
                }
            } else {
                alias_column_names.push(column_name);
            }
        }
        return alias_column_names;
    }

    get_category_fields() {
        let category_fields = [];
        if (this.is_get_data_from_model()) {

            // get from raw fields
            if (category_fields.length == 0) {
                let raw_fields = this.get_raw_fields();
                for (let i = 0; i < raw_fields.length; i++) {
                    let raw_field = raw_fields[i];
                    if (raw_field.category || this.fields_as_category()) {
                        category_fields.push(raw_field);
                    }
                }
            }

            if (category_fields.length == 0) {
                // get first group by
                let group_by_infos = this.get_group_by_infos();
                if (group_by_infos.length > 0) {
                    let group_by_info = group_by_infos[0];
                    category_fields.push(group_by_info);
                }
            }

        } else {
            // get from raw fields
            let raw_fields = this.get_raw_fields();
            for (let i = 0; i < raw_fields.length; i++) {
                let raw_field = raw_fields[i];
                if (raw_field.category || this.fields_as_category()) {
                    category_fields.push(raw_field);
                }
            }
        }
        return category_fields;
    }

    get_hidden_fields() {
        let hidden_fields = {};
        let raw_fields = this.get_raw_fields();
        for (let i = 0; i < raw_fields.length; i++) {
            let raw_field = raw_fields[i];
            if (raw_field.hidden) {
                hidden_fields[raw_field.name] = raw_field;
            }
        }
        return hidden_fields;
    }

    is_hide_field(column_name) {
        if (column_name in this.hidden_fields) {
            return true;
        }
        return false;
    }

    /**
     * maybe has multi category
     * @returns 
     */
    get_categories() {
        let categories = [];
        // get category from fields info
        if (this.is_get_data_from_model()) {

            // get from raw fields
            if (categories.length == 0) {
                let raw_fields = this.get_raw_fields();
                for (let i = 0; i < raw_fields.length; i++) {
                    let raw_field = raw_fields[i];
                    if (raw_field.hidden) {
                        continue;
                    }
                    if (raw_field.category || this.fields_as_category()) {
                        categories.push(raw_field.name);
                    }
                }
            }

            if (categories.length == 0) {
                // get first group by
                let group_by_infos = this.get_group_by_infos();
                if (group_by_infos.length > 0) {
                    let group_by_info = group_by_infos[0];
                    categories.push(group_by_info.full_name);
                }
            }

        } else {
            // get from raw fields
            let raw_fields = this.get_raw_fields();
            for (let i = 0; i < raw_fields.length; i++) {
                let raw_field = raw_fields[i];
                if (raw_field.hidden) {
                    continue;
                }
                if (raw_field.category || this.fields_as_category()) {
                    categories.push(raw_field.name);
                }
            }
        }

        return categories;
    }

    get_category(index) {
        let categories = this.get_categories();
        if (index >= categories.length) {
            return null;
        }
        return categories[index];
    }

    /**
     * get category values
     * @param {*} category_name 
     * @returns 
     */
    get_category_values(category_name_or_index) {
        if (typeof category_name_or_index === 'number') {
            let category_name = this.get_category(category_name_or_index);
            return this.get_category_values(category_name);
        } else {
            let category_values = [];
            for (let i = 0; i < this.records.length; i++) {
                let record = this.records[i];
                let value = record.get_value(category_name);
                category_values.push(value);
            }
            return category_values;
        }
    }

    get_dimensions() {
        if (this.records.length == 0) {
            return [];
        }
        // get the first record keys
        let keys = Object.keys(this.records[0].record);
        return keys;
    }

    get_dimension_values(dimension_name) {
        let values = [];
        for (let i = 0; i < this.records.length; i++) {
            let record = this.records[i];
            let value = record.get_value(dimension_name);
            values.push(value);
        }
        return values;
    }

    get_array_style_datas() {
        let datas = [];
        let dimension_values = this.get_dimension_values();
        datas.push(dimension_values);
        for (let i = 0; i < this.records.length; i++) {
            let record = this.records[i];
            let values = [];
            for (let j = 0; j < dimension_values.length; j++) {
                let col_name = dimension_values[j];
                let value = record.get_value(col_name);
                values.push(value);
            }
            datas.push(values);
        }

        return datas;
    }

    get_field_info_by_name(field_name) {
        let fields_info = this.get_fields_info();
        for (let i = 0; i < fields_info.length; i++) {
            let field_info = fields_info[i];
            if (field_info.field_name == field_name) {
                return field_info;
            }
        }
        return null;
    }

    get_group_by_names() {
        let group_by_names = [];
        if (this.is_get_data_from_model()) {
            let group_by_infos = this.get_group_by_infos();
            for (let i = 0; i < group_by_infos.length; i++) {
                let group_by_info = group_by_infos[i];
                group_by_names.push(group_by_info.field_name);
            }
        } else {
            // get from raw fields
            let raw_fields = this.get_raw_fields();
            for (let i = 0; i < raw_fields.length; i++) {
                let raw_field = raw_fields[i];
                if (raw_field.group_by) {
                    group_by_names.push(raw_field.name);
                }
            }
        }
        return group_by_names;
    }

    get_field_names() {
        let field_names = [];
        let fields_info = this.get_fields_info();
        for (let i = 0; i < fields_info.length; i++) {
            let field_info = fields_info[i];
            field_names.push(field_info.field_name);
        }
        return field_names;
    }

    get_raw_field_names() {
        let field_names = [];
        let raw_fields = this.get_raw_fields();
        for (let i = 0; i < raw_fields.length; i++) {
            let raw_field = raw_fields[i];
            field_names.push(raw_field.field_name);
        }
        return field_names;
    }

    get_col_names(just_visible = true) {
        let col_names = [];
        let records = this.get_records();
        if (records.length > 0) {
            let record = records[0];
            let keys = record.get_col_names();
            col_names = keys.filter((key) => {
                if (just_visible) {
                    if (this.is_hide_field(key)) {
                        return false;
                    }
                }
                return true;
            });
            return col_names;
        }
        return [];
    }

    get_measures() {
        let measures = [];

        // get from raw fields first
        let fields = this.get_raw_fields();
        for (let i = 0; i < fields.length; i++) {
            let field = fields[i];
            if (field.measure) {
                measures.push(field.name);
            }
        }

        if (measures.length == 0) {
            if (this.is_get_data_from_model()) {
                let fields_info = this.get_fields_info();
                for (let i = 0; i < fields_info.length; i++) {
                    let field_info = fields_info[i];
                    if (field_info.measure) {
                        measures.push(field_info.field_name);
                    }
                }

                // use _count as measure
                if (measures.length == 0) {

                    for (let i = 0; i < fields.length; i++) {
                        let field = fields[i];
                        if (field.name == '__count') {
                            measures.push('__count');
                            break;
                        }
                    }

                    let col_names = this.get_col_names();
                    if (col_names.indexOf('__count') != -1) {
                        measures.push('__count');
                    }
                }

                // get integer float as measure
                if (measures.length == 0) {
                    let field_infos = this.get_fields_info();
                    for (let i = 0; i < field_infos.length; i++) {
                        let field_info = field_infos[i];
                        if (field_info.field_type == 'integer' || field_info.field_type == 'float') {
                            measures.push(field_info.field_name);
                        }
                    }
                }
            }
        }

        // unique
        measures = _.uniq(measures);
        return measures;
    }

    get_aggregate_columns() {
        let aggregate_columns = [];
        let fields = this.get_raw_fields();
        for (let i = 0; i < fields.length; i++) {
            let field = fields[i];
            if (field.column_arggregation) {
                aggregate_columns.push(field);
            }
        }
        return aggregate_columns;
    }

    get_first_aggregate_column_value() {
        let aggregate_columns = this.get_aggregate_columns();
        if (aggregate_columns.length > 0) {
            let aggregate_column = aggregate_columns[0];
            let aggregate_column_name = aggregate_column.name;
            let aggregate_column_value = this.get_aggregate_value(
                aggregate_column_name, aggregate_column.column_arggregation);
            return aggregate_column_value;
        } else {
            // check has __count
            let col_names = this.get_col_names();
            if (col_names.indexOf('__count') != -1) {
                let aggregate_column_value = this.get_aggregate_value('__count', 'sum');
                return aggregate_column_value;
            } else {
                // cout all records
                let records = this.get_records();
                return records.length;
            }
        }
    }

    format_name(name) {

        if (!name) {
            return ''
        }

        if (Array.isArray(name)) {
            if (name.length == 2) {
                if (Number.isInteger(name[0]) && typeof name[1] === 'string') {
                    return name[1];
                }
            }
            return name.join(',');
        }

        return name;
    }

    is_selection(col_name) {
        if (col_name in this.selections) {
            return true;
        }
        return false;
    }

    get_selection_val(col_name, key) {
        let selections = this.selections[col_name];
        for (let i = 0; i < selections.length; i++) {
            let selection = selections[i];
            if (selection[0] == key) {
                return selection[1];
            }
        }
        return key;
    }

    default_formater(col_name, val) {

        // check field type
        if (val instanceof Array) {
            if (val.length == 2) {
                return {
                    value: val[1],
                    origin_value: val
                }
            }
        }

        // check field is selction
        if (this.is_selection(col_name)) {
            return {
                value: this.get_selection_val(col_name, val),
                origin_value: val,
            }
        }

        return val
    }

    get_col_values(col_name, format = true, formatter = null) {
        let values = [];
        for (let i = 0; i < this.records.length; i++) {
            let record = this.records[i];
            let value = record.get_value(col_name);

            // check if it is a array
            if (format) {
                if (formatter) {
                    value = formatter(value);
                } else {
                    value = this.default_formater(col_name, value);
                }
            }
            values.push(value);
        }
        return values;
    }

    get_column_values(col_name, format = false) {
        return this.get_col_values(col_name, format);
    }

    get_unique_col_values(col_name, formatter = null) {
        let values = this.get_col_values(col_name, formatter);
        return _.uniq(values);
    }

    get_aggregate_value(col_name, aggregate_type) {
        let values = this.get_col_values(col_name);
        let aggregate_value = this.get_aggregate(values, aggregate_type);
        return aggregate_value;
    }

    get_aggregate(values, aggregate_type) {
        if (!values || values.length == 0) {
            return 0;
        }
        let aggregate_value = 0;
        if (aggregate_type == 'sum') {
            aggregate_value = this.get_sum(values);
        } else if (aggregate_type == 'avg') {
            aggregate_value = this.get_avg(values);
        } else if (aggregate_type == 'max') {
            aggregate_value = this.get_max(values);
        } else if (aggregate_type == 'min') {
            aggregate_value = this.get_min(values);
        } else if (aggregate_type == 'count') {
            aggregate_value = (values || []).length;
        }
        return aggregate_value;
    }

    get_sum(values) {
        let sum = 0;
        for (let i = 0; i < values.length; i++) {
            let value = values[i];
            sum += value;
        }
        return sum;
    }

    get_avg(values) {
        let sum = this.get_sum(values);
        let avg = sum / values.length;
        return avg;
    }

    get_max(values) {
        let max = values[0];
        for (let i = 1; i < values.length; i++) {
            let value = values[i];
            if (value > max) {
                max = value;
            }
        }
        return max;
    }

    get_min(values) {
        let min = values[0];
        for (let i = 1; i < values.length; i++) {
            let value = values[i];
            if (value < min) {
                min = value;
            }
        }
        return min;
    }

    get_cols_values(col_names) {
        let values = [];
        for (let i = 0; i < this.records.length; i++) {
            let record = this.records[i];
            let row_values = [];
            for (let j = 0; j < col_names.length; j++) {
                let col_name = col_names[j];
                let value = record.get_value(col_name);
                row_values.push(value);
            }
            values.push(row_values);
        }
        return values;
    }

    get_col_value(row_index, col_name) {
        let record = this.records[row_index];
        let value = record.get_value(col_name);
        return value;
    }

    get_row_values(row_index) {
        let record = this.records[row_index];
        let values = record.get_values();
        return values;
    }

    get_row_by_value(col_name, value) {
        let row_index = this.get_row_index_by_value(col_name, value);
        if (row_index != -1) {
            let record = this.records[row_index];
            return record;
        }
        return null;
    }

    get_row_index_by_value(col_name, value) {
        let row_index = -1;
        let tmp_val = value;
        // check if it is a array
        if (Array.isArray(tmp_val)) {
            // convert to string
            tmp_val = tmp_val.join(',');
        } else if (typeof tmp_val === 'object') {
            // convert to string
            tmp_val = JSON.stringify(tmp_val);
        }

        for (let i = 0; i < this.records.length; i++) {
            let record = this.records[i];
            let record_value = record.get_value(col_name);
            // check if it is a array
            if (Array.isArray(record_value)) {
                // convert to string
                record_value = record_value.join(',');
            } else if (typeof record_value === 'object') {
                // convert to string
                record_value = JSON.stringify(record_value);
            }
            if (record_value == tmp_val) {
                row_index = i;
                break;
            }
        }
        return row_index;
    }

    /**
     * get series data when group by greater than 1
     * @param {*} __group_by_name 
     * @param {*} measure_name 
     * @param {*} unique_category_values 
     * @param {*} category_name 
     * @returns 
     */
    get_group_by_name_values(
        __group_by_name, measure_name, unique_category_values, category_name) {
        let values = {};
        for (let i = 0; i < unique_category_values.length; i++) {
            let key = unique_category_values[i] + '__' + __group_by_name
            values[key] = 0;
        }
        // fill the values when _group_by_name and measure_name equal to the col_name
        for (let i = 0; i < this.records.length; i++) {
            let record = this.records[i];
            let category_value = record.get_value(category_name);
            let group_by_value = record.get_value('__group_by_name');
            let key = category_value + '__' + group_by_value;
            let value = record.get_value(measure_name);
            values[key] = value;
        }
        // return the values
        let result = [];
        for (let i = 0; i < unique_category_values.length; i++) {
            let key = unique_category_values[i] + '__' + __group_by_name;
            let value = values[key];
            result.push(value);
        }
        return result;
    }
}
