/*@odoo-module*/

/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : <https://store.webkul.com/license.html/> */


import { Orderline, Order } from "@point_of_sale/app/store/models";
import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";
import { PosStore } from "@point_of_sale/app/store/pos_store";
import { ComboPopupWidget } from "@pos_combo_products/overrides/popup/popup";
import { parseFloat as oParseFloat } from "@web/views/fields/parsers";
import {
    formatFloat,
    roundDecimals as round_di,
    roundPrecision as round_pr,
    floatIsZero,
} from "@web/core/utils/numbers";
patch(PosStore.prototype, {
    async _processData(loadedData) {
        await super._processData(...arguments);
        this._loadPosComboGroups(loadedData["combo.groups"])
        this._loadPosComboProducts(loadedData["combo.products"])
    },
    _loadPosComboGroups: function (combo_groups) {
        if (combo_groups) {
            var self = this;
            self.db.all_combo_groups = combo_groups;
            self.db.all_combo_groups_by_id = {};
            combo_groups.forEach(function (combo_group) {
                self.db.all_combo_groups_by_id[combo_group.id] = combo_group;
            });
        }
    },
    _loadPosComboProducts: function (combo_products) {
        if (combo_products) {
            var self = this;
            self.db.all_combo_products = combo_products;
            self.db.all_combo_products_by_id = {};
            combo_products.forEach(function (combo_product) {
                self.db.all_combo_products_by_id[combo_product.id] = combo_product;
            });
        }
    },

    async addProductToCurrentOrder(product, options = {}) {
        if (Number.isInteger(product)) {
            product = this.db.get_product_by_id(product);
        }
        var self = this;
        if (product.is_combo_product) {
            var line;
            if (product.pos_combo_groups_ids && !product.product_variant_ids) {

                self.popup.add(ComboPopupWidget, {
                    title: product.display_name,
                    groups: product.pos_combo_groups_ids,
                    product: product,
                    line: line,
                });
            } else {
                this.get_order() || this.add_new_order();
                options = { ...options, ...(await product.getAddProductOptions()) };
                if (!Object.keys(options).length) {
                    return;
                }
                self.popup.add(ComboPopupWidget, {
                    title: product.display_name,
                    groups: product.pos_combo_groups_ids,
                    product: product,
                    line: line,
                    options: options,
                });
            }
        }
        else {
            super.addProductToCurrentOrder(product, options)
        }

    }

});
patch(Order.prototype, {
    setup(_defaultObj, options) {
        super.setup(...arguments)
        self = this;
        if (!options.json) {
            this.qty_combo_dict = this.qty_combo_dict || {};
            this.qty_wk_combo_ids = this.qty_wk_combo_ids || [];
            this.qty_combo_list_name = this.qty_combo_list_name || [];
        }

    },

    init_from_JSON(json) {
        super.init_from_JSON(...arguments);
        if (json.qty_combo_dict) {
            this.qty_combo_dict = json.qty_combo_dict
        }
        if (json.qty_wk_combo_ids) {
            this.qty_wk_combo_ids = json.qty_wk_combo_ids
        }
        if (json.qty_combo_list_name) {
            this.qty_combo_list_name = json.qty_combo_list_name
        }
    },
    export_as_JSON() {
        var json = super.export_as_JSON(...arguments);
        var current_order = this;
        if (current_order != null) {
            json.qty_combo_dict = current_order.qty_combo_dict;
            json.qty_wk_combo_ids = current_order.qty_wk_combo_ids;
            json.qty_combo_list_name = current_order.qty_combo_list_name;
        }
        return json;
    }
});
patch(Orderline.prototype, {
    setup(_defaultObj, options) {
        super.setup(...arguments)
        self = this;
        if (!options.json) {
            this.checked_wk_combo_ids = this.checked_wk_combo_ids || [];
            this.sel_combo_prod = this.sel_combo_prod || [];
            this.is_combo_product = this.is_combo_product || false;
            this.template_dict = this.template_dict || {};
            this.grid_template_dict = this.grid_template_dict || {};
            this.temp_arr = this.temp_arr || [];
            this.grid_temp_arr = this.grid_temp_arr || [];
            this.qty_combo_dict = this.qty_combo_dict || {};
        }

    },
    grid_get_combo_product() {
        var grid_temp_arr = []
        var self = this;
        for (var key of Object.keys(self.grid_template_dict)) {
            grid_temp_arr.push(self.grid_template_dict[key])
        }
        return grid_temp_arr;
    },
    get_combo_product() {
        var temp_arr = []
        var self = this;
        for (var key of Object.keys(self.template_dict)) {
            temp_arr.push(self.template_dict[key])
        }
        return temp_arr;
    },

    export_for_printing() {
        var self = this;
        var dict = super.export_for_printing(...arguments);
        dict.checked_wk_combo_ids = self.checked_wk_combo_ids;
        dict.sel_combo_prod = self.sel_combo_prod;
        dict.is_combo_product = self.is_combo_product;
        dict.template_dict = self.template_dict;
        dict.grid_template_dict = self.grid_template_dict;
        dict.grid_temp_arr = self.grid_temp_arr;
        dict.temp_arr = self.temp_arr;
        return dict;
    },
    init_from_JSON(json) {
        super.init_from_JSON(...arguments);
        var self = this
        if (json) {
            if (json.qty_combo_dict)
                this.qty_combo_dict = json.qty_combo_dict;
            if (json.checked_wk_combo_ids)
                this.checked_wk_combo_ids = json.checked_wk_combo_ids;
            if (json.sel_combo_prod)
                this.sel_combo_prod = JSON.parse(json.sel_combo_prod).combo_product_data;
            if (json.is_combo_product)
                this.is_combo_product = json.is_combo_product;
            this.template_dict = JSON.parse(json.sel_combo_prod).template_dict;
            this.grid_template_dict = JSON.parse(json.sel_combo_prod).grid_template_dict;
            this.temp_arr = json.temp_arr;
            this.grid_temp_arr = json.grid_temp_arr;
        }
    },
    export_as_JSON() {
        var json = super.export_as_JSON(...arguments);
        var current_order = this;
        if (current_order != null) {
            if (current_order.checked_wk_combo_ids)
                json.checked_wk_combo_ids = current_order.checked_wk_combo_ids;
            json.sel_combo_prod = JSON.stringify({ 'combo_product_data': current_order.sel_combo_prod, 'grid_template_dict': current_order.grid_template_dict, 'template_dict': current_order.template_dict });
            if (current_order.is_combo_product)
                json.is_combo_product = current_order.is_combo_product;
            if (current_order.template_dict)
                json.template_dict = current_order.template_dict;
            if (current_order.grid_template_dict)
                json.grid_template_dict = current_order.grid_template_dict;
            if (current_order.temp_arr)
                json.temp_arr = current_order.temp_arr;
            if (current_order.grid_temp_arr)
                json.grid_temp_arr = current_order.grid_temp_arr;
            if (current_order.qty_combo_dict)
                json.qty_combo_dict = current_order.qty_combo_dict;
        }
        return json;
    },
    getDisplayData() {
        var res =super.getDisplayData()
        res["orderline"]=this
        return res
    },
    can_be_merged_with(orderline) {
        var price = parseFloat(
            round_di(this.price || 0, this.pos.dp["Product Price"]).toFixed(
                this.pos.dp["Product Price"]
            )
        );
        var order_line_price = orderline
            .get_product()
            .get_price(orderline.order.pricelist, this.get_quantity());
        order_line_price = round_di(
            orderline.compute_fixed_price(order_line_price),
            this.pos.currency.decimal_places
        );
        if (this.get_product().id !== orderline.get_product().id) {    //only orderline of the same product can be merged
            return false;
        }
        else if (this.is_combo_product) {
            return false;
        }
        else if (!this.get_unit() || !this.get_unit().is_pos_groupable) {
            return false;
        } else if (this.get_discount() > 0) {             // we don't merge discounted orderlines
            return false;
        } else if (!floatIsZero(price - order_line_price - orderline.get_price_extra(),
            this.pos.currency.decimal_places)) {
            return false;
        } else if (this.product.tracking == 'lot' && (this.pos.picking_type.use_create_lots || this.pos.picking_type.use_existing_lots)) {
            return false;
        } else if (this.description !== orderline.description) {
            return false;
        } else if (orderline.get_customer_note() !== this.get_customer_note()) {
            return false;
        } else if (this.refunded_orderline_id) {
            return false;
        } else {
            return true;
        }
    },

});
