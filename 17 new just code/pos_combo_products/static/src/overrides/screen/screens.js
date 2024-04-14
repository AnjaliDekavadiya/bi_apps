/*@odoo-module */
/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : <https://store.webkul.com/license.html/> */
import { patch } from "@web/core/utils/patch";
import { onMounted } from "@odoo/owl";
import { ProductCard } from "@point_of_sale/app/generic_components/product_card/product_card";
import { Orderline } from "@point_of_sale/app/generic_components/orderline/orderline";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";
import { ComboPopupWidget } from "@pos_combo_products/overrides/popup/popup";
patch(ProductScreen.prototype, {
    async _clickProduct(event) {
        const product = event.detail;
        var self = this;
        if (product.is_combo_product) {
            var line;
            if (product.pos_combo_groups_ids && !product.product_variant_ids) {

                self.env.services.Popup.add(ComboPopupWidget, {
                    title: product.display_name,
                    groups: product.pos_combo_groups_ids,
                    product: product,
                    line: line,
                });
            } else {
                if (!this.currentOrder) {
                    this.env.services.pos.add_new_order();
                }
                const options = await this._getAddProductOptions(product);
                if (!options) return;

                self.env.services.Popup.add(ComboPopupWidget, {
                    title: product.display_name,
                    groups: product.pos_combo_groups_ids,
                    product: product,
                    line: line,
                    options: options,
                });
            }
        }
        else {
            super._clickProduct(event)
        }
    }
    ,
    _setValue(val) {
        var self = this;
        var curr_orderline = self.currentOrder.get_selected_orderline()
        if (curr_orderline === undefined) {
            super._setValue(val)
        } else {
            var combo_line = self.currentOrder.get_selected_orderline().product.is_combo_product;
            if (curr_orderline) {
                if (self.env.services.pos.numpadMode === 'quantity') {
                    if (!combo_line) {
                        super._setValue(val)
                    } else {
                        if (val != 'remove') {
                            curr_orderline.input_quantity = val
                            curr_orderline.set_quantity(val)
                            curr_orderline.set_unit_price(curr_orderline.price);
                        } else {
                            self.currentOrder.removeOrderline(curr_orderline)
                        }
                    }
                } else if (self.env.services.pos.numpadMode === 'price') {
                    if (!combo_line) {
                        super._setValue(val);
                    } else {

                        self.env.services.Popup.add(ErrorPopup, {
                            title: this.env._t('Not Allowed'),
                            body: this.env._t("You cannot change price of a Combo Product."),
                        });
                    }
                } else {
                    super._setValue(val)
                }
            } else {
                super._setValue(val)
            }
        }
    }
});
patch(ProductCard.prototype, {
    wk_is_combo_product(product_id) {
        var self = this;
        // var combo_products = self.env.services.pos.db.product_by_id;
        var combo_prod_items={}
        var len=0
        for (const product in self.env.services.pos.db.product_by_id){
            if (self.env.services.pos.db.product_by_id[product].is_combo_product == true){            
                combo_prod_items[product]=self.env.services.pos.db.product_by_id[product]
                len+=1
            }
        }
        // var combo_prod_items = combo_products.filter((product) => { return product.is_combo_product == true; });
        for (var i in combo_prod_items) {
            if (combo_prod_items[i].id == product_id && combo_prod_items[product_id].hide_product_price) {
               
                return true;
            }
        }
    }
});
patch(Orderline.prototype, {
    open_combo_popup() {
        self.env.services.popup.add(ComboPopupWidget, {
            title: this.props.line.orderline.product.display_name,
            groups: this.props.line.orderline.product.pos_combo_groups_ids,
            product: this.props.line.orderline.product,
            line: this.props.line.orderline,
        });
    }
})