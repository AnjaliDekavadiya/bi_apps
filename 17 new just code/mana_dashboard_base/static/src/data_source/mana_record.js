/** @odoo-module alias=mana_dashboard.record **/

export class Record {

    constructor(record_data) {
        this.record_data = record_data;
    }

    get_value(col_name) {
        return this.record_data[col_name];
    }

    get col_names() {
        let col_names = [];
        for (let col_name in this.record_data) {
            col_names.push(col_name);
        }
        return col_names;
    }

    get_col_names() {
        return this.col_names;
    }

    get values() {
        let values = [];
        for (let col_name in this.record_data) {
            values.push(this.record_data[col_name]);
        }
        return values;
    }

    get_values() {
        return this.values;
    }
}
