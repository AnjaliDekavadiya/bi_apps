odoo.define('sale_pricelist_gcs_advance.models', function (require) {
"use strict";

const { Product} = require('point_of_sale.models');
const Registries = require('point_of_sale.Registries');
const core = require('web.core');

const PosProduct = (Product) => class PosProduct extends Product {
    // Inherited the function to include product brand based pricelist rule
    get_price(pricelist, quantity, price_extra) {
        var self = this;
        var date = moment();
        // In case of nested pricelist, it is necessary that all pricelist are made available in
        // the POS. Display a basic alert to the user in this case.
        if (!pricelist) {
            alert(_t(
                'An error occurred when loading product prices. ' +
                'Make sure all pricelist are available in the POS.'
            ));
        }

        var category_ids = [];
        var category = this.categ;
        while (category) {
            category_ids.push(category.id);
            category = category.parent;
        }

        var pricelist_items = _.filter(self.applicablePricelistItems[pricelist.id], function (item) {
            return (! item.categ_id || _.contains(category_ids, item.categ_id[0])) &&
                   (! item.product_brand || _.contains([self.product_brand_gcs[0]], item.product_brand[0])) &&
                   (! item.categ_product_brand || _.contains([self.product_brand_gcs[0]], item.categ_product_brand[0])) &&
                   (! item.categ_brand_id || _.contains([self.categ_id[0]], item.categ_brand_id[0])) &&
                   (! item.date_start || moment.utc(item.date_start).isSameOrBefore(date)) &&
                   (! item.date_end || moment.utc(item.date_end).isSameOrAfter(date));
        });
        var price = self.lst_price;
        if (price_extra){
            price += price_extra;
        }
        _.find(pricelist_items, function (rule) {
            if (rule.min_quantity && quantity < rule.min_quantity) {
                return false;
            }

            if (rule.base === 'pricelist') {
                let base_pricelist = _.find(self.pos.pricelists, function (pricelist) {
                    return pricelist.id === rule.base_pricelist_id[0];});
                if (base_pricelist) {
                    price = self.get_price(base_pricelist, quantity);
                }
            } else if (rule.base === 'standard_price') {
                price = self.standard_price;
            }

            if (rule.compute_price === 'fixed') {
                price = rule.fixed_price;
                return true;
            } else if (rule.compute_price === 'percentage') {
                price = price - (price * (rule.percent_price / 100));
                return true;
            } else {
                var price_limit = price;
                price = price - (price * (rule.price_discount / 100));
                if (rule.price_round) {
                    price = round_pr(price, rule.price_round);
                }
                if (rule.price_surcharge) {
                    price += rule.price_surcharge;
                }
                if (rule.price_min_margin) {
                    price = Math.max(price, price_limit + rule.price_min_margin);
                }
                if (rule.price_max_margin) {
                    price = Math.min(price, price_limit + rule.price_max_margin);
                }
                return true;
            }
            return false;
        });
        // This return value has to be rounded with round_di before
        // being used further. Note that this cannot happen here,
        // because it would cause inconsistencies with the backend for
        // pricelist that have base == 'pricelist'.
        return price;
    }
}
Registries.Model.extend(Product, PosProduct);
});