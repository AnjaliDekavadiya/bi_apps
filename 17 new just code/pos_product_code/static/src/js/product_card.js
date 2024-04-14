/** @odoo-module */

import { Component } from "@odoo/owl";
import { ProductCard } from "@point_of_sale/app/generic_components/product_card/product_card";


export class CustomProductCard extends ProductCard {
    static template = "point_of_sale.ProductCard";
    
    static props = {
        ...ProductCard.props,
        defaultCode: { String, optional: true },
    };

    static defaultProps = {
        ...ProductCard.defaultProps,
        defaultCode: "",
    };
}
